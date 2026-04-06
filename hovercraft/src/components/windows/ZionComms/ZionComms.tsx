"use client";

import React from "react";

export const ZionComms: React.FC = () => {
  return (
    <section className="col-span-5 row-span-2 flex flex-col terminal-window overflow-hidden">
      <div className="terminal-header px-2 py-1 flex justify-between items-center">
        <span className="text-[10px] font-mono text-green-500 crt-glow">ZION_COMMS.ext</span>
        <div className="flex items-center gap-2">
          <span className="text-[8px] font-mono text-green-900">ENCRYPTION: 1024_RSA</span>
        </div>
      </div>
      <div className="flex-1 p-3 flex flex-col font-mono text-[10px]">
        <div className="flex gap-2 mb-2">
          <span className="text-green-900">[MORPHEUS]</span>
          <span className="text-green-400 italic">"We need the operator to pull the main sequence."</span>
        </div>
        <div className="flex gap-2">
          <span className="text-green-900">[TANK]</span>
          <span className="text-green-400 italic">"Loading the program now. Hold on."</span>
        </div>
      </div>
      <div className="bg-black/50 border-t border-green-900/30 p-2 flex items-center gap-2">
        <span className="text-green-600 font-mono text-[10px]">tank@neb:~#</span>
        <input className="bg-transparent border-none text-[10px] font-mono text-green-400 focus:ring-0 p-0 flex-1 outline-none" placeholder="say --voice morpheus 'Initiate exit'" type="text" />
        <span className="w-1.5 h-3 bg-green-500 cursor-blink"></span>
      </div>
    </section>
  );
};
