#!/usr/bin/env python3
"""Block B orchestrator for the FL-NIDS SURVEY paper (R3 + R6 on 3 real EC2).

Menjalankan seluruh Blok B dari laptop/SageMaker lewat boto3 (tanpa SSH, hanya SSM):
  upload skrip node -> deploy stack -> tunggu SSM online -> setup node ->
  run S_R3 (FedAvg) -> tunggu global_final.npz -> run S_R6 (adv-training) ->
  tunggu hasil -> lapor ringkas. Teardown TIDAK otomatis (lihat --teardown).

Prasyarat (sudah dikerjakan di jalur s01):
  s3://<BUCKET>/unsw-far/federated_survey/data/{cic,unsw}/{cic,unsw}_train.npz

Contoh pakai:
  # 1) uji pipeline cepat (10 ronde) untuk memastikan semuanya nyambung
  python run_survey_blockB.py --rounds 10 --up --deploy --setup --run-r3 --run-r6

  # 2) run penuh 100 ronde (kalau uji 10 ronde sukses)
  python run_survey_blockB.py --rounds 100 --run-r3 --run-r6

  # 3) cek hasil di S3 kapan saja
  python run_survey_blockB.py --status

  # 4) WAJIB setelah hasil aman: hapus stack (biaya -> nol)
  python run_survey_blockB.py --teardown

Catatan: langkah-langkah bisa dijalankan terpisah (flag per-tahap). Tanpa flag
tahap apa pun, skrip hanya mencetak status. Jalankan dari folder ini (federated/aws)
agar template & skrip node ketemu, atau pakai --here untuk path eksplisit.
"""
import argparse
import io
import os
import sys
import time

import boto3

# --------------------------- KONFIG ---------------------------
BUCKET = "ssh-detection-features-232032302717"
REGION = "ap-southeast-1"
STACK = "fed-nids-survey"
BASE = "unsw-far/federated_survey"
SCRIPT_KEY = f"{BASE}/scripts/fed_node_survey.py"
TEMPLATE = "fed-vpc-3ec2-public.yaml"
NODE_SCRIPT = "fed_node_survey.py"

cf = boto3.client("cloudformation", region_name=REGION)
ssm = boto3.client("ssm", region_name=REGION)
s3 = boto3.client("s3", region_name=REGION)


# --------------------------- helpers ---------------------------
def log(msg):
    print(f"[blockB] {msg}", flush=True)


def here(path):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), path)


def s3_exists(key):
    try:
        s3.head_object(Bucket=BUCKET, Key=key)
        return True
    except Exception:
        return False


def stack_outputs():
    try:
        st = cf.describe_stacks(StackName=STACK)["Stacks"][0]
    except Exception:
        return None
    if st["StackStatus"] not in ("CREATE_COMPLETE", "UPDATE_COMPLETE"):
        return {"_status": st["StackStatus"]}
    out = {o["OutputKey"]: o["OutputValue"] for o in st.get("Outputs", [])}
    out["_status"] = st["StackStatus"]
    return out


def upload_node_script():
    p = here(NODE_SCRIPT)
    assert os.path.exists(p), f"tidak ketemu {p}"
    s3.upload_file(p, BUCKET, SCRIPT_KEY)
    log(f"upload skrip node -> s3://{BUCKET}/{SCRIPT_KEY}")


def deploy_stack():
    with open(here(TEMPLATE)) as f:
        body = f.read()
    exists = stack_outputs() is not None
    if exists:
        log(f"stack {STACK} sudah ada; lewati create.")
        return
    log(f"create-stack {STACK} ...")
    cf.create_stack(
        StackName=STACK,
        TemplateBody=body,
        Parameters=[{"ParameterKey": "ProjectName", "ParameterValue": STACK}],
        Capabilities=["CAPABILITY_IAM"],
    )
    cf.get_waiter("stack_create_complete").wait(StackName=STACK)
    log("stack CREATE_COMPLETE")


def wait_ssm_online(instance_ids, timeout=600):
    log("menunggu SSM agent online di 3 instance ...")
    t0 = time.time()
    while time.time() - t0 < timeout:
        info = ssm.describe_instance_information(
            Filters=[{"Key": "InstanceIds", "Values": instance_ids}]
        )["InstanceInformationList"]
        online = {i["InstanceId"] for i in info if i["PingStatus"] == "Online"}
        if set(instance_ids).issubset(online):
            log("semua instance online di SSM")
            return True
        time.sleep(10)
    log("TIMEOUT menunggu SSM online")
    return False


