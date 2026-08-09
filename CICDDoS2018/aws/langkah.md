

#Testing 1 vpc 1 node untuk semua attacker,target dan analyzer

#1. create vpc 
aws cloudformation create-stack --stack-name multidetect-network --template-body file://05-single-node-debian.yaml --region ap-southeast-1 --no-cli-pager


aws cloudformation delete-stack --stack-name multidetect-network --region ap-southeast-1 --no-cli-pager; 


#2. create instance
aws cloudformation create-stack --stack-name multidetect-instance --template-body file://06-debian-instance.yaml --capabilities CAPABILITY_NAMED_IAM --region ap-southeast-1 --no-cli-pager

aws cloudformation delete-stack --stack-name multidetect-instance --region ap-southeast-1 --no-cli-pager; 

aws cloudformation describe-stacks --stack-name multidetect-instance --region ap-southeast-1 --query "Stacks[0].StackStatus" --output text --no-cli-pager


# stop instance
aws ec2 stop-instances --instance-ids INSTANCE_ID --region ap-southeast-1 --no-cli-pager

# start instance
aws ec2 start-instances --instance-ids INSTANCE_ID --region ap-southeast-1 --no-cli-pager

Installasi untuk attacker-1
sudo yum update -y

Attack tools:
# Hydra (SSH/FTP brute-force)
sudo yum install -y gcc make openssl-devel libssh-devel
cd /tmp && curl -sL -o hydra.tar.gz https://github.com/vanhauser-thc/thc-hydra/archive/refs/tags/v9.5.tar.gz
tar xzf hydra.tar.gz && cd thc-hydra-9.5 && ./configure && make && sudo make install

# Nmap + nping (SYN flood)
sudo yum install -y nmap

# Slowloris + GoldenEye
sudo yum install -y python3 python3-pip git
sudo pip3 install slowloris
sudo git clone https://github.com/jseidl/GoldenEye.git /opt/GoldenEye

# SlowHTTPTest
sudo yum install -y gcc-c++
cd /tmp && curl -sL -o slowhttp.tar.gz https://github.com/shekyan/slowhttptest/archive/refs/tags/v1.9.0.tar.gz
tar xzf slowhttp.tar.gz && cd slowhttptest-1.9.0 && ./configure && make && sudo make install

# ApacheBench (HTTP flood)
sudo yum install -y httpd-tools

# tcpdump
sudo yum install -y tcpdump


