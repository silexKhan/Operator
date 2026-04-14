import type { NextConfig } from "next";
import path from "path";

const nextConfig: NextConfig = {
  /* config options here */
  // Next.js 15/16 Turbopack root 설정
  // @ts-ignore - Turbopack root option
  turbopack: {
    root: path.resolve(__dirname),
  },
  transpilePackages: ["tailwindcss"],
  typescript: {
    ignoreBuildErrors: false,
  }
};

export default nextConfig;
