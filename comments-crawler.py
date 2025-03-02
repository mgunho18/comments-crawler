import re
import random
from googleapiclient.discovery import build


# 유튜브 URL에서 영상 ID를 추출하는 함수
def extract_video_id(url):
    # 여러 URL 패턴에 대응하는 정규표현식
    patterns = [
        r"(?:https?:\/\/)?(?:www\.)?youtu\.be\/([^?&]+)",
        r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([^?&]+)",
        r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([^?&]+)"
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError("유효한 유튜브 링크가 아닙니다.")


# 주어진 영상 ID의 댓글들을 가져오는 함수
def get_video_comments(video_id, api_key, max_results=100):
    comments = []
    youtube = build('youtube', 'v3', developerKey=api_key)
    count = 0  # 댓글 순서를 기록할 변수(최신순)
    
    # 최초 요청
    request = youtube.commentThreads().list(
        part='snippet',
        videoId=video_id,
        maxResults=100,  # API 최대 반환 개수
        textFormat='plainText'
    )
    response = request.execute()

    # 페이지네이션 처리
    while response:
        for item in response.get('items', []):
            comment_info = item['snippet']['topLevelComment']['snippet']
            author = comment_info.get('authorDisplayName')
            text = comment_info.get('textDisplay')
            count += 1  # 댓글 번호 증가
            comments.append((count, author, text))
            # max_results를 넘으면 중단
            if len(comments) >= max_results:
                break

        if 'nextPageToken' in response:
            request = youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                maxResults=100,
                pageToken=response['nextPageToken'],
                textFormat='plainText'
            )
            response = request.execute()
        else:
            break
    return comments


if __name__ == "__main__":
    video_url = input("유튜브 링크를 입력하세요: ")
    try:
        video_id = extract_video_id(video_url)
    except ValueError as e:
        print(e)
        exit()

    # API 키를 본인의 것으로 대체하세요.
    api_key = "myAPIkey"
    
    print("댓글을 불러오는 중입니다...")
    comments = get_video_comments(video_id, api_key)
    
    if len(comments) < 5:
        print("댓글이 5개 미만입니다.")
    else:
        random_comments = random.sample(comments, 5)
        print("\n랜덤 추출된 댓글 (댓글 순번, 작성자, 내용):")
        for idx, author, text in random_comments:
            print(f"{idx}번째 댓글 - {author}: {text}")
