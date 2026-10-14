#!/usr/bin/env python3
# fed_node_survey.py -- SURVEY paper federated node (aggregator | client) over S3.
# Turunan dari aws/fed_node.py (Paper 4), DISESUAIKAN untuk paper SURVEY:
#   - TIDAK memakai SFM. Fitur = hasil "manual feature-name alignment" (lihat
#     notebooks2/s01_fed_data_partition.ipynb). Node ini agnostik: ia hanya memuat
#     X dari <id>_train.npz; penyelarasan fitur sudah dilakukan di s01.
#   - Prefix S3 TERPISAH: unsw-far/federated_survey/ (agar tak menimpa Paper 4).
#   - Tambahan HOOK ADVERSARIAL TRAINING (R6): FGSM constrained pada ruang fitur
#     ter-standardisasi (z-space), dikendalikan --adv-ratio dan --adv-eps.
#
# Pola operasional Paper 2/4: AL2023 + boto3 (JANGAN `aws s3 cp` di instance).
# Transport: S3 unsw-far/federated_survey/run_<RUN>/round_<t>/...
#   aggregator: tulis global_<t>.npz -> tunggu client_<k>_<t>.npz -> FedAvg -> global_<t+1>.npz
#   client:     tunggu global_<t>.npz -> latih lokal E epoch -> tulis client_<id>_<t>.npz
#
# Contoh (via SSM pada tiap EC2):
#   python3 fed_node_survey.py --role aggregator --run S_R3 --clients cic,unsw --rounds 100 --mu 0.0
#   python3 fed_node_survey.py --role client --client-id cic  --run S_R3 --rounds 100 --local-epochs 5
#   python3 fed_node_survey.py --role client --client-id unsw --run S_R3 --rounds 100 --local-epochs 5
# R1 (FedProx): tambah --mu 0.01 (atau 0.1) di SEMUA client.
# R6 (adv-training): tambah --adv-ratio 0.5 --adv-eps 0.1 di SEMUA client.
#
# Data klien (dari s01) diharapkan di S3 unsw-far/federated_survey/data/<id>/<id>_train.npz

import argparse, io, time, sys
import numpy as np

try:
    import boto3
except ImportError:
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "boto3"], check=True)
    import boto3

BUCKET = "ssh-detection-features-232032302717"
REGION = "ap-southeast-1"
BASE   = "unsw-far/federated_survey"          # <-- prefix survey, TERPISAH dari Paper 4
s3 = boto3.client("s3", region_name=REGION)

# ---------- S3 helpers (npz in-memory) ----------
def s3_put_npz(key, **arrs):
    buf = io.BytesIO(); np.savez_compressed(buf, **arrs); buf.seek(0)
    s3.put_object(Bucket=BUCKET, Key=key, Body=buf.getvalue())

def s3_get_npz(key):
    try:
        obj = s3.get_object(Bucket=BUCKET, Key=key)
    except s3.exceptions.NoSuchKey:
        return None
    except Exception:
        return None
    return np.load(io.BytesIO(obj["Body"].read()), allow_pickle=True)

def s3_exists(key):
    try:
        s3.head_object(Bucket=BUCKET, Key=key); return True
    except Exception:
        return False

def wait_for(key, timeout=1800, poll=5):
    t0 = time.time()
    while time.time() - t0 < timeout:
        if s3_exists(key): return True
        time.sleep(poll)
    return False

# ---------- Tiny MLP (numpy): 9 -> 128 -> 64 -> 1 (sigmoid) ----------
# Input 9 = jumlah fitur hasil manual alignment (s01). Jika s01 memakai jumlah
# fitur lain, sesuaikan LAYERS[0].
LAYERS = [9, 128, 64, 1]

def init_weights(seed=42):
    rng = np.random.RandomState(seed); W=[]
    for a,b in zip(LAYERS[:-1], LAYERS[1:]):
        W.append(rng.randn(a,b)*np.sqrt(2.0/a)); W.append(np.zeros(b))
    return W

def _relu(x): return np.maximum(0,x)
def _sig(x):  return 1.0/(1.0+np.exp(-np.clip(x,-30,30)))

