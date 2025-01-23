import os
import random
import sys
import time

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# OAuth 2.0 정보 파일 경로
CLIENT_SECRETS_FILE = "./client_secrets.json"

# 업로드 권한 범위
YOUTUBE_UPLOAD_SCOPE = ["https://www.googleapis.com/auth/youtube.upload"]
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")


def get_authenticated_service():
    """인증된 YouTube API 서비스를 반환합니다."""
    creds = None
    # 토큰 저장 파일
    token_file = "./token.json"

    # 저장된 자격 증명이 있으면 로드
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, YOUTUBE_UPLOAD_SCOPE)

    # 자격 증명이 없거나 유효하지 않으면 새로 인증
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, YOUTUBE_UPLOAD_SCOPE)
            creds = flow.run_local_server(port=8080, access_type="offline", prompt="consent")
        # 새 자격 증명을 저장
        with open(token_file, "w") as token:
            token.write(creds.to_json())

    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, credentials=creds)


def initialize_upload(youtube, options):
    """동영상을 업로드합니다."""
    tags = options.keywords.split(",") if options.keywords else None

    body = {
        "snippet": {
            "title": options.title,
            "description": options.description,
            "tags": tags,
            "categoryId": options.category,
        },
        "status": {
            "privacyStatus": options.privacyStatus,
        },
    }

    insert_request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=MediaFileUpload(options.file, chunksize=-1, resumable=True),
    )

    resumable_upload(insert_request)


def resumable_upload(insert_request):
    """동영상 업로드 요청을 처리합니다."""
    response = None
    error = None
    retry = 0

    while response is None:
        try:
            print("Uploading file...")
            status, response = insert_request.next_chunk()
            if response:
                if "id" in response:
                    print(f"Video id '{response['id']}' was successfully uploaded.")
                else:
                    sys.exit(f"The upload failed with an unexpected response: {response}")
        except HttpError as e:
            if e.resp.status in [500, 502, 503, 504]:
                error = f"A retriable HTTP error {e.resp.status} occurred:\n{e.content}"
            else:
                raise
        if error:
            print(error)
            retry += 1
            if retry > 10:
                sys.exit("No longer attempting to retry.")
            sleep_seconds = random.random() * (2**retry)
            print(f"Sleeping {sleep_seconds} seconds and then retrying...")
            time.sleep(sleep_seconds)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True, help="Video file to upload")
    parser.add_argument("--title", help="Video title", default="Test Title")
    parser.add_argument("--description", help="Video description", default="Test Description")
    parser.add_argument(
        "--category",
        default="22",
        help="Numeric video category. See https://developers.google.com/youtube/v3/docs/videoCategories/list",
    )
    parser.add_argument("--keywords", help="Video keywords, comma separated", default="")
    parser.add_argument(
        "--privacyStatus",
        choices=VALID_PRIVACY_STATUSES,
        default="public",
        help="Video privacy status.",
    )
    args = parser.parse_args()

    if not os.path.exists(args.file):
        sys.exit("Please specify a valid file using the --file= parameter.")

    youtube = get_authenticated_service()
    try:
        initialize_upload(youtube, args)
    except HttpError as e:
        print(f"An HTTP error {e.resp.status} occurred:\n{e.content}")
