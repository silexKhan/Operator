"use client";

import React from "react";

interface UnitProtocolsProps {
  systemStatus: any;
}

export const UnitProtocols: React.FC<UnitProtocolsProps> = ({ systemStatus }) => {
  const units = systemStatus.details?.units || [];

  return (
    <section className="col-span-5 row-span-2 flex flex-col terminal-window overflow-hidden">
      <div className="terminal-header px-2 py-1 flex justify-between items-center bg-orange-500/10">
        <div className="flex items-center gap-2">
          <span className="material-symbols-outlined text-[10px] text-orange-400">rule</span>
          <span className="text-[10px] font-mono text-orange-500 crt-glow">UNIT_PROTOCOLS.ext</span>
        </div>
        <span className="text-[9px] font-mono text-orange-900 uppercase">Deployed: {units.length} Units</span>
      </div>
      <div className="flex-1 p-3 font-mono text-[10px] text-orange-500/80 overflow-y-auto telemetry-scroll">
        <p className="text-orange-900 text-[8px] uppercase tracking-widest border-b border-orange-900/30 pb-1 mb-2">Active Unit Rules</p>
        <div className="space-y-3">
          {units.length > 0 ? (
            units.map((unit: any, i: number) => (
              <div key={i} className="border-l-2 border-orange-900/50 pl-2">
                <div className="flex justify-between items-center mb-1">
                  <span className="text-[9px] text-orange-400 font-bold uppercase">{unit.name} Unit</span>
                  <span className="text-[8px] text-orange-900 font-mono">ID: {unit.name.slice(0, 3).toUpperCase()}_0{i+1}</span>
                </div>
                <p className="text-[8px] text-orange-700 italic mb-1">{unit.mission}</p>
                <div className="space-y-0.5">
                  {unit.rules.map((rule: string, j: number) => (
                    <p key={j} className="text-[8px] text-orange-500/80 leading-tight">└ {rule}</p>
                  ))}
                </div>
              </div>
            ))
          ) : (
            <p className="text-orange-400 opacity-60 italic text-[9px]">Awaiting active technology unit deployment...</p>
          )}
        </div>
      </div>
    </section>
  );
};
