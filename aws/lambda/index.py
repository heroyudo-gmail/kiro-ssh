import json
import boto3
import os
import csv
from io import StringIO
import numpy as np

s3 = boto3.client('s3')
sns = boto3.client('sns')

# The 10 optimized features from our XGBoost training (in order)
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

# XGBoost model loaded at cold start
# Model file should be included in deployment package or Lambda Layer
MODEL = None


def load_model():
    """Load XGBoost model from deployment package."""
    global MODEL
    if MODEL is None:
        try:
            import xgboost as xgb
            MODEL = xgb.Booster()
            # Model file location: same directory or /opt (Lambda Layer)
            model_path = os.path.join(os.path.dirname(__file__), 'xgboost_model.json')
            if not os.path.exists(model_path):
                model_path = '/opt/xgboost_model.json'  # Lambda Layer path
            MODEL.load_model(model_path)
            print(f"XGBoost model loaded from {model_path}")
        except Exception as e:
            print(f"Failed to load XGBoost model: {e}")
            MODEL = None
    return MODEL


def predict_flow_xgboost(features_array):
    """
    Predict using XGBoost model.
    features_array: 2D numpy array (n_samples, 10 features)
    Returns: list of predictions (0=benign, 1=attack)
    """
    import xgboost as xgb
    model = load_model()
    if model is None:
        print("WARNING: Model not loaded, falling back to rule-based")
        return predict_flow_rules(features_array)

    dmatrix = xgb.DMatrix(features_array, feature_names=FEATURE_NAMES)
    probabilities = model.predict(dmatrix)
    predictions = (probabilities > 0.5).astype(int).tolist()
    return predictions


def predict_flow_rules(features_array):
    """
    Fallback rule-based prediction if XGBoost model unavailable.
    Uses Flow Pkts/s threshold.
    """
    predictions = []
    for row in features_array:
        flow_pkts_s = row[3]  # Index 3 = Flow Pkts/s
        if flow_pkts_s > 1.0:
            predictions.append(1)
        else:
            predictions.append(0)
    return predictions


def parse_csv_features(content):
    """
    Parse CSV content and extract the 10 required features.
    Returns numpy array of shape (n_flows, 10).
    """
    reader = csv.DictReader(StringIO(content))
    features_list = []

    for row in reader:
        try:
            feature_values = []
            for feat_name in FEATURE_NAMES:
                val = float(row.get(feat_name, 0))
                feature_values.append(val)
            features_list.append(feature_values)
        except (ValueError, KeyError) as e:
            print(f"Skipping row due to parse error: {e}")
            continue

    if not features_list:
        return np.array([]).reshape(0, 10)

    return np.array(features_list)


def handler(event, context):
    """
    Lambda handler - triggered by S3 event.
    1. Read feature CSV from S3
    2. Predict each flow using XGBoost model
    3. Send SNS alert if attack detected
    """
    try:
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = event['Records'][0]['s3']['object']['key']
        print(f"Processing: s3://{bucket}/{key}")

        # Read CSV from S3
        response = s3.get_object(Bucket=bucket, Key=key)
        content = response['Body'].read().decode('utf-8')

        # Parse features
        features_array = parse_csv_features(content)
        total_flows = len(features_array)

        if total_flows == 0:
            print("No valid flows found in CSV")
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'total_flows': 0,
                    'attacks': 0,
                    'status': 'no_data'
                })
            }

        # Predict using XGBoost model
        predictions = predict_flow_xgboost(features_array)
        attack_count = sum(predictions)

        print(f"Results: {attack_count}/{total_flows} attacks detected")

        if attack_count > 0:
            # Send SNS alert
            topic_arn = os.environ.get('SNS_TOPIC_ARN')
            if topic_arn:
                message = (
                    f"SSH BRUTE-FORCE DETECTED!\n\n"
                    f"Source: s3://{bucket}/{key}\n"
                    f"Total flows analyzed: {total_flows}\n"
                    f"Attacks detected: {attack_count}\n"
                    f"Benign flows: {total_flows - attack_count}\n"
                    f"Detection rate: {attack_count/total_flows*100:.1f}%\n"
                    f"\nAction: Investigate source IPs immediately.\n"
                    f"Model: XGBoost (10 features, 84 KB)\n"
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
                'benign': total_flows - attack_count,
                'status': 'alert_sent' if attack_count > 0 else 'clear',
                'model': 'xgboost'
            })
        }

    except Exception as e:
        print(f"ERROR: {str(e)}")
        raise
