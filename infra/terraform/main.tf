provider "aws" {
  region = "us-east-1"
}

# Upload SSH Key lên AWS
resource "aws_key_pair" "deployer" {
  key_name   = "devops-lab-key"
  public_key = file("${pathexpand("~")}/.ssh/devops_key.pub")
}

# VPC
resource "aws_vpc" "devops_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "devops-vpc"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.devops_vpc.id

  tags = {
    Name = "devops-igw"
  }
}

# Public Subnet
resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.devops_vpc.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "us-east-1a"
  map_public_ip_on_launch = true

  tags = {
    Name = "devops-public-subnet"
  }
}

# Route Table
resource "aws_route_table" "public_rt" {
  vpc_id = aws_vpc.devops_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = {
    Name = "devops-public-rt"
  }
}

# Associate Route Table với Subnet
resource "aws_route_table_association" "public_assoc" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public_rt.id
}


# Security Group allowing inbound traffic
resource "aws_security_group" "allow_all" {
  name        = "devops-lab-sg"
  description = "Allow inbound traffic"
  vpc_id      = aws_vpc.devops_vpc.id

# SSH
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

# Jenkins
  ingress {
    from_port   = 8081
    to_port     = 8081
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

# SonarQube
  ingress {
    from_port   = 9001
    to_port     = 9001
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

# Argo CD NodePort (HTTPS)
  ingress {
    from_port   = 30443
    to_port     = 30443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

# Argo CD NodePort (HTTP - nếu cần)
  ingress {
    from_port   = 30080
    to_port     = 30080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

# App NodePort (Ví dụ app chạy port 30000-32767)
  ingress {
    from_port   = 30000
    to_port     = 32767
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# 3. Tạo EC2 cho CI/CD (Jenkins + Sonar) Server
variable "ami_id" {}

resource "aws_instance" "ci_server" {
  depends_on = [
    aws_internet_gateway.igw,
    aws_route_table_association.public_assoc
  ]
  ami           = var.ami_id
  instance_type = "t3.small" # Cần RAM 4GB
  key_name      = aws_key_pair.deployer.key_name
  
  subnet_id              = aws_subnet.public.id
  vpc_security_group_ids = [aws_security_group.allow_all.id]

  root_block_device {
    volume_size = 30 # Tăng ổ cứng lên 30GB
  }

  tags = { Name = "Jenkins-Sonar-Server" }
}

# 4. Tạo EC2 cho Target Cluster (K3s + ArgoCD)
resource "aws_instance" "target_server" {
  depends_on = [
    aws_internet_gateway.igw,
    aws_route_table_association.public_assoc
  ]
  ami           = var.ami_id
  instance_type = "t3.small" # Cần RAM 8GB
  key_name      = aws_key_pair.deployer.key_name
  
  subnet_id              = aws_subnet.public.id
  vpc_security_group_ids = [aws_security_group.allow_all.id]

  tags = { Name = "K8s-Target-Server" }
}

# 5. Tạo file inventory cho Ansible tự động
resource "local_file" "ansible_inventory" {
  content = templatefile("${path.module}/templates/inventory.tpl", {
    ci_ip     = aws_instance.ci_server.public_ip
    target_ip = aws_instance.target_server.public_ip
    ssh_key   = "${pathexpand("~")}/.ssh/devops_key"
    ssh_user  = "ec2-user"
  })
  filename = "../ansible/inventory.ini"
}

output "jenkins_url" {
  value = "http://${aws_instance.ci_server.public_ip}:8081"
}

output "sonar_url" {
  value = "http://${aws_instance.ci_server.public_ip}:9001"
}

output "argocd_ui" {
  value = "https://${aws_instance.target_server.public_ip}:30443"
}
