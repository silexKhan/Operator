"use client";

import React from "react";

interface MissionSpecsProps {
  systemStatus: any;
}

export const MissionSpecs: React.FC<MissionSpecsProps> = ({ systemStatus }) => {
  const details = systemStatus.details;
  
  return (
    <section className="col-span-5 row-span-4 flex flex-col terminal-window overflow-hidden">
      <div className="terminal-header px-2 py-1 flex justify-between items-center bg-green-500/10">
        <div className="flex items-center gap-2">
          <span className="material-symbols-outlined text-[10px] text-green-400">assignment</span>
          <span className="text-[10px] font-mono text-green-500 crt-glow">MISSION_SPECS.sys</span>
        </div>
        <span className="text-[9px] font-mono text-green-900 uppercase">Status: {details ? "SPEC_LOADED" : "AWAITING_DATA"}</span>
      </div>
      <div className="flex-1 p-3 font-mono text-[10px] text-green-500/80 overflow-y-auto telemetry-scroll">
        <div className="space-y-4">
          <p className="text-green-900 text-[8px] uppercase tracking-widest border-b border-green-900/30 pb-1">Current Active Circuit</p>
          <div className="p-3 border border-green-900/30 bg-green-500/5">
            <div className="flex justify-between items-start mb-2">
              <span className="text-[12px] text-green-400 font-black tracking-tighter uppercase">{systemStatus.active_circuit}</span>
              <span className="px-1 bg-green-900 text-black text-[7px] font-bold">READY</span>
            </div>
            
            {details ? (
              <div className="space-y-3">
                <div className="border-l border-green-900 pl-2 py-1">
                  <p className="text-[8px] text-green-800 uppercase mb-1">Architect's Summary</p>
                  <p className="text-[9px] text-green-500 leading-relaxed italic">
                    {details.description || "No description provided for this circuit node."}
                  </p>
                </div>

                <div className="space-y-2">
                  <p className="text-[8px] text-green-800 uppercase">Operational Dependencies</p>
                  <div className="flex flex-wrap gap-2">
                    {details.units?.map((u: any, i: number) => (
                      <span key={i} className="text-[7px] border border-green-900/50 px-1 py-0.5 text-green-700">
                        {u.name.toUpperCase()}
                      </span>
                    ))}
                  </div>
                </div>
                
                <div className="mt-2 text-[8px] text-green-900 border-t border-green-900/20 pt-2 flex gap-4">
                  <span>FILES: {details.actions?.length || 0}</span>
                  <span>UNITS: {details.units?.length || 0}</span>
                </div>
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-8 opacity-20">
                <span className="material-symbols-outlined text-[32px] mb-2 animate-pulse">file_open</span>
                <p className="text-[8px]">AWAITING DETAILED SPECS FROM CORE</p>
              </div>
            )}
          </div>

          <div className="mt-4 p-2 border border-green-900/20 opacity-40">
            <p className="text-[7px] text-green-900 mb-1 font-bold uppercase">System Broadcast</p>
            <p className="text-[8px] text-green-800 leading-tight">
              NEBUCHADNEZZAR OS V2.5 // ALL SYSTEMS NOMINAL // UPLINK_SECURE: 100%
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};
