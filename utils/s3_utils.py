import boto3, random, string
from datetime import datetime
from botocore.exceptions import NoCredentialsError
from urllib.parse import urlparse
from django.conf import settings

def get_random_text(prefix='', length=10):
    random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    return f"{prefix}{random_str}"

def s3_file_upload_by_file_data(upload_file, region_name, bucket_name, bucket_path, content_type=None, extension=None):
    """
    S3에 파일을 업로드하고 URL을 반환하는 함수
    - upload_file: 업로드할 파일 객체
    - content_type: 파일의 Content-Type (선택 사항)
    - extension: 파일 확장자 (선택 사항)
    - return 업로드된 파일의 S3 URL 또는 False
    """
    bucket_name = bucket_name.replace('/', '')
    content_type = content_type or upload_file.content_type
    extension = extension or upload_file.name.split('.')[-1]

    now = datetime.now().strftime('%Y%m%d%H%M%S')
    random_str = get_random_text('A', 20)
    random_file_name = f"{now}_{random_str}.{extension}"
    upload_file_path_name = f"{bucket_path}/{random_file_name}"

    try:
        upload_file.seek(0)  # 파일의 시작 위치로 이동
    except Exception:
        pass

    s3 = boto3.resource(
        's3',
        region_name=region_name,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )

    result = s3.Bucket(bucket_name).put_object(
        Key=upload_file_path_name,
        Body=upload_file,
        ContentType=content_type,
        #ACL='public-read'
    )

    if result:
        return f"https://{bucket_name}.s3.{region_name}.amazonaws.com/{bucket_path}/{random_file_name}"

    return False

def generate_presigned_url(s3_url, expiration=3600):
    """
    S3 URL을 pre-signed URL로 변환합니다.
    """
    s3_client = boto3.client(
        's3',
        region_name=settings.AWS_S3_REGION_NAME,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )

    # URL 파싱
    parsed_url = urlparse(s3_url)
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME

    # S3 객체 키 추출
    if parsed_url.netloc.endswith(f"{bucket_name}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com"):
        # https://<bucket_name>.s3.<region>.amazonaws.com/<object_key> 형식
        object_key = parsed_url.path.lstrip('/')
    elif parsed_url.netloc == f"s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com":
        # https://s3.<region>.amazonaws.com/<bucket_name>/<object_key> 형식
        object_key = parsed_url.path.lstrip('/').split(f"{bucket_name}/")[-1]
    else:
        raise ValueError("Invalid S3 URL format")

    # Pre-signed URL 생성
    try:
        response = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': object_key},
            ExpiresIn=expiration,
        )
        return response
    except NoCredentialsError:
        raise ValueError("AWS credentials not available")
        
# def generate_presigned_url(s3_url, expiration=3600):
#     """
#     S3 URL을 pre-signed URL로 변환합니다.
#     """
#     s3_client = boto3.client(
#         's3',
#         region_name=settings.AWS_S3_REGION_NAME,
#         aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
#         aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
#     )

#     bucket_name = settings.AWS_STORAGE_BUCKET_NAME
#     try:
#         object_key = s3_url.split(f"{bucket_name}/")[1]  # S3 객체 키 추출
#     except IndexError:
#         raise ValueError("Invalid S3 URL format")

#     try:
#         response = s3_client.generate_presigned_url(
#             'get_object',
#             Params={'Bucket': bucket_name, 'Key': object_key},
#             ExpiresIn=expiration,
#         )
#         return response
#     except NoCredentialsError:
#         raise ValueError("AWS credentials not available")