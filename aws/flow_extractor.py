#!/usr/bin/env python3
"""
SSH Flow Extractor & Detector v3 (All-in-One)
Captures mirrored traffic, extracts 10 XGBoost features, predicts, and alerts via SNS.

All processing done on Analyzer Node — no Lambda required.

Pipeline: tcpdump → extract features → XGBoost predict → SNS alert (if attack)
"""
import subprocess
import time
import csv
import boto3
import os
import json
import numpy as np
from datetime import datetime
from collections import defaultdict

# ===== CONFIGURATION =====
SNS_TOPIC_ARN = "arn:aws:sns:ap-southeast-1:232032302717:ssh-detection-alerts"
S3_BUCKET = "ssh-detection-features-232032302717"
S3_PREFIX = "results/"
CAPTURE_DURATION = 60  # seconds per capture window
INTERFACE = "ens5"
MODEL_PATH = "/home/ssm-user/xgboost_ddos_model.json"
REGION = "ap-southeast-1"

# Multi-class labels (from training)
CLASS_NAMES = ['BENIGN', 'DNS', 'LDAP', 'MSSQL', 'NETBIOS', 'NTP',
               'SNMP', 'SSDP', 'SYN', 'TFTP', 'UDP', 'UDP-LAG', 'WEBDDOS']

# The 10 features our model expects (in order)
# NOTE: Model was trained with 82 features using CICDDoS2019 column names
# We extract what we can from tcpdump and fill rest with 0
FEATURE_NAMES = [
    'Dst Port',
    'Init Bwd Win Byts',
    'Fwd Seg Size Min',
    'Flow Pkts/s',
    'Flow Duration',
    'Fwd Header Len',
    'Bwd Header Len',
    'Bwd IAT Min',
    'Init Fwd Win Byts',
    'ACK Flag Cnt'
]

# Full feature names as in the CICDDoS2019 dataset (model was trained with these)
FULL_FEATURE_NAMES = [
    'ACK Flag Count', 'Active Max', 'Active Mean', 'Active Min', 'Active Std',
    'Average Packet Size', 'Avg Bwd Segment Size', 'Avg Fwd Segment Size',
    'Bwd Avg Bulk Rate', 'Bwd Avg Bytes/Bulk', 'Bwd Avg Packets/Bulk',
    'Bwd Header Length', 'Bwd IAT Max', 'Bwd IAT Mean', 'Bwd IAT Min',
    'Bwd IAT Std', 'Bwd IAT Total', 'Bwd PSH Flags', 'Bwd Packet Length Max',
    'Bwd Packet Length Mean', 'Bwd Packet Length Min', 'Bwd Packet Length Std',
    'Bwd Packets/s', 'Bwd URG Flags', 'CWE Flag Count', 'Destination Port',
    'Down/Up Ratio', 'ECE Flag Count', 'FIN Flag Count', 'Flow Bytes/s',
    'Flow Duration', 'Flow IAT Max', 'Flow IAT Mean', 'Flow IAT Min',
    'Flow IAT Std', 'Flow Packets/s', 'Fwd Avg Bulk Rate', 'Fwd Avg Bytes/Bulk',
    'Fwd Avg Packets/Bulk', 'Fwd Header Length', 'Fwd Header Length.1',
    'Fwd IAT Max', 'Fwd IAT Mean', 'Fwd IAT Min', 'Fwd IAT Std', 'Fwd IAT Total',
    'Fwd PSH Flags', 'Fwd Packet Length Max', 'Fwd Packet Length Mean',
    'Fwd Packet Length Min', 'Fwd Packet Length Std', 'Fwd Packets/s',
    'Fwd URG Flags', 'Idle Max', 'Idle Mean', 'Idle Min', 'Idle Std',
    'Inbound', 'Init_Win_bytes_backward', 'Init_Win_bytes_forward',
    'Max Packet Length', 'Min Packet Length', 'PSH Flag Count',
    'Packet Length Mean', 'Packet Length Std', 'Packet Length Variance',
    'Protocol', 'RST Flag Count', 'SYN Flag Count', 'Source Port',
    'Subflow Bwd Bytes', 'Subflow Bwd Packets', 'Subflow Fwd Bytes',
    'Subflow Fwd Packets', 'Total Backward Packets', 'Total Fwd Packets',
    'Total Length of Bwd Packets', 'Total Length of Fwd Packets',
    'URG Flag Count', 'Unnamed: 0', 'act_data_pkt_fwd', 'min_seg_size_forward'
]

