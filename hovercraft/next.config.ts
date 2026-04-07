import type { NextConfig } from "next";
import path from "path";

const nextConfig: NextConfig = {
  /* 
     [Sentinel] Next.js 15.2+ / 16 표준 설정
     Turbopack의 탐색 범위를 현재 프로젝트 루트로 엄격히 한정하여
     상위 디렉토리의 package-lock.json이나 가상환경(symlink) 간섭을 원천 차단합니다.
  */
  // @ts-ignore: Next.js 15.2+ / 16 stable turbopack key
  turbopack: {
    root: path.resolve(__dirname),
  },
};

export default nextConfig;
