@echo off
TITLE Operator Hub Control Center 🛡️⚡️
SETLOCAL

echo 🚀 지휘소 기동 프로세스를 시작합니다 (Windows)...

:: [추가됨] Git SSH 권한 오류 방지: 패키지 다운로드 시 HTTPS 강제 사용 설정
git config --global url."https://github.com/".insteadOf ssh://git@github.com/

:: 1. Node.js 존재 여부 1차 점검
node -v >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ Node.js가 설치되어 있지 않습니다.
    echo 🔗 공식 다운로드 페이지를 엽니다. 설치 후 이 파일을 다시 실행해 주세요.
    start https://nodejs.org/en/download/
    pause
    exit /b 1
)

:: 2. 자동 환경 세팅 (이제 web 폴더 내부이므로 상대 경로 주의 🕵️‍♂️)
node scripts/setup.js

if %errorlevel% neq 0 (
    echo ❌ 환경 구축에 실패했습니다. 상단의 에러 로그를 확인해 주세요.
    pause
    exit /b %errorlevel%
)

:: 3. 웹 서버 가동
echo 📡 회선 연결 중... (Dashboard: http://localhost:3000)
npm run dev
pause
