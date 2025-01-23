# Python-YouTube-Uploader

python과 YouTube API를 이용하여 동영상을 업로드 할 수 있습니다.
 
https://developers.google.com/youtube/v3/guides/uploading_a_video 에 있는 예제 코드를 python 3 문법에 맞게 수정하였습니다.

Google Console에서 App 생성 후 나온 client_secrets.json 파일을 같은 경로에 두고 실행하면 되며, 최초 실행 시 google 로그인을 오구합니다.
로그인을 하게 되면 token.json 파일이 생성되며, 이후에는 로그인 없이 바로 동영상 업로드가 가능합니다.

인증 정보를 초기화하려면 token.json 파일을 삭제하면 됩니다.

자세한 건 추후 서술하겠습니다.

사용 방법
---
1. requirements.txt 파일의 모듈 설치
2. console에서 다음 명령어 실행

```python
python upload_video.py --file="동영상 파일 경로"
			--title="동영상 제목"
			--description="동영상 설명"
			--keywords="동영상 키워드"
			--category="카테고리 번호"
			--privacyStatus="동영상 상태 (public, private, unlisted)"
```
											
3. 다른 파일에서 실행하는 경우 아래 코드 참고

```python
import os
os.systempayload = 'python ./upload_video.py'  
payload += f' --file="{filename}"'  
payload += f' --title="{writeTitle(info, type)}"'  
payload += f' --privacyStatus="{STATUS}"'
...  
    
os.system(payload)
```