# Mapping from our extracted names to CICDDoS2019 dataset names
FEATURE_MAPPING = {
    'Dst Port': 'Destination Port',
    'Init Bwd Win Byts': 'Init_Win_bytes_backward',
    'Fwd Seg Size Min': 'min_seg_size_forward',
    'Flow Pkts/s': 'Flow Packets/s',
    'Flow Duration': 'Flow Duration',
    'Fwd Header Len': 'Fwd Header Length',
    'Bwd Header Len': 'Bwd Header Length',
    'Bwd IAT Min': 'Bwd IAT Min',
    'Init Fwd Win Byts': 'Init_Win_bytes_forward',
    'ACK Flag Cnt': 'ACK Flag Count'
}

# ===== GLOBAL MODEL =====
MODEL = None


def load_model():
    """Load XGBoost model once at startup."""
    global MODEL
    if MODEL is not None:
        return MODEL

    try:
        import xgboost as xgb
        MODEL = xgb.Booster()
        MODEL.load_model(MODEL_PATH)
        print(f"[OK] XGBoost model loaded from {MODEL_PATH}")
        return MODEL
    except Exception as e:
        print(f"[ERROR] Failed to load model: {e}")
        return None


def capture_packets(duration=60):
    """Capture packets using tcpdump for specified duration."""
    output_file = f"/tmp/capture_{int(time.time())}.pcap"
    cmd = [
        "timeout", str(duration),
        "tcpdump", "-i", INTERFACE, "-w", output_file,
        "udp port 4789 or tcp port 22"
    ]
    print(f"[CAPTURE] Listening for {duration}s on {INTERFACE}...")
    try:
        subprocess.run(cmd, timeout=duration + 10, capture_output=True)
    except subprocess.TimeoutExpired:
        pass
    return output_file


def parse_pcap_to_flows(pcap_file):
    """Parse pcap into per-flow statistics using tcpdump verbose output."""
    cmd = ["tcpdump", "-r", pcap_file, "-nn", "-tttt", "-v"]
    result = subprocess.run(cmd, capture_output=True, text=True)

    flows = defaultdict(lambda: {
        'dst_port': 0,
        'init_fwd_win': 0,
        'init_bwd_win': 0,
        'fwd_seg_sizes': [],
        'bwd_seg_sizes': [],
        'fwd_header_lens': [],
        'bwd_header_lens': [],
        'fwd_timestamps': [],
        'bwd_timestamps': [],
        'ack_count': 0,
        'packets_fwd': 0,
        'packets_bwd': 0,
        'is_first_fwd': True,
        'is_first_bwd': True,
    })

    for line in result.stdout.strip().split('\n'):
        if not line:
            continue
        try:
            parts = line.split()
            if len(parts) < 5:
                continue

            # Parse timestamp
            try:
                ts_parts = parts[1] if '-' in parts[0] else parts[0]
                time_components = ts_parts.split(':')
                if len(time_components) >= 3:
                    timestamp = (float(time_components[0]) * 3600 +
                                float(time_components[1]) * 60 +
                                float(time_components[2]))
                else:
                    timestamp = time.time()
            except (ValueError, IndexError):
                timestamp = time.time()

            # Filter SSH traffic only
            if '.22 ' not in line and '.22:' not in line:
                continue

            # Extract src/dst
            src = dst = None
            for i, p in enumerate(parts):
                if p == '>':
                    src = parts[i - 1].rstrip(':')
                    dst = parts[i + 1].rstrip(':')
                    break
            if not src or not dst:
                continue

            # Determine direction
            if '.22' in dst:
                flow_key = f"{src}->{dst}"
                direction = 'fwd'
            else:
                flow_key = f"{dst}->{src}"
                direction = 'bwd'

            flow = flows[flow_key]
            flow['dst_port'] = 22

            # TCP window size
            win_size = 0
            if 'win ' in line:
                try:
                    win_idx = line.index('win ')
                    win_str = line[win_idx + 4:].split(',')[0].split(')')[0].split(' ')[0]
                    win_size = int(win_str)
                except (ValueError, IndexError):
                    pass

            # Segment length
            seg_size = 0
            if 'length ' in line:
                try:
                    len_idx = line.index('length ')
                    len_str = line[len_idx + 7:].split(' ')[0].split(',')[0].split(')')[0]
                    seg_size = int(len_str)
                except (ValueError, IndexError):
                    pass

            # ACK flag
            if ' ack ' in line.lower() or ('Flags [' in line and '.' in line):
                flow['ack_count'] += 1

            # Header length estimate
            header_len = 32 if 'options [' in line.lower() else 20

            if direction == 'fwd':
                flow['packets_fwd'] += 1
                flow['fwd_timestamps'].append(timestamp)
                flow['fwd_seg_sizes'].append(seg_size)
                flow['fwd_header_lens'].append(header_len)
                if flow['is_first_fwd']:
                    flow['init_fwd_win'] = win_size
                    flow['is_first_fwd'] = False
            else:
                flow['packets_bwd'] += 1
                flow['bwd_timestamps'].append(timestamp)
                flow['bwd_seg_sizes'].append(seg_size)
                flow['bwd_header_lens'].append(header_len)
                if flow['is_first_bwd']:
                    flow['init_bwd_win'] = win_size
                    flow['is_first_bwd'] = False

        except Exception:
            continue

    return flows