def forward(W, X):
    h = X
    a1=h@W[0]+W[1]; z1=_relu(a1)
    a2=z1@W[2]+W[3]; z2=_relu(a2)
    a3=z2@W[4]+W[5]; out=_sig(a3).ravel()
    cache=(X,a1,z1,a2,z2,a3,out)
    return out, cache

# ---------- Gradien terhadap INPUT (untuk FGSM adversarial, R6) ----------
def input_gradient(W, X, y):
    """dL/dX untuk BCE+sigmoid (dipakai membuat adversarial examples FGSM)."""
    out,(X_,a1,z1,a2,z2,a3,o)=forward(W,X)
    g=(o-y.astype(float))[:,None]          # dL/da3  (N,1)
    d2=(g@W[4].T)*(a2>0)                    # ke z2 -> a2
    d1=(d2@W[2].T)*(a1>0)                   # ke z1 -> a1
    dX=d1@W[0].T                            # ke input
    return dX

def make_adv_fgsm(W, X, y, eps, lo, hi):
    """FGSM CONSTRAINED di z-space: x' = clip(x + eps*sign(dL/dX), [lo,hi]).
    Clip ke rentang [lo,hi] (persentil fitur) menjaga plausibilitas flow."""
    dX = input_gradient(W, X, y)
    Xadv = X + eps*np.sign(dX)
    return np.clip(Xadv, lo, hi)

def train_local(W, X, y, epochs=1, lr=1e-3, batch=256, mu=0.0, W_global=None, seed=42,
                adv_ratio=0.0, adv_eps=0.1, feat_lo=None, feat_hi=None):
    # SGD BCE; FedProx proximal (mu) menarik ke W_global.
    # adv_ratio>0 -> ADVERSARIAL TRAINING (R6): sebagian batch diganti FGSM example.
    rng=np.random.RandomState(seed); n=len(y); W=[w.copy() for w in W]
    if feat_lo is None: feat_lo = X.min(0)
    if feat_hi is None: feat_hi = X.max(0)
    for _ in range(epochs):
        idx=rng.permutation(n)
        for s in range(0,n,batch):
            bi=idx[s:s+batch]; Xb=X[bi].copy(); yb=y[bi].astype(float)
            # --- Adversarial training hook (R6) ---
            if adv_ratio>0.0:
                m=int(len(bi)*adv_ratio)
                if m>0:
                    sel=rng.choice(len(bi), size=m, replace=False)
                    Xb[sel]=make_adv_fgsm(W, Xb[sel], yb[sel], adv_eps, feat_lo, feat_hi)
            # --- forward + backprop ---
            out,(X_,a1,z1,a2,z2,a3,o)=forward(W,Xb)
            g=(o-yb)/len(yb)                       # dL/da3 (BCE+sigmoid)
            gW4=z2.T@g[:,None]; gb4=g.sum(0)
            d2=(g[:,None]@W[4].T)*(a2>0)
            gW2=z1.T@d2; gb2=d2.sum(0)
            d1=(d2@W[2].T)*(a1>0)
            gW0=X_.T@d1; gb0=d1.sum(0)
            gall=[gW0,gb0,gW2,gb2,gW4,gb4]
            for i,gv in enumerate(gall):
                gv=np.asarray(gv).reshape(W[i].shape)
                if mu>0 and W_global is not None:
                    gv=gv+mu*(W[i]-W_global[i])
                W[i]=W[i]-lr*gv
    return W

def fedavg(weight_list, sizes):
    tot=float(sum(sizes)); out=[]
    for i in range(len(weight_list[0])):
        acc=sum((sizes[k]/tot)*weight_list[k][i] for k in range(len(weight_list)))
        out.append(acc)
    return out

def zscore_fit(X):
    mu=X.mean(0); sd=X.std(0); sd[sd==0]=1.0; return mu,sd
def zscore_apply(X,mu,sd): return (X-mu)/sd

