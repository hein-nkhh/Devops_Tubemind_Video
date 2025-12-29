output "cloudfront_domain_name" {
  description = "Domain name của CloudFront"
  value       = aws_cloudfront_distribution.this.domain_name
}

output "cloudfront_distribution_id" {
  value = aws_cloudfront_distribution.this.id
}
output "cloudfront_arn" {
  description = "ARN của CloudFront Distribution"
  value       = aws_cloudfront_distribution.this.arn
}