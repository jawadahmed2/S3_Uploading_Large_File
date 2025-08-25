from fastapi import FastAPI, HTTPException
import boto3
import os
from pydantic import BaseModel
from mangum import Mangum

#Allow Swagger UI
app = FastAPI(docs_url="/api/docs",)
# AWS Lambda handler
handler = Mangum(app)
# AWS Configuration
S3_BUCKET = "<S3BucketName>" #Replace with your S3 Bucket's name
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
        response = s3_client.create_multipart_upload(Bucket=S3_BUCKET, Key=request.fileName)
        return {"uploadId": response["UploadId"], "key": request.fileName}
    except Exception as e:
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