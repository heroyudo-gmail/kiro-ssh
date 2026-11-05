#!/usr/bin/env python3
"""Near-domain orchestrator for the JOURNAL (extended) paper.

Menjalankan FL near-domain (Client-CIC2017 + Client-CIC2018, ~76 fitur) di 3 EC2
yang SAMA dengan survei (template & stack dipakai ulang), tetapi:
  - node = fed_node_journal.py (input-dim dinamis, prefix S3 bisa di-set, + eval akhir)
  - prefix S3 = federated_journal/neardomain (TERPISAH dari data survei)
  - pemetaan instance: ClientCIC -> client-id cic2017, ClientUNSW -> client-id cic2018
  - multi-seed; aggregator menjalankan --eval di akhir (MCC fed/centralized/local-only)

Prasyarat (dari jA_01_partition_neardomain.ipynb):
  s3://<BUCKET>/federated_journal/neardomain/data/{cic2017,cic2018}/{..}_train.npz, _test.npz

Contoh:
  # 1) uji pipeline cepat 10 ronde (1 seed)
  python run_journal_neardomain.py --rounds 10 --up --deploy --setup --run --seeds 42
  # 2) run penuh 5 seed, 100 ronde
  python run_journal_neardomain.py --rounds 100 --run --seeds 13 42 101 202 303
  # 3) status / teardown
  python run_journal_neardomain.py --status
  python run_journal_neardomain.py --teardown
"""
import argparse, os, sys, time
import boto3

BUCKET = "ssh-detection-features-232032302717"
REGION = "ap-southeast-1"
STACK = "fed-nids-survey"                       # reuse stack yang sama (hemat)
BASE = "federated_journal/neardomain"
SCRIPT_KEY = f"{BASE}/scripts/fed_node_journal.py"
TEMPLATE = "fed-vpc-3ec2-public.yaml"
NODE_SCRIPT = "fed_node_journal.py"
CLIENTS = ["cic2017", "cic2018"]               # ClientCIC -> cic2017, ClientUNSW -> cic2018

cf = boto3.client("cloudformation", region_name=REGION)
ssm = boto3.client("ssm", region_name=REGION)
s3 = boto3.client("s3", region_name=REGION)


def log(m): print(f"[journal-near] {m}", flush=True)
def here(p): return os.path.join(os.path.dirname(os.path.abspath(__file__)), p)

def s3_exists(key):
    try: s3.head_object(Bucket=BUCKET, Key=key); return True
    except Exception: return False

def stack_outputs():
    try: st = cf.describe_stacks(StackName=STACK)["Stacks"][0]
    except Exception: return None
    if st["StackStatus"] not in ("CREATE_COMPLETE", "UPDATE_COMPLETE"):
        return {"_status": st["StackStatus"]}
    out = {o["OutputKey"]: o["OutputValue"] for o in st.get("Outputs", [])}
    out["_status"] = st["StackStatus"]; return out

def upload_node_script():
    p = here(NODE_SCRIPT); assert os.path.exists(p), f"tidak ketemu {p}"
    s3.upload_file(p, BUCKET, SCRIPT_KEY); log(f"upload node -> s3://{BUCKET}/{SCRIPT_KEY}")

def deploy_stack():
    if stack_outputs() is not None:
        log(f"stack {STACK} sudah ada; lewati create."); return
    with open(here(TEMPLATE)) as f: body = f.read()
    log(f"create-stack {STACK} ...")
    cf.create_stack(StackName=STACK, TemplateBody=body,
                    Parameters=[{"ParameterKey": "ProjectName", "ParameterValue": STACK}],
                    Capabilities=["CAPABILITY_IAM"])
    cf.get_waiter("stack_create_complete").wait(StackName=STACK)
    log("stack CREATE_COMPLETE")

def wait_ssm_online(ids, timeout=600):
    log("menunggu SSM online ..."); t0 = time.time()
    while time.time() - t0 < timeout:
        info = ssm.describe_instance_information(
            Filters=[{"Key": "InstanceIds", "Values": ids}])["InstanceInformationList"]
        if set(ids).issubset({i["InstanceId"] for i in info if i["PingStatus"] == "Online"}):
            log("semua online"); return True
        time.sleep(10)
    log("TIMEOUT SSM"); return False

def ssm_run(iid, cmds, timeout=900, wait=True):
    r = ssm.send_command(InstanceIds=[iid], DocumentName="AWS-RunShellScript",
                         TimeoutSeconds=timeout, Parameters={"commands": cmds})
    cid = r["Command"]["CommandId"]
    if not wait: return cid
    time.sleep(3)
    while True:
        inv = ssm.get_command_invocation(CommandId=cid, InstanceId=iid)
        if inv["Status"] in ("Success", "Failed", "Cancelled", "TimedOut"): return inv
        time.sleep(5)

def setup_nodes(ids):
    dl = ("import boto3; boto3.client('s3',region_name='%s')"
          ".download_file('%s','%s','/opt/fed/%s'); print('ready')"
          % (REGION, BUCKET, SCRIPT_KEY, NODE_SCRIPT))
    cmds = ["sudo dnf -y install python3-pip >/tmp/pip.log 2>&1",
            "python3 -m pip install -q --user boto3 numpy >/tmp/pipuser.log 2>&1",
            "mkdir -p /opt/fed", 'python3 -c "%s"' % dl]
    for iid in ids:
        log(f"setup {iid} ..."); inv = ssm_run(iid, cmds, timeout=900)
        if inv["Status"] != "Success":
            log(f"  setup GAGAL {iid}: {inv['Status']}\n{inv.get('StandardErrorContent','')[:500]}")
            return False
    log("setup selesai"); return True

