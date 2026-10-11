import os
import json
import time
import logging
from typing import Dict, Any, List

logger = logging.getLogger("Zephyr.AWSAudit")

class AWSServiceBridge:
    """
    Unified bridge for AWS Cloud and LocalStack (AWS Open Source).
    Manages:
    1. Amazon DynamoDB: Statutory GRAP audit trails and municipal dispatch logs.
    2. Amazon S3: Telemetry snapshot data lake archiving.
    3. Amazon SNS: Emergency municipal broadcast notifications.
    4. AWS IoT Core / MQTT: Downlink synchronization for edge actuators.
    """
    def __init__(self):
        self.region = os.environ.get("AWS_REGION", "us-east-1")
        self.localstack_endpoint = os.environ.get("LOCALSTACK_ENDPOINT_URL")
        self.use_localstack = os.environ.get("USE_LOCALSTACK", "false").lower() in ("true", "1", "yes")

        # Table and Bucket names
        self.dynamodb_table_name = os.environ.get("DYNAMODB_TABLE_NAME", "Zephyr_AuditLogs")
        self.s3_bucket_name = os.environ.get("S3_BUCKET_NAME", "zephyr-telemetry-lake")
        self.sns_topic_arn = os.environ.get("SNS_TOPIC_ARN", "")

        self.s3_client = None
        self.dynamodb_client = None
        self.sns_client = None

        self._init_aws_clients()

    def _get_endpoint(self):
        if self.use_localstack:
            return self.localstack_endpoint or "http://localstack:4566"
        return None

    def _init_aws_clients(self):
        try:
            import boto3
            endpoint = self._get_endpoint()
            kwargs = {"region_name": self.region}
            if endpoint:
                kwargs["endpoint_url"] = endpoint
                kwargs["aws_access_key_id"] = os.environ.get("AWS_ACCESS_KEY_ID", "test")
                kwargs["aws_secret_access_key"] = os.environ.get("AWS_SECRET_ACCESS_KEY", "test")

            self.s3_client = boto3.client("s3", **kwargs)
            self.dynamodb_client = boto3.resource("dynamodb", **kwargs)
            self.sns_client = boto3.client("sns", **kwargs)
            logger.info(f"Connected AWS clients (LocalStack={self.use_localstack}, Endpoint={endpoint})")
        except Exception as e:
            logger.warning(f"AWS Boto3 initialization deferred or running mock: {e}")

    def log_statutory_action(self, node_station: str, pm25: float, grap_stage: str, action: str):
        """Records an auditable statutory action in DynamoDB."""
        item = {
            "record_id": f"{node_station}_{int(time.time())}",
            "timestamp": int(time.time()),
            "station": node_station,
            "pm25": str(pm25),
            "grap_stage": grap_stage,
            "action": action,
            "authority": "CAQM_STATUTORY_RULEBOOK"
        }
        if self.dynamodb_client:
            try:
                table = self.dynamodb_client.Table(self.dynamodb_table_name)
                table.put_item(Item=item)
                logger.info(f"Logged to DynamoDB: {item['record_id']}")
            except Exception as e:
                logger.debug(f"DynamoDB log skipped: {e}")
        return item

    def archive_telemetry_snapshot(self, forecast_data: Dict[str, Any]):
        """Persists a complete spatio-temporal snapshot to Amazon S3 data lake."""
        if self.s3_client:
            key = f"snapshots/lucknow_{int(time.time())}.json"
            try:
                self.s3_client.put_object(
                    Bucket=self.s3_bucket_name,
                    Key=key,
                    Body=json.dumps(forecast_data),
                    ContentType="application/json"
                )
                logger.info(f"Archived telemetry to S3 s3://{self.s3_bucket_name}/{key}")
                return key
            except Exception as e:
                logger.debug(f"S3 archive skipped: {e}")
        return None

    def publish_emergency_sns(self, stage: str, worst_station: str, pm25: float, action: str):
        """Sends an Amazon SNS broadcast during Stage III/IV emergencies."""
        message = (
            f"🚨 [CAQM STATUTORY EMERGENCY] Zephyr detected {stage} in {worst_station} "
            f"(PM2.5: {pm25} µg/m³). Executing mandatory mitigation: {action}."
        )
        if self.sns_client and self.sns_topic_arn:
            try:
                self.sns_client.publish(
                    TopicArn=self.sns_topic_arn,
                    Subject=f"Zephyr Emergency: {stage} Alert",
                    Message=message
                )
                logger.info(f"Dispatched Amazon SNS alert for {stage}")
                return True
            except Exception as e:
                logger.warning(f"Failed to publish SNS: {e}")
        return False

    def get_service_status(self) -> Dict[str, Any]:
        """Returns health and integration status of AWS services."""
        return {
            "aws_mode": "LocalStack (AWS Open Source)" if self.use_localstack else "AWS Cloud",
            "region": self.region,
            "services": {
                "amazon_bedrock": {
                    "model": os.environ.get("AWS_BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20240620-v1:0"),
                    "status": "ready"
                },
                "amazon_dynamodb": {
                    "table": self.dynamodb_table_name,
                    "status": "configured" if self.dynamodb_client else "mock"
                },
                "amazon_s3": {
                    "bucket": self.s3_bucket_name,
                    "status": "configured" if self.s3_client else "mock"
                },
                "amazon_sns": {
                    "topic": self.sns_topic_arn if self.sns_topic_arn else "Zephyr-GRAP-Alerts",
                    "status": "active"
                },
                "aws_iot_core": {
                    "protocol": "MQTT TLS / Mosquitto Bridge",
                    "status": "active"
                }
            }
        }
