# Uploading_Large_File_FastAPI_S3_AWS

This README provides an overview of how the client-side and backend work together to enable efficient, resumable uploads to Amazon S3 using multipart upload.

## Overview
Amazon S3's multipart upload allows large files to be uploaded in smaller parts, improving reliability and performance. This implementation divides responsibilities between the client-side and the backend:

- **Client-Side**: Handles file splitting, part uploads, and progress tracking.
- **Backend**: FastAPI interacts with AWS S3 to initiate uploads, generate presigned URLs, track parts, and finalize uploads. FastAPI runs in a Lambda Function with Lambda Function's URL enabled.

---

## Client-Side Workflow

The client-side application is implemented using HTML, CSS, and JavaScript. 

**Client-side code is found in the client-side folder: "index.html".** 

Its main responsibilities include:

1. **File Selection**:
   - The user selects a file for upload.

2. **Splitting the File**:
   - The file is divided into smaller parts (e.g., 5 MB each).
   - Each part is assigned a sequential part number starting from 1.

3. **Requesting Presigned URLs**:
   - For each part, the client sends a request to the backend to get a presigned URL.

4. **Uploading Parts**:
   - Each part is uploaded directly to S3 using the presigned URL.
   - The response from S3 includes an `ETag` for the uploaded part, which is stored for later.

5. **Tracking Progress**:
   - A progress bar visually updates as parts are uploaded.
   - Upload state (e.g., `UploadId`, part numbers, and `ETag`s) is saved in `localStorage` to enable resuming after interruptions.

6. **Completing the Upload**:
   - Once all parts are uploaded, the client sends a request to the backend with the `UploadId` and part details (part numbers and `ETag`s) to finalize the upload.

7. **Error Handling**:
   - Failed parts are retried automatically.
   - If the connection is interrupted, the client uses `localStorage` and the backend to resume from the last successful part.

---

## Backend Workflow

The backend is implemented using FastAPI and Boto3. It serves as the intermediary between the client and S3. 

**Back-end code is found in the back-end/lambda folder: "lambda_function.py".** 

Upload lambda_function.py as zip. You can just copy and paste the code in the code editor with the lambda' user interface.

Make sure to **Deploy** lambda function if you copy and paste the code or make any changes to the code.

Its main responsibilities include:

1. **Starting Multipart Upload**:
   - The backend handles requests from the client to initiate a multipart upload by calling S3's `CreateMultipartUpload` API.
   - It returns the `UploadId` and object key to the client.

2. **Generating Presigned URLs**:
   - For each part, the client requests a presigned URL from the backend.
   - The backend generates the URL using S3's `GeneratePresignedUrl` API with the appropriate `UploadId` and `PartNumber`.

3. **Listing Uploaded Parts**:
   - If the client resumes after an interruption, it requests the list of uploaded parts.
   - The backend uses S3's `ListParts` API to retrieve already uploaded parts and returns them to the client.

4. **Completing Multipart Upload**:
   - After all parts are uploaded, the client sends the `UploadId`, part numbers, and `ETag`s to the backend.
   - The backend calls S3's `CompleteMultipartUpload` API to finalize the upload.

---

## Error Handling

### Client-Side
- Retries failed parts using stored upload state.
- Alerts the user if an upload cannot proceed.

### Backend
- Validates API requests and ensures the required parameters are present.
- Handles S3 errors (e.g., invalid `UploadId`, missing parts) gracefully.

---

## Instructions
1. **Clone this repository**
    - Clone this GitHub repository. Seek other resources if you do not know how to clone GitHub repositories.
    - If you do not want to clone this GiHub repository, just download it to your personal computer. After the download, unzip the folder. 
2. **Setup S3 Bucket on AWS**
    - Create a S3 Bucket that will be used to store uploaded files.
    - Refer to the Configuration section down below. Apply the first configuration to your newly created S3 Bucket.

3. **Setup Lambda Function**:
    - Create a new Lambda Function on AWS. Seek other resources if you do not know how to create a Lambda Function on AWS.
    - Open lambda_function.py on VS Code. The path to the Lambda Function: back-end/lambda/lambda_function.py
    - Insert the name of your S3 Bucket in the following code:
        ```python
        S3_BUCKET = "<S3BucketName>" #Replace with your S3 Bucket's name
        ```
    - Save the file.
    - Upload lambda_function.py as zip or just copy and paste the code in the code editor with the Lambda's user interface. The Lambda Function is found in the following path: back-end/lambda/lambda_function.py
    - Refer to the Configuration section down below. Apply 2-5 configurations to your newly created Lambda Function.
