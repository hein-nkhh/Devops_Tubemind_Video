# 1. Tạo Subnet Group cho RDS
resource "aws_db_subnet_group" "default" {
  name       = "tubemind-db-subnet-group"
  subnet_ids = var.subnet_ids # Truyền danh sách subnet vào đây

  tags = { Name = "My DB subnet group" }
}

# 2. Tạo Database PostgreSQL
resource "aws_db_instance" "postgres" {
  identifier           = "tubemind-postgres-db"
  allocated_storage    = 20    # 20GB (Free tier)
  storage_type         = "gp2"
  engine               = "postgres"
  engine_version       = "15"  # Hoặc 14, tuỳ nhu cầu
  instance_class       = "db.t3.micro" # Free tier eligible
  db_name              = "tubemind_db"
  username             = var.db_username
  password             = var.db_password
  
  # Network
  db_subnet_group_name   = aws_db_subnet_group.default.name
  vpc_security_group_ids = [var.sg_id]
  publicly_accessible    = true # Để K3s (ở public subnet) kết nối được dễ dàng
  skip_final_snapshot    = true # Để xoá cho nhanh, ko backup cuối

  tags = { Name = "Tubemind-Postgres" }
}