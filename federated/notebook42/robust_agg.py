#!/usr/bin/env python3
# robust_agg.py -- Paper 4-2: robust aggregation rules + attack models.
# Sumber TUNGGAL yg di-reuse semua notebook 42_* (jangan tulis-ulang logika).
# Bekerja pada format bobot fed_node.py: W = list of np.ndarray (W0,b0,W2,b2,W4,b4).
# Serangan beroperasi pada DATA lokal (label-flip, backdoor) atau pada BOBOT (scaling).

import numpy as np

# ---------- Util: flatten/unflatten bobot utk aturan berbasis jarak ----------
def flatten(W):
    return np.concatenate([w.ravel() for w in W])

def unflatten(vec, like):
    out=[]; i=0
    for w in like:
        n=w.size; out.append(vec[i:i+n].reshape(w.shape)); i+=n
    return out

def _pairwise_sqdist(V):
    # V: (m, d) matriks update ter-flatten; kembalikan matriks jarak kuadrat (m,m)
    sq=np.sum(V*V, axis=1)
    d2=sq[:,None]+sq[None,:]-2.0*(V@V.T)
    return np.maximum(d2, 0.0)

# ---------- Aturan agregasi ----------
def agg_fedavg(weight_list, sizes):
    tot=float(sum(sizes)); out=[]
    for i in range(len(weight_list[0])):
        out.append(sum((sizes[k]/tot)*weight_list[k][i] for k in range(len(weight_list))))
    return out

def agg_median(weight_list, sizes=None):
    # koordinat-wise median
    out=[]
    for i in range(len(weight_list[0])):
        stack=np.stack([W[i] for W in weight_list], axis=0)
        out.append(np.median(stack, axis=0))
    return out

def agg_trimmed_mean(weight_list, sizes=None, beta=1):
    # buang beta terkecil & beta terbesar per-koordinat, rata-ratakan sisanya
    m=len(weight_list)
    if 2*beta>=m: beta=max(0,(m-1)//2)
    out=[]
    for i in range(len(weight_list[0])):
        stack=np.stack([W[i] for W in weight_list], axis=0)   # (m, ...)
        s=np.sort(stack, axis=0)
        sl=s[beta:m-beta] if (m-2*beta)>0 else s
        out.append(sl.mean(axis=0))
    return out

def _krum_scores(weight_list, f):
    m=len(weight_list)
    V=np.stack([flatten(W) for W in weight_list], axis=0)
    D=_pairwise_sqdist(V)
    # jumlah (m - f - 2) jarak terdekat (eksklusif diri sendiri)
    kk=max(1, m - f - 2)
    scores=np.zeros(m)
    for i in range(m):
        di=np.sort(D[i])          # D[i,i]=0 di depan
        scores[i]=np.sum(di[1:kk+1])
    return scores, V

def agg_krum(weight_list, sizes=None, f=1):
    scores,_=_krum_scores(weight_list, f)
    idx=int(np.argmin(scores))
    return [w.copy() for w in weight_list[idx]], idx

def agg_multi_krum(weight_list, sizes=None, f=1, mkeep=None):
    m=len(weight_list)
    scores,_=_krum_scores(weight_list, f)
    if mkeep is None: mkeep=max(1, m - f)
    sel=list(np.argsort(scores)[:mkeep])
    sub=[weight_list[k] for k in sel]
    sz=[1.0]*len(sub) if sizes is None else [sizes[k] for k in sel]
    return agg_fedavg(sub, sz), sel

def aggregate(rule, weight_list, sizes, f=1, beta=1):
    # dispatcher seragam -> kembalikan (W_global, info)
    if rule=='fedavg':       return agg_fedavg(weight_list, sizes), {}
    if rule=='median':       return agg_median(weight_list), {}
    if rule=='trimmed_mean': return agg_trimmed_mean(weight_list, beta=beta), {'beta':beta}
    if rule=='krum':         W,idx=agg_krum(weight_list, f=f); return W, {'selected':idx}
    if rule=='multi_krum':   W,sel=agg_multi_krum(weight_list, sizes, f=f); return W, {'selected':list(sel)}
    raise ValueError('rule tak dikenal: %s'%rule)

# ---------- Model serangan ----------
def attack_label_flip(y, rng):
    # balik label biner attack<->benign pada data lokal klien jahat
    return 1 - np.asarray(y, int)

def attack_scale_weights(W_update, gamma=10.0):
    # perbesar update bobot klien jahat (dominasi rata-rata)
    return [gamma*w for w in W_update]

# Backdoor: trigger = set beberapa fitur ke nilai ekstrem tetap; target label=benign(0).
BACKDOOR_FEATURES = [0, 1, 2]      # indeks fitur SFM yg dipakai sbg trigger
BACKDOOR_VALUE    = 5.0            # nilai trigger (pada ruang ter-z-score, ~5 sigma)
BACKDOOR_TARGET   = 0             # label target (benign) -> serangan lolos deteksi

def apply_backdoor_trigger(X):
    # kembalikan salinan X dgn trigger disisipkan (dipakai saat latih jahat & saat ukur ASR)
    Xb=np.array(X, dtype=float, copy=True)
    Xb[:, BACKDOOR_FEATURES] = BACKDOOR_VALUE
    return Xb

def poison_backdoor_data(X, y, frac, rng):
    # pada data klien jahat: sisipkan trigger ke sebagian sampel + set label=target
    X=np.array(X,float,copy=True); y=np.array(y,int,copy=True)
    n=len(y); k=int(frac*n)
    if k<=0: return X,y
    idx=rng.choice(n, size=k, replace=False)
    X[np.ix_(idx, BACKDOOR_FEATURES)] = BACKDOOR_VALUE
    y[idx] = BACKDOOR_TARGET
    return X,y

def attack_success_rate(predict_fn, X_test, y_test):
    # ASR: dari sampel yg SEBENARNYA attack(1), berapa yg -> target(0) setelah diberi trigger
    mask = (np.asarray(y_test,int)==1)
    if mask.sum()==0: return float('nan')
    Xtrig = apply_backdoor_trigger(X_test[mask])
    pred = predict_fn(Xtrig)
    return float(np.mean(pred==BACKDOOR_TARGET))

__all__=['flatten','unflatten','aggregate','agg_fedavg','agg_median','agg_trimmed_mean',
         'agg_krum','agg_multi_krum','attack_label_flip','attack_scale_weights',
         'apply_backdoor_trigger','poison_backdoor_data','attack_success_rate',
         'BACKDOOR_FEATURES','BACKDOOR_VALUE','BACKDOOR_TARGET']
