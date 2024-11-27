import boto3, random, string
from datetime import datetime
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