import time
import base64
import openai

from datetime import timedelta, datetime
from aws import AWSManager

from botocore.exceptions import ClientError

from ratelimit import limits, sleep_and_retry

openai.api_key = AWSManager.get_secret("openai")["api_key"]

# API_REQUEST_LIMIT = 1.2
# __requestTimeList__ = -1.0

s3_client = AWSManager.get_s3_client()

bucket_name = s3_client.list_buckets()["Buckets"][0]["Name"]
# print("bucket_name", bucket_name)

expires_in = int(timedelta(days=1).total_seconds())  # URL의 만료 시간 (초 단위)


@sleep_and_retry
@limits(calls=50, period=60)
def create_image(uuid: str, prompt: str) -> str:
    # 동기 작업 수행
    # global __requestTimeList__

    # dt = time.perf_counter() - __requestTimeList__
    # if dt < API_REQUEST_LIMIT:
    #     time.sleep(API_REQUEST_LIMIT - dt)

    try:
        start_time = time.time()
        response = openai.Image.create(
            prompt=prompt, n=1, size="256x256", response_format="b64_json"
        )  # user: id of end-user, for detect abuse

        # for d in response['data']:
        #     print(d['url'])

        # __requestTimeList__ = time.perf_counter()

        image_data = response["data"][0]["b64_json"]
        decoded_data = base64.b64decode(image_data)

        s3_client.put_object(Bucket=bucket_name, Key=uuid, Body=decoded_data)

        # except ClientError as e: # aws 에러처리 추가

        url, expiration_time = generate_presigned_url(uuid)

        if not url:
            return None, None, None, "Error generating presigned URL"

        end_time = time.time()
        processing_time = end_time - start_time

        print("pre-signed URL:", url)

        return url, processing_time, expiration_time, None

    except openai.error.OpenAIError as e:
        error_message = e.error  # str(e.error)
        print(e.http_status, error_message)

        return None, None, None, error_message


@sleep_and_retry
@limits(calls=5, period=1)  # 임의 지정
def generate_presigned_url(object_name):
    try:
        expiration_time = datetime.utcnow() + timedelta(seconds=expires_in)

        # Pre-signed URL 생성
        response = s3_client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": bucket_name,
                "Key": object_name,
                "ResponseContentType": "image/png",
            },
            ExpiresIn=expires_in,
        )

        return response, expiration_time
    except ClientError as e:
        print(f"Error generating presigned URL: {e}")
        return None, None


# # 객체 목록 출력
# response = s3_client.list_objects(Bucket=bucket_name)
# if "Contents" in response:
#     print("Objects in the bucket:")
#     for obj in response["Contents"]:
#         print(obj["Key"])
# else:
#     print("No objects found in the bucket.")

# # 파일 다운로드
# download_path = "./file.txt"
# s3_client.download_file(bucket_name, key, download_path)

# # 파일 삭제
# s3_client.delete_object(Bucket=bucket_name, Key=key)
