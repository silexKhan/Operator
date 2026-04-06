"use client";

import React from "react";

export const SentinelTracking: React.FC = () => {
  return (
    <section className="col-span-4 row-span-3 flex flex-col terminal-window overflow-hidden">
      <div className="terminal-header px-2 py-1 flex justify-between items-center">
        <span className="text-[10px] font-mono text-green-500 crt-glow">SENTINEL_TRACKING.bin</span>
        <span className="material-symbols-outlined text-[10px] text-red-500 animate-ping">emergency</span>
      </div>
      <div className="flex-1 p-3 font-mono text-[9px] text-green-500/80 overflow-hidden flex flex-col">
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="border border-green-900/50 p-2 bg-green-500/5">
            <div className="text-[8px] text-green-900 mb-1">SIGNATURE_ALPHA</div>
            <div className="h-2 bg-black border border-green-900 relative">
              <div className="h-full bg-green-500 w-[72%] shadow-[0_0_8px_rgba(0,255,65,0.4)]"></div>
            </div>
          </div>
          <div className="border border-green-900/50 p-2 bg-green-500/5">
            <div className="text-[8px] text-green-900 mb-1">INTERCEPT_PROB</div>
            <div className="h-2 bg-black border border-green-900 relative">
              <div className="h-full bg-green-500 w-[12%]"></div>
            </div>
          </div>
        </div>
        <div className="flex-1 overflow-hidden opacity-40 leading-none">
          01100111 01101111 01100100 00100000 01101001 01110011 00100000 01100100 01100001 01100100 00101110 00100000 01110111 01100101 00100000 01101011 01100001 01110110 01100101 00100000 01101011 01101001 01101100 01101100 01100101 01100100 00100000 01101000 01101001 01101101
        </div>
      </div>
      <div className="bg-black/50 border-t border-green-900/30 p-2 flex items-center gap-2">
        <span className="text-green-600 font-mono text-[10px]">track@neb:~#</span>
        <input className="bg-transparent border-none text-[10px] font-mono text-green-400 focus:ring-0 p-0 flex-1 outline-none" placeholder="scramble --all" type="text" />
        <span className="w-1.5 h-3 bg-green-500 cursor-blink"></span>
      </div>
    </section>
  );
};
