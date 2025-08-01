import json
import boto3
import requests
import tempfile
from pdf2image import convert_from_path

s3 = boto3.client('s3')
BUCKET = 'metalicosalesassistant'  # Change if needed

def lambda_handler(event, context):
    # 👇 Fix: Parse JSON string from API Gateway event body
    try:
        body = json.loads(event["body"])
    except Exception as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': f'Invalid request body: {str(e)}'})
        }

    pdf_url = body.get('pdf_url')
    record_id = body.get('record_id', 'unknown')

    if not pdf_url:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing PDF URL'})
        }

    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as pdf_file:
            r = requests.get(pdf_url)
            r.raise_for_status()
            pdf_file.write(r.content)
            pdf_file_path = pdf_file.name

        images = convert_from_path(pdf_file_path, dpi=200)

        image_urls = []
        for i, img in enumerate(images):
            tmp_img_path = f"/tmp/{record_id}_page_{i+1}.png"
            img.save(tmp_img_path, "PNG")

            s3_key = f"pdf-pages/{record_id}/page_{i+1}.png"
            s3.upload_file(tmp_img_path, BUCKET, s3_key)

            public_url = f"https://{BUCKET}.s3.amazonaws.com/{s3_key}"
            image_urls.append(public_url)

        return {
            'statusCode': 200,
            'body': json.dumps({'image_urls': image_urls})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Processing failed: {str(e)}'})
        }
