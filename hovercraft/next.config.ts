import type { NextConfig } from "next";
import path from "path";

const nextConfig: NextConfig = {
  /* 
     [Sentinel] Next.js 15.2+ / 16 표준 설정
     Turbopack의 탐색 범위를 현재 프로젝트 루트로 엄격히 한정하여
     상위 디렉토리의 package-lock.json이나 가상환경(symlink) 간섭을 원천 차단합니다.
  */
  turbopack: {
    root: "./", // [사용자] 상대 경로를 사용하여 현재 패키지 루트를 명시
  },
};

export default nextConfig;
