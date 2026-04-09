"use client";

import React from "react";

interface LogEntry {
  timestamp: string;
  level: string;
  message: string;
  category: string;
}

interface SystemLogsProps {
  logs: LogEntry[];
  status: string;
  logEndRef: React.RefObject<HTMLDivElement | null>;
}

export const SystemLogs: React.FC<SystemLogsProps> = ({ logs, status, logEndRef }) => {
  return (
    <div className="flex flex-col h-full bg-neutral-950/80 font-mono text-[11px]">
      {/* Log Header */}
      <div className="px-6 py-2 border-b border-neutral-800/50 flex justify-between items-center bg-neutral-900/30">
        <div className="flex items-center gap-4">
          <span className="text-neutral-500 font-bold uppercase tracking-widest text-[10px]">System Telemetry</span>
          <div className="flex items-center gap-2">
            <span className={`w-1.5 h-1.5 rounded-full ${status === 'CONNECTED' ? 'bg-emerald-500' : 'bg-rose-500 animate-pulse'}`} />
            <span className="text-neutral-600 text-[9px]">{status === 'CONNECTED' ? 'UPLINK_STABLE' : 'UPLINK_TERMINATED'}</span>
          </div>
        </div>
        <div className="text-neutral-700 text-[9px]">
          SESSION_LOG_BUFFER: {logs.length}/50
        </div>
      </div>

      {/* Log Content */}
      <div className="flex-1 overflow-y-auto px-6 py-3 custom-scrollbar">
        <div className="space-y-0.5">
          {logs.length === 0 ? (
            <p className="text-neutral-700 italic py-2">Awaiting telemetry downlink...</p>
          ) : (
            logs.map((log, i) => (
              <div key={i} className="flex gap-4 group hover:bg-white/5 transition-colors py-0.5 px-1 rounded">
                <span className="text-neutral-600 shrink-0 select-none">[{log.timestamp}]</span>
                <span className={`shrink-0 font-bold w-12 text-center select-none ${
                  log.level === 'ERROR' ? 'text-rose-500' : 
                  log.level === 'WARNING' ? 'text-amber-500' : 
                  'text-blue-500/70'
                }`}>
                  {log.level}
                </span>
                <span className="text-neutral-500 shrink-0 font-bold">[{log.category}]</span>
                <span className="text-neutral-300 break-all leading-tight">
                  {log.message}
                </span>
              </div>
            ))
          )}
          <div ref={logEndRef} />
        </div>
      </div>

      {/* Log Footer / Quick Info */}
      <div className="px-6 py-1.5 border-t border-neutral-800/30 bg-neutral-900/20 flex items-center justify-between text-[10px] text-neutral-600">
        <div className="flex gap-4">
          <span>OPERATOR_ID: CYPHER_01</span>
          <span>NODE: NEBUCHADNEZZAR</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="material-symbols-outlined text-[12px]">filter_list</span>
          <span>ALL_TRAFFIC</span>
        </div>
      </div>
    </div>
  );
};
