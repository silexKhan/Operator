"use client";

import React from "react";

interface UnitProtocolsProps {
  systemStatus: any;
}

export const UnitProtocols: React.FC<UnitProtocolsProps> = ({ systemStatus }) => {
  const details = systemStatus?.details;
  const globalProtocols = details?.protocols || [];
  const units = details?.units || [];
  const isActive = !!details;

  return (
    <section className="col-span-5 row-span-2 flex flex-col terminal-window overflow-hidden border-orange-900/40">
      <div className="terminal-header px-2 py-1 flex justify-between items-center bg-orange-500/10">
        <div className="flex items-center gap-2">
          <span className="material-symbols-outlined text-[10px] text-orange-400">rule</span>
          <span className="text-[10px] font-mono text-orange-500 crt-glow uppercase">UNIT_PROTOCOLS.ext</span>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-[7px] font-mono text-orange-900 uppercase tracking-widest">
            {isActive ? "Uplink: Synchronized" : "Uplink: Awaiting Core Signal"}
          </span>
          <span className="text-[9px] font-mono text-orange-500 uppercase">UNITS: {units.length}</span>
        </div>
      </div>

      <div className="flex-1 p-3 font-mono text-[9px] text-orange-500/80 overflow-hidden flex gap-4">
        
        {/* Left Column: Global Directives */}
        <div className="w-1/3 flex flex-col border-r border-orange-900/20 pr-3">
          <p className="text-orange-900 text-[7px] uppercase tracking-widest border-b border-orange-900/30 pb-0.5 mb-2 font-black flex items-center gap-1">
            <span className="material-symbols-outlined text-[9px]">gavel</span>
            GLOBAL_DIRECTIVES
          </p>
          <div className="flex-1 overflow-y-auto telemetry-scroll space-y-1.5 pr-1">
            {globalProtocols.length > 0 ? (
              globalProtocols.map((rule: string, i: number) => (
                <div key={i} className="text-[7px] leading-tight text-orange-800 flex gap-1.5 italic">
                  <span className="text-orange-500 font-bold shrink-0">[{rule.split(':')[0]}]</span>
                  <span>{rule.split(':').slice(1).join(':').trim() || rule}</span>
                </div>
              ))
            ) : (
              <p className="text-[7px] opacity-20 uppercase">No Global Protocols Loaded</p>
            )}
          </div>
        </div>

        {/* Right Column: Deployed Units & Their Protocols */}
        <div className="flex-1 flex flex-col">
          <p className="text-orange-900 text-[7px] uppercase tracking-widest border-b border-orange-900/30 pb-0.5 mb-2 font-black flex items-center gap-1">
            <span className="material-symbols-outlined text-[9px]">hub</span>
            DEPLOYED_TECHNOLOGY_UNITS
          </p>
          <div className="flex-1 overflow-y-auto telemetry-scroll pr-1 grid grid-cols-2 gap-3">
            {units.length > 0 ? (
              units.map((unit: any, i: number) => (
                <div key={i} className="border border-orange-900/20 bg-orange-500/5 p-2 rounded-sm relative group hover:border-orange-500/30 transition-all">
                  <div className="flex justify-between items-start mb-1.5">
                    <span className="text-[9px] text-orange-400 font-black uppercase tracking-tighter">{unit.name} UNIT</span>
                    <span className="text-[6px] px-1 bg-orange-900 text-black font-bold">ACT_0{i+1}</span>
                  </div>
                  
                  {unit.mission && unit.mission !== "N/A" && (
                    <div className="mb-2 opacity-80">
                      <p className="text-[6px] text-orange-900 uppercase font-bold mb-0.5">Primary Mission</p>
                      <p className="text-[7.5px] text-orange-400/90 leading-tight border-l border-orange-900/50 pl-1.5 py-0.5">{unit.mission}</p>
                    </div>
                  )}

                  <div className="space-y-0.5 opacity-60">
                    <p className="text-[6px] text-orange-900 uppercase font-bold mb-0.5">Active Ruleset</p>
                    {unit.rules?.slice(0, 3).map((rule: string, j: number) => (
                      <p key={j} className="text-[7px] text-orange-600 truncate leading-none">└ {rule}</p>
                    ))}
                    {unit.rules?.length > 3 && <p className="text-[6px] text-orange-900 italic">... and {unit.rules.length - 3} more</p>}
                  </div>
                  
                  <div className="absolute top-0 right-0 p-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <span className="material-symbols-outlined text-[8px] text-orange-500">info</span>
                  </div>
                </div>
              ))
            ) : (
              <div className="col-span-2 flex flex-col items-center justify-center py-6 opacity-20 border border-dashed border-orange-900/50">
                <span className="material-symbols-outlined text-[20px] mb-1 animate-pulse">radar</span>
                <p className="text-[8px]">AWAITING UNIT DEPLOYMENT SIGNALS</p>
              </div>
            )}
          </div>
        </div>

      </div>

      {/* Footer System Status */}
      <div className="px-2 py-0.5 bg-orange-900/10 border-t border-orange-900/20 flex justify-between items-center text-[6px] text-orange-900 uppercase">
        <div className="flex gap-4">
          <span>Unit Runtime: Stable</span>
          <span>Sync ID: 0xCC_FF_A0</span>
        </div>
        <div className="flex items-center gap-1">
          <span className="w-1 h-1 rounded-full bg-orange-500 animate-pulse"></span>
          <span>PROTOCOL_UPLINK_SECURE</span>
        </div>
      </div>
    </section>
  );
};
