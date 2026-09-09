locals {
  name          = "growthpilot-${var.environment}"
  public_cidrs  = ["10.40.0.0/24", "10.40.1.0/24"]
  private_cidrs = ["10.40.10.0/24", "10.40.11.0/24"]
}

resource "aws_kms_key" "main" {
  description             = "GrowthPilot ${var.environment} data encryption"
  deletion_window_in_days = 30
  enable_key_rotation     = true
}

resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true
  tags                 = { Name = local.name }
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
}

resource "aws_subnet" "public" {
  count                   = 2
  vpc_id                  = aws_vpc.main.id
  cidr_block              = local.public_cidrs[count.index]
  availability_zone       = var.availability_zones[count.index]
  map_public_ip_on_launch = false
  tags                    = { Name = "${local.name}-public-${count.index + 1}" }
}

resource "aws_subnet" "private" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = local.private_cidrs[count.index]
  availability_zone = var.availability_zones[count.index]
  tags              = { Name = "${local.name}-private-${count.index + 1}" }
}

resource "aws_eip" "nat" {
  domain     = "vpc"
  depends_on = [aws_internet_gateway.main]
}

resource "aws_nat_gateway" "main" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public[0].id
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }
}

resource "aws_route_table_association" "public" {
  count          = 2
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id
  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.main.id
  }
}

resource "aws_route_table_association" "private" {
  count          = 2
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private.id
}

resource "aws_security_group" "alb" {
  name   = "${local.name}-alb"
  vpc_id = aws_vpc.main.id
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "application" {
  name   = "${local.name}-application"
  vpc_id = aws_vpc.main.id
  ingress {
    from_port       = 3000
    to_port         = 3000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }
  ingress {
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "data" {
  name   = "${local.name}-data"
  vpc_id = aws_vpc.main.id
  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.application.id]
  }
  ingress {
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.application.id]
  }
}

resource "aws_s3_bucket" "objects" {
  bucket_prefix = "${local.name}-objects-"
  force_destroy = false
}

