resource "aws_security_group" "allow_all" {
  name        = "devops-lab-sg"
  description = "Allow inbound traffic"
  vpc_id      = var.vpc_id # Lấy từ module Networking truyền vào

  # Dynamic block để code ngắn gọn hơn
  dynamic "ingress" {
    for_each = [22, 8081, 9001, 30443, 30080, 5432] # 5432 cho DB
    content {
      from_port   = ingress.value
      to_port     = ingress.value
      protocol    = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
    }
  }

  # Range port cho App NodePort
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