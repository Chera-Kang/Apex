import os
from pathlib import Path
from dotenv import load_dotenv

# 프로젝트 루트 및 precondition 폴더 경로 탐색
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / "precondition" / ".env"

if ENV_PATH.exists():
    load_dotenv(ENV_PATH)
else:
    load_dotenv(BASE_DIR / ".env")

# 환경 변수 로드 (코드 내 하드코딩 방지)
SHEET_URL = os.getenv("GOOGLE_SHEET_URL", "")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID", "")
CREDS_PATH = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", str(BASE_DIR / "precondition" / "auth" / "credentials.json"))

# 상대 경로로 지정된 경우 절대 경로로 정규화
if CREDS_PATH and not os.path.isabs(CREDS_PATH):
    CREDS_PATH = str(BASE_DIR / CREDS_PATH)