def extract_features(flows):
    """Extract 10 XGBoost features from parsed flows."""
    features_list = []

    for flow_key, flow in flows.items():
        if flow['packets_fwd'] == 0 and flow['packets_bwd'] == 0:
            continue

        # Calculate duration
        all_ts = flow['fwd_timestamps'] + flow['bwd_timestamps']
        duration_sec = (max(all_ts) - min(all_ts)) if len(all_ts) >= 2 else 0
        total_pkts = flow['packets_fwd'] + flow['packets_bwd']

        features = {
            'Dst Port': flow['dst_port'],
            'Init Bwd Win Byts': flow['init_bwd_win'],
            'Fwd Seg Size Min': min(flow['fwd_seg_sizes']) if flow['fwd_seg_sizes'] else 0,
            'Flow Pkts/s': total_pkts / max(duration_sec, 0.001),
            'Flow Duration': duration_sec * 1_000_000,
            'Fwd Header Len': sum(flow['fwd_header_lens']),
            'Bwd Header Len': sum(flow['bwd_header_lens']),
            'Bwd IAT Min': _calc_bwd_iat_min(flow['bwd_timestamps']),
            'Init Fwd Win Byts': flow['init_fwd_win'],
            'ACK Flag Cnt': flow['ack_count']
        }
        features_list.append(features)

    return features_list


def _calc_bwd_iat_min(timestamps):
    """Calculate minimum backward inter-arrival time in microseconds."""
    if len(timestamps) < 2:
        return 0
    sorted_ts = sorted(timestamps)
    iats = [sorted_ts[i+1] - sorted_ts[i] for i in range(len(sorted_ts) - 1)]
    return min(iats) * 1_000_000 if iats else 0


def predict(features_list):
    """
    Run XGBoost inference on extracted features.
    Maps our 10 extracted features to the full 82-feature vector expected by model.
    Returns list of (class_index, class_name, probability) tuples.
    """
    import xgboost as xgb

    model = load_model()
    if model is None:
        print("[WARN] Model unavailable, using fallback rule-based")
        return predict_fallback(features_list)

    if not features_list:
        return []

    # Build full feature array (82 features, fill with 0 for unknown)
    data = []
    for feat_dict in features_list:
        row = np.zeros(len(FULL_FEATURE_NAMES), dtype=np.float32)
        for our_name, dataset_name in FEATURE_MAPPING.items():
            if dataset_name in FULL_FEATURE_NAMES:
                idx = FULL_FEATURE_NAMES.index(dataset_name)
                row[idx] = feat_dict.get(our_name, 0)
        data.append(row)

    data_array = np.array(data, dtype=np.float32)
    dmatrix = xgb.DMatrix(data_array, feature_names=FULL_FEATURE_NAMES)
    predictions = model.predict(dmatrix)

    results = []
    for pred in predictions:
        cls_idx = int(pred)
        cls_name = CLASS_NAMES[cls_idx] if cls_idx < len(CLASS_NAMES) else f'UNKNOWN_{cls_idx}'
        results.append((cls_idx, cls_name, 1.0))

    return results


