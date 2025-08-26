from fastapi import FastAPI, HTTPException
import boto3
import os
from pydantic import BaseModel
from mangum import Mangum
import logging, os, traceback
from botocore.exceptions import BotoCoreError, ClientError

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

#Allow Swagger UI
app = FastAPI(docs_url="/api/docs")

# AWS Configuration
S3_BUCKET = ""
S3_PREFIX = ""
s3_client = boto3.client('s3')

class StartUploadRequest(BaseModel):
    fileName: str

class PresignedUrlRequest(BaseModel):
    uploadId: str
    key: str
    partNumber: int

class CompleteUploadRequest(BaseModel):
    uploadId: str
    key: str
    parts: list

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.options("/{full_path:path}")
async def options_handler():
    return {"message": "OK"}

@app.post("/list-parts")
async def list_parts(request: PresignedUrlRequest):
    try:
        response = s3_client.list_parts(
            Bucket=S3_BUCKET,
            Key=request.key,
            UploadId=request.uploadId
        )
        parts = [{"PartNumber": part["PartNumber"], "ETag": part["ETag"]} for part in response.get("Parts", [])]
        return {"parts": parts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing parts: {e}")

@app.post("/start-multipart-upload")
async def start_multipart_upload(request: StartUploadRequest):
    try:
        # IMPORTANT: bucket name must be pure bucket, prefix goes in key
        bucket = os.getenv("S3_BUCKET", "ftp-hfcontents")
        prefix = os.getenv("S3_PREFIX", "content-ai/PPT-Files-Input/")
        key = f"{prefix}{request.fileName}"

        logger.info(f"Starting MPU: bucket={bucket}, key={key}, region={os.getenv('AWS_REGION')}")
        resp = s3_client.create_multipart_upload(Bucket=bucket, Key=key)
        return {"uploadId": resp["UploadId"], "key": key}
    except (ClientError, BotoCoreError) as e:
        logger.exception("Boto3 error in start_multipart_upload")
        # expose minimal detail for test; OK for dev
        raise HTTPException(status_code=500, detail=f"AWS error: {e}")
    except Exception as e:
        logger.exception("Unhandled error in start_multipart_upload")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/get-presigned-url")
async def get_presigned_url(request: PresignedUrlRequest):
    try:
        presigned_url = s3_client.generate_presigned_url(
            "upload_part",
            Params={
                "Bucket": S3_BUCKET,
                "Key": request.key,
                "UploadId": request.uploadId,
                "PartNumber": request.partNumber,
            },
            ExpiresIn=3600
        )
        return {"presignedUrl": presigned_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/complete-multipart-upload")
async def complete_multipart_upload(request: CompleteUploadRequest):
    try:
        parts = [{"ETag": f'"{part["ETag"]}"', "PartNumber": part["PartNumber"]} for part in request.parts]

        print(f"complete-multipart-upload: {str(parts)}")
        s3_client.complete_multipart_upload(
            Bucket=S3_BUCKET,
            Key=request.key,
            UploadId=request.uploadId,
            MultipartUpload={"Parts": parts}
        )
        return {"message": "Upload completed successfully"}
    except Exception as e:
        print(f"complete-multipart-upload: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# AWS Lambda handler with robust event handling
def lambda_handler(event, context):
    try:
        logger.info(f"Received event: {event}")

        # Handle different event formats
        # Check if it's an API Gateway event
        if 'requestContext' in event and 'http' in event['requestContext']:
            # API Gateway v2 format
            asgi_handler = Mangum(app, lifespan="off")
        elif 'requestContext' in event and 'requestId' in event['requestContext']:
            # API Gateway v1 format
            asgi_handler = Mangum(app, lifespan="off")
        elif 'version' in event and event['version'] == '2.0':
            # Lambda Function URL format
            asgi_handler = Mangum(app, lifespan="off")
        elif 'headers' in event and 'rawPath' in event:
            # Another Lambda Function URL format
            asgi_handler = Mangum(app, lifespan="off")
        else:
            # Try to transform the event to Lambda Function URL format
            if 'httpMethod' not in event and 'method' not in event:
                # Assume it's a direct invocation, create a simple GET request
                event = {
                    "version": "2.0",
                    "routeKey": "$default",
                    "rawPath": "/",
                    "rawQueryString": "",
                    "headers": {},
                    "requestContext": {
                        "http": {
                            "method": "GET",
                            "path": "/",
                            "protocol": "HTTP/1.1",
                            "sourceIp": "127.0.0.1"
                        }
                    },
                    "body": "",
                    "isBase64Encoded": False
                }
            asgi_handler = Mangum(app, lifespan="off")

        response = asgi_handler(event, context)

        return response

    except Exception as e:
        logger.exception("Error in lambda_handler")
        return {
            "statusCode": 500,
            "body": f"Lambda handler error: {str(e)}",
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Amz-Date, X-Api-Key, X-Amz-Security-Token"
            }
        }

# Multiple handler definitions for different invocation methods
handler = lambda_handler

# Alternative handlers for different configurations
def mangum_handler(event, context):
    asgi_handler = Mangum(app, lifespan="off")
    return asgi_handler(event, context)
