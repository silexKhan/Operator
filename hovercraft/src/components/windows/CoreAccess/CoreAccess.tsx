"use client";

import React, { useEffect, useState } from "react";

interface CoreAccessProps {
  requestMcpStatus: () => void;
  requestSwitchCircuit: (name: string) => void;
  systemStatus: {
    active_circuit: string;
    circuits: string[];
    details?: {
      name: string;
      protocols: string[];
      units: { name: string; mission: string; rules: string[] }[];
      actions: { name: string; description: string }[];
    }
  };
}

export const CoreAccess: React.FC<CoreAccessProps> = ({ requestMcpStatus, requestSwitchCircuit, systemStatus }) => {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  // 마운트 전에는 서버와 동일한 최소한의 구조만 렌더링 (하이드레이션 방지)
  if (!mounted) {
    return (
      <section className="col-span-4 row-span-3 flex flex-col terminal-window overflow-hidden">
        <div className="terminal-header px-2 py-1 flex justify-between items-center">
          <span className="text-[10px] font-mono text-green-500 crt-glow">CORE_ACCESS.sys</span>
          <div className="flex gap-1">
            <div className="w-2 h-2 rounded-full bg-green-900"></div>
            <div className="w-2 h-2 rounded-full bg-green-500"></div>
          </div>
        </div>
        <div className="flex-1 p-3 font-mono text-[10px] text-green-500/80 overflow-hidden flex flex-col">
          <p className="text-green-400 opacity-60">Initializing core handshake...</p>
        </div>
      </section>
    );
  }

  return (
    <section className="col-span-4 row-span-3 flex flex-col terminal-window overflow-hidden">
      <div className="terminal-header px-2 py-1 flex justify-between items-center">
        <span className="text-[10px] font-mono text-green-500 crt-glow">CORE_ACCESS.sys</span>
        <div className="flex items-center gap-2">
          <span className="text-[9px] font-mono text-green-900 uppercase tracking-tighter">
            Nexus: <span className="text-green-500 font-bold">{systemStatus.active_circuit}</span>
          </span>
          <div className="flex gap-1 ml-2">
            <div className="w-2 h-2 rounded-full bg-green-900"></div>
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
          </div>
        </div>
      </div>
      <div className="flex-1 p-3 font-mono text-[10px] text-green-500/80 overflow-y-auto telemetry-scroll flex flex-col">
        <div className="space-y-1">
          <p className="text-green-400 opacity-60">Handshake established with main_node_0</p>
          <p className="text-green-400">Welcome, Operator. Awaiting instructions.</p>
          
          <div className="mt-4 p-3 border border-green-900/30 bg-green-500/5">
            <p className="text-green-900 text-[8px] mb-2 uppercase tracking-widest border-b border-green-900/30 pb-1">Circuit Selection</p>
            <div className="flex flex-wrap gap-2">
              {systemStatus.circuits.map((name) => (
                <button
                  key={name}
                  onClick={() => requestSwitchCircuit(name)}
                  className={`px-2 py-0.5 border text-[9px] transition-all cursor-pointer uppercase ${
                    systemStatus.active_circuit === name 
                    ? "bg-green-500 text-black border-green-500 font-bold shadow-[0_0_8px_#22c55e]" 
                    : "border-green-900 text-green-700 hover:border-green-500 hover:text-green-500"
                  }`}
                >
                  {name}
                </button>
              ))}
            </div>
          </div>

          {systemStatus.details && (
            <div className="mt-4 space-y-4">
              {/* Protocols Section */}
              <div className="p-3 border border-green-900/30 bg-green-500/5">
                <p className="text-green-900 text-[8px] mb-2 uppercase tracking-widest border-b border-green-900/30 pb-1">Active Protocols</p>
                <div className="space-y-1 max-h-32 overflow-y-auto pr-1">
                  {systemStatus.details.protocols.map((protocol, i) => (
                    <p key={i} className="text-[9px] text-green-500/70 flex gap-2">
                      <span className="text-green-800">[{i+1}]</span> {protocol}
                    </p>
                  ))}
                </div>
              </div>

              {/* Units Section */}
              <div className="p-3 border border-green-900/30 bg-green-500/5">
                <p className="text-green-900 text-[8px] mb-2 uppercase tracking-widest border-b border-green-900/30 pb-1">Technology Units</p>
                <div className="space-y-3">
                  {systemStatus.details.units.map((unit, i) => (
                    <div key={i} className="border-l border-green-900 pl-2">
                      <p className="text-[9px] text-green-400 font-bold uppercase">{unit.name} Unit</p>
                      <p className="text-[8px] text-green-700 italic mb-1">{unit.mission}</p>
                      <div className="space-y-0.5">
                        {unit.rules.map((rule, j) => (
                          <p key={j} className="text-[8px] text-green-600/80">└ {rule}</p>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          <div className="flex gap-3 mt-4">
            <button 
              onClick={requestMcpStatus}
              className="flex-1 px-3 py-1.5 border border-green-500 text-[10px] font-mono text-green-500 hover:bg-green-500 hover:text-black transition-all cursor-pointer flex items-center justify-center gap-2 uppercase"
            >
              <span className="material-symbols-outlined text-xs">analytics</span>
              Status Report
            </button>
          </div>
        </div>
      </div>
      <div className="bg-black/50 border-t border-green-900/30 p-2 flex items-center gap-2">
        <span className="text-green-600 font-mono text-[10px]">root@neb:~#</span>
        <input autoFocus className="bg-transparent border-none text-[10px] font-mono text-green-400 focus:ring-0 p-0 flex-1 outline-none" placeholder="execute command..." type="text" />
        <span className="w-1.5 h-3 bg-green-500 cursor-blink"></span>
      </div>
    </section>
  );
};
