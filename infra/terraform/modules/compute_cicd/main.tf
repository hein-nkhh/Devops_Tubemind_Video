# 1. Tạo Role cho Jenkins
resource "aws_iam_role" "jenkins_role" {
  name = "jenkins_ecr_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = { Service = "ec2.amazonaws.com" }
    }]
  })
}

# 2. Gắn quyền PowerUser (Full quyền với ECR)
resource "aws_iam_role_policy_attachment" "jenkins_policy" {
  role       = aws_iam_role.jenkins_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryPowerUser"
}

# 3. Tạo Instance Profile (Để gắn vào EC2)
resource "aws_iam_instance_profile" "jenkins_profile" {
  name = "jenkins_instance_profile"
  role = aws_iam_role.jenkins_role.name
}


resource "aws_instance" "ci_server" {
  ami                    = var.ami_id
  instance_type          = "t3.small"
  key_name               = var.key_name
  subnet_id              = var.subnet_id
  vpc_security_group_ids = [var.sg_id]

  root_block_device {
    volume_size = 30
  }

  tags = { Name = "Jenkins-Sonar-Server" }
  
  iam_instance_profile = aws_iam_instance_profile.jenkins_profile.name
}