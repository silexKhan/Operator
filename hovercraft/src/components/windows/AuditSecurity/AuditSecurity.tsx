"use client";

import React from "react";

interface AuditSecurityProps {
  logs: any[];
  systemStatus?: any;
}

export const AuditSecurity: React.FC<AuditSecurityProps> = ({ logs, systemStatus }) => {
  // 1. 실시간 세션 로그 기반 보안 로그 필터링
  const sessionSecurityLogs = logs.filter(log => 
    log.level === "ERROR" || 
    log.level === "WARNING" || 
    log.message.includes("AUDIT") || 
    log.message.includes("VIOLATION")
  ).slice(-5).reverse();

  // 2. 백엔드로부터 받은 정식 감사 이력 (History)
  const auditHistory = systemStatus?.details?.audit_logs || [];
  
  // 3. 보안 무결성 점수 계산 (가상의 점수 또는 로그 기반 계산)
  const violationCount = auditHistory.filter((a: any) => a.status === 'VIOLATION').length;
  const integrityScore = Math.max(0, 100 - (violationCount * 15));

  return (
    <section className="col-span-4 row-span-3 flex flex-col terminal-window overflow-hidden border-red-900/40">
      {/* Header */}
      <div className={`terminal-header px-2 py-1 flex justify-between items-center ${violationCount > 0 ? "bg-red-500/20 animate-pulse" : "bg-red-500/10"}`}>
        <div className="flex items-center gap-2">
          <span className="material-symbols-outlined text-[10px] text-red-500">security</span>
          <span className="text-[10px] font-mono text-red-500 crt-glow">AUDIT_SECURITY.bin</span>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-[7px] font-mono text-red-900 uppercase">Integrity: {integrityScore}%</span>
          <span className="text-[9px] font-mono text-red-500 uppercase">ALERTS: {violationCount}</span>
        </div>
      </div>

      <div className="flex-1 p-3 font-mono text-[9px] text-red-500/80 overflow-hidden flex flex-col space-y-3">
        
        {/* Integrity Gauge Section */}
        <div className="space-y-1">
          <div className="flex justify-between text-[7px] text-red-900 uppercase font-black">
            <span>System Compliance Integrity</span>
            <span>{integrityScore}%</span>
          </div>
          <div className="h-1.5 w-full bg-red-950/30 border border-red-900/20 relative overflow-hidden">
            <div 
              className={`h-full transition-all duration-1000 ${integrityScore < 70 ? 'bg-red-500 animate-pulse' : 'bg-red-800'}`}
              style={{ width: `${integrityScore}%` }}
            ></div>
            <div className="absolute inset-0 scanline-mini opacity-30"></div>
          </div>
        </div>

        {/* Audit History (Official) */}
        <div className="flex-1 flex flex-col overflow-hidden">
          <p className="text-red-900 text-[7px] uppercase tracking-widest border-b border-red-900/30 pb-0.5 mb-2 font-bold">Official Audit History</p>
          <div className="flex-1 overflow-y-auto pr-1 space-y-1.5 telemetry-scroll">
            {auditHistory.length > 0 ? (
              auditHistory.map((audit: any, i: number) => (
                <div key={i} className={`border-l-2 pl-2 py-1 bg-red-500/5 ${audit.status === 'VIOLATION' ? 'border-red-500' : 'border-red-900/30'}`}>
                  <div className="flex justify-between items-center text-[7px] mb-0.5">
                    <span className="text-red-900 uppercase tracking-tighter">{audit.timestamp}</span>
                    <span className={`font-black px-1 ${audit.status === 'VIOLATION' ? 'bg-red-500 text-black' : 'text-red-700'}`}>
                      [{audit.status}]
                    </span>
                  </div>
                  <p className={`text-[8px] leading-tight ${audit.status === 'VIOLATION' ? 'text-red-400 font-bold' : 'text-red-600/70'}`}>
                    {audit.message || audit.rule_id}
                  </p>
                </div>
              ))
            ) : (
              <div className="flex flex-col items-center justify-center py-6 opacity-20">
                <span className="material-symbols-outlined text-[24px] mb-1">verified_user</span>
                <p className="text-[7px]">NO REGISTERED AUDIT DATA</p>
              </div>
            )}
          </div>
        </div>

        {/* Real-time Session Alerts */}
        {sessionSecurityLogs.length > 0 && (
          <div className="h-16 flex flex-col opacity-60">
            <p className="text-red-900 text-[7px] uppercase mb-1 font-bold">Session Alerts</p>
            <div className="flex-1 overflow-hidden space-y-1">
              {sessionSecurityLogs.slice(0, 2).map((log, i) => (
                <div key={i} className="text-[7px] flex gap-2 text-red-800 leading-none">
                  <span className="whitespace-nowrap font-black">!</span>
                  <span className="truncate">{log.message}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Footer Info */}
        <div className="pt-1 border-t border-red-900/20 flex justify-between items-center text-[7px] text-red-900 uppercase">
          <div className="flex gap-2">
            <span>SENTINEL_ACTIVE: 1</span>
            <span>ENCRYPT: AES-256</span>
          </div>
          <span className="animate-pulse">● MONITORING</span>
        </div>
      </div>
    </section>
  );
};
