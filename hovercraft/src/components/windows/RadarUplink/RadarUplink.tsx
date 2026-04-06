"use client";

import React from "react";

export const RadarUplink: React.FC = () => {
  return (
    <section className="col-span-5 row-span-4 flex flex-col terminal-window overflow-hidden">
      <div className="terminal-header px-2 py-1 flex justify-between items-center">
        <span className="text-[10px] font-mono text-green-500 crt-glow">RADAR_UPLINK.map</span>
        <span className="text-[9px] text-green-900 font-mono">LAT: 32.122 / LONG: -114.908</span>
      </div>
      <div className="flex-1 relative flex items-center justify-center p-4 bg-green-950/5">
        <img alt="3D tactical wireframe map" className="w-full h-full object-cover opacity-10 mix-blend-screen absolute" src="https://lh3.googleusercontent.com/aida-public/AB6AXuCxXrbq5q9X1NfJ1x-_3WVDQ2cKJKf3kdR2GmS_ZRrAQbA_oOqw8PNEGJ7ST0REQO4uQpxIO-S6uwB0OCWK4wd_4HVxdql-2Wk3maHZV7AwCvOOiS9h4bPQ2OfBHtov9S40jdUZKLWMUwYO9fpvyZy5w_09yZf1sm-EHut52_wARZsflLYvulymZws3KfRL-KCz2AFayo___m122Dj-VlKdtaTdtdsRLjOSc7ezbcSz5IfH4OBnwvpinoAAjXBSPTSWZvZ5aWaX9w" />
        <div className="w-[200px] h-[200px] border border-green-500/20 rounded-full flex items-center justify-center relative">
          <div className="w-[100px] h-[100px] border border-green-500/10 rounded-full"></div>
          <div className="absolute w-full h-[1px] bg-green-500/10"></div>
          <div className="absolute h-full w-[1px] bg-green-500/10"></div>
          <div className="w-1.5 h-1.5 bg-green-400 rounded-full absolute translate-x-10 -translate-y-12 animate-pulse"></div>
          <div className="w-1.5 h-1.5 bg-green-400 rounded-full absolute -translate-x-20 translate-y-4 animate-pulse"></div>
        </div>
        <div className="absolute bottom-4 left-4 font-mono text-[9px] text-green-500/60 leading-tight uppercase">
          TARGET_LOCKED: SENTINEL_01<br />
          RANGE: 0.42km<br />
          THREAT_LEVEL: OMEGA
        </div>
      </div>
      <div className="bg-black/50 border-t border-green-900/30 p-2 flex items-center gap-2">
        <span className="text-green-600 font-mono text-[10px]">scan@neb:~#</span>
        <input className="bg-transparent border-none text-[10px] font-mono text-green-400 focus:ring-0 p-0 flex-1 outline-none" placeholder="ping --freq 0.8hz" type="text" />
        <span className="w-1.5 h-3 bg-green-500 cursor-blink"></span>
      </div>
    </section>
  );
};
