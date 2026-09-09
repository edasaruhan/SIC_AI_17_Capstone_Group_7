output "load_balancer_dns_name" {
  value = aws_lb.main.dns_name
}

output "object_bucket" {
  value = aws_s3_bucket.objects.id
}

output "application_secret_arn" {
  value = aws_secretsmanager_secret.application.arn
}

output "database_endpoint" {
  value     = aws_db_instance.main.endpoint
  sensitive = true
}

output "redis_endpoint" {
  value     = aws_elasticache_replication_group.main.primary_endpoint_address
  sensitive = true
}
