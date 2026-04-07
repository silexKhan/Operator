"use client";

import React from "react";

interface AuditSecurityProps {
  logs: any[];
}

export const AuditSecurity: React.FC<AuditSecurityProps> = ({ logs }) => {
  // 보안 관련 로그 필터링
  const securityLogs = logs.filter(log => 
    log.level === "ERROR" || 
    log.level === "WARNING" || 
    log.message.includes("AUDIT") || 
    log.message.includes("VIOLATION")
  ).slice(-10).reverse();

  return (
    <section className="col-span-4 row-span-3 flex flex-col terminal-window overflow-hidden">
      <div className={`terminal-header px-2 py-1 flex justify-between items-center ${securityLogs.length > 0 ? "bg-red-500/20 animate-pulse" : "bg-red-500/10"}`}>
        <div className="flex items-center gap-2">
          <span className="material-symbols-outlined text-[10px] text-red-500">security</span>
          <span className="text-[10px] font-mono text-red-500 crt-glow">AUDIT_SECURITY.bin</span>
        </div>
        <span className="text-[9px] font-mono text-red-900 uppercase">Alerts: {securityLogs.length}</span>
      </div>
      <div className="flex-1 p-3 font-mono text-[9px] text-red-500/80 overflow-hidden flex flex-col">
        <p className="text-red-900 text-[8px] uppercase tracking-widest border-b border-red-900/30 pb-1 mb-2">Security Breach Log</p>
        <div className="flex-1 overflow-y-auto pr-1 space-y-1.5 scrollbar-hide">
          {securityLogs.length > 0 ? (
            securityLogs.map((log, i) => (
              <div key={i} className="border-l border-red-900/50 pl-2 py-0.5">
                <div className="flex justify-between items-center text-[7px] text-red-900">
                  <span>{log.timestamp}</span>
                  <span className="font-bold">[{log.level}]</span>
                </div>
                <p className={`text-[8px] leading-tight ${log.level === 'ERROR' ? 'text-red-400 font-bold' : 'text-red-500/80'}`}>
                  {log.message}
                </p>
              </div>
            ))
          ) : (
            <div className="flex flex-col items-center justify-center h-full opacity-30">
              <span className="material-symbols-outlined text-[20px] mb-2">shield_check</span>
              <p className="italic">No security violations detected in the current session.</p>
            </div>
          )}
        </div>
      </div>
    </section>
  );
};
