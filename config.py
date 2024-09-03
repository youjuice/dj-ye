import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 환경 변수에서 토큰 가져오기
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
PREFIX = os.getenv('DISCORD_BOT_PREFIX', '/')

# 토큰이 없으면 에러 발생
if TOKEN is None:
    raise ValueError("DISCORD_BOT_TOKEN is not set in the environment variables or .env file")
