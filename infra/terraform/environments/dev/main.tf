# 1. Tạo SSH Key Pair (Resource này thuộc về Environment)
resource "aws_key_pair" "deployer" {
  key_name   = "devops-lab-key"
  # Dùng pathexpand để Terraform hiểu dấu ~ trên Linux/WSL
  public_key = file("${pathexpand("~")}/.ssh/devops_key.pub")
}

# 2. Gọi Module Networking
module "networking" {
  source = "../../modules/networking"
}

# 3. Gọi Module Security
module "security" {
  source = "../../modules/security"
  vpc_id = module.networking.vpc_id # Lấy VPC ID từ module trên truyền xuống
}

# 4. Gọi Module CI/CD (Jenkins)
module "jenkins_server" {
  source    = "../../modules/compute_cicd"
  ami_id    = var.ami_id
  key_name  = aws_key_pair.deployer.key_name
  subnet_id = module.networking.public_subnet_1_id
  sg_id     = module.security.sg_id
}

# 5. Gọi Module K8s (Target)
module "k8s_server" {
  source    = "../../modules/compute_k8s"
  ami_id    = var.ami_id
  key_name  = aws_key_pair.deployer.key_name
  subnet_id = module.networking.public_subnet_1_id
  sg_id     = module.security.sg_id
}

# 6. Tạo file Inventory cho Ansible
resource "local_file" "ansible_inventory" {
  # Lưu ý đường dẫn file template. Mình giả định nó nằm ở infra/terraform/templates/
  content = templatefile("../../templates/inventory.tpl", {
    ci_ip     = module.jenkins_server.public_ip
    target_ip = module.k8s_server.public_ip
    ssh_key   = "${pathexpand("~")}/.ssh/devops_key"
    ssh_user  = "ec2-user" # AMI Amazon Linux dùng ec2-user, Ubuntu dùng ubuntu
  })
  filename = "../../../ansible/inventory.ini"
}

# 7. Gọi Module Database
module "database" {
  source = "../../modules/database"
  
  # Truyền 2 subnet (đã tạo ở Networking) vào để đảm bảo High Availability
  subnet_ids  = [
    module.networking.public_subnet_1_id, 
    module.networking.public_subnet_2_id
  ]
  sg_id       = module.security.sg_id
  
  # Pass này nên để trong secrets, nhưng dev thì hardcode tạm cũng được
  db_password = "super_secret_password_123" 
}

# 8. Gọi Module Storage
module "storage" {
  source = "../../modules/storage"
}

# 9. Gọi Module CDN CloudFront
module "cdn" {
  source = "../../modules/cdn_cloudfront"

  bucket_name        = module.storage.bucket_name
  bucket_arn         = module.storage.bucket_arn
  bucket_domain_name = module.storage.bucket_domain_name
}

# 10. Gọi Module ECR
module "ecr" {
  source = "../../modules/ecr"
  # Tạo trước 4 cái repo cho 4 service của bạn
  repo_names = ["tubemind/api-gateway", "tubemind/transcriber", "tubemind/summarizer", "tubemind/notifier"]
}