resource "aws_s3_bucket_versioning" "objects" {
  bucket = aws_s3_bucket.objects.id
  versioning_configuration { status = "Enabled" }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "objects" {
  bucket = aws_s3_bucket.objects.id
  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.main.arn
      sse_algorithm     = "aws:kms"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "objects" {
  bucket                  = aws_s3_bucket.objects.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_db_subnet_group" "main" {
  name       = local.name
  subnet_ids = aws_subnet.private[*].id
}

resource "aws_db_instance" "main" {
  identifier                   = local.name
  engine                       = "postgres"
  instance_class               = "db.t4g.medium"
  allocated_storage            = 50
  max_allocated_storage        = 250
  storage_encrypted            = true
  kms_key_id                   = aws_kms_key.main.arn
  db_name                      = var.database_name
  username                     = var.database_username
  password                     = var.database_password
  db_subnet_group_name         = aws_db_subnet_group.main.name
  vpc_security_group_ids       = [aws_security_group.data.id]
  backup_retention_period      = 14
  copy_tags_to_snapshot        = true
  deletion_protection          = true
  multi_az                     = true
  auto_minor_version_upgrade   = true
  performance_insights_enabled = true
  skip_final_snapshot          = false
  final_snapshot_identifier    = "${local.name}-final"
}

resource "aws_elasticache_subnet_group" "main" {
  name       = local.name
  subnet_ids = aws_subnet.private[*].id
}

resource "aws_elasticache_replication_group" "main" {
  replication_group_id       = local.name
  description                = "GrowthPilot broker, coordination and rate-limit Redis"
  node_type                  = "cache.t4g.small"
  num_cache_clusters         = 2
  port                       = 6379
  subnet_group_name          = aws_elasticache_subnet_group.main.name
  security_group_ids         = [aws_security_group.data.id]
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  auth_token                 = var.redis_auth_token
  automatic_failover_enabled = true
  multi_az_enabled           = true
  snapshot_retention_limit   = 7
}

resource "aws_secretsmanager_secret" "application" {
  name        = "${local.name}/application"
  kms_key_id  = aws_kms_key.main.id
  description = "Populate OIDC, database runtime, Redis, HMAC and optional provider credentials outside Terraform."
}

resource "aws_cloudwatch_log_group" "application" {
  name              = "/growthpilot/${var.environment}/application"
  retention_in_days = 30
  kms_key_id        = aws_kms_key.main.arn
}

resource "aws_ecs_cluster" "main" {
  name = local.name
  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

data "aws_iam_policy_document" "task_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "execution" {
  name               = "${local.name}-execution"
  assume_role_policy = data.aws_iam_policy_document.task_assume.json
}

resource "aws_iam_role_policy_attachment" "execution" {
  role       = aws_iam_role.execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

data "aws_iam_policy_document" "execution_secret" {
  statement {
    actions   = ["secretsmanager:GetSecretValue", "kms:Decrypt"]
    resources = [aws_secretsmanager_secret.application.arn, aws_kms_key.main.arn]
  }
}

resource "aws_iam_role_policy" "execution_secret" {
  role   = aws_iam_role.execution.id
  policy = data.aws_iam_policy_document.execution_secret.json
}

resource "aws_iam_role" "task" {
  name               = "${local.name}-task"
  assume_role_policy = data.aws_iam_policy_document.task_assume.json
}

data "aws_iam_policy_document" "task" {
  statement {
    actions   = ["s3:GetObject", "s3:PutObject", "s3:AbortMultipartUpload"]
    resources = ["${aws_s3_bucket.objects.arn}/*"]
  }
  statement {
    actions   = ["s3:ListBucket"]
    resources = [aws_s3_bucket.objects.arn]
  }
  statement {
    actions   = ["kms:Decrypt", "kms:Encrypt", "kms:GenerateDataKey"]
    resources = [aws_kms_key.main.arn]
  }
}

resource "aws_iam_role_policy" "task" {
  role   = aws_iam_role.task.id
  policy = data.aws_iam_policy_document.task.json
}

resource "aws_lb" "main" {
  name               = substr(local.name, 0, 32)
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id
}

resource "aws_lb_target_group" "web" {
  name        = substr("${local.name}-web", 0, 32)
  port        = 3000
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"
  health_check {
    path    = "/"
    matcher = "200-399"
  }
}

resource "aws_lb_target_group" "api" {
  name        = substr("${local.name}-api", 0, 32)
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"
  health_check {
    path    = "/health/live"
    matcher = "200"
  }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = 80
  protocol          = "HTTP"
  default_action {
    type = "redirect"
    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}

resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.main.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"
  certificate_arn   = var.certificate_arn
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.web.arn
  }
}

resource "aws_lb_listener_rule" "api" {
  listener_arn = aws_lb_listener.https.arn
  priority     = 10
  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.api.arn
  }
  condition {
    path_pattern {
      values = ["/api/*", "/health/*"]
    }
  }
}

locals {
  common_environment = [
    { name = "GP_ENVIRONMENT", value = "production" },
    { name = "GP_AUTH_MODE", value = "oidc" },
    { name = "GP_OBJECT_BACKEND", value = "s3" },
    { name = "GP_S3_BUCKET", value = aws_s3_bucket.objects.id },
    { name = "GP_MARKETING_KILL_SWITCH", value = "true" },
    { name = "GP_MAX_CAMPAIGN_BUDGET", value = "0" },
  ]
}

resource "aws_ecs_task_definition" "api" {
  family                   = "${local.name}-api"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = 512
  memory                   = 1024
  execution_role_arn       = aws_iam_role.execution.arn
  task_role_arn            = aws_iam_role.task.arn
  container_definitions    = jsonencode([{ name = "api", image = var.backend_image, essential = true, portMappings = [{ containerPort = 8000 }], environment = local.common_environment, secrets = [{ name = "GP_DATABASE_URL", valueFrom = "${aws_secretsmanager_secret.application.arn}:database_url::" }, { name = "GP_REDIS_URL", valueFrom = "${aws_secretsmanager_secret.application.arn}:redis_url::" }, { name = "GP_IDENTIFIER_HMAC_SECRET", valueFrom = "${aws_secretsmanager_secret.application.arn}:identifier_hmac_secret::" }, { name = "GP_OIDC_ISSUER", valueFrom = "${aws_secretsmanager_secret.application.arn}:oidc_issuer::" }, { name = "GP_OIDC_AUDIENCE", valueFrom = "${aws_secretsmanager_secret.application.arn}:oidc_audience::" }, { name = "GP_OIDC_JWKS_URL", valueFrom = "${aws_secretsmanager_secret.application.arn}:oidc_jwks_url::" }], logConfiguration = { logDriver = "awslogs", options = { "awslogs-group" = aws_cloudwatch_log_group.application.name, "awslogs-region" = var.aws_region, "awslogs-stream-prefix" = "api" } } }])
}

resource "aws_ecs_task_definition" "web" {
  family                   = "${local.name}-web"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = 512
  memory                   = 1024
  execution_role_arn       = aws_iam_role.execution.arn
  task_role_arn            = aws_iam_role.task.arn
  container_definitions    = jsonencode([{ name = "web", image = var.web_image, essential = true, portMappings = [{ containerPort = 3000 }], secrets = [{ name = "GP_API_URL", valueFrom = "${aws_secretsmanager_secret.application.arn}:api_url::" }, { name = "GP_SERVER_TOKEN", valueFrom = "${aws_secretsmanager_secret.application.arn}:server_token::" }, { name = "GP_ORGANIZATION_ID", valueFrom = "${aws_secretsmanager_secret.application.arn}:organization_id::" }], logConfiguration = { logDriver = "awslogs", options = { "awslogs-group" = aws_cloudwatch_log_group.application.name, "awslogs-region" = var.aws_region, "awslogs-stream-prefix" = "web" } } }])
}

resource "aws_ecs_task_definition" "worker" {
  family                   = "${local.name}-worker"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = 512
  memory                   = 1024
  execution_role_arn       = aws_iam_role.execution.arn
  task_role_arn            = aws_iam_role.task.arn
  container_definitions    = jsonencode([{ name = "worker", image = var.backend_image, essential = true, command = ["dramatiq", "app.platform.jobs"], environment = local.common_environment, secrets = [{ name = "GP_DATABASE_URL", valueFrom = "${aws_secretsmanager_secret.application.arn}:database_url::" }, { name = "GP_REDIS_URL", valueFrom = "${aws_secretsmanager_secret.application.arn}:redis_url::" }, { name = "GP_IDENTIFIER_HMAC_SECRET", valueFrom = "${aws_secretsmanager_secret.application.arn}:identifier_hmac_secret::" }, { name = "GP_OIDC_ISSUER", valueFrom = "${aws_secretsmanager_secret.application.arn}:oidc_issuer::" }, { name = "GP_OIDC_AUDIENCE", valueFrom = "${aws_secretsmanager_secret.application.arn}:oidc_audience::" }, { name = "GP_OIDC_JWKS_URL", valueFrom = "${aws_secretsmanager_secret.application.arn}:oidc_jwks_url::" }], logConfiguration = { logDriver = "awslogs", options = { "awslogs-group" = aws_cloudwatch_log_group.application.name, "awslogs-region" = var.aws_region, "awslogs-stream-prefix" = "worker" } } }])
}

resource "aws_ecs_service" "api" {
  name            = "api"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.api.arn
  desired_count   = var.desired_api_count
  launch_type     = "FARGATE"
  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.application.id]
    assign_public_ip = false
  }
  load_balancer {
    target_group_arn = aws_lb_target_group.api.arn
    container_name   = "api"
    container_port   = 8000
  }
  depends_on = [aws_lb_listener.https]
}

resource "aws_ecs_service" "web" {
  name            = "web"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.web.arn
  desired_count   = var.desired_web_count
  launch_type     = "FARGATE"
  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.application.id]
    assign_public_ip = false
  }
  load_balancer {
    target_group_arn = aws_lb_target_group.web.arn
    container_name   = "web"
    container_port   = 3000
  }
  depends_on = [aws_lb_listener.https]
}

resource "aws_ecs_service" "worker" {
  name            = "worker"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.worker.arn
  desired_count   = var.desired_worker_count
  launch_type     = "FARGATE"
  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.application.id]
    assign_public_ip = false
  }
}