4. **Setup Client-Side**:
    - Open index.html file located in client-side/index.html
    - Insert your Lambda Function' URL in the following code:
        ```javascript
        const API_BASE_URL = '<Lambda function URL>'; //Replace with your Lambda function's URL endpoint

        ```
    - Save file.
5. **Attempt S3 Multipart Upload**
    - Open the index.html file in your browser of choice.
    - Inspect browser. Go to Network tab.
    - Attach your file to be uploaded.
    - Click on the upload button.
    - The Network tab will demonstrate how the S3 Multipart works
    - If the upload creates an error, check your AWS CloudWatch logs. Under logs in the sidebar, click on log groups. Find the name of your Lambda Function that you created earlier to right side of the sidebar. Click on the log streams tab. Click on the first log file and then determine where the error had occured.
---

## Configuration
1. **CORS Permission for S3 Bucket**:
   
   Ensure the S3 Bucket's CORS policy allows required methods and headers within S3 Bucket's permissions.
  ```json
  [
    {
        "AllowedHeaders": [
            "*"
        ],
        "AllowedMethods": [
            "GET",
            "PUT",
            "POST",
            "DELETE",
            "HEAD"
        ],
        "AllowedOrigins": [
            "*"
        ],
        "ExposeHeaders": [
            "Content-Type",
            "ETag"
        ],
        "MaxAgeSeconds": 3000
    }
]
  ```
2. **Lambda Function's IAM Policy**:
   
   Create an IAM policy for your lambda function to allow CloudWatch to create log groups. The log groups help tacking down bugs that may occur with your lambda function.
 ```json
  {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "logs:CreateLogGroup",
            "Resource": "arn:aws:logs:<enter reagon>:<enter account id>:*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": [
                "arn:aws:logs:<enter reagon>:<enter account id>:log-group:/aws/lambda/<enter lambda function's name>:*"
            ]
        }
    ]
}
  ```
3. **Lambda Function's IAM Role**:
   
   Create an IAM role for your lambda function. Include the following IAM policies in your lambda function's role:

- **AmazonS3FullAccess**: AWS managed policy.
- **IAM Policy you created earlier**: Customer managed policy.

4. **Setup Lambda Function's URL**

    Configure your lambda function's URL.

    - Go to your lambda function you created. 
    - Click on the Configuration tag.
    - On the left hand side, click on Function URL.
    - On the right hand side, click on Create function URL button.
    - Configure the following URL settings:
        - **Auth Type:** None
        - **Additional Settings:**
            - **Invoke Mode:** BUFFERED (default)
            - **Allow Origin:** *
            - **Expose headers:** content-type
            - **Allow headers:** content-type
            - **Allow methods:** *
        - Disregard other settings.
        - Click on the Save button.

5. **Create Lambda Layer**

    A lambda layer is required because the lambda function has dependencies. This configuration will be done on your personal computer.
    
    - Download Git Bash to your personal computer if you do not have it yet.
    - Open Git Bash.
    - cd to where you saved or cloned this repository.
    - Given that you cloned this repository, run the following Git Bash prompt:

        ```
        cd s3-multipart-upload-using-fastapi-python-guide/back-end/lambda_layer
        ```
        ```
        ./create_lambda_layer.sh
        ```
    - Follow the instructions in the prompt.
---

## Security Considerations
1. **Authentication and Authorization**:
   - Use AWS IAM roles and policies to restrict access to the S3 bucket.
   - Implement user authentication on the backend (e.g., JWT).

2. **Presigned URL Expiry**:
   - Set a short expiry time (e.g., 15 minutes) for presigned URLs.

3. **CORS**
    - Only allow certain websites to use your Lambda Function's URL. If asterisk (*) is used then any website can use your URL. Asterisk was only used in this guide for the purpose of testing. In production, specify the websites that you want your Lambda Function's URL to allow access. 
---
## Resumable Upload Workflow Considerations
1. The client tracks upload progress and stores the state (`UploadId`, parts, etc.) in `localStorage`.
2. On reconnecting, the client fetches the list of already uploaded parts from the backend.
3. The client resumes uploading remaining parts.
4. Once all parts are uploaded, the backend finalizes the upload.

## Conclusion
This implementation leverages S3's multipart upload for efficient, reliable, and resumable uploads. By distributing responsibilities between the client-side and backend, it ensures scalability and fault tolerance while keeping the system secure.