def run_tag(seed): return f"J_NEAR_s{seed}"

def build_cmds(tag, rounds, seed):
    b = f"cd /opt/fed && python3 {NODE_SCRIPT} --base-prefix {BASE}"
    return {
        "cic": f'{b} --role client --client-id cic2017 --run {tag} --rounds {rounds} '
               f'--local-epochs 5 --seed {seed} >/tmp/{tag}_cic2017.log 2>&1 &',
        "unsw": f'{b} --role client --client-id cic2018 --run {tag} --rounds {rounds} '
                f'--local-epochs 5 --seed {seed} >/tmp/{tag}_cic2018.log 2>&1 &',
        "agg": f'{b} --role aggregator --clients {",".join(CLIENTS)} --run {tag} '
               f'--rounds {rounds} --seed {seed} --eval >/tmp/{tag}_agg.log 2>&1 &',
    }

def run_done(tag): return s3_exists(f"{BASE}/run_{tag}/eval_results.json")

def launch(out, tag, rounds, seed):
    cmds = build_cmds(tag, rounds, seed)
    ssm_run(out["ClientCICId"], [cmds["cic"]], wait=False)
    ssm_run(out["ClientUNSWId"], [cmds["unsw"]], wait=False)
    time.sleep(5)
    ssm_run(out["AggregatorId"], [cmds["agg"]], wait=False)
    log(f"run {tag} dilepas (seed={seed}, rounds={rounds})")

def wait_done(tag, rounds, poll=20):
    key = f"{BASE}/run_{tag}/eval_results.json"
    timeout = max(1200, rounds * 40)   # +eval di akhir -> sedikit lebih lama
    log(f"menunggu s3://{BUCKET}/{key} (timeout ~{timeout}s) ...")
    t0 = time.time()
    while time.time() - t0 < timeout:
        if s3_exists(key): log(f"SELESAI: {tag}/eval_results.json"); return True
        time.sleep(poll)
    log(f"TIMEOUT: {tag} belum eval_results.json. Cek /tmp/{tag}_agg.log via --tail."); return False

def tail_log(out, which, seed, n=30):
    tag = run_tag(seed)
    iid = {"agg": out["AggregatorId"], "cic": out["ClientCICId"], "unsw": out["ClientUNSWId"]}[which]
    nm = {"agg": "agg", "cic": "cic2017", "unsw": "cic2018"}[which]
    inv = ssm_run(iid, [f"tail -n {n} /tmp/{tag}_{nm}.log 2>/dev/null"], timeout=60)
    print(inv.get("StandardOutputContent", ""))

def show_status():
    out = stack_outputs()
    if out is None: log("stack TIDAK ada.")
    else:
        log(f"stack status: {out.get('_status')}")
        for k in ("AggregatorId", "ClientCICId", "ClientUNSWId"):
            if k in out: log(f"  {k} = {out[k]}")
    for seed in (13, 42, 101, 202, 303):
        tag = run_tag(seed)
        log(f"  seed {seed:<3} {tag}/eval_results.json : {'ADA' if run_done(tag) else 'belum'}")

def teardown():
    log(f"delete-stack {STACK} ...")
    cf.delete_stack(StackName=STACK)
    cf.get_waiter("stack_delete_complete").wait(StackName=STACK)
    log("stack dihapus. Biaya -> nol. Hasil aman di S3.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rounds", type=int, default=100)
    ap.add_argument("--up", action="store_true")
    ap.add_argument("--deploy", action="store_true")
    ap.add_argument("--setup", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--seeds", type=int, nargs="+", default=[42])
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--tail", choices=["agg", "cic", "unsw"])
    ap.add_argument("--tail-seed", type=int, default=42)
    ap.add_argument("--teardown", action="store_true")
    a = ap.parse_args()

    if a.dry_run:
        for seed in a.seeds:
            tag = run_tag(seed); print(f"[dry-run] seed={seed} tag={tag}")
            for role, cmd in build_cmds(tag, a.rounds, seed).items():
                print(f"   {role:5s} {cmd}")
        return
    if a.teardown: teardown(); return
    if a.up: upload_node_script()
    if a.deploy: deploy_stack()

    out = stack_outputs()
    need = a.setup or a.run or a.tail
    if need:
        if out is None or "AggregatorId" not in out:
            log("stack belum siap. Jalankan --deploy dulu."); sys.exit(1)
        ids = [out["AggregatorId"], out["ClientCICId"], out["ClientUNSWId"]]
    if a.setup:
        if not wait_ssm_online(ids): sys.exit(1)
        if not setup_nodes(ids): sys.exit(1)
    if a.run:
        for seed in a.seeds:
            tag = run_tag(seed)
            if run_done(tag): log(f"lewati {tag}: eval_results.json sudah ada"); continue
            launch(out, tag, a.rounds, seed)
            if not wait_done(tag, a.rounds):
                log(f"GAGAL menunggu {tag}; stop. Cek --tail agg --tail-seed {seed}"); sys.exit(1)
    if a.tail: tail_log(out, a.tail, a.tail_seed)
    if a.status or not any([a.up, a.deploy, a.setup, a.run, a.tail]):
        show_status()


if __name__ == "__main__":
    main()
