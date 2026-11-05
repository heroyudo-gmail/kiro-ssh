#!/usr/bin/env python3
# fed_node_journal.py -- JOURNAL (extended) federated node over S3.
#
# Turunan dari fed_node_survey.py, tetapi DIBUAT FLEKSIBEL untuk paper JURNAL:
#   - Dimensi input DINAMIS: dibaca dari data (<id>_train.npz), bukan hardcode 9.
#     Jadi notebook partisi boleh menghasilkan 9 (cross-domain) atau 76 (near-domain).
#   - Prefix S3 bisa di-set via --base-prefix (default: federated_journal/neardomain),
#     TERPISAH dari data survei (unsw-far/federated_survey) agar tak saling menimpa.
#   - Client-id bebas (mis. cic2017, cic2018). Node agnostik terhadap nama.
#   - Aggregator melakukan EVALUASI akhir bila diberi --eval: menghitung MCC/recall
#     per-client dan union untuk model FEDERATED, CENTRALIZED (pooled & local-norm),
#     dan LOCAL-ONLY, dengan protokol z-score BEBAS-KEBOCORAN (per-client, konsisten
#     train<->eval). Hasil ditulis ke run_<RUN>/eval_results.json di S3.
#
# Protokol normalisasi (kontribusi jurnal): tiap test set dinormalisasi dgn statistik
# train KLIEN PEMILIKNYA (match training). Baseline centralized dilaporkan dua cara
# (pooled-norm dan local-norm) agar efek normalisasi terpisah dari efek federasi.
#
# Transport S3 sama pola dgn survei:
#   <BASE>/data/<id>/<id>_train.npz , <id>_test.npz   (dari jA_01)
#   <BASE>/run_<RUN>/round_<t>/{global_<t>.npz, client_<id>_<t>.npz}
#   <BASE>/run_<RUN>/global_final.npz
#   <BASE>/run_<RUN>/eval_results.json   (bila --eval)
#
# Contoh (via SSM tiap EC2):
#   python3 fed_node_journal.py --role client --client-id cic2017 \
#       --base-prefix federated_journal/neardomain --run J_NEAR --rounds 100 --local-epochs 5
#   python3 fed_node_journal.py --role client --client-id cic2018 \
#       --base-prefix federated_journal/neardomain --run J_NEAR --rounds 100 --local-epochs 5
#   python3 fed_node_journal.py --role aggregator --clients cic2017,cic2018 \
#       --base-prefix federated_journal/neardomain --run J_NEAR --rounds 100 --eval

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
s3 = boto3.client("s3", region_name=REGION)

HID = [128, 64]   # hidden layers (input dim ditentukan dinamis dari data)


# ---------- S3 helpers ----------
def s3_put_npz(key, **arrs):
    buf = io.BytesIO(); np.savez_compressed(buf, **arrs); buf.seek(0)
    s3.put_object(Bucket=BUCKET, Key=key, Body=buf.getvalue())

def s3_put_bytes(key, data):
    s3.put_object(Bucket=BUCKET, Key=key, Body=data)

def s3_get_npz(key):
    try:
        obj = s3.get_object(Bucket=BUCKET, Key=key)
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


# ---------- MLP (numpy), input dim dinamis ----------
def layers_for(in_dim):
    return [in_dim] + HID + [1]

def init_weights(in_dim, seed=42):
    rng = np.random.RandomState(seed); W = []; L = layers_for(in_dim)
    for a, b in zip(L[:-1], L[1:]):
        W.append(rng.randn(a, b) * np.sqrt(2.0 / a)); W.append(np.zeros(b))
    return W

def _relu(x): return np.maximum(0, x)
def _sig(x):  return 1.0 / (1.0 + np.exp(-np.clip(x, -30, 30)))

def forward(W, X):
    a1 = X @ W[0] + W[1]; z1 = _relu(a1)
    a2 = z1 @ W[2] + W[3]; z2 = _relu(a2)
    a3 = z2 @ W[4] + W[5]; out = _sig(a3).ravel()
    return out, (X, a1, z1, a2, z2, a3, out)

def train_local(W, X, y, epochs=1, lr=3e-3, batch=256, mu=0.0, W_global=None, seed=42):
    rng = np.random.RandomState(seed); n = len(y); W = [w.copy() for w in W]
    for _ in range(epochs):
        idx = rng.permutation(n)
        for s in range(0, n, batch):
            bi = idx[s:s + batch]; Xb = X[bi]; yb = y[bi].astype(float)
            out, (X_, a1, z1, a2, z2, a3, o) = forward(W, Xb)
            g = (o - yb) / len(yb)
            gW4 = z2.T @ g[:, None]; gb4 = g.sum(0)
            d2 = (g[:, None] @ W[4].T) * (a2 > 0)
            gW2 = z1.T @ d2; gb2 = d2.sum(0)
            d1 = (d2 @ W[2].T) * (a1 > 0)
            gW0 = X_.T @ d1; gb0 = d1.sum(0)
            gall = [gW0, gb0, gW2, gb2, gW4, gb4]
            for i, gv in enumerate(gall):
                gv = np.asarray(gv).reshape(W[i].shape)
                if mu > 0 and W_global is not None:
                    gv = gv + mu * (W[i] - W_global[i])
                W[i] = W[i] - lr * gv
    return W

