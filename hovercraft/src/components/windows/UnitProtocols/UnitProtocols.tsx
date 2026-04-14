"use client";

import React, { useState } from "react";
import { I18N } from "@/constants/i18n";
import { SystemStatus } from "@/types/mcp";

interface UnitProtocolsProps {
  systemStatus: SystemStatus;
  language: "ko" | "en";
}

export const UnitProtocols: React.FC<UnitProtocolsProps> = ({ systemStatus, language }) => {
  const [selectedRuleIndex, setSelectedRuleIndex] = useState<number | null>(null);
  const [editedRule, setEditedRule] = useState("");
  const [isSaving, setIsSaving] = useState(false);

  const details = systemStatus.details;
  
  // protocols가 배열인지 혹은 RULES 객체인지 판별
  const getProtocolsArray = (): string[] => {
    if (!details?.protocols) return [];
    if (Array.isArray(details.protocols)) return details.protocols;
    if (typeof details.protocols === 'object' && 'RULES' in details.protocols) {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      return (details.protocols as any).RULES as string[];
    }
    return [];
  };

  const globalProtocols = getProtocolsArray();

  const handleRuleSelect = (index: number) => {
    setSelectedRuleIndex(index);
    const rule = globalProtocols[index];
    const ruleText = typeof rule === 'object' && rule !== null ? (rule[language] || rule.ko || rule.en || JSON.stringify(rule)) : (rule || "");
    setEditedRule(ruleText);
  };

  const handleSaveRule = async () => {
    if (selectedRuleIndex === null) return;
    setIsSaving(true);
    
    const newProtocols = [...globalProtocols];
    newProtocols[selectedRuleIndex] = editedRule;

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
        setSelectedRuleIndex(null);
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
      {/* Header */}
      <div className="px-8 py-5 border-b border-neutral-800 flex justify-between items-center bg-neutral-900/80 backdrop-blur-md z-10 flex-shrink-0">
        <div className="flex items-center gap-4">
          <div className="p-2.5 bg-amber-500/10 rounded-xl border border-amber-500/20 shadow-inner">
            <span className="material-symbols-outlined text-amber-500 text-2xl">rule</span>
          </div>
          <div>
            <h3 className="text-white font-bold tracking-tight uppercase text-sm">{I18N.Protocols[language]} Governance</h3>
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
        {/* Left Panel: Navigation */}
        <div className="w-80 border-r border-neutral-800 flex flex-col bg-neutral-950/40 flex-shrink-0">
          <div className="p-6 flex-1 overflow-y-auto space-y-3 custom-scrollbar">
            <label className="text-[9px] font-bold text-neutral-600 uppercase tracking-[0.2em] px-2 mb-4 block">Active Directive Registry</label>
            {globalProtocols.map((rule: any, i: number) => {
              const ruleText = typeof rule === 'object' && rule !== null ? (rule[language] || rule.ko || rule.en || JSON.stringify(rule)) : rule;
              return (
                <button 
                  key={i} 
                  onClick={() => handleRuleSelect(i)}
                  className={`w-full text-left p-4 rounded-xl border transition-all duration-300 flex gap-4 group ${
                    selectedRuleIndex === i 
                    ? 'bg-amber-500/10 border-amber-500/50 shadow-[0_0_20px_rgba(245,158,11,0.05)]' 
                    : 'bg-neutral-900/50 border-neutral-800 text-neutral-500 hover:border-neutral-600 hover:bg-neutral-800/50'
                  }`}
                >
                  <span className={`font-mono text-xs font-bold ${selectedRuleIndex === i ? 'text-amber-500' : 'text-neutral-700'}`}>
                    {String(i + 1).padStart(2, '0')}
                  </span>
                  <p className={`text-xs leading-relaxed truncate font-medium ${selectedRuleIndex === i ? 'text-neutral-100' : 'text-neutral-400 group-hover:text-neutral-300'}`}>
                    {ruleText}
                  </p>
                </button>
              );
            })}
            {globalProtocols.length === 0 && (
              <div className="h-full flex flex-col items-center justify-center opacity-30 py-20">
                <span className="material-symbols-outlined text-4xl mb-2">inbox</span>
                <p className="text-[10px] uppercase font-bold tracking-widest text-center">No directives found</p>
              </div>
            )}
          </div>
        </div>

        {/* Right Panel: Editor Area */}
        <div className="flex-1 bg-neutral-950/20 flex flex-col p-10 overflow-hidden relative">
          {selectedRuleIndex !== null ? (
            <div className="flex-1 flex flex-col space-y-8 max-w-4xl mx-auto w-full animate-in fade-in zoom-in-98 duration-500">
              <div className="flex justify-between items-start bg-neutral-900/30 border border-neutral-800/50 p-6 rounded-2xl">
                <div>
                  <h4 className="text-white font-bold mb-1 uppercase tracking-tight text-sm">
                    Modifying Protocol Node #{selectedRuleIndex + 1}
                  </h4>
                  <p className="text-[10px] text-neutral-500 font-mono uppercase tracking-widest">
                    Governance_Persistence_Module
                  </p>
                </div>
                <button 
                  onClick={handleSaveRule}
                  disabled={isSaving}
                  className="flex items-center gap-2 px-6 py-2.5 bg-amber-600 hover:bg-amber-500 text-black text-[10px] font-black rounded-xl transition-all active:scale-95 shadow-lg shadow-amber-900/20"
                >
                  <span className="material-symbols-outlined text-sm">publish</span>
                  {isSaving ? "Syncing..." : "Apply Protocol"}
                </button>
              </div>

              <div className="flex-1 flex flex-col space-y-3 overflow-hidden">
                <div className="flex items-center gap-2 px-1">
                  <span className="material-symbols-outlined text-amber-500/60 text-lg">edit_note</span>
                  <label className="text-[10px] font-bold text-neutral-500 uppercase tracking-[0.2em]">Protocol Context Buffer</label>
                </div>
                <textarea 
                  value={editedRule}
                  onChange={(e) => setEditedRule(e.target.value)}
                  className="flex-1 w-full bg-neutral-950 border border-neutral-800/80 rounded-2xl p-8 text-sm font-mono text-amber-200/90 outline-none focus:border-amber-500/40 focus:ring-1 focus:ring-amber-500/20 transition-all resize-none leading-relaxed shadow-inner custom-scrollbar"
                  placeholder="Enter rule content..."
                />
              </div>
            </div>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-center space-y-6 opacity-40 animate-in fade-in duration-700">
              <div className="p-10 bg-neutral-900/30 rounded-full border border-neutral-800/30 animate-pulse">
                <span className="material-symbols-outlined text-7xl text-neutral-800">account_tree</span>
              </div>
              <div className="max-w-xs mx-auto">
                <h4 className="text-neutral-500 font-bold uppercase tracking-[0.3em] text-xs">Protocol_Awaiting_Focus</h4>
                <p className="text-[10px] text-neutral-700 font-mono mt-3 uppercase tracking-tighter leading-relaxed">
                  Select a governance directive from the registry to engage the editing interface.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