def predict_fallback(features_list):
    """Fallback: rule-based prediction (Flow Pkts/s > 1.0)."""
    results = []
    for feat_dict in features_list:
        pkts_s = feat_dict.get('Flow Pkts/s', 0)
        if pkts_s > 1.0:
            results.append((8, 'SYN', pkts_s))  # default attack
        else:
            results.append((0, 'BENIGN', pkts_s))
    return results


def send_alert(attack_count, total_flows, features_list, predictions):
    """Send SNS alert if attacks detected."""
    try:
        sns = boto3.client('sns', region_name=REGION)
        message = (
            f"SSH BRUTE-FORCE DETECTED!\n\n"
            f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Total flows analyzed: {total_flows}\n"
            f"Attacks detected: {attack_count}\n"
            f"Benign flows: {total_flows - attack_count}\n"
            f"\nModel: XGBoost (10 features, 84 KB)\n"
            f"Analyzer Node: 10.0.1.45\n"
            f"\nAction: Investigate source IPs immediately.\n"
        )
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject='[SSH Detection] Brute-Force Attack Detected!',
            Message=message
        )
        print(f"[ALERT] SNS notification sent ({attack_count} attacks)")
    except Exception as e:
        print(f"[ERROR] Failed to send SNS: {e}")


def save_results(features_list, predictions):
    """Save results to S3 for audit/logging."""
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"/tmp/result_{timestamp}.json"

        results = []
        for i, feat_dict in enumerate(features_list):
            cls_idx, cls_name, prob = predictions[i]
            results.append({
                'features': feat_dict,
                'prediction': cls_name,
                'class_index': cls_idx,
                'probability': round(prob, 4)
            })

        from collections import Counter
        class_counts = Counter(r['prediction'] for r in results)

        output = {
            'timestamp': timestamp,
            'total_flows': len(results),
            'attacks': sum(1 for r in results if r['prediction'] != 'BENIGN'),
            'class_distribution': dict(class_counts),
            'flows': results
        }

        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)

        s3 = boto3.client('s3', region_name=REGION)
        s3_key = f"{S3_PREFIX}result_{timestamp}.json"
        s3.upload_file(filename, S3_BUCKET, s3_key)
        print(f"[S3] Results saved to s3://{S3_BUCKET}/{s3_key}")
        os.remove(filename)
    except Exception as e:
        print(f"[WARN] Failed to save to S3: {e}")


def main():
    print("=" * 60)
    print("  SSH Brute-Force Detector v3 (All-in-One)")
    print("  Analyzer Node — XGBoost Inference")
    print(f"  Model: {MODEL_PATH}")
    print(f"  Capture: {CAPTURE_DURATION}s windows on {INTERFACE}")
    print(f"  SNS: {SNS_TOPIC_ARN}")
    print("=" * 60)

    # Pre-load model
    load_model()

    while True:
        try:
            # 1. Capture
            pcap_file = capture_packets(CAPTURE_DURATION)

            # 2. Parse
            if os.path.exists(pcap_file) and os.path.getsize(pcap_file) > 24:
                flows = parse_pcap_to_flows(pcap_file)
                print(f"[PARSE] {len(flows)} flows found")

                # 3. Extract features
                features = extract_features(flows)

                if features:
                    # 4. Predict
                    predictions = predict(features)
                    
                    # Count per class
                    from collections import Counter
                    class_counts = Counter(name for _, name, _ in predictions)
                    attack_count = sum(1 for _, name, _ in predictions if name != 'BENIGN')
                    total = len(predictions)

                    print(f"[PREDICT] {total} flows: {dict(class_counts)}")

                    # 5. Alert if attacks found
                    if attack_count > 0:
                        send_alert(attack_count, total, features, predictions)

                    # 6. Save results to S3 (for audit)
                    save_results(features, predictions)
                else:
                    print("[PARSE] No SSH flows in this window")

                os.remove(pcap_file)
            else:
                print("[CAPTURE] No traffic captured")
                if os.path.exists(pcap_file):
                    os.remove(pcap_file)

            time.sleep(5)

        except KeyboardInterrupt:
            print("\n[STOP] Shutting down...")
            break
        except Exception as e:
            print(f"[ERROR] {e}")
            time.sleep(10)


if __name__ == "__main__":
    main()
