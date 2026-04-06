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
    <section className="col-span-3 row-span-3 flex flex-col terminal-window overflow-hidden">
      <div className="terminal-header px-2 py-1 flex justify-between items-center">
        <span className="text-[10px] font-mono text-green-500 crt-glow">SYSTEM_LOGS.raw</span>
        <span className={`text-[9px] ${status === 'CONNECTED' ? 'text-green-400 drop-shadow-[0_0_5px_rgba(74,222,128,0.5)]' : 'text-red-600'} font-bold animate-pulse`}>
          ● {status === 'CONNECTED' ? 'OPERATOR ONLINE' : 'OPERATOR OFFLINE'}
        </span>
      </div>
      <div className="flex-1 p-3 font-mono text-[9px] text-green-500/70 overflow-y-auto custom-scrollbar flex flex-col">
        <div className="space-y-1">
          {logs.length === 0 ? (
            <p className="opacity-50 italic">Awaiting telemetry downlink...</p>
          ) : (
            logs.map((log, i) => (
              <p key={i} className="leading-tight">
                <span className="text-green-900">[{log.timestamp}]</span>{' '}
                <span className={log.level === 'END' ? 'text-blue-400' : 'text-green-400'}>
                  {log.category}: {log.message}
                </span>
              </p>
            ))
          )}
          <div ref={logEndRef} />
        </div>
      </div>
      <div className="bg-black/50 border-t border-green-900/30 p-2 flex items-center gap-2">
        <span className="text-green-600 font-mono text-[10px]">logs@neb:~#</span>
        <input className="bg-transparent border-none text-[10px] font-mono text-green-400 focus:ring-0 p-0 flex-1 outline-none" placeholder="tail -f /var/log/sys" type="text" />
        <span className="w-1.5 h-3 bg-green-500 cursor-blink"></span>
      </div>
    </section>
  );
};
