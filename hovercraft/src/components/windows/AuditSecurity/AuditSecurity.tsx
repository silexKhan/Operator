"use client";

import React, { useState, useEffect } from "react";

interface AuditSecurityProps {
  logs: any[];
  systemStatus?: any;
}

export const AuditSecurity: React.FC<AuditSecurityProps> = ({ logs, systemStatus }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [globalRules, setGlobalRules] = useState("");
  const [isSaving, setIsSaving] = useState(false);

  // 실시간 세션 로그 기반 보안 로그 필터링
  const sessionSecurityLogs = logs.filter(log => 
    log.level === "ERROR" || 
    log.level === "WARNING" || 
    log.message.includes("AUDIT") || 
    log.message.includes("VIOLATION")
  ).slice(-5).reverse();

  // 백엔드로부터 받은 정식 감사 이력 (History)
  const auditHistory = systemStatus?.details?.audit_logs || [];
  const violationCount = auditHistory.filter((a: any) => a.status === 'VIOLATION').length;
  const integrityScore = Math.max(0, 100 - (violationCount * 15));

  const fetchGlobalProtocols = async () => {
    try {
      const res = await fetch("/api/mcp/protocols?type=global");
      if (res.ok) {
        const data = await res.json();
        setGlobalRules(data.content || "");
      }
    } catch (e) {
      console.error("Failed to fetch global protocols:", e);
    }
  };

  useEffect(() => {
    if (isEditing) fetchGlobalProtocols();
  }, [isEditing]);

  const handleSave = async () => {
    setIsSaving(true);
    try {
      const res = await fetch("/api/mcp/update", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          target: "global_protocols",
          data: globalRules
        })
      });
      if (res.ok) setIsEditing(false);
    } catch (e) {
      alert("Failed to save global protocols.");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="bg-neutral-900 border border-neutral-800 rounded-xl overflow-hidden flex flex-col shadow-sm">
      {/* Header */}
      <div className={`px-6 py-4 border-b border-neutral-800 flex justify-between items-center ${violationCount > 0 ? "bg-rose-500/5" : "bg-neutral-900/50"}`}>
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg ${violationCount > 0 ? "bg-rose-500/10 text-rose-500" : "bg-emerald-500/10 text-emerald-500"}`}>
            <span className="material-symbols-outlined text-xl">security</span>
          </div>
          <div>
            <h3 className="text-white font-medium">Security & Audit</h3>
            <p className="text-[11px] text-neutral-500 font-mono uppercase tracking-wider">Sentinel_Watchdog_Engine</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {!isEditing ? (
            <button 
              onClick={() => setIsEditing(true)}
              className="flex items-center gap-2 px-3 py-1.5 bg-neutral-800 hover:bg-neutral-700 text-neutral-200 text-xs rounded-md transition-colors"
            >
              <span className="material-symbols-outlined text-sm">gavel</span>
              Global Protocols
            </button>
          ) : (
            <div className="flex items-center gap-2">
              <button 
                onClick={handleSave}
                disabled={isSaving}
                className="flex items-center gap-2 px-3 py-1.5 bg-rose-600 hover:bg-rose-500 text-white text-xs rounded-md transition-colors font-medium"
              >
                <span className="material-symbols-outlined text-sm">save</span>
                {isSaving ? "Syncing..." : "Apply Global Rules"}
              </button>
              <button 
                onClick={() => setIsEditing(false)}
                className="flex items-center gap-2 px-3 py-1.5 bg-neutral-800 hover:bg-neutral-700 text-neutral-400 text-xs rounded-md transition-colors"
              >
                Cancel
              </button>
            </div>
          )}
        </div>
      </div>

      <div className="p-6 space-y-6 flex-1 flex flex-col overflow-hidden">
        {isEditing ? (
          <div className="flex-1 flex flex-col space-y-3 min-h-[400px]">
            <label className="text-[10px] font-bold text-neutral-500 uppercase tracking-widest block">System Protocol Source Code</label>
            <textarea 
              value={globalRules}
              onChange={(e) => setGlobalRules(e.target.value)}
              className="flex-1 w-full bg-neutral-950 border border-neutral-800 rounded-xl p-4 text-sm font-mono text-neutral-300 outline-none focus:border-rose-500/30 transition-colors resize-none leading-relaxed shadow-inner"
              placeholder="# Operator Global Protocols (Source)..."
            />
            <p className="text-[10px] text-neutral-600 italic">
              * Critical: Modification of global protocols affects all underlying circuit operations.
            </p>
          </div>
        ) : (
          <>
            {/* Integrity Score Section */}
            <section>
              <div className="flex justify-between items-end mb-2">
                <label className="text-[10px] font-bold text-neutral-500 uppercase tracking-widest">Compliance Integrity</label>
                <span className={`text-lg font-bold font-mono ${integrityScore < 70 ? 'text-rose-500' : 'text-emerald-500'}`}>
                  {integrityScore}%
                </span>
              </div>
              <div className="h-2 w-full bg-neutral-800 rounded-full overflow-hidden">
                <div 
                  className={`h-full transition-all duration-1000 ${integrityScore < 70 ? 'bg-rose-500 shadow-[0_0_8px_rgba(244,63,94,0.5)]' : 'bg-emerald-500'}`}
                  style={{ width: `${integrityScore}%` }}
                ></div>
              </div>
            </section>

            {/* Audit History Section */}
            <section className="flex-1 flex flex-col overflow-hidden">
              <label className="text-[10px] font-bold text-neutral-500 uppercase tracking-widest mb-4 block">Official Audit History</label>
              <div className="flex-1 overflow-y-auto space-y-2 pr-2 custom-scrollbar">
                {auditHistory.length > 0 ? (
                  auditHistory.map((audit: any, i: number) => (
                    <div 
                      key={i} 
                      className={`p-3 rounded-lg border flex items-start gap-4 transition-all hover:bg-neutral-800/50 ${
                        audit.status === 'VIOLATION' 
                        ? 'border-rose-500/30 bg-rose-500/5' 
                        : 'border-neutral-800 bg-neutral-950/30'
                      }`}
                    >
                      <div className={`mt-1 flex-shrink-0 w-2 h-2 rounded-full ${audit.status === 'VIOLATION' ? 'bg-rose-500 animate-pulse' : 'bg-neutral-700'}`} />
                      <div className="flex-1 min-w-0">
                        <div className="flex justify-between items-center mb-1">
                          <span className="text-[10px] text-neutral-500 font-mono">{audit.timestamp}</span>
                          <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded uppercase tracking-tighter ${
                            audit.status === 'VIOLATION' ? 'bg-rose-500 text-white' : 'bg-neutral-800 text-neutral-400'
                          }`}>
                            {audit.status}
                          </span>
                        </div>
                        <p className={`text-sm leading-snug ${audit.status === 'VIOLATION' ? 'text-rose-200 font-medium' : 'text-neutral-400'}`}>
                          {audit.message || audit.rule_id}
                        </p>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="flex flex-col items-center justify-center py-12 text-neutral-600 opacity-50">
                    <span className="material-symbols-outlined text-4xl mb-2">verified_user</span>
                    <p className="text-sm">No registered audit violations</p>
                  </div>
                )}
              </div>
            </section>
          </>
        )}
      </div>

      {/* Footer / Meta */}
      {!isEditing && (
        <div className="px-6 py-4 bg-neutral-950/50 border-t border-neutral-800 flex justify-between items-center">
          <div className="flex items-center gap-4 text-[10px] text-neutral-600 font-mono uppercase tracking-widest">
            <span className="flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
              Sentinel_Active
            </span>
            <span className="flex items-center gap-1.5">
              <span className="material-symbols-outlined text-[12px]">lock</span>
              AES-256
            </span>
          </div>
          <div className="text-[10px] text-rose-500/50 font-bold animate-pulse">
            ● LIVE_MONITORING
          </div>
        </div>
      )}
    </div>
  );
};
