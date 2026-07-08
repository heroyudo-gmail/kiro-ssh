#!/usr/bin/env python3
"""
Simplified SSH Flow Extractor
Captures mirrored traffic, extracts 10 features per flow, uploads CSV to S3.
"""
import subprocess
import time
import csv
import boto3
import os
from datetime import datetime
from collections import defaultdict

S3_BUCKET = "ssh-detection-features-232032302717"
S3_PREFIX = "features/"
CAPTURE_DURATION = 60  # seconds per capture window
INTERFACE = "eth0"  # mirrored traffic arrives here

def capture_packets(duration=60):
    """Capture packets using tcpdump for specified duration."""
    output_file = f"/tmp/capture_{int(time.time())}.pcap"
    cmd = [
        "tcpdump", "-i", INTERFACE, "-w", output_file,
        "-G", str(duration), "-W", "1",
        "tcp port 22 or (udp port 4789)"  # SSH or VXLAN encapsulated
    ]
    print(f"Capturing packets for {duration}s...")
    subprocess.run(cmd, timeout=duration + 5, capture_output=True)
    return output_file

def parse_pcap_to_flows(pcap_file):
    """Parse pcap file into flow statistics using tcpdump text output."""
    cmd = ["tcpdump", "-r", pcap_file, "-nn", "-q"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    flows = defaultdict(lambda: {
        'packets_fwd': 0, 'packets_bwd': 0,
        'bytes_fwd': 0, 'bytes_bwd': 0,
        'start_time': None, 'end_time': None,
        'dst_port': 0, 'fwd_pkt_lengths': [],
        'bwd_pkt_lengths': []
    })
    
    for line in result.stdout.strip().split('\n'):
        if not line:
            continue
        try:
            parts = line.split()
            timestamp = parts[0]
            # Simple parsing - identify SSH flows by port 22
            if '22' in line:
                # Extract source > destination
                for i, p in enumerate(parts):
                    if '>' in p or p == '>':
                        src = parts[i-1] if '>' in p else parts[i-1]
                        dst = parts[i+1] if '>' in p else parts[i+1]
                        break
                else:
                    continue
                
                flow_key = f"{src}->{dst}"
                flow = flows[flow_key]
                flow['dst_port'] = 22
                flow['packets_fwd'] += 1
                
                # Estimate packet length from tcpdump output
                length = 0
                for p in parts:
                    if p.startswith('length'):
                        try:
                            length = int(parts[parts.index(p) + 1])
                        except (ValueError, IndexError):
                            pass
                flow['bytes_fwd'] += max(length, 64)
                flow['fwd_pkt_lengths'].append(max(length, 64))
                
                if flow['start_time'] is None:
                    flow['start_time'] = timestamp
                flow['end_time'] = timestamp
        except Exception:
            continue
    
    return flows

def extract_features(flows):
    """Extract 10 features from flow data."""
    features_list = []
    
    for flow_key, flow in flows.items():
        if flow['packets_fwd'] == 0:
            continue
        
        duration_ms = 1000  # default 1s if can't calculate
        tot_fwd_pkts = flow['packets_fwd']
        tot_bwd_pkts = flow['packets_bwd']
        totlen_fwd = flow['bytes_fwd']
        
        fwd_lengths = flow['fwd_pkt_lengths'] if flow['fwd_pkt_lengths'] else [0]
        fwd_pkt_len_mean = sum(fwd_lengths) / len(fwd_lengths)
        fwd_pkt_len_min = min(fwd_lengths) if fwd_lengths else 0
        
        flow_pkts_s = (tot_fwd_pkts + tot_bwd_pkts) / max(duration_ms/1000, 0.001)
        flow_byts_s = totlen_fwd / max(duration_ms/1000, 0.001)
        bwd_pkts_s = tot_bwd_pkts / max(duration_ms/1000, 0.001)
        
        features = {
            'Dst Port': flow['dst_port'],
            'TotLen Fwd Pkts': totlen_fwd,
            'Init Fwd Win Byts': 8192,  # default TCP window
            'Fwd Pkt Len Mean': fwd_pkt_len_mean,
            'Down/Up Ratio': tot_bwd_pkts / max(tot_fwd_pkts, 1),
            'Fwd Pkt Len Min': fwd_pkt_len_min,
            'Tot Bwd Pkts': tot_bwd_pkts,
            'Flow Pkts/s': flow_pkts_s,
            'Flow Byts/s': flow_byts_s,
            'Bwd Pkts/s': bwd_pkts_s
        }
        features_list.append(features)
    
    return features_list

def upload_to_s3(features_list):
    """Write features to CSV and upload to S3."""
    if not features_list:
        print("No flows to upload.")
        return
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"/tmp/features_{timestamp}.csv"
    s3_key = f"{S3_PREFIX}features_{timestamp}.csv"
    
    fieldnames = ['Dst Port', 'TotLen Fwd Pkts', 'Init Fwd Win Byts',
                  'Fwd Pkt Len Mean', 'Down/Up Ratio', 'Fwd Pkt Len Min',
                  'Tot Bwd Pkts', 'Flow Pkts/s', 'Flow Byts/s', 'Bwd Pkts/s']
    
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(features_list)
    
    s3 = boto3.client('s3', region_name='ap-southeast-1')
    s3.upload_file(filename, S3_BUCKET, s3_key)
    print(f"Uploaded {len(features_list)} flows to s3://{S3_BUCKET}/{s3_key}")
    
    # Cleanup
    os.remove(filename)

def main():
    print("=" * 50)
    print("SSH Flow Extractor - Starting")
    print(f"Bucket: {S3_BUCKET}")
    print(f"Capture duration: {CAPTURE_DURATION}s")
    print("=" * 50)
    
    while True:
        try:
            # Capture
            pcap_file = capture_packets(CAPTURE_DURATION)
            
            # Parse
            if os.path.exists(pcap_file) and os.path.getsize(pcap_file) > 24:
                flows = parse_pcap_to_flows(pcap_file)
                print(f"Found {len(flows)} flows")
                
                # Extract features
                features = extract_features(flows)
                
                # Upload
                if features:
                    upload_to_s3(features)
                else:
                    print("No SSH flows detected in this window.")
                
                # Cleanup pcap
                os.remove(pcap_file)
            else:
                print("No traffic captured.")
                if os.path.exists(pcap_file):
                    os.remove(pcap_file)
            
            time.sleep(5)
        except KeyboardInterrupt:
            print("\nStopping...")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()