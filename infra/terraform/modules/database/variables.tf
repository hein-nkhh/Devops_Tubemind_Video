variable "subnet_ids" { type = list(string) }
variable "sg_id" {}
variable "db_username" { default = "tubemind_user" }
variable "db_password" {} # Sẽ truyền từ file secret hoặc biến môi trường