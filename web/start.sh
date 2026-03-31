#!/bin/bash
# [대장님 🎯] Operator Hub 통합 기동 스크립트 (Encapsulated) 🛡️⚡️

echo "🚀 지휘소 기동 프로세스를 시작합니다..."

# [추가됨] Git SSH 권한 오류(Three.js 등) 방지용 네트워크 HTTPS 우회 설정
git config --global url."https://github.com/".insteadOf ssh://git@github.com/

# 1. 자동 환경 세팅 (Node install + Python venv)
# 이제 파일이 web 폴더 안에 있으므로 직접 setup 실행
node scripts/setup.js

if [ $? -eq 0 ]; then
  # 2. 웹 서버 가동
  echo "📡 회선 연결 중..."
  npm run dev
else
  echo "❌ 환경 구축에 실패했습니다. 로그를 확인해 주세요."
  exit 1
fi
