resource "aws_ecr_repository" "repos" {
  for_each             = toset(var.repo_names)
  name                 = each.value
  image_tag_mutability = "MUTABLE"

  # Scan lỗ hổng bảo mật khi push image lên (Tính năng xịn của AWS)
  image_scanning_configuration {
    scan_on_push = true
  }

  # Xoá repo là xoá sạch image bên trong (Dùng cho môi trường Dev/Lab)
  force_delete = true 
}