def ssm_run(instance_id, commands, timeout=900, wait=True):
    r = ssm.send_command(
        InstanceIds=[instance_id],
        DocumentName="AWS-RunShellScript",
        TimeoutSeconds=timeout,
        Parameters={"commands": commands},
    )
    cid = r["Command"]["CommandId"]
    if not wait:
        return cid
    time.sleep(3)
    while True:
        inv = ssm.get_command_invocation(CommandId=cid, InstanceId=instance_id)
        if inv["Status"] in ("Success", "Failed", "Cancelled", "TimedOut"):
            return inv
        time.sleep(5)


def setup_nodes(ids):
    dl = ("import boto3; "
          "boto3.client('s3',region_name='%s')"
          ".download_file('%s','%s','/opt/fed/%s'); "
          "print('ready')" % (REGION, BUCKET, SCRIPT_KEY, NODE_SCRIPT))
    cmds = [
        "sudo dnf -y install python3-pip >/tmp/pip.log 2>&1",
        "python3 -m pip install -q --user boto3 numpy >/tmp/pipuser.log 2>&1",
        "mkdir -p /opt/fed",
        'python3 -c "%s"' % dl,
    ]
    for iid in ids:
        log(f"setup node {iid} ...")
        inv = ssm_run(iid, cmds, timeout=900)
        if inv["Status"] != "Success":
            log(f"  setup GAGAL di {iid}: {inv['Status']}\n{inv.get('StandardErrorContent','')[:500]}")
            return False
    log("setup 3 node selesai")
    return True


LEGACY_SEED = 42   # run lama S_R3 / S_R6 memakai seed 42 (nama tanpa sufiks)


def run_tag_for(base, seed):
    """Seed 42 -> nama lama (S_R3 / S_R6); seed lain -> S_R3_s13, S_R6_s13, ..."""
    return base if seed == LEGACY_SEED else f"{base}_s{seed}"


def build_cmds(run_tag, rounds, extra_client="", seed=LEGACY_SEED):
    base = f"cd /opt/fed && python3 {NODE_SCRIPT}"
    # log per-run agar dua run paralel tidak saling menimpa
    return {
        "cic": f'{base} --role client --client-id cic --run {run_tag} --rounds {rounds} '
               f'--local-epochs 5 --seed {seed} {extra_client} >/tmp/{run_tag}_cic.log 2>&1 &',
        "unsw": f'{base} --role client --client-id unsw --run {run_tag} --rounds {rounds} '
                f'--local-epochs 5 --seed {seed} {extra_client} >/tmp/{run_tag}_unsw.log 2>&1 &',
        "agg": f'{base} --role aggregator --run {run_tag} --clients cic,unsw --rounds {rounds} '
               f'--mu 0.0 --seed {seed} >/tmp/{run_tag}_agg.log 2>&1 &',
    }


def run_exists(run_tag):
    return s3_exists(f"{BASE}/run_{run_tag}/global_final.npz")


def launch_run(out, run_tag, rounds, extra_client="", seed=LEGACY_SEED):
    agg, cic, unsw = out["AggregatorId"], out["ClientCICId"], out["ClientUNSWId"]
    cmds = build_cmds(run_tag, rounds, extra_client, seed)
    # client dulu (background), lalu aggregator (background)
    ssm_run(cic, [cmds["cic"]], wait=False)
    ssm_run(unsw, [cmds["unsw"]], wait=False)
    time.sleep(5)
    ssm_run(agg, [cmds["agg"]], wait=False)
    log(f"run {run_tag} dilepas (seed={seed}, rounds={rounds}, extra_client='{extra_client.strip()}')")


def wait_final(run_tag, rounds, poll=20):
    key = f"{BASE}/run_{run_tag}/global_final.npz"
    # timeout kasar: proporsional ke rounds (2 klien kecil, numpy MLP -> cepat)
    timeout = max(900, rounds * 30)
    log(f"menunggu s3://{BUCKET}/{key} (timeout ~{timeout}s) ...")
    t0 = time.time()
    while time.time() - t0 < timeout:
        if s3_exists(key):
            log(f"SELESAI: {run_tag}/global_final.npz tersedia")
            return True
        time.sleep(poll)
    log(f"TIMEOUT: {run_tag} belum menghasilkan global_final.npz. Cek /tmp/agg.log via SSM.")
    return False


