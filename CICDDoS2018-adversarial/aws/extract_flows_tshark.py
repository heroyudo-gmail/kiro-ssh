#!/usr/bin/env python3
"""
Extract flow features from tshark raw_packets.csv (FAST, no scapy).
Reads per-packet CSV → groups into flows → computes features → outputs flow CSV.

Usage:
    python3 extract_flows_tshark.py /opt/ids2018/flows/raw_packets.csv /opt/ids2018/flows/output.csv
"""
import sys
import pandas as pd
import numpy as np

def extract(input_csv, output_csv):
    print(f"Reading {input_csv}...")
    df = pd.read_csv(input_csv, low_memory=False)
    print(f"  Loaded: {len(df)} packets")

    # Rename columns (tshark field names)
    col_map = {
        'frame.time_epoch': 'timestamp',
        'ip.src': 'src_ip',
        'ip.dst': 'dst_ip',
        'tcp.srcport': 'src_port',
        'tcp.dstport': 'dst_port',
        'udp.srcport': 'udp_src',
        'udp.dstport': 'udp_dst',
        'ip.proto': 'proto',
        'frame.len': 'pkt_len',
        'tcp.flags': 'flags'
    }
    df = df.rename(columns=col_map)

    # Merge TCP/UDP ports
    df['src_port'] = df['src_port'].fillna(df.get('udp_src', 0)).fillna(0).astype(int)
    df['dst_port'] = df['dst_port'].fillna(df.get('udp_dst', 0)).fillna(0).astype(int)
    df['timestamp'] = pd.to_numeric(df['timestamp'], errors='coerce')
    df['pkt_len'] = pd.to_numeric(df['pkt_len'], errors='coerce').fillna(0).astype(int)
    df['proto'] = pd.to_numeric(df['proto'], errors='coerce').fillna(0).astype(int)

    # Drop rows without IP
    df = df.dropna(subset=['src_ip', 'dst_ip']).reset_index(drop=True)
    print(f"  Valid IP packets: {len(df)}")

    # Parse TCP flags (hex string like "0x00000002")
    def parse_flags(flag_str):
        try:
            f = int(str(flag_str), 16) if pd.notna(flag_str) else 0
            return {
                'FIN': (f >> 0) & 1, 'SYN': (f >> 1) & 1,
                'RST': (f >> 2) & 1, 'PSH': (f >> 3) & 1,
                'ACK': (f >> 4) & 1, 'URG': (f >> 5) & 1
            }
        except:
            return {'FIN':0,'SYN':0,'RST':0,'PSH':0,'ACK':0,'URG':0}

    print("  Parsing flags...")
    flags_df = df['flags'].apply(parse_flags).apply(pd.Series)
    df = pd.concat([df, flags_df], axis=1)

    # Create flow key (bidirectional)
    def flow_key(row):
        a = (str(row['src_ip']), int(row['src_port']))
        b = (str(row['dst_ip']), int(row['dst_port']))
        if a <= b:
            return f"{a[0]}:{a[1]}-{b[0]}:{b[1]}-{row['proto']}"
        else:
            return f"{b[0]}:{b[1]}-{a[0]}:{a[1]}-{row['proto']}"

    print("  Computing flow keys...")
    df['flow_key'] = df.apply(flow_key, axis=1)

    # Group by flow
    print("  Aggregating flows...")
    flows = []
    for key, group in df.groupby('flow_key'):
        if len(group) < 2:
            continue

        g = group.sort_values('timestamp')
        first_row = g.iloc[0]
        src = first_row['src_ip']
        dst = first_row['dst_ip']

        # Forward = same direction as first packet
        fwd = g[g['src_ip'] == src]
        bwd = g[g['src_ip'] != src]

        duration = (g['timestamp'].max() - g['timestamp'].min()) * 1e6  # microseconds
        dur_sec = duration / 1e6 if duration > 0 else 0.001

        fwd_lens = fwd['pkt_len'].values
        bwd_lens = bwd['pkt_len'].values
        all_lens = g['pkt_len'].values

        # IAT (inter-arrival time)
        fwd_times = fwd['timestamp'].values
        bwd_times = bwd['timestamp'].values
        fwd_iat = np.diff(fwd_times) * 1e6 if len(fwd_times) > 1 else [0]
        bwd_iat = np.diff(bwd_times) * 1e6 if len(bwd_times) > 1 else [0]

        flows.append({
            'Flow Duration': duration,
            'Tot Fwd Pkts': len(fwd),
            'Tot Bwd Pkts': len(bwd),
            'TotLen Fwd Pkts': fwd_lens.sum(),
            'TotLen Bwd Pkts': bwd_lens.sum(),
            'Fwd Pkt Len Max': fwd_lens.max() if len(fwd_lens) > 0 else 0,
            'Fwd Pkt Len Min': fwd_lens.min() if len(fwd_lens) > 0 else 0,
            'Fwd Pkt Len Mean': fwd_lens.mean() if len(fwd_lens) > 0 else 0,
            'Bwd Pkt Len Max': bwd_lens.max() if len(bwd_lens) > 0 else 0,
            'Bwd Pkt Len Min': bwd_lens.min() if len(bwd_lens) > 0 else 0,
            'Bwd Pkt Len Mean': bwd_lens.mean() if len(bwd_lens) > 0 else 0,
            'Flow Byts/s': all_lens.sum() / dur_sec,
            'Flow Pkts/s': len(g) / dur_sec,
            'Fwd IAT Tot': fwd_iat.sum(),
            'Fwd IAT Mean': fwd_iat.mean() if len(fwd_iat) > 0 else 0,
            'Bwd IAT Tot': bwd_iat.sum(),
            'Bwd IAT Mean': bwd_iat.mean() if len(bwd_iat) > 0 else 0,
            'Fwd PSH Flags': fwd['PSH'].sum() if 'PSH' in fwd.columns else 0,
            'SYN Flag Cnt': g['SYN'].sum(),
            'RST Flag Cnt': g['RST'].sum(),
            'ACK Flag Cnt': g['ACK'].sum(),
            'Fwd Pkts/s': len(fwd) / dur_sec,
            'Bwd Pkts/s': len(bwd) / dur_sec,
            'Pkt Len Min': all_lens.min(),
            'Pkt Len Max': all_lens.max(),
            'Pkt Len Mean': all_lens.mean(),
            'FIN Flag Cnt': g['FIN'].sum(),
            'PSH Flag Cnt': g['PSH'].sum(),
            'URG Flag Cnt': g['URG'].sum(),
            'Down/Up Ratio': len(bwd) / len(fwd) if len(fwd) > 0 else 0,
            'Init Fwd Win Byts': -1,
            'Init Bwd Win Byts': -1,
            'Fwd Seg Size Min': fwd_lens.min() if len(fwd_lens) > 0 else 0,
            'Fwd Act Data Pkts': (fwd['PSH'].sum() if 'PSH' in fwd.columns else 0),
            'Timestamp': g['timestamp'].min(),
            'Src IP': src,
            'Dst IP': dst
        })

    result = pd.DataFrame(flows)
    result.to_csv(output_csv, index=False)
    print(f"  Extracted {len(result)} flows → {output_csv}")

if __name__ == "__main__":
    input_f = sys.argv[1] if len(sys.argv) > 1 else "/opt/ids2018/flows/raw_packets.csv"
    output_f = sys.argv[2] if len(sys.argv) > 2 else "/opt/ids2018/flows/output.csv"
    extract(input_f, output_f)
