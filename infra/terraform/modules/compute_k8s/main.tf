# 1. Tạo Role cho K8s Node
resource "aws_iam_role" "k8s_role" {
  name = "k8s_ecr_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = { Service = "ec2.amazonaws.com" }
    }]
  })
}

# 2. Gắn quyền ReadOnly (Chỉ được kéo Image về)
resource "aws_iam_role_policy_attachment" "k8s_policy" {
  role       = aws_iam_role.k8s_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}

# 3. Tạo Instance Profile
resource "aws_iam_instance_profile" "k8s_profile" {
  name = "k8s_instance_profile"
  role = aws_iam_role.k8s_role.name
}

resource "aws_instance" "target_server" {
  ami                    = var.ami_id
  instance_type          = "t3.small"
  key_name               = var.key_name
  subnet_id              = var.subnet_id
  vpc_security_group_ids = [var.sg_id]
  
  # K3s server không cần ổ cứng quá lớn nếu data lưu ở S3/RDS
  root_block_device {
    volume_size = 20 
  }

  tags = { Name = "K8s-Target-Server" }
  
  iam_instance_profile = aws_iam_instance_profile.k8s_profile.name
}