resource "aws_vpc" "devops_vpc" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags = { Name = "devops-vpc" }
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.devops_vpc.id
  tags = { Name = "devops-igw" }
}

# Subnet 1 (us-east-1a)
resource "aws_subnet" "public_1" {
  vpc_id                  = aws_vpc.devops_vpc.id
  cidr_block              = var.public_subnet_1_cidr
  availability_zone       = "us-east-1a"
  map_public_ip_on_launch = true
  tags = { Name = "devops-public-subnet-1" }
}

# Subnet 2 (us-east-1b) - CẦN THIẾT CHO RDS SAU NÀY
resource "aws_subnet" "public_2" {
  vpc_id                  = aws_vpc.devops_vpc.id
  cidr_block              = var.public_subnet_2_cidr
  availability_zone       = "us-east-1b"
  map_public_ip_on_launch = true
  tags = { Name = "devops-public-subnet-2" }
}

resource "aws_route_table" "public_rt" {
  vpc_id = aws_vpc.devops_vpc.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }
  tags = { Name = "devops-public-rt" }
}

resource "aws_route_table_association" "public_assoc_1" {
  subnet_id      = aws_subnet.public_1.id
  route_table_id = aws_route_table.public_rt.id
}

resource "aws_route_table_association" "public_assoc_2" {
  subnet_id      = aws_subnet.public_2.id
  route_table_id = aws_route_table.public_rt.id
}