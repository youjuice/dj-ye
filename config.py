import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 환경 변수에서 토큰 가져오기
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
PREFIX = os.getenv('DISCORD_BOT_PREFIX', '/')
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')

required_vars = ['DISCORD_BOT_TOKEN', 'SPOTIFY_CLIENT_ID', 'SPOTIFY_CLIENT_SECRET']
missing_vars = [var for var in required_vars if os.getenv(var) is None]

# 토큰이 없으면 에러 발생
if missing_vars:
    raise ValueError(f"The following environment variables are not set: {', '.join(missing_vars)}")
