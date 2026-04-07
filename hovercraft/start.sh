#!/bin/bash
# [사용자] Operator Hub 통합 기동 스크립트 (Encapsulated) 

echo " 지휘소 기동 프로세스를 시작합니다..."

# [추가됨] Git SSH 권한 오류(Three.js 등) 방지용 네트워크 HTTPS 우회 설정
git config --global url."https://github.com/".insteadOf ssh://git@github.com/

# 1. 자동 환경 세팅 (Node install + Python venv)
# node_modules와 상위 .venv가 없거나 --force 인자가 있을 때만 실행
if [ ! -d "node_modules" ] || [ ! -d "../.venv" ] || [ "$1" == "--force" ]; then
  echo " [SYSTEM] 환경 무결성 점검 및 구축 중..."
  node scripts/setup.js
else
  echo " [SYSTEM] 기존 환경 감지됨. 환경 구축을 건너뜁니다. (강제 재설치: ./start.sh --force)"
fi

if [ $? -eq 0 ]; then
  # 2. 웹 서버 가동
  echo " 회선 연결 중..."
  export MCP_ROOT=$(cd .. && pwd)
  npm run dev
else
  echo " 환경 구축에 실패했습니다. 로그를 확인해 주세요."
  exit 1
fi
