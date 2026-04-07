"use client";

import React from "react";

interface ResourceMonitorProps {
  systemStatus: any;
}

export const ResourceMonitor: React.FC<ResourceMonitorProps> = ({ systemStatus }) => {
  const isConnected = systemStatus.active_circuit !== "None";

  return (
    <section className="col-span-3 row-span-3 flex flex-col terminal-window overflow-hidden">
      <div className="terminal-header px-2 py-1 flex justify-between items-center bg-blue-500/10">
        <div className="flex items-center gap-2">
          <span className="material-symbols-outlined text-[10px] text-blue-400">speed</span>
          <span className="text-[10px] font-mono text-blue-500 crt-glow">RESOURCE_MONITOR.sys</span>
        </div>
        <div className={`w-1.5 h-1.5 rounded-full ${isConnected ? "bg-blue-500 animate-pulse shadow-[0_0_8px_#3b82f6]" : "bg-blue-900"}`}></div>
      </div>
      <div className="flex-1 p-3 font-mono text-[10px] text-blue-500/80 overflow-y-auto telemetry-scroll flex flex-col">
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-2">
            <div className="border border-blue-900/30 p-2 bg-blue-500/5">
              <p className="text-[7px] text-blue-900 uppercase">Uplink Strength</p>
              <p className="text-[14px] text-blue-400 font-black">{isConnected ? "98.2%" : "0.0%"}</p>
            </div>
            <div className="border border-blue-900/30 p-2 bg-blue-500/5">
              <p className="text-[7px] text-blue-900 uppercase">Latency (ms)</p>
              <p className="text-[14px] text-blue-400 font-black">{isConnected ? "12ms" : "---"}</p>
            </div>
          </div>

          <div className="space-y-3">
            <div className="space-y-1">
              <div className="flex justify-between text-[7px] text-blue-900 uppercase">
                <span>Core CPU Load</span>
                <span>{isConnected ? "14.2%" : "0.0%"}</span>
              </div>
              <div className="h-1 bg-blue-950/50 rounded-full overflow-hidden border border-blue-900/20">
                <div className="h-full bg-blue-500 transition-all duration-1000" style={{ width: isConnected ? "14.2%" : "0%" }}></div>
              </div>
            </div>

            <div className="space-y-1">
              <div className="flex justify-between text-[7px] text-blue-900 uppercase">
                <span>Neural Memory</span>
                <span>{isConnected ? "65.8%" : "0.0%"}</span>
              </div>
              <div className="h-1 bg-blue-950/50 rounded-full overflow-hidden border border-blue-900/20">
                <div className="h-full bg-blue-500 transition-all duration-1000" style={{ width: isConnected ? "65.8%" : "0%" }}></div>
              </div>
            </div>

            <div className="space-y-1">
              <div className="flex justify-between text-[7px] text-blue-900 uppercase">
                <span>Uptime (Session)</span>
                <span className="text-blue-400 font-bold">04:12:33</span>
              </div>
            </div>
          </div>

          <div className="mt-auto pt-2 border-t border-blue-900/20">
            <div className="flex justify-between items-center opacity-40">
              <span className="text-[7px] text-blue-900 uppercase font-bold tracking-widest">Operator Node Status</span>
              <span className="text-[7px] text-blue-400 uppercase">{isConnected ? "Online" : "Awaiting Connection"}</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
