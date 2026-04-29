"use client";

import React, { useState, useEffect, useCallback } from "react";
import { AuditLog, SystemStatus } from "@/types/mcp";

interface AuditSecurityProps {
  logs: AuditLog[];
  systemStatus: SystemStatus;
  language: "ko" | "en";
}

export const AuditSecurity: React.FC<AuditSecurityProps> = ({ logs, systemStatus, language }) => {

  const [isEditing, setIsEditing] = useState(false);
  const [globalRulesText, setGlobalRulesText] = useState("");
  const [parsedGlobalRules, setParsedGlobalRules] = useState<string[]>([]);
  const [isSaving, setIsSaving] = useState(false);

  // 실시간 세션 로그 기반 보안 로그 필터링
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const sessionSecurityLogs = logs.filter(log => 
    log.level === "ERROR" || 
    log.level === "WARNING" || 
    log.message.includes("AUDIT") || 
    log.message.includes("VIOLATION")
  ).slice(-5).reverse();

  // 백엔드로부터 받은 정식 감사 이력 (History)
  const auditHistory = systemStatus.details?.audit_logs || [];
  const violationCount = auditHistory.filter((a: AuditLog) => a.status === 'VIOLATION').length;
  const integrityScore = Math.max(0, 100 - (violationCount * 15));

  const fetchGlobalProtocols = useCallback(async () => {
    try {
      const res = await fetch("/api/mcp/protocols?type=global");
      if (res.ok) {
        const data = await res.json();
        setGlobalRulesText(data.content || "");
        
        // 언어별 파싱된 룰 추출
        if (data.data?.LANGUAGES && data.data.LANGUAGES[language]) {
          setParsedGlobalRules(data.data.LANGUAGES[language].RULES || []);
        }
      }
    } catch {
      // ignore
    }
  }, [language]);

  useEffect(() => {
    fetchGlobalProtocols();
  }, [fetchGlobalProtocols]);

  const handleSave = async () => {
    setIsSaving(true);
    try {
      const res = await fetch("/api/mcp/update", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          target: "global_protocols",
          data: globalRulesText
        })
      });
      if (res.ok) {
        setIsEditing(false);
        fetchGlobalProtocols(); // 저장 후 갱신
      }
    } catch {
      alert("Failed to save global protocols.");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="bg-neutral-900 border border-neutral-800 rounded-2xl overflow-hidden flex flex-col h-full shadow-2xl animate-in fade-in slide-in-from-right-4 duration-500">
      {/* Header */}
      <div className={`px-8 py-5 border-b border-neutral-800 flex justify-between items-center bg-neutral-900/80 backdrop-blur-md z-10 flex-shrink-0 ${violationCount > 0 ? "shadow-[inset_0_0_20px_rgba(244,63,94,0.05)]" : ""}`}>
        <div className="flex items-center gap-4">
          <div className={`p-2.5 rounded-xl border shadow-inner ${violationCount > 0 ? "bg-rose-500/10 text-rose-500 border-rose-500/20" : "bg-emerald-500/10 text-emerald-500 border-emerald-500/20"}`}>
            <span className="material-symbols-outlined text-2xl font-light">security</span>
          </div>
          <div>
            <h3 className="text-white font-bold tracking-tight uppercase text-sm">System Audit & Security</h3>
            <p className="text-[10px] text-neutral-500 font-mono mt-0.5 tracking-wider uppercase">Sentinel_Sentinel_Engine</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          {!isEditing ? (
            <button 
              onClick={() => setIsEditing(true)}
              className="flex items-center gap-2 px-4 py-2 bg-neutral-800 hover:bg-neutral-700 text-white text-[10px] font-black rounded-xl transition-all active:scale-95 border border-neutral-700 uppercase tracking-widest shadow-lg"
            >
              <span className="material-symbols-outlined text-sm">gavel</span>
              Global Rules
            </button>
          ) : (
            <div className="flex items-center gap-3 animate-in fade-in slide-in-from-right-4 duration-300">
              <button 
                onClick={handleSave}
                disabled={isSaving}
                className="flex items-center gap-2 px-6 py-2 bg-rose-600 hover:bg-rose-500 text-black text-[10px] font-black rounded-xl transition-all active:scale-95 uppercase tracking-widest shadow-lg shadow-rose-900/20"
              >
                <span className="material-symbols-outlined text-sm">save</span>
                {isSaving ? "Syncing..." : "Apply Global"}
              </button>
              <button 
                onClick={() => setIsEditing(false)}
                className="flex items-center gap-2 px-4 py-2 bg-neutral-900 hover:bg-neutral-800 text-neutral-500 hover:text-white text-[10px] font-bold rounded-xl transition-all uppercase tracking-widest"
              >
                Cancel
              </button>
            </div>
          )}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-8 custom-scrollbar bg-neutral-950/20">
        <div className="max-w-2xl mx-auto space-y-10 animate-in fade-in zoom-in-98 duration-500">
          {isEditing ? (
            <div className="flex flex-col space-y-4">
              <div className="flex items-center gap-2 px-1">
                <span className="material-symbols-outlined text-rose-500/60 text-lg">code</span>
                <label className="text-[10px] font-bold text-neutral-500 uppercase tracking-[0.2em]">Global Governance Source</label>
              </div>
              <textarea 
                value={globalRulesText}
                onChange={(e) => setGlobalRulesText(e.target.value)}
                className="w-full bg-neutral-950 border border-neutral-800 rounded-2xl p-8 text-xs font-mono text-rose-200/80 outline-none focus:border-rose-500/40 focus:ring-1 focus:ring-rose-500/20 transition-all resize-none h-[600px] leading-relaxed shadow-inner custom-scrollbar"
                placeholder="# Operator Global Protocols (Source)..."
              />
              <div className="p-5 bg-rose-500/5 border border-rose-500/20 rounded-2xl flex gap-3 items-start">
                 <span className="material-symbols-outlined text-rose-500 text-lg mt-0.5">warning</span>
                 <p className="text-[10px] text-neutral-500 leading-relaxed font-mono uppercase tracking-tighter">
                   Critical Warning: Modifying the global governance source will immediately propagate new constraints across all active and dormant circuits.
                 </p>
              </div>
            </div>
          ) : (
            <div className="space-y-12">
              {/* System Resource Quick Look */}
              <section className="grid grid-cols-2 gap-4">
                <div className="bg-neutral-900/40 border border-neutral-800/60 rounded-3xl p-6 shadow-inner group hover:border-emerald-500/20 transition-all">
                  <div className="flex justify-between items-center mb-3 px-1">
                    <div className="flex items-center gap-2">
                      <span className="material-symbols-outlined text-sm text-emerald-500">memory</span>
                      <label className="text-[9px] font-black text-neutral-500 uppercase tracking-widest">CPU_LOAD</label>
                    </div>
                    <span className="text-xs font-mono font-bold text-emerald-500">24%</span>
                  </div>
                  <div className="h-1.5 w-full bg-neutral-950 rounded-full overflow-hidden p-0.5 border border-neutral-800">
                    <div className="h-full bg-emerald-500 rounded-full w-[24%]" />
                  </div>
                </div>
                <div className="bg-neutral-900/40 border border-neutral-800/60 rounded-3xl p-6 shadow-inner group hover:border-amber-500/20 transition-all">
                  <div className="flex justify-between items-center mb-3 px-1">
                    <div className="flex items-center gap-2">
                      <span className="material-symbols-outlined text-sm text-amber-500">database</span>
                      <label className="text-[9px] font-black text-neutral-500 uppercase tracking-widest">MEM_USAGE</label>
                    </div>
                    <span className="text-xs font-mono font-bold text-amber-500">1.2GB</span>
                  </div>
                  <div className="h-1.5 w-full bg-neutral-950 rounded-full overflow-hidden p-0.5 border border-neutral-800">
                    <div className="h-full bg-amber-500 rounded-full w-[45%]" />
                  </div>
                </div>
              </section>

              {/* Integrity Score Section */}
              <section className="bg-neutral-900/40 border border-neutral-800/60 rounded-3xl p-8 shadow-inner group hover:border-emerald-500/20 transition-all duration-500">
                <div className="flex justify-between items-end mb-4 px-1">
                  <div className="flex items-center gap-2">
                    <span className={`material-symbols-outlined text-lg ${integrityScore < 70 ? 'text-rose-500' : 'text-emerald-500'}`}>
                      {integrityScore < 70 ? 'security_update_warning' : 'verified_user'}
                    </span>
                    <label className="text-[10px] font-bold text-neutral-400 uppercase tracking-[0.2em]">Compliance Integrity</label>
                  </div>
                  <span className={`text-2xl font-black font-mono tracking-tighter ${integrityScore < 70 ? 'text-rose-500' : 'text-emerald-500'}`}>
                    {integrityScore}%
                  </span>
                </div>
                <div className="h-3 w-full bg-neutral-950 border border-neutral-800 rounded-full overflow-hidden shadow-inner p-0.5">
                  <div 
                    className={`h-full rounded-full transition-all duration-1000 ${integrityScore < 70 ? 'bg-gradient-to-r from-rose-600 to-rose-400 shadow-[0_0_15px_rgba(244,63,94,0.3)]' : 'bg-gradient-to-r from-emerald-600 to-emerald-400 shadow-[0_0_15px_rgba(16,185,129,0.3)]'}`}
                    style={{ width: `${integrityScore}%` }}
                  ></div>
                </div>
              </section>

              {/* Global Protocols Section */}
              <section className="space-y-6">
                <div className="flex items-center gap-2 px-2">
                  <span className="material-symbols-outlined text-neutral-500/60 text-lg">gavel</span>
                  <label className="text-[10px] font-bold text-neutral-500 uppercase tracking-[0.2em]">Global Governance Protocols</label>
                </div>
                <div className="grid grid-cols-1 gap-3">
                  {parsedGlobalRules.length > 0 ? (
                    parsedGlobalRules.map((rule, i) => (
                      <div 
                        key={i} 
                        className="p-5 rounded-2xl border border-neutral-800/60 bg-neutral-900/20 hover:bg-neutral-900/40 transition-all group"
                      >
                        <div className="flex gap-4 items-start">
                           <span className="text-[10px] font-mono text-neutral-600 mt-1 font-bold">{(i+1).toString().padStart(2, '0')}</span>
                           <p className="text-xs text-neutral-400 leading-relaxed font-medium group-hover:text-neutral-200 transition-colors">
                             {rule}
                           </p>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="py-10 text-center border-2 border-dashed border-neutral-800 rounded-3xl opacity-20">
                       <p className="text-[10px] font-bold uppercase tracking-widest">No Global Protocols Loaded</p>
                    </div>
                  )}
                </div>
              </section>

              {/* Audit History Section */}
              <section className="space-y-6">
                <div className="flex items-center gap-2 px-2">
                  <span className="material-symbols-outlined text-neutral-500/60 text-lg">history_edu</span>
                  <label className="text-[10px] font-bold text-neutral-500 uppercase tracking-[0.2em]">Official Audit History</label>
                </div>
                <div className="space-y-3">
                  {auditHistory.length > 0 ? (
                    auditHistory.map((audit: AuditLog, i: number) => (
                      <div 
                        key={i} 
                        className={`p-5 rounded-2xl border flex items-start gap-5 transition-all duration-300 hover:scale-[1.01] ${
                          audit.status === 'VIOLATION' 
                          ? 'border-rose-500/40 bg-rose-500/5 shadow-[0_0_30px_rgba(244,63,94,0.05)]' 
                          : 'border-neutral-800 bg-neutral-900/40 hover:bg-neutral-900/60'
                        }`}
                      >
                        <div className={`mt-1.5 flex-shrink-0 w-2.5 h-2.5 rounded-full ${audit.status === 'VIOLATION' ? 'bg-rose-500 animate-pulse shadow-[0_0_10px_rgba(244,63,94,0.8)]' : 'bg-neutral-700'}`} />
                        <div className="flex-1 min-w-0">
                          <div className="flex justify-between items-center mb-2">
                            <span className="text-[10px] text-neutral-500 font-mono font-bold">{audit.timestamp}</span>
                            <div className={`px-2 py-0.5 rounded text-[9px] font-black uppercase tracking-tighter ${
                              audit.status === 'VIOLATION' ? 'bg-rose-500 text-black' : 'bg-neutral-800 text-neutral-500'
                            }`}>
                              {audit.status}
                            </div>
                          </div>
                          <p className={`text-sm leading-relaxed ${audit.status === 'VIOLATION' ? 'text-rose-100 font-bold' : 'text-neutral-400 font-medium'}`}>
                            {audit.message || audit.rule_id}
                          </p>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="flex flex-col items-center justify-center py-20 bg-neutral-900/20 border-2 border-dashed border-neutral-800 rounded-3xl opacity-30">
                      <span className="material-symbols-outlined text-5xl mb-3">verified_user</span>
                      <p className="text-[10px] font-bold uppercase tracking-widest text-center">No security violations recorded</p>
                    </div>
                  )}
                </div>
              </section>
            </div>
          )}
        </div>
      </div>

      {/* Footer / Meta */}
      {!isEditing && (
        <div className="px-8 py-5 bg-neutral-900/80 backdrop-blur-sm border-t border-neutral-800 flex justify-between items-center flex-shrink-0">
          <div className="flex items-center gap-6 text-[10px] text-neutral-600 font-mono uppercase tracking-widest font-bold">
            <span className="flex items-center gap-2 group">
              <span className="w-2 h-2 rounded-full bg-emerald-500 group-hover:animate-ping" />
              Sentinel_Shield: ON
            </span>
            <span className="flex items-center gap-2">
              <span className="material-symbols-outlined text-sm">enhanced_encryption</span>
              Neural_AES_256
            </span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-1.5 h-1.5 bg-rose-500 rounded-full animate-pulse"></div>
            <span className="text-[10px] text-rose-500/70 font-black tracking-widest uppercase">Live_Watchdog</span>
          </div>
        </div>
      )}
    </div>
  );
};
