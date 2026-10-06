#!/usr/bin/env python3
# fed_node.py -- Paper 4 federated node (aggregator | client) over S3 weight transport.
# Pola Paper 2: AL2023 + boto3 (JANGAN aws s3 cp di instance). MLP ringan (numpy).
# Transport: S3 unsw-far/federated/run_<RUN>/round_<t>/...
#   aggregator: tulis global_<t>.npz  -> tunggu client_<k>_<t>.npz -> FedAvg -> global_<t+1>.npz
#   client:     tunggu global_<t>.npz -> latih lokal E epoch -> tulis client_<id>_<t>.npz
#
# Jalankan via SSM pada tiap EC2:
#   python3 fed_node.py --role aggregator --run R2 --clients cic,unsw --rounds 100 --mu 0.0
#   python3 fed_node.py --role client --client-id cic  --run R2 --rounds 100 --local-epochs 5
#   python3 fed_node.py --role client --client-id unsw --run R2 --rounds 100 --local-epochs 5
#
# Data klien (dari nb01) diharapkan di S3 unsw-far/federated/data/<id>/<id>_train.npz
# ARG --mu > 0 mengaktifkan FedProx (proximal term).

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
BASE   = "unsw-far/federated"
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
def train_local(W, X, y, epochs=1, lr=1e-3, batch=256, mu=0.0, W_global=None, seed=42):
    # SGD BCE; FedProx proximal (mu) menarik ke W_global.
    rng=np.random.RandomState(seed); n=len(y); W=[w.copy() for w in W]
    for _ in range(epochs):
        idx=rng.permutation(n)
        for s in range(0,n,batch):
            bi=idx[s:s+batch]; Xb=X[bi]; yb=y[bi].astype(float)
            out,(X_,a1,z1,a2,z2,a3,o)=forward(W,Xb)
            g=(o-yb)/len(yb)                       # dL/da3 (BCE+sigmoid)
            gW4=z2.T@g[:,None]; gb4=g.sum(0)
            d2=(g[:,None]@W[4].T)*(a2>0)
            gW2=z1.T@d2; gb2=d2.sum(0)
            d1=(d2@W[2].T)*(a1>0)
            gW0=X_.T@d1; gb0=d1.sum(0)
            # index mapping: W[0]=W0,W[1]=b0,W[2]=W2,W[3]=b2,W[4]=W4,W[5]=b4
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

def run_client(cid, run, rounds, epochs, lr, mu, seed):
    d=s3_get_npz(f"{BASE}/data/{cid}/{cid}_train.npz")
    if d is None: print(f"[client {cid}] data not found in S3"); return
    X=np.asarray(d["X"],float); y=np.asarray(d["y"],int)
    mu_z,sd_z=zscore_fit(X); Xz=zscore_apply(X,mu_z,sd_z)   # per-client LOCAL z-score (privasi)
    print(f"[client {cid}] data {X.shape}, pos-rate {y.mean():.3f}", flush=True)
    for t in range(rounds):
        gkey=f"{BASE}/run_{run}/round_{t}/global_{t}.npz"
        if not wait_for(gkey): print(f"[client {cid}] TIMEOUT global r{t}"); return
        g=s3_get_npz(gkey); Wg=[g[f"w{i}"] for i in range(6)]
        Wl=train_local(Wg, Xz, y, epochs=epochs, lr=lr, mu=mu, W_global=Wg, seed=seed)
        s3_put_npz(f"{BASE}/run_{run}/round_{t}/client_{cid}_{t}.npz",
                   **{f"w{i}":w for i,w in enumerate(Wl)}, n=np.array(len(y)))
        print(f"[client {cid}] round {t}: local update sent", flush=True)
    print(f"[client {cid}] DONE", flush=True)

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--role", required=True, choices=["aggregator","client"])
    ap.add_argument("--run", default="R1")
    ap.add_argument("--clients", default="cic,unsw", help="aggregator: comma list of client ids")
    ap.add_argument("--client-id", default="cic")
    ap.add_argument("--rounds", type=int, default=100)
    ap.add_argument("--local-epochs", type=int, default=5)
    ap.add_argument("--lr", type=float, default=3e-3)
    ap.add_argument("--mu", type=float, default=0.0, help=">0 enables FedProx")
    ap.add_argument("--seed", type=int, default=42)
    a=ap.parse_args()
    if a.role=="aggregator":
        run_aggregator(a.run, [c.strip() for c in a.clients.split(",")], a.rounds, a.mu, a.seed)
    else:
        run_client(a.client_id, a.run, a.rounds, a.local_epochs, a.lr, a.mu, a.seed)
