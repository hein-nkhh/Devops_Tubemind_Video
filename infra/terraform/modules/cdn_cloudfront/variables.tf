variable "bucket_name" {
  description = "Tên bucket S3 chứa video"
  type        = string
}

variable "bucket_arn" {
  description = "ARN của bucket S3"
  type        = string
}

variable "bucket_domain_name" {
  description = "Regional domain name của S3 bucket"
  type        = string
}
variable "cloudfront_comment" {
  description = "Comment cho CloudFront Distribution"
  type        = string
  default     = "CDN for Tubemind Video Platform"
}