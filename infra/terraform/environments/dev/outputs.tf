output "jenkins_url" {
  value = "http://${module.jenkins_server.public_ip}:8081"
}
output "sonar_url" {
  value = "http://${module.jenkins_server.public_ip}:9001"
}
output "argocd_ui" {
  value = "https://${module.k8s_server.public_ip}:30443"
}
output "rds_endpoint" {
  value = module.database.db_endpoint
}
output "s3_bucket_name" {
  value = module.storage.bucket_name
}
output "s3_bucket_arn" {
  value = module.storage.bucket_arn
}
output "ecr_repository_urls" {
  value = module.ecr.repository_urls
}