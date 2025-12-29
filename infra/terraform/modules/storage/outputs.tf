output "bucket_name" {
  value = aws_s3_bucket.video_bucket.id
}
output "bucket_arn" {
  value = aws_s3_bucket.video_bucket.arn
}
output "bucket_domain_name" {
  value = aws_s3_bucket.video_bucket.bucket_regional_domain_name
}