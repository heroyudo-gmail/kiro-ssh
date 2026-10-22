#!/usr/bin/env python3
"""
IDS2018 — Inference Script (runs on Analyzer EC2)
==================================================
Reads CICFlowMeter CSV output, predicts with 3 models,
compares vs ground truth schedule, outputs performance metrics.

Usage:
    python3 inference.py \
        --flows-dir /opt/ids2018/flows/ \
        --models-dir /opt/ids2018/models/ \
        --schedule /opt/ids2018/schedule/schedule.json \
        --output-dir /opt/ids2018/results/
"""

import argparse
import json
import os
import glob
import time
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import pickle

def load_models(models_dir):
    """Load all models + metadata from deploy directory."""
    models = []
    meta_files = sorted(glob.glob(os.path.join(models_dir, '*_meta.json')))

    for meta_path in meta_files:
        with open(meta_path, 'r') as f:
            meta = json.load(f)

        model_path = os.path.join(models_dir, meta['model_file'])
        model_type = meta.get('model_type', 'XGBoost')

        if model_path.endswith('.json'):
            # XGBoost native
            import xgboost as xgb
            model = xgb.XGBClassifier()
            model.load_model(model_path)
        elif model_path.endswith('.pkl'):
            # sklearn (RF, SVM)
            with open(model_path, 'rb') as f:
                model = pickle.load(f)
        else:
            print(f"  WARNING: Unknown model format: {model_path}")
            continue

        models.append({
            'model': model,
            'meta': meta,
            'name': f"Rank{meta.get('rank', '?')}_{model_type}_{meta.get('feature_scenario', '')}"
        })
        print(f"  Loaded: {models[-1]['name']} ({len(meta['feature_names'])} features)")

    return models


def load_schedule(schedule_path):
    """Load ground truth schedule."""
    with open(schedule_path, 'r') as f:
        schedule = json.load(f)
    return schedule


def get_ground_truth_label(timestamp, test_start_time, schedule):
    """Determine ground truth label based on timestamp and schedule."""
    elapsed_min = (timestamp - test_start_time).total_seconds() / 60.0

    for phase in schedule['phases']:
        if phase['start_min'] <= elapsed_min < phase['end_min']:
            return phase['label']

    return 'Benign'  # default


def preprocess_flow(row, meta):
    """Extract and scale features for a single flow."""
    feature_names = meta['feature_names']
    scaler_mean = np.array(meta['scaler']['mean'])
    scaler_scale = np.array(meta['scaler']['scale'])

    # Extract features
    features = []
    for feat in feature_names:
        val = row.get(feat, 0)
        try:
            val = float(val)
            if np.isinf(val) or np.isnan(val):
                val = 0.0
        except (ValueError, TypeError):
            val = 0.0
        features.append(val)

    X = np.array(features).reshape(1, -1)

    # Scale
    X_scaled = (X - scaler_mean) / scaler_scale
    X_scaled = np.nan_to_num(X_scaled, nan=0.0, posinf=0.0, neginf=0.0)

    return X_scaled


def predict_flow(X_scaled, model_info):
    """Predict a single flow with one model."""
    model = model_info['model']
    meta = model_info['meta']
    inverse_map = meta['inverse_label_mapping']

    pred_idx = model.predict(X_scaled)[0]
    pred_label = inverse_map.get(str(int(pred_idx)), f'Unknown_{pred_idx}')

    return pred_label


