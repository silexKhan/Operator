"use client";

import React, { useState, useEffect } from "react";

interface UnitProtocolsProps {
  systemStatus: any;
}

export const UnitProtocols: React.FC<UnitProtocolsProps> = ({ systemStatus }) => {
  const [selectedRuleIndex, setSelectedRuleIndex] = useState<number | null>(null);
  const [editedRule, setEditedRule] = useState("");
  const [isSaving, setIsSaving] = useState(false);

  const details = systemStatus?.details;
  const globalProtocols = details?.protocols || [];

  const handleRuleSelect = (index: number) => {
    setSelectedRuleIndex(index);
    setEditedRule(globalProtocols[index] || "");
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
        // 성공 시 상태 유지 또는 알림
      }
    } catch (e) {
      alert("Failed to save protocol directive.");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="bg-neutral-900 border border-neutral-800 rounded-xl overflow-hidden flex flex-col h-[600px] shadow-sm">
      {/* Header */}
      <div className="px-6 py-4 border-b border-neutral-800 flex justify-between items-center bg-neutral-900/50">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-amber-500/10 rounded-lg">
            <span className="material-symbols-outlined text-amber-500 text-xl">rule</span>
          </div>
          <div>
            <h3 className="text-white font-medium">Protocol Directives</h3>
            <p className="text-[11px] text-neutral-500 font-mono uppercase tracking-wider">{systemStatus.active_circuit}_Governance_Engine</p>
          </div>
        </div>
      </div>

      <div className="flex-1 flex overflow-hidden">
        {/* Left Panel: Navigation */}
        <div className="w-80 border-r border-neutral-800 flex flex-col bg-neutral-950/20">
          <div className="p-4 flex-1 overflow-y-auto space-y-6">
            <section>
              <label className="text-[10px] font-bold text-neutral-500 uppercase tracking-widest mb-3 block">Global Directives</label>
              <div className="space-y-2">
                {globalProtocols.map((rule: string, i: number) => (
                  <button 
                    key={i} 
                    onClick={() => handleRuleSelect(i)}
                    className={`w-full text-left p-3 rounded-lg border transition-all flex gap-3 group ${
                      selectedRuleIndex === i 
                      ? 'bg-amber-500/10 border-amber-500/50' 
                      : 'bg-neutral-900 border-neutral-800 hover:border-neutral-700'
                    }`}
                  >
                    <span className={`font-mono text-xs ${selectedRuleIndex === i ? 'text-amber-500' : 'text-neutral-600'}`}>
                      {String(i + 1).padStart(2, '0')}
                    </span>
                    <p className={`text-xs leading-relaxed truncate ${selectedRuleIndex === i ? 'text-neutral-100' : 'text-neutral-400 group-hover:text-neutral-200'}`}>
                      {rule}
                    </p>
                  </button>
                ))}
              </div>
            </section>
          </div>
        </div>

        {/* Right Panel: Editor Area */}
        <div className="flex-1 bg-neutral-950 flex flex-col p-8 overflow-hidden">
          {selectedRuleIndex !== null ? (
            <div className="flex-1 flex flex-col space-y-6 max-w-3xl">
              <div className="flex justify-between items-start">
                <div>
                  <h4 className="text-white font-medium mb-1">
                    Editing Directive #{selectedRuleIndex + 1}
                  </h4>
                  <p className="text-xs text-neutral-500">
                    Modify the specific behavioral protocol for this circuit.
                  </p>
                </div>
                <button 
                  onClick={handleSaveRule}
                  disabled={isSaving}
                  className="flex items-center gap-2 px-4 py-2 bg-amber-600 hover:bg-amber-500 text-white text-xs rounded-lg transition-colors font-medium shadow-lg shadow-amber-900/20"
                >
                  <span className="material-symbols-outlined text-sm">publish</span>
                  {isSaving ? "Syncing..." : "Update Directive"}
                </button>
              </div>

              <div className="flex-1 flex flex-col space-y-2 overflow-hidden">
                <label className="text-[10px] font-bold text-neutral-500 uppercase tracking-widest">Protocol Content</label>
                <textarea 
                  value={editedRule}
                  onChange={(e) => setEditedRule(e.target.value)}
                  className="flex-1 w-full bg-neutral-900 border border-neutral-800 rounded-xl p-6 text-sm font-mono text-amber-200/80 outline-none focus:border-amber-500/50 transition-colors resize-none leading-relaxed"
                  placeholder="Enter rule content..."
                />
              </div>
            </div>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-center p-12 opacity-50">
              <span className="material-symbols-outlined text-5xl text-neutral-700 mb-4">account_tree</span>
              <h4 className="text-white font-medium mb-2">Select a Directive</h4>
              <p className="text-sm text-neutral-500 max-w-xs">
                Choose a protocol from the left panel to view or edit its specific operational requirements.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
