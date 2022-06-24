provider "aws" {
  region  = var.region
  profile = var.aws_profile
}
data aws_caller_identity current {}


locals {
 prefix = var.prefix
 account_id          = data.aws_caller_identity.current.account_id
}


resource "aws_ecr_repository" "netcdf_to_zarr" {
  name                 = "${var.prefix}_netcdf_to_zarr"
  image_scanning_configuration {
    scan_on_push = false
  }
  tags = {
    "name" = "netCDF4 to Zarr"
  }
}


resource "aws_iam_role_policy" "lambda_policy" {
  name = "lambda_policy"
  role = aws_iam_role.lambda_role.id

  # Terraform's "jsonencode" function converts a
  # Terraform expression result to valid JSON syntax.
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "ecr:BatchGetImage",
          "ecr:GetDownloadUrlForLayer",


        ]
        Effect   = "Allow"
        Resource = "arn:aws:ecr:${var.region}:${local.account_id}:repository/innovation*"
      },
      {
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Effect   = "Allow"
        Resource = "arn:aws:logs:*:*:*"
      },
            {
        Action = [
          "s3:*"
        ]
        Effect   = "Allow"
        Resource = [
          "arn:aws:s3:::${var.prefix}*",
          "arn:aws:s3:::${var.prefix}*/*"
        ]
      },
    ]
  })
}

resource "aws_iam_role" "lambda_role" {
  name = "processing_role"

  # Terraform's "jsonencode" function converts a
  # Terraform expression result to valid JSON syntax.
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = "LambdaECRImageRetrievalPolicy"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    name = "${var.prefix}-lambda-role"
  }
}


resource "null_resource" "netcdf_to_zarr_ecr_image" {
 triggers = {
   python_file = md5(file("${path.module}/netcdf_to_zarr/handler.py"))
   python_file = md5(file("${path.module}/netcdf_to_zarr/convert.py"))
   docker_file = md5(file("${path.module}/Dockerfile"))
 }

 provisioner "local-exec" {
   command = <<EOF
           aws ecr get-login-password --region ${var.region} | docker login --username AWS --password-stdin ${local.account_id}.dkr.ecr.${var.region}.amazonaws.com
           docker build -t ${aws_ecr_repository.netcdf_to_zarr.repository_url}:latest .
           docker push ${aws_ecr_repository.netcdf_to_zarr.repository_url}:latest
       EOF
 }
}




data "aws_ecr_image" "lambda_image_ecr" {
 depends_on = [
   aws_ecr_repository.netcdf_to_zarr
 ]
 repository_name = aws_ecr_repository.netcdf_to_zarr.name
  image_tag = "latest"
}

resource "aws_lambda_function" "netcdf_to_zarr" {
  depends_on = [
   null_resource.netcdf_to_zarr_ecr_image
 ]
 function_name = "${var.prefix}-netcdf_to_zarr"
 role = aws_iam_role.lambda_role.arn
 timeout = 300
 image_uri = "${aws_ecr_repository.netcdf_to_zarr.repository_url}@${data.aws_ecr_image.lambda_image_ecr.id}"
 package_type = "Image"
}


resource "aws_s3_bucket" "innovation_s3_bucket" {
  bucket = "${var.prefix}-netcdfs"
}

resource "aws_lambda_permission" "allow_bucket" {
  statement_id  = "AllowExecutionFromS3Bucket"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.netcdf_to_zarr.arn
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.innovation_s3_bucket.arn
}


resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = aws_s3_bucket.innovation_s3_bucket.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.netcdf_to_zarr.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "ncs/"
    filter_suffix       = ".nc"
  }

  depends_on = [aws_lambda_permission.allow_bucket]
}


resource "aws_cloudwatch_log_group" "lambda_log_group" {
  name              = "/aws/lambda/${aws_lambda_function.netcdf_to_zarr.function_name}"
  retention_in_days = 14
}