def fedavg(weight_list, sizes):
    tot = float(sum(sizes)); out = []
    for i in range(len(weight_list[0])):
        out.append(sum((sizes[k] / tot) * weight_list[k][i] for k in range(len(weight_list))))
    return out

def zscore_fit(X):
    mu = X.mean(0); sd = X.std(0); sd[sd == 0] = 1.0; return mu, sd
def zscore_apply(X, mu, sd): return (X - mu) / sd


# ---------- Metrics ----------
def mcc(y, p):
    y = np.asarray(y).astype(int); p = np.asarray(p).astype(int)
    tp = int(np.sum((p == 1) & (y == 1))); tn = int(np.sum((p == 0) & (y == 0)))
    fp = int(np.sum((p == 1) & (y == 0))); fn = int(np.sum((p == 0) & (y == 1)))
    denom = np.sqrt(float(tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
    return ((tp * tn - fp * fn) / denom) if denom > 0 else 0.0

def recall(y, p):
    y = np.asarray(y).astype(int); p = np.asarray(p).astype(int)
    tp = int(np.sum((p == 1) & (y == 1))); fn = int(np.sum((p == 0) & (y == 1)))
    return tp / (tp + fn) if (tp + fn) > 0 else 0.0

def metrics(y, prob):
    p = (prob >= 0.5).astype(int)
    return {"mcc": round(mcc(y, p), 4), "recall": round(recall(y, p), 4),
            "n": int(len(y)), "pos_rate": round(float(np.mean(y)), 4)}


# ---------- Roles ----------
def load_client(base, cid, split):
    d = s3_get_npz(f"{base}/data/{cid}/{cid}_{split}.npz")
    if d is None: return None, None
    return np.asarray(d["X"], float), np.asarray(d["y"], int)

def run_client(base, cid, run, rounds, epochs, lr, mu, seed):
    X, y = load_client(base, cid, "train")
    if X is None:
        print(f"[client {cid}] train data not found ({base}/data/{cid}/)"); return
    in_dim = X.shape[1]
    mu_z, sd_z = zscore_fit(X); Xz = zscore_apply(X, mu_z, sd_z)   # per-client LOCAL z-score
    print(f"[client {cid}] data {X.shape} (d={in_dim}), pos-rate {y.mean():.3f}", flush=True)
    for t in range(rounds):
        gkey = f"{base}/run_{run}/round_{t}/global_{t}.npz"
        if not wait_for(gkey): print(f"[client {cid}] TIMEOUT global r{t}"); return
        g = s3_get_npz(gkey); Wg = [g[f"w{i}"] for i in range(6)]
        Wl = train_local(Wg, Xz, y, epochs=epochs, lr=lr, mu=mu, W_global=Wg, seed=seed)
        s3_put_npz(f"{base}/run_{run}/round_{t}/client_{cid}_{t}.npz",
                   **{f"w{i}": w for i, w in enumerate(Wl)}, n=np.array(len(y)))
        print(f"[client {cid}] round {t}: local update sent", flush=True)
    print(f"[client {cid}] DONE", flush=True)

def run_aggregator(base, clients, run, rounds, seed, do_eval):
    # dimensi input ditentukan dari data klien pertama (konsisten antar-klien)
    X0, _ = load_client(base, clients[0], "train")
    if X0 is None:
        print(f"[agg] train data {clients[0]} not found; cannot set input dim"); return
    in_dim = X0.shape[1]
    print(f"[agg] input dim = {in_dim} (from {clients[0]})", flush=True)
    W = init_weights(in_dim, seed)
    for t in range(rounds):
        s3_put_npz(f"{base}/run_{run}/round_{t}/global_{t}.npz",
                   **{f"w{i}": w for i, w in enumerate(W)})
        print(f"[agg] round {t}: global published, waiting clients...", flush=True)
        cw = []; cs = []
        for cid in clients:
            key = f"{base}/run_{run}/round_{t}/client_{cid}_{t}.npz"
            if not wait_for(key): print(f"[agg] TIMEOUT waiting {cid} r{t}"); return
            d = s3_get_npz(key); cw.append([d[f"w{i}"] for i in range(6)]); cs.append(int(d["n"]))
        W = fedavg(cw, cs)
        print(f"[agg] round {t}: aggregated (sizes={cs})", flush=True)
    s3_put_npz(f"{base}/run_{run}/global_final.npz", **{f"w{i}": w for i, w in enumerate(W)})
    print("[agg] DONE -> global_final.npz", flush=True)
    if do_eval:
        evaluate(base, clients, run, W, seed)

def evaluate(base, clients, run, W_fed, seed):
    """Protokol bebas-kebocoran: tiap test set dinormalisasi dgn statistik TRAIN pemiliknya.
    Lapor FEDERATED, CENTRALIZED(pooled & local-norm), LOCAL-ONLY (per klien) -> union."""
    import json
    tr = {}; te = {}
    for c in clients:
        Xtr, ytr = load_client(base, c, "train"); Xte, yte = load_client(base, c, "test")
        if Xtr is None or Xte is None:
            print(f"[eval] data {c} tak lengkap; lewati eval"); return
        tr[c] = (Xtr, ytr); te[c] = (Xte, yte)
    in_dim = tr[clients[0]][0].shape[1]

    # z-score per-klien dari TRAIN masing-masing
    zstat = {c: zscore_fit(tr[c][0]) for c in clients}

    def eval_model(W, norm="local"):
        """norm='local': tiap test pakai stat train pemiliknya (bebas-kebocoran).
           norm='pooled': semua test pakai stat gabungan train (diagnostik)."""
        if norm == "pooled":
            Xall = np.vstack([tr[c][0] for c in clients]); mup, sdp = zscore_fit(Xall)
        per = {}; probs_all = []; y_all = []
        for c in clients:
            Xte, yte = te[c]
            if norm == "local":
                mz, sz = zstat[c]
            else:
                mz, sz = mup, sdp
            prob, _ = forward(W, zscore_apply(Xte, mz, sz))
            per[c] = metrics(yte, prob)
            probs_all.append(prob); y_all.append(yte)
        union = metrics(np.concatenate(y_all), np.concatenate(probs_all))
        return {"per_client": per, "union": union}

    res = {"run": run, "clients": clients, "in_dim": int(in_dim), "seed": seed}
    # 1) FEDERATED (local-norm = protokol utama; pooled = diagnostik)
    res["federated_local"] = eval_model(W_fed, "local")
    res["federated_pooled_diagnostic"] = eval_model(W_fed, "pooled")

    # 2) CENTRALIZED: latih 1 model pada data gabungan (pooled train)
    Xcat = np.vstack([tr[c][0] for c in clients]); ycat = np.concatenate([tr[c][1] for c in clients])
    # 2a) pooled-norm: z-score dari gabungan
    mup, sdp = zscore_fit(Xcat)
    Wc_p = init_weights(in_dim, seed)
    Wc_p = train_local(Wc_p, zscore_apply(Xcat, mup, sdp), ycat, epochs=100, lr=3e-3, seed=seed)
    res["centralized_pooled"] = eval_model(Wc_p, "pooled")
    # 2b) local-norm eval terhadap model centralized pooled-trained
    res["centralized_localnorm"] = eval_model(Wc_p, "local")

    # 3) LOCAL-ONLY: tiap klien latih sendiri, lalu diuji ke union (local-norm)
    for c in clients:
        Xtr, ytr = tr[c]; mz, sz = zstat[c]
        Wl = init_weights(in_dim, seed)
        Wl = train_local(Wl, zscore_apply(Xtr, mz, sz), ytr, epochs=100, lr=3e-3, seed=seed)
        res[f"local_only[{c}]"] = eval_model(Wl, "local")

    out = json.dumps(res, indent=2).encode("utf-8")
    s3_put_bytes(f"{base}/run_{run}/eval_results.json", out)
    print("[eval] DONE -> eval_results.json", flush=True)
    print(json.dumps({k: v.get("union") if isinstance(v, dict) and "union" in v else v
                      for k, v in res.items()}, indent=2))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--role", required=True, choices=["aggregator", "client"])
    ap.add_argument("--base-prefix", default="federated_journal/neardomain")
    ap.add_argument("--run", default="J_NEAR")
    ap.add_argument("--clients", default="cic2017,cic2018", help="aggregator: comma list")
    ap.add_argument("--client-id", default="cic2017")
    ap.add_argument("--rounds", type=int, default=100)
    ap.add_argument("--local-epochs", type=int, default=5)
    ap.add_argument("--lr", type=float, default=3e-3)
    ap.add_argument("--mu", type=float, default=0.0, help=">0 enables FedProx")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--eval", action="store_true", help="aggregator: run final evaluation")
    a = ap.parse_args()
    base = a.base_prefix.strip("/")
    if a.role == "aggregator":
        run_aggregator(base, [c.strip() for c in a.clients.split(",")],
                       a.run, a.rounds, a.seed, a.eval)
    else:
        run_client(base, a.client_id, a.run, a.rounds, a.local_epochs, a.lr, a.mu, a.seed)
