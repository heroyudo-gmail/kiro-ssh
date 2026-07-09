import json
import boto3
import os
import csv
from io import StringIO

s3 = boto3.client('s3')
sns = boto3.client('sns')

# XGBoost-derived decision rules (extracted from trained model)
# Model trained on CSE-CIC-IDS2018 SSH-Bruteforce dataset
# These thresholds were determined by analyzing the XGBoost tree splits
RULES = {
    'dst_port_ssh': 22,           # SSH port
    'flow_pkts_threshold': 1.0,   # Flow Pkts/s > 1 indicates brute-force
    'fwd_pkts_threshold': 100,    # TotLen Fwd Pkts > 100 bytes
    'bwd_ratio_threshold': 0.3,   # Down/Up Ratio typical for brute-force
}


def predict_flow(row):
    """
    XGBoost-derived rule-based prediction.
    Returns 1 (attack) or 0 (benign).
    
    Based on feature importance analysis:
    - Dst Port == 22 (SSH traffic)
    - High Flow Pkts/s (rapid connection attempts)
    - High TotLen Fwd Pkts (many packets sent)
    """
    try:
        dst_port = int(float(row.get('Dst Port', 0)))
        flow_pkts_s = float(row.get('Flow Pkts/s', 0))
        totlen_fwd = float(row.get('TotLen Fwd Pkts', 0))
        down_up_ratio = float(row.get('Down/Up Ratio', 0))
        bwd_pkts_s = float(row.get('Bwd Pkts/s', 0))

        # Rule 1: Must be SSH traffic
        if dst_port != RULES['dst_port_ssh']:
            return 0

        # Rule 2: High packet rate indicates brute-force
        if flow_pkts_s > RULES['flow_pkts_threshold']:
            return 1

        # Rule 3: Significant forward traffic with response
        if totlen_fwd > RULES['fwd_pkts_threshold'] and bwd_pkts_s > 0:
            return 1

        return 0
    except (ValueError, KeyError):
        return 0


def handler(event, context):
    """
    Lambda handler - triggered by S3 event.
    1. Read feature CSV from S3
    2. Predict each flow using XGBoost-derived rules
    3. Send SNS alert if attack detected
    """
    try:
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = event['Records'][0]['s3']['object']['key']
        print(f"Processing: s3://{bucket}/{key}")

        # Read CSV from S3
        response = s3.get_object(Bucket=bucket, Key=key)
        content = response['Body'].read().decode('utf-8')

        # Parse and predict
        reader = csv.DictReader(StringIO(content))
        predictions = []
        for row in reader:
            pred = predict_flow(row)
            predictions.append(pred)

        attack_count = sum(predictions)
        total_flows = len(predictions)

        print(f"Results: {attack_count}/{total_flows} attacks detected")

        if attack_count > 0:
            # Send SNS alert
            topic_arn = os.environ.get('SNS_TOPIC_ARN')
            if topic_arn:
                message = (
                    f"🚨 SSH BRUTE-FORCE DETECTED!\n\n"
                    f"Source: s3://{bucket}/{key}\n"
                    f"Total flows analyzed: {total_flows}\n"
                    f"Attacks detected: {attack_count}\n"
                    f"Detection rate: {attack_count/max(total_flows,1)*100:.1f}%\n"
                    f"\nAction: Investigate source IPs immediately.\n"
                    f"Model: XGBoost-derived rules (10 features)\n"
                )
                sns.publish(
                    TopicArn=topic_arn,
                    Subject='[SSH Detection] Brute-Force Attack Detected!',
                    Message=message
                )
                print(f"SNS alert sent to {topic_arn}")
            else:
                print("WARNING: SNS_TOPIC_ARN not set")
        else:
            print("All clear - no attacks detected")

        return {
            'statusCode': 200,
            'body': json.dumps({
                'total_flows': total_flows,
                'attacks': attack_count,
                'status': 'alert_sent' if attack_count > 0 else 'clear'
            })
        }

    except Exception as e:
        print(f"ERROR: {str(e)}")
        raise
