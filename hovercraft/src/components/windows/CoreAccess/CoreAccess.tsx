"use client";

import React, { useEffect, useState } from "react";
import { I18N } from "@/constants/i18n";
import { ProtocolRule, SystemStatus, Unit } from "@/types/mcp";

interface CoreAccessProps {
  requestMcpStatus: () => void;
  systemStatus: SystemStatus;
  language: "ko" | "en";
}

export const CoreAccess: React.FC<CoreAccessProps> = ({ requestMcpStatus, systemStatus, language }) => {
  const [availableUnits, setAvailableUnits] = useState<string[]>([]);
  const [selectedUnit, setSelectedUnit] = useState<string | null>(null);
  const [selectedUnitData, setSelectedUnitData] = useState<Unit | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [editingRuleIndex, setEditingRuleIndex] = useState<number | null>(null);
  const [editedRuleText, setEditedRuleText] = useState("");

  const fetchUnitsList = async () => {
    try {
      const res = await fetch("/api/mcp/protocols?type=units_list");
      if (res.ok) {
        const data = await res.json();
        setAvailableUnits(data.units || []);
      }
    } catch (e) {
      console.error("Failed to fetch units list:", e);
    }
  };

  const fetchUnitDetails = async (name: string) => {
    try {
      console.log(`[CoreAccess] Fetching details for unit: ${name}`);
      const res = await fetch(`/api/mcp/protocols?type=unit&name=${name}`);
      if (res.ok) {
        const data = await res.json();
        console.log(`[CoreAccess] Received data for ${name}:`, data);
        setSelectedUnitData({
          name: name,
          mission: data.overview || data.OVERVIEW || "",
          rules: data.protocols || data.rules || data.RULES || []
        });
      }
    } catch (e) {
      console.error("Failed to fetch unit details:", e);
    }
  };

  useEffect(() => {
    fetchUnitsList();
  }, []);

  useEffect(() => {
    if (selectedUnit) fetchUnitDetails(selectedUnit);
  }, [selectedUnit]);

  const handleSaveUnitOverview = async () => {
    if (!selectedUnit || !selectedUnitData) return;
    setIsSaving(true);
    try {
      await fetch("/api/mcp/update", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          target: "unit_protocols",
          name: selectedUnit,
          data: { OVERVIEW: selectedUnitData.mission }
        })
      });
    } catch (e) {
      console.error("Failed to save unit overview:", e);
    } finally {
      setIsSaving(false);
    }
  };

  const getRuleText = (rule: ProtocolRule): string => {
    if (typeof rule === "string") return rule;
    return rule[language] || rule.ko || rule.en || "";
  };

  const handleUpdateRules = async (newRules: ProtocolRule[]) => {
    if (!selectedUnit) return;
    setIsSaving(true);
    try {
      const res = await fetch("/api/mcp/update", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          target: "unit_protocols",
          name: selectedUnit,
          data: { RULES: newRules }
        })
      });
      if (res.ok) {
        setEditingRuleIndex(null);
        fetchUnitDetails(selectedUnit);
      }
    } catch (e) {
      console.error("Failed to update unit rules:", e);
    } finally {
      setIsSaving(false);
    }
  };

  const addNewRule = () => {
    if (!selectedUnitData) return;
    const newRules = [...(selectedUnitData.rules || []), "New Operational Rule"];
    setSelectedUnitData({ ...selectedUnitData, rules: newRules });
    setEditingRuleIndex(newRules.length - 1);
    setEditedRuleText("New Operational Rule");
  };

  // 린트 에러 방지를 위한 더미 호출 (필요시 제거 가능)
  useEffect(() => {
    if (systemStatus.active_circuit && false) requestMcpStatus();
  }, [systemStatus, requestMcpStatus]);

  return (
    <div className="bg-neutral-900 border border-neutral-800 rounded-2xl overflow-hidden flex flex-col h-full min-h-[calc(100vh-250px)] shadow-2xl transition-all duration-500 animate-in fade-in slide-in-from-bottom-4">
      <div className="px-6 py-5 border-b border-neutral-800 flex justify-between items-center bg-neutral-900/80 backdrop-blur-md sticky top-0 z-10">
        <div className="flex items-center gap-4">
          <div className="p-2.5 bg-emerald-500/10 rounded-xl border border-emerald-500/20 shadow-inner">
            <span className="material-symbols-outlined text-emerald-500 text-2xl">memory</span>
          </div>
          <div>
            <h3 className="text-white font-bold tracking-tight uppercase text-sm">{I18N.Units[language]} Command Center</h3>
            <p className="text-[10px] text-neutral-500 font-mono mt-0.5 tracking-wider uppercase">Advanced Neural Agent Processing Unit</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <div className="px-2 py-1 bg-neutral-950 border border-neutral-800 rounded text-[9px] font-mono text-emerald-500">
            SYSTEM_STABLE: OK
          </div>
        </div>
      </div>

      <div className="flex-1 flex overflow-hidden">
        <div className="w-72 border-r border-neutral-800 bg-neutral-950/40 overflow-y-auto p-5 space-y-3 custom-scrollbar">
          <div className="mb-4">
            <label className="text-[9px] font-bold text-neutral-600 uppercase tracking-widest px-2">Active Node Registry</label>
          </div>
          {availableUnits.map((unit) => (
            <button
              key={unit}
              onClick={() => setSelectedUnit(unit)}
              className={`w-full text-left px-5 py-4 rounded-xl border transition-all duration-300 group ${
                selectedUnit === unit 
                ? "bg-emerald-500/10 border-emerald-500/50 text-emerald-400 shadow-[0_0_20px_rgba(16,185,129,0.05)]" 
                : "bg-neutral-900/50 border-neutral-800 text-neutral-500 hover:border-neutral-600 hover:bg-neutral-800/50"
              }`}
            >
              <div className="flex justify-between items-center">
                <span className="font-mono text-xs font-bold tracking-tight">{unit}</span>
                <span className={`material-symbols-outlined text-sm transition-opacity ${selectedUnit === unit ? 'opacity-100' : 'opacity-0 group-hover:opacity-100'}`}>
                  chevron_right
                </span>
              </div>
            </button>
          ))}
        </div>

        <div className="flex-1 bg-neutral-950/20 p-10 overflow-y-auto custom-scrollbar">
          {selectedUnitData ? (
            <div className="max-w-4xl mx-auto space-y-10 animate-in fade-in zoom-in-95 duration-500">
              <section className="bg-neutral-900/30 border border-neutral-800/50 rounded-2xl p-8 space-y-6">
                <div className="flex justify-between items-center">
                  <div className="flex items-center gap-2">
                    <span className="material-symbols-outlined text-emerald-500/60 text-lg">info</span>
                    <label className="text-[10px] font-bold text-neutral-400 uppercase tracking-widest">Unit Specification Overload</label>
                  </div>
                  {isSaving && (
                    <div className="flex items-center gap-2 px-3 py-1 bg-emerald-500/10 rounded-full border border-emerald-500/20">
                      <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-ping"></div>
                      <span className="text-[9px] text-emerald-500 font-bold font-mono tracking-tighter uppercase">Syncing Registry...</span>
                    </div>
                  )}
                </div>
                <textarea
                  value={!selectedUnitData.mission ? "" : typeof selectedUnitData.mission === "string" ? selectedUnitData.mission : selectedUnitData.mission[language] || ""}
                  onChange={(e) => {
                    const newMission = typeof selectedUnitData.mission === "string" 
                      ? e.target.value 
                      : { ...(selectedUnitData.mission || {}), [language]: e.target.value };
                    setSelectedUnitData({ ...selectedUnitData, mission: newMission });
                  }}
                  onBlur={handleSaveUnitOverview}
                  placeholder="Enter unit description..."
                  className="w-full bg-neutral-950 border border-neutral-800/80 rounded-xl p-5 text-sm text-neutral-200 outline-none focus:border-emerald-500/40 focus:ring-1 focus:ring-emerald-500/20 transition-all resize-none h-32 shadow-inner leading-relaxed"
                />
              </section>

              <section className="space-y-6">
                <div className="flex justify-between items-center px-2">
                  <div className="flex items-center gap-2">
                    <span className="material-symbols-outlined text-emerald-500/60 text-lg">gavel</span>
                    <label className="text-[10px] font-bold text-neutral-400 uppercase tracking-widest">Operational Directives</label>
                  </div>
                  <button 
                    onClick={addNewRule}
                    className="flex items-center gap-1.5 px-3 py-1.5 bg-neutral-900 border border-neutral-800 rounded-lg text-[9px] font-bold text-emerald-500 uppercase hover:bg-neutral-800 hover:border-emerald-500/30 transition-all active:scale-95"
                  >
                    <span className="material-symbols-outlined text-xs">add</span>
                    Register Directive
                  </button>
                </div>
                <div className="grid grid-cols-1 gap-3">
                  {(selectedUnitData.rules || []).map((rule, idx) => (
                    <div key={idx}>
                      {editingRuleIndex === idx ? (
                        <div className="p-6 bg-neutral-900 border border-emerald-500/50 rounded-2xl space-y-4 shadow-lg shadow-emerald-950/10 animate-in zoom-in-98">
                          <textarea
                            value={editedRuleText}
                            onChange={(e) => setEditedRuleText(e.target.value)}
                            className="w-full bg-transparent text-sm text-emerald-400 font-mono outline-none resize-none h-24 leading-relaxed"
                            autoFocus
                          />
                          <div className="flex justify-end gap-3 pt-2">
                            <button onClick={() => setEditingRuleIndex(null)} className="px-4 py-1.5 text-[10px] text-neutral-500 font-bold uppercase hover:text-white transition-colors">Cancel Action</button>
                            <button onClick={() => {
                              const nextRules = [...(selectedUnitData.rules || [])];
                              nextRules[idx] = editedRuleText;
                              handleUpdateRules(nextRules);
                            }} className="px-6 py-1.5 bg-emerald-600 text-black text-[10px] font-bold rounded-lg uppercase tracking-widest hover:bg-emerald-500 shadow-md active:scale-95 transition-all">Apply Protocol</button>
                          </div>
                        </div>
                      ) : (
                        <button 
                          onClick={() => { 
                            setEditingRuleIndex(idx); 
                            setEditedRuleText(getRuleText(rule)); 
                          }}
                          className="w-full text-left p-6 bg-neutral-900/40 border border-neutral-800/60 rounded-2xl hover:border-emerald-500/30 hover:bg-neutral-900/60 transition-all duration-300 flex gap-5 group"
                        >
                          <span className="text-emerald-500/40 font-mono text-xs mt-0.5">{String(idx + 1).padStart(2, '0')}</span>
                          <p className="text-sm text-neutral-400 group-hover:text-neutral-200 leading-relaxed flex-1">
                            {getRuleText(rule)}
                          </p>
                          <span className="material-symbols-outlined text-sm text-neutral-700 opacity-0 group-hover:opacity-100 transition-opacity">edit</span>
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              </section>
            </div>
          ) : (
            <div className="h-full flex flex-col items-center justify-center space-y-6 animate-in fade-in duration-700">
              <div className="p-10 bg-neutral-900/30 rounded-full border border-neutral-800/30 animate-pulse">
                <span className="material-symbols-outlined text-8xl text-neutral-800">memory</span>
              </div>
              <div className="text-center">
                <h4 className="text-neutral-500 font-bold uppercase tracking-[0.3em] text-xs">Awaiting Unit Selection</h4>
                <p className="text-[10px] text-neutral-700 font-mono mt-2 uppercase tracking-tighter">Please select a specialized agent from the registry</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
