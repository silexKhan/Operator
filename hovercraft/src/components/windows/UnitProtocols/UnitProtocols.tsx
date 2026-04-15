"use client";

import React, { useState, useEffect, useCallback } from "react";
import { SystemStatus } from "@/types/mcp";

interface UnitProtocolsProps {
  systemStatus: SystemStatus;
  language: "ko" | "en";
}

type SelectedRule = {
  type: "global" | "circuit";
  index: number;
} | null;

interface GlobalProtocolsData {
  data?: {
    LANGUAGES: {
      [key: string]: {
        RULES: string[];
      };
    };
  };
}

export const UnitProtocols: React.FC<UnitProtocolsProps> = ({ systemStatus, language }) => {
  const [selectedRule, setSelectedRule] = useState<SelectedRule>(null);
  const [editedRule, setEditedRule] = useState("");
  const [isSaving, setIsSaving] = useState(false);
  
  const [globalRules, setGlobalRules] = useState<string[]>([]);
  const [isGlobalLoading, setIsGlobalLoading] = useState(true);

  const details = systemStatus.details;

  // 1. 글로벌 규약 로드
  const fetchGlobalProtocols = useCallback(async () => {
    try {
      const res = await fetch("/api/mcp/protocols?type=global");
      if (res.ok) {
        const data: GlobalProtocolsData = await res.json();
        if (data.data?.LANGUAGES && data.data.LANGUAGES[language]) {
          setGlobalRules(data.data.LANGUAGES[language].RULES || []);
        }
      }
    } catch (e) {
      console.error("Failed to fetch global protocols", e);
    } finally {
      setIsGlobalLoading(false);
    }
  }, [language]);

  useEffect(() => {
    fetchGlobalProtocols();
  }, [fetchGlobalProtocols]);
  
  // 2. 현재 회선의 규약 배열 추출
  const getCircuitRulesArray = (): (string | Record<string, string>)[] => {
    if (!details?.protocols) return [];
    if (Array.isArray(details.protocols)) return details.protocols;
    if (typeof details.protocols === 'object' && 'RULES' in details.protocols) {
      return (details.protocols as { RULES: (string | Record<string, string>)[] }).RULES;
    }
    return [];
  };

  const circuitRules = getCircuitRulesArray();

  // 3. 규약 선택 핸들러
  const handleSelectRule = (type: "global" | "circuit", index: number) => {
    setSelectedRule({ type, index });
    if (type === "global") {
      setEditedRule(globalRules[index] || "");
    } else {
      const rule = circuitRules[index];
      const ruleText = typeof rule === 'object' && rule !== null 
        ? (rule[language] || rule.ko || rule.en || JSON.stringify(rule)) 
        : (rule || "");
      setEditedRule(ruleText);
    }
  };

  const handleSaveRule = async () => {
    if (!selectedRule || selectedRule.type === "global") return;
    setIsSaving(true);
    
    const newProtocols = [...circuitRules];
    newProtocols[selectedRule.index] = editedRule;

    try {
      const res = await fetch("/api/mcp/update", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          target: "circuit_protocols",
          name: systemStatus.active_circuit,
          data: { RULES: newProtocols }
        })
      });
      if (res.ok) {
        setSelectedRule(null);
      }
    } catch (e) {
      console.error(e);
      alert("Failed to save protocol directive.");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="bg-neutral-900 border border-neutral-800 rounded-2xl overflow-hidden flex flex-col h-full shadow-2xl animate-in fade-in slide-in-from-bottom-4 duration-500">
      {/* Main Header */}
      <div className="px-8 py-5 border-b border-neutral-800 flex justify-between items-center bg-neutral-900/80 backdrop-blur-md z-10 flex-shrink-0">
        <div className="flex items-center gap-4">
          <div className="p-2.5 bg-amber-500/10 rounded-xl border border-amber-500/20 shadow-inner">
            <span className="material-symbols-outlined text-amber-500 text-2xl">rule</span>
          </div>
          <div>
            <h3 className="text-white font-bold tracking-tight uppercase text-sm">Governance Protocols</h3>
            <p className="text-[10px] text-neutral-500 font-mono mt-0.5 tracking-wider uppercase">{systemStatus.active_circuit}_Directive_Cluster</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <div className="px-2 py-1 bg-neutral-950 border border-neutral-800 rounded text-[9px] font-mono text-amber-500">
            GOVERNANCE_ACTIVE
          </div>
        </div>
      </div>

      <div className="flex-1 flex overflow-hidden">
        {/* Left Panel: Two Stacked Windows */}
        <div className="w-80 border-r border-neutral-800 flex flex-col bg-neutral-950/40 flex-shrink-0 divide-y divide-neutral-800">
          
          {/* Window 1: Global Governance (Fixed Scroll Area) */}
          <div className="flex-1 flex flex-col overflow-hidden min-h-[200px]">
            <div className="p-4 px-6 bg-neutral-900/40 border-b border-neutral-800/50 flex items-center justify-between">
              <label className="text-[9px] font-black text-rose-500/80 uppercase tracking-[0.2em] flex items-center gap-2">
                <span className="w-1.5 h-1.5 bg-rose-500 rounded-full animate-pulse shadow-[0_0_5px_rgba(244,63,94,0.5)]" />
                Global Governance
              </label>
              <span className="material-symbols-outlined text-neutral-600 text-sm">lock</span>
            </div>
            <div className="flex-1 overflow-y-auto p-4 space-y-1.5 custom-scrollbar">
              {isGlobalLoading ? (
                <div className="space-y-2">
                  {[1, 2, 3].map(i => <div key={i} className="h-12 bg-neutral-900/30 animate-pulse rounded-xl border border-neutral-800/50" />)}
                </div>
              ) : (
                globalRules.map((rule, i) => (
                  <button 
                    key={`global-${i}`} 
                    onClick={() => handleSelectRule("global", i)}
                    className={`w-full text-left p-4 rounded-xl border transition-all duration-300 flex gap-3 group ${
                      selectedRule?.type === "global" && selectedRule.index === i 
                      ? 'bg-rose-500/10 border-rose-500/50 shadow-[0_0_15px_rgba(244,63,94,0.1)]' 
                      : 'bg-neutral-900/40 border-neutral-800/50 text-neutral-500 hover:border-rose-500/30 hover:bg-neutral-800/50'
                    }`}
                  >
                    <span className={`font-mono text-[10px] font-bold ${selectedRule?.type === "global" && selectedRule.index === i ? 'text-rose-500' : 'text-neutral-700'}`}>
                      G{i}
                    </span>
                    <p className={`text-[11px] leading-relaxed line-clamp-1 font-medium ${selectedRule?.type === "global" && selectedRule.index === i ? 'text-neutral-200' : 'text-neutral-500 group-hover:text-neutral-400'}`}>
                      {rule}
                    </p>
                  </button>
                ))
              )}
            </div>
          </div>

          {/* Window 2: Circuit Directives (Fixed Scroll Area) */}
          <div className="flex-1 flex flex-col overflow-hidden">
            <div className="p-4 px-6 bg-neutral-900/40 border-b border-neutral-800/50 flex items-center justify-between">
              <label className="text-[9px] font-black text-emerald-500/80 uppercase tracking-[0.2em] flex items-center gap-2">
                 <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full shadow-[0_0_5px_rgba(16,185,129,0.5)]" />
                 Circuit Directives
              </label>
              <span className="material-symbols-outlined text-neutral-600 text-sm">edit_square</span>
            </div>
            <div className="flex-1 overflow-y-auto p-4 space-y-1.5 custom-scrollbar">
              {circuitRules.map((rule, i) => {
                const ruleText = typeof rule === 'object' && rule !== null ? (rule[language] || rule.ko || rule.en || JSON.stringify(rule)) : rule;
                return (
                  <button 
                    key={i} 
                    onClick={() => handleSelectRule("circuit", i)}
                    className={`w-full text-left p-4 rounded-xl border transition-all duration-300 flex gap-4 group ${
                      selectedRule?.type === "circuit" && selectedRule.index === i 
                      ? 'bg-emerald-500/10 border-emerald-500/50 shadow-[0_0_15px_rgba(16,185,129,0.1)]' 
                      : 'bg-neutral-900/50 border-neutral-800 text-neutral-500 hover:border-emerald-500/30 hover:bg-neutral-800/50'
                    }`}
                  >
                    <span className={`font-mono text-xs font-bold ${selectedRule?.type === "circuit" && selectedRule.index === i ? 'text-emerald-500' : 'text-neutral-700'}`}>
                      {String(i + 1).padStart(2, '0')}
                    </span>
                    <p className={`text-xs leading-relaxed line-clamp-1 font-medium ${selectedRule?.type === "circuit" && selectedRule.index === i ? 'text-neutral-100' : 'text-neutral-400 group-hover:text-neutral-300'}`}>
                      {ruleText}
                    </p>
                  </button>
                );
              })}
              {circuitRules.length === 0 && (
                <div className="py-10 text-center opacity-20 border-2 border-dashed border-neutral-800 rounded-2xl mx-4 my-4">
                   <p className="text-[9px] font-bold uppercase tracking-widest">No Circuit Rules</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Right Panel: Shared Editor / Viewer Area */}
        <div className="flex-1 bg-neutral-950/20 flex flex-col p-10 overflow-hidden relative">
          {selectedRule ? (
            <div className="flex-1 flex flex-col space-y-8 max-w-4xl mx-auto w-full animate-in fade-in zoom-in-98 duration-500">
              <div className={`flex justify-between items-start border p-6 rounded-2xl ${
                selectedRule.type === "global" 
                ? 'bg-rose-500/5 border-rose-500/20 shadow-[inset_0_0_20px_rgba(244,63,94,0.02)]' 
                : 'bg-neutral-900/30 border-neutral-800/50 shadow-inner'
              }`}>
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className={`material-symbols-outlined text-sm ${selectedRule.type === "global" ? 'text-rose-500' : 'text-emerald-500'}`}>
                      {selectedRule.type === "global" ? 'lock' : 'edit_square'}
                    </span>
                    <h4 className="text-white font-bold uppercase tracking-tight text-sm">
                      {selectedRule.type === "global" ? 'Global Governance Node' : `Circuit Protocol Node #${selectedRule.index + 1}`}
                    </h4>
                  </div>
                  <p className="text-[10px] text-neutral-500 font-mono uppercase tracking-widest">
                    {selectedRule.type === "global" ? 'Immutable_System_Core' : 'Circuit_Persistence_Module'}
                  </p>
                </div>
                
                {selectedRule.type === "circuit" && (
                  <div className="flex gap-3">
                    <button 
                      onClick={handleSaveRule}
                      disabled={isSaving}
                      className="flex items-center gap-2 px-6 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-black text-[10px] font-black rounded-xl transition-all active:scale-95 shadow-lg shadow-emerald-900/20"
                    >
                      <span className="material-symbols-outlined text-sm">publish</span>
                      {isSaving ? "Syncing..." : "Apply Protocol"}
                    </button>
                    <button 
                      onClick={() => setSelectedRule(null)}
                      className="px-4 py-2.5 bg-neutral-900 hover:bg-neutral-800 text-neutral-500 text-[10px] font-bold rounded-xl transition-all"
                    >
                      Cancel
                    </button>
                  </div>
                )}
                {selectedRule.type === "global" && (
                   <div className="px-4 py-2 bg-rose-500/20 border border-rose-500/30 rounded-xl">
                      <span className="text-rose-500 text-[9px] font-black uppercase tracking-widest flex items-center gap-2">
                        <span className="w-1.5 h-1.5 bg-rose-500 rounded-full animate-pulse" />
                        System Immutable
                      </span>
                   </div>
                )}
              </div>

              <div className="flex-1 flex flex-col space-y-3 overflow-hidden">
                <div className="flex items-center gap-2 px-1 text-neutral-500">
                  <span className="material-symbols-outlined text-lg">description</span>
                  <label className="text-[10px] font-bold uppercase tracking-[0.2em]">Full Directive Content</label>
                </div>
                <textarea 
                  value={editedRule}
                  onChange={(e) => selectedRule.type === "circuit" && setEditedRule(e.target.value)}
                  readOnly={selectedRule.type === "global"}
                  className={`flex-1 w-full border rounded-2xl p-8 text-sm leading-relaxed outline-none transition-all resize-none shadow-inner custom-scrollbar font-medium ${
                    selectedRule.type === "global"
                    ? 'bg-neutral-950 border-rose-500/10 text-neutral-400 cursor-default'
                    : 'bg-neutral-950 border-neutral-800/80 text-emerald-100 focus:border-emerald-500/40 focus:ring-1 focus:ring-emerald-500/20'
                  }`}
                  placeholder="No content available..."
                />
              </div>

              {selectedRule.type === "global" && (
                <div className="p-5 bg-neutral-900/40 border border-neutral-800 rounded-2xl flex gap-4 items-start animate-in slide-in-from-bottom-2 duration-700">
                   <span className="material-symbols-outlined text-rose-500/60 mt-0.5">security</span>
                   <p className="text-[11px] text-neutral-500 leading-relaxed font-medium">
                     이 규약은 시스템 평형 유지를 위한 **글로벌 거버넌스**입니다. 현재 회선 맥락에서는 수동 수정이 불가능하며, 수정을 원하실 경우 전역 설정 권한이 있는 [System Monitor] 유닛을 통해야 합니다.
                   </p>
                </div>
              )}
            </div>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-center space-y-6 opacity-40 animate-in fade-in duration-700">
              <div className="p-12 bg-neutral-900/30 rounded-full border border-neutral-800/30 animate-pulse">
                <span className="material-symbols-outlined text-8xl text-neutral-800">account_tree</span>
              </div>
              <div className="max-w-xs mx-auto">
                <h4 className="text-neutral-500 font-bold uppercase tracking-[0.3em] text-xs">Directive_Selector_Active</h4>
                <p className="text-[10px] text-neutral-700 font-mono mt-3 uppercase tracking-tighter leading-relaxed">
                  Select a core governance or circuit directive to analyze or modify its neural constraints.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};