def tail_log(out, which="agg", n=25, tag="S_R3"):
    iid = {"agg": out["AggregatorId"], "cic": out["ClientCICId"],
           "unsw": out["ClientUNSWId"]}[which]
    inv = ssm_run(iid, [f"tail -n {n} /tmp/{tag}_{which}.log 2>/dev/null || tail -n {n} /tmp/{which}.log"],
                  timeout=60)
    print(inv.get("StandardOutputContent", ""))


def show_status():
    out = stack_outputs()
    if out is None:
        log("stack TIDAK ada (belum deploy atau sudah teardown).")
    else:
        log(f"stack status: {out.get('_status')}")
        for k in ("AggregatorId", "ClientCICId", "ClientUNSWId"):
            if k in out:
                log(f"  {k} = {out[k]}")
    for seed in (13, 42, 101, 202, 303):
        for base in ("S_R3", "S_R6"):
            tag = run_tag_for(base, seed)
            log(f"  seed {seed:<3} {tag}/global_final.npz : {'ADA' if run_exists(tag) else 'belum'}")


def teardown():
    log(f"delete-stack {STACK} ...")
    cf.delete_stack(StackName=STACK)
    cf.get_waiter("stack_delete_complete").wait(StackName=STACK)
    log("stack dihapus. Biaya EC2 -> nol. Hasil tetap aman di S3.")


# --------------------------- main ---------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rounds", type=int, default=100)
    ap.add_argument("--up", action="store_true", help="upload skrip node ke S3")
    ap.add_argument("--deploy", action="store_true", help="create stack 3 EC2")
    ap.add_argument("--setup", action="store_true", help="setup node via SSM")
    ap.add_argument("--run-r3", action="store_true", help="jalankan S_R3 (FedAvg) + tunggu")
    ap.add_argument("--run-r6", action="store_true", help="jalankan S_R6 (adv-training) + tunggu")
    ap.add_argument("--seeds", type=int, nargs="+", default=None,
                    help="daftar seed untuk --run-r3/--run-r6 (default: 42 = run lama). "
                         "Contoh: --seeds 13 101 202 303")
    ap.add_argument("--dry-run", action="store_true",
                    help="cetak perintah per run lalu keluar (tanpa menyentuh AWS)")
    ap.add_argument("--status", action="store_true", help="cek status stack & hasil")
    ap.add_argument("--tail", choices=["agg", "cic", "unsw"], help="tail log via SSM")
    ap.add_argument("--teardown", action="store_true", help="hapus stack (WAJIB setelah selesai)")
    a = ap.parse_args()
    seeds = a.seeds or [LEGACY_SEED]
    kinds = []
    if a.run_r3:
        kinds.append(("S_R3", ""))
    if a.run_r6:
        kinds.append(("S_R6", "--adv-ratio 0.5 --adv-eps 0.1"))

    if a.dry_run:
        for seed in seeds:
            for base, extra in kinds:
                tag = run_tag_for(base, seed)
                print(f"[dry-run] seed={seed} tag={tag}")
                for role, cmd in build_cmds(tag, a.rounds, extra, seed).items():
                    print(f"   {role:5s} {cmd}")
        return

    if a.teardown:
        teardown()
        return
    if a.up:
        upload_node_script()
    if a.deploy:
        deploy_stack()

    out = stack_outputs()
    need_nodes = a.setup or a.run_r3 or a.run_r6 or a.tail
    if need_nodes:
        if out is None or "AggregatorId" not in out:
            log("stack belum siap. Jalankan --deploy dulu.")
            sys.exit(1)
        ids = [out["AggregatorId"], out["ClientCICId"], out["ClientUNSWId"]]

    if a.setup:
        if not wait_ssm_online(ids):
            sys.exit(1)
        if not setup_nodes(ids):
            sys.exit(1)

    # per seed: R3 dan R6 dilepas bersamaan (paralel), lalu ditunggu keduanya.
    # Run yang global_final.npz-nya sudah ada dilewati (aman untuk di-resume).
    for seed in seeds:
        pending = []
        for base, extra in kinds:
            tag = run_tag_for(base, seed)
            if run_exists(tag):
                log(f"lewati {tag}: global_final.npz sudah ada")
                continue
            launch_run(out, tag, a.rounds, extra_client=extra, seed=seed)
            pending.append(tag)
        for tag in pending:
            if not wait_final(tag, a.rounds):
                log(f"GAGAL menunggu {tag}; hentikan agar tidak boros. Cek log via --tail.")
                sys.exit(1)

    if a.tail:
        tail_log(out, a.tail)

    if a.status or not any([a.up, a.deploy, a.setup, a.run_r3, a.run_r6, a.tail]):
        show_status()


if __name__ == "__main__":
    main()