# ---------- Roles ----------
def run_aggregator(run, clients, rounds, mu, seed):
    W=init_weights(seed)
    for t in range(rounds):
        s3_put_npz(f"{BASE}/run_{run}/round_{t}/global_{t}.npz", **{f"w{i}":w for i,w in enumerate(W)})
        print(f"[agg] round {t}: global published, waiting clients...", flush=True)
        cw=[]; cs=[]
        for cid in clients:
            key=f"{BASE}/run_{run}/round_{t}/client_{cid}_{t}.npz"
            if not wait_for(key): print(f"[agg] TIMEOUT waiting {cid} r{t}"); return
            d=s3_get_npz(key); cw.append([d[f"w{i}"] for i in range(6)]); cs.append(int(d["n"]))
        W=fedavg(cw,cs)
        print(f"[agg] round {t}: aggregated from {len(cw)} clients (sizes={cs})", flush=True)
    s3_put_npz(f"{BASE}/run_{run}/global_final.npz", **{f"w{i}":w for i,w in enumerate(W)})
    print("[agg] DONE -> global_final.npz", flush=True)

def run_client(cid, run, rounds, epochs, lr, mu, seed, adv_ratio, adv_eps):
    d=s3_get_npz(f"{BASE}/data/{cid}/{cid}_train.npz")
    if d is None: print(f"[client {cid}] data not found in S3 ({BASE}/data/{cid}/)"); return
    X=np.asarray(d["X"],float); y=np.asarray(d["y"],int)
    mu_z,sd_z=zscore_fit(X); Xz=zscore_apply(X,mu_z,sd_z)   # per-client LOCAL z-score (privasi)
    # Batas fitur untuk clip adversarial (persentil 1-99 di z-space, menjaga plausibilitas)
    feat_lo=np.percentile(Xz,1,axis=0); feat_hi=np.percentile(Xz,99,axis=0)
    tag = f"adv(ratio={adv_ratio},eps={adv_eps})" if adv_ratio>0 else "clean"
    print(f"[client {cid}] data {X.shape}, pos-rate {y.mean():.3f}, mode={tag}", flush=True)
    for t in range(rounds):
        gkey=f"{BASE}/run_{run}/round_{t}/global_{t}.npz"
        if not wait_for(gkey): print(f"[client {cid}] TIMEOUT global r{t}"); return
        g=s3_get_npz(gkey); Wg=[g[f"w{i}"] for i in range(6)]
        Wl=train_local(Wg, Xz, y, epochs=epochs, lr=lr, mu=mu, W_global=Wg, seed=seed,
                        adv_ratio=adv_ratio, adv_eps=adv_eps, feat_lo=feat_lo, feat_hi=feat_hi)
        s3_put_npz(f"{BASE}/run_{run}/round_{t}/client_{cid}_{t}.npz",
                   **{f"w{i}":w for i,w in enumerate(Wl)}, n=np.array(len(y)))
        print(f"[client {cid}] round {t}: local update sent", flush=True)
    print(f"[client {cid}] DONE", flush=True)

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--role", required=True, choices=["aggregator","client"])
    ap.add_argument("--run", default="S_R1")
    ap.add_argument("--clients", default="cic,unsw", help="aggregator: comma list of client ids")
    ap.add_argument("--client-id", default="cic")
    ap.add_argument("--rounds", type=int, default=100)
    ap.add_argument("--local-epochs", type=int, default=5)
    ap.add_argument("--lr", type=float, default=3e-3)
    ap.add_argument("--mu", type=float, default=0.0, help=">0 enables FedProx (R1)")
    ap.add_argument("--adv-ratio", type=float, default=0.0, help=">0 enables adversarial training (R6)")
    ap.add_argument("--adv-eps", type=float, default=0.1, help="FGSM epsilon in z-space (R6)")
    ap.add_argument("--seed", type=int, default=42)
    a=ap.parse_args()
    if a.role=="aggregator":
        run_aggregator(a.run, [c.strip() for c in a.clients.split(",")], a.rounds, a.mu, a.seed)
    else:
        run_client(a.client_id, a.run, a.rounds, a.local_epochs, a.lr, a.mu, a.seed,
                   a.adv_ratio, a.adv_eps)
