resource "aws_s3_bucket" "video_bucket" {
  bucket_prefix = "tubemind-videos-"
  force_destroy = true

  tags = {
    Name = "Tubemind Video Storage"
  }
}

# Block toàn bộ public access (BẮT BUỘC)
resource "aws_s3_bucket_public_access_block" "this" {
  bucket = aws_s3_bucket.video_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
