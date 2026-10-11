#!/bin/bash
# LocalStack initialization script for Zephyr
echo "Initializing Zephyr AWS resources in LocalStack..."

# 1. Create S3 Telemetry Lake Bucket
awslocal s3 mb s3://zephyr-telemetry-lake --region us-east-1
echo "Created S3 Bucket: zephyr-telemetry-lake"

# 2. Create DynamoDB Statutory Audit Table
awslocal dynamodb create-table \
    --table-name Zephyr_AuditLogs \
    --attribute-definitions AttributeName=record_id,AttributeType=S \
    --key-schema AttributeName=record_id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --region us-east-1
echo "Created DynamoDB Table: Zephyr_AuditLogs"

# 3. Create SNS Emergency Topic
awslocal sns create-topic --name Zephyr-GRAP-Alerts --region us-east-1
echo "Created SNS Topic: Zephyr-GRAP-Alerts"

echo "Zephyr AWS Open-Source Stack Ready!"