def run_inference(flows_dir, models_dir, schedule_path, output_dir):
    """Main inference pipeline."""
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 60)
    print("IDS2018 INFERENCE — Analyzer")
    print("=" * 60)

    # Load models
    print("\n[1] Loading models...")
    models = load_models(models_dir)
    if not models:
        print("ERROR: No models found!")
        return
    print(f"  Total models: {len(models)}")

    # Load schedule
    print("\n[2] Loading schedule...")
    schedule = load_schedule(schedule_path)
    print(f"  Phases: {len(schedule['phases'])}")
    print(f"  Target IP: {schedule['target_ip']}")

    # Find test start time (from first flow file or schedule)
    # We'll use the earliest timestamp in flow data
    print("\n[3] Loading flow data...")
    flow_files = sorted(glob.glob(os.path.join(flows_dir, '*.csv')))
    if not flow_files:
        print("ERROR: No flow CSV files found!")
        return
    print(f"  Flow files: {len(flow_files)}")

    # Read all flows
    all_flows = []
    for fpath in flow_files:
        try:
            df = pd.read_csv(fpath, low_memory=False)
            df.columns = df.columns.str.strip()
            all_flows.append(df)
        except Exception as e:
            print(f"  WARNING: Error reading {fpath}: {e}")

    if not all_flows:
        print("ERROR: No valid flow data!")
        return

    df_flows = pd.concat(all_flows, ignore_index=True)
    print(f"  Total flows: {len(df_flows)}")

    # Parse timestamps
    ts_col = [c for c in df_flows.columns if 'timestamp' in c.lower()]
    if ts_col:
        df_flows['_timestamp'] = pd.to_datetime(df_flows[ts_col[0]], errors='coerce')
    else:
        # If no timestamp, assign sequential timestamps
        df_flows['_timestamp'] = pd.date_range(start=datetime.now(), periods=len(df_flows), freq='1s')

    test_start_time = df_flows['_timestamp'].min()
    print(f"  Test start: {test_start_time}")
    print(f"  Test end: {df_flows['_timestamp'].max()}")

    # Run predictions
    print(f"\n[4] Running predictions ({len(models)} models × {len(df_flows)} flows)...")
    results = []

    for idx, row in df_flows.iterrows():
        if idx % 1000 == 0:
            print(f"  Processing flow {idx}/{len(df_flows)}...")

        timestamp = row['_timestamp']
        actual_label = get_ground_truth_label(timestamp, test_start_time, schedule)

        result_row = {
            'flow_id': idx,
            'timestamp': str(timestamp),
            'src_ip': row.get('Src IP', row.get('src_ip', '')),
            'dst_ip': row.get('Dst IP', row.get('dst_ip', '')),
            'actual_label': actual_label
        }

        # Predict with each model
        for i, model_info in enumerate(models):
            try:
                X_scaled = preprocess_flow(row, model_info['meta'])
                pred_label = predict_flow(X_scaled, model_info)
            except Exception as e:
                pred_label = 'ERROR'

            result_row[f'predicted_rank{i+1}'] = pred_label
            result_row[f'correct_rank{i+1}'] = (pred_label == actual_label)

        results.append(result_row)

    df_results = pd.DataFrame(results)
    print(f"  Done! {len(df_results)} flows processed")

    # Save detailed results
    print("\n[5] Saving results...")
    results_csv = os.path.join(output_dir, 'target1_ml_results.csv')
    df_results.to_csv(results_csv, index=False)
    print(f"  Saved: {results_csv}")

    # Calculate performance metrics
    print("\n[6] Calculating performance metrics...")
    metrics_rows = []

    for i, model_info in enumerate(models):
        pred_col = f'predicted_rank{i+1}'
        correct_col = f'correct_rank{i+1}'

        total = len(df_results)
        correct = df_results[correct_col].sum()
        accuracy = correct / total * 100 if total > 0 else 0

        # Per-class metrics
        from sklearn.metrics import precision_score, recall_score, f1_score
        y_true = df_results['actual_label']
        y_pred = df_results[pred_col]

        precision = precision_score(y_true, y_pred, average='weighted', zero_division=0) * 100
        recall = recall_score(y_true, y_pred, average='weighted', zero_division=0) * 100
        f1 = f1_score(y_true, y_pred, average='weighted', zero_division=0) * 100

        metrics_rows.append({
            'model': model_info['name'],
            'accuracy': round(accuracy, 2),
            'precision': round(precision, 2),
            'recall': round(recall, 2),
            'f1_score': round(f1, 2),
            'total_flows': total,
            'correct': int(correct)
        })

        print(f"  {model_info['name']}: Acc={accuracy:.2f}% F1={f1:.2f}%")

    df_metrics = pd.DataFrame(metrics_rows)
    metrics_csv = os.path.join(output_dir, 'target1_ml_performance.csv')
    df_metrics.to_csv(metrics_csv, index=False)
    print(f"  Saved: {metrics_csv}")

    # Summary
    print(f"\n{'=' * 60}")
    print("INFERENCE COMPLETE!")
    print(f"{'=' * 60}")
    print(f"  Flows processed: {len(df_results)}")
    print(f"  Models evaluated: {len(models)}")
    print(f"  Results: {results_csv}")
    print(f"  Metrics: {metrics_csv}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='IDS2018 Inference')
    parser.add_argument('--flows-dir', default='/opt/ids2018/flows/')
    parser.add_argument('--models-dir', default='/opt/ids2018/models/')
    parser.add_argument('--schedule', default='/opt/ids2018/schedule/schedule.json')
    parser.add_argument('--output-dir', default='/opt/ids2018/results/')
    args = parser.parse_args()

    run_inference(args.flows_dir, args.models_dir, args.schedule, args.output_dir)
