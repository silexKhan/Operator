"use client";

import React, { useState, useEffect, useCallback } from "react";
import { I18N } from "@/constants/i18n";
import { I18nText, ProtocolRule, SystemStatus } from "@/types/mcp";

interface MissionSpecsProps {
  systemStatus: SystemStatus;
  language: "ko" | "en";
}

export const MissionSpecs: React.FC<MissionSpecsProps> = ({ systemStatus, language }) => {
  const details = systemStatus.details;
  
  const [isEditing, setIsEditing] = useState(false);
  const [editedObjective, setEditedObjective] = useState("");
  const [editedCriteria, setEditedCriteria] = useState<string[]>([]);
  const [editedDescription, setEditedDescription] = useState("");
  const [isSaving, setIsSaving] = useState(false);
  const [isDirty, setIsDirty] = useState(false);

  const getI18nText = useCallback((value: I18nText | undefined): string => {
    if (!value) return "";
    if (typeof value === "string") return value;
    return value[language] || value.ko || value.en || "";
  }, [language]);

  const getRuleText = useCallback((value: ProtocolRule): string => {
    if (typeof value === "string") return value;
    return value[language] || value.ko || value.en || "";
  }, [language]);

  const syncLocalState = useCallback(() => {
    if (details) {
      setEditedObjective(getI18nText(details.mission?.objective));
      setEditedCriteria(details.mission?.criteria?.map(getRuleText) || []);
      setEditedDescription(getI18nText(details.description));
    }
  }, [details, getI18nText, getRuleText]);

  useEffect(() => {
    syncLocalState();
  }, [syncLocalState]);

  const handleSave = async () => {
    if (!details) return;
    setIsSaving(true);
    try {
      const response = await fetch("/api/mcp/update", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          target: "circuit_overview",
          name: details.name,
          data: {
            ...details,
            description: editedDescription,
            mission: { objective: editedObjective, criteria: editedCriteria }
          }
        })
      });
      if (response.ok) {
        setIsEditing(false);
        setIsDirty(false);
      }
    } catch (e) {
      console.error(e);
      alert("Failed to save mission specs.");
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    syncLocalState();
    setIsEditing(false);
    setIsDirty(false);
  };

  const addCriteria = () => {
    setEditedCriteria([...editedCriteria, ""]);
    setIsDirty(true);
  };

  const removeCriteria = (index: number) => {
    setEditedCriteria(editedCriteria.filter((_, i) => i !== index));
    setIsDirty(true);
  };

  const updateCriteria = (index: number, value: string) => {
    const newCriteria = [...editedCriteria];
    newCriteria[index] = value;
    setEditedCriteria(newCriteria);
    setIsDirty(true);
  };

  if (!details) {
    return (
      <div className="flex-1 flex items-center justify-center p-12 bg-neutral-900 border border-neutral-800 rounded-xl opacity-50">
        <div className="text-center">
          <span className="material-symbols-outlined text-6xl mb-4 text-neutral-700 animate-pulse">radar</span>
          <p className="text-sm font-medium text-neutral-500 uppercase tracking-widest">{I18N.AwaitingSpecs[language]}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-neutral-900 border border-neutral-800 rounded-2xl overflow-hidden flex flex-col h-full shadow-2xl animate-in fade-in slide-in-from-bottom-4 duration-500">
      {/* Header */}
      <div className="px-8 py-5 border-b border-neutral-800 flex justify-between items-center bg-neutral-900/80 backdrop-blur-md z-10 flex-shrink-0">
        <div className="flex items-center gap-4">
          <div className="p-2.5 bg-blue-500/10 rounded-xl border border-blue-500/20 shadow-inner">
            <span className="material-symbols-outlined text-blue-500 text-2xl">assignment</span>
          </div>
          <div>
            <h3 className="text-white font-bold tracking-tight uppercase text-sm">Mission & Strategic Objectives</h3>
            <p className="text-[10px] text-neutral-500 font-mono mt-0.5 tracking-wider uppercase">Circuit_Identifier: {systemStatus.active_circuit}</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          {!isEditing ? (
            <button 
              onClick={() => setIsEditing(true)}
              className="flex items-center gap-2 px-6 py-2 bg-neutral-800 hover:bg-neutral-700 text-white text-[10px] font-black rounded-xl transition-all active:scale-95 border border-neutral-700 uppercase tracking-widest shadow-lg"
            >
              <span className="material-symbols-outlined text-sm">edit</span>
              Modify Mission
            </button>
          ) : (
            <div className="flex items-center gap-3 animate-in fade-in slide-in-from-right-4 duration-300">
              <button 
                onClick={handleSave}
                disabled={!isDirty || isSaving}
                className={`flex items-center gap-2 px-6 py-2 text-black text-[10px] font-black rounded-xl transition-all active:scale-95 uppercase tracking-widest shadow-lg ${
                  isDirty && !isSaving ? "bg-emerald-600 hover:bg-emerald-500 shadow-emerald-900/20" : "bg-neutral-800 text-neutral-600 cursor-not-allowed border border-neutral-700"
                }`}
              >
                <span className="material-symbols-outlined text-sm">save</span>
                {isSaving ? "Syncing..." : "Apply Changes"}
              </button>
              <button 
                onClick={handleCancel}
                className="flex items-center gap-2 px-4 py-2 bg-neutral-900 hover:bg-neutral-800 text-neutral-500 hover:text-white text-[10px] font-bold rounded-xl transition-all uppercase tracking-widest"
              >
                Cancel
              </button>
            </div>
          )}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-10 custom-scrollbar bg-neutral-950/20">
        <div className="max-w-5xl mx-auto space-y-12 animate-in fade-in zoom-in-98 duration-500">
          {/* Objective Section */}
          <section className="bg-neutral-900/40 border border-neutral-800/60 rounded-3xl p-10 space-y-8 shadow-inner relative overflow-hidden group">
            <div className="absolute top-0 right-0 p-8 opacity-5">
              <span className="material-symbols-outlined text-9xl">radar</span>
            </div>
            <div className="relative z-10 space-y-4">
              <div className="flex items-center gap-2 px-1">
                <span className="material-symbols-outlined text-emerald-500/60 text-lg">crisis_alert</span>
                <label className="text-[10px] font-bold text-neutral-500 uppercase tracking-[0.3em]">{I18N.PrimaryObjective[language]}</label>
              </div>
              {isEditing ? (
                <input 
                  value={editedObjective}
                  onChange={(e) => { setEditedObjective(e.target.value); setIsDirty(true); }}
                  placeholder="Enter mission objective..."
                  className="w-full bg-neutral-950 border border-neutral-800 rounded-2xl px-6 py-5 text-lg text-emerald-400 font-bold outline-none focus:border-emerald-500/40 focus:ring-1 focus:ring-emerald-500/20 transition-all shadow-inner"
                />
              ) : (
                <h4 className="text-3xl font-black text-white tracking-tight leading-tight px-1 max-w-4xl">
                  {editedObjective || "AWAITING_MISSION_SPECIFICATION"}
                </h4>
              )}
            </div>
          </section>

          {/* Criteria Section */}
          <section className="space-y-8">
            <div className="flex justify-between items-center px-2">
              <div className="flex items-center gap-2">
                <span className="material-symbols-outlined text-blue-500/60 text-lg">verified</span>
                <label className="text-[10px] font-bold text-neutral-500 uppercase tracking-[0.3em]">{I18N.SuccessCriteria[language]}</label>
              </div>
              {isEditing && (
                <button 
                  onClick={addCriteria}
                  className="flex items-center gap-2 px-4 py-1.5 bg-neutral-900 border border-neutral-800 rounded-xl text-[9px] font-black text-blue-400 uppercase tracking-widest hover:bg-neutral-800 hover:border-blue-500/30 transition-all active:scale-95 shadow-lg shadow-blue-900/10"
                >
                  <span className="material-symbols-outlined text-xs">add</span>
                  Add Criterion
                </button>
              )}
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {editedCriteria.map((c, i) => (
                <div key={i} className="animate-in fade-in slide-in-from-left-4 duration-300" style={{ animationDelay: `${i * 50}ms` }}>
                  {isEditing ? (
                    <div className="flex gap-2 group">
                      <input 
                        value={c}
                        onChange={(e) => updateCriteria(i, e.target.value)}
                        placeholder={`Success Criterion #${i + 1}`}
                        className="flex-1 bg-neutral-950 border border-neutral-800 rounded-2xl px-5 py-4 text-xs text-neutral-300 outline-none focus:border-blue-500/40 transition-all shadow-inner"
                      />
                      <button onClick={() => removeCriteria(i)} className="p-3 bg-neutral-900/50 text-neutral-600 hover:text-red-500 hover:bg-red-500/10 rounded-xl transition-all border border-transparent hover:border-red-500/20 active:scale-90">
                        <span className="material-symbols-outlined text-sm">delete</span>
                      </button>
                    </div>
                  ) : (
                    <div className="flex items-start gap-4 p-6 bg-neutral-900/40 border border-neutral-800/60 rounded-2xl group hover:border-blue-500/30 hover:bg-neutral-900/60 transition-all duration-300 shadow-sm min-h-[80px]">
                      <div className={`mt-0.5 p-1 rounded-full ${c.includes('완료') || c.includes('확인') || c.includes('DONE') ? 'bg-emerald-500/10 text-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.2)]' : 'bg-neutral-800 text-neutral-600'}`}>
                        <span className="material-symbols-outlined text-xs font-bold leading-none">
                          {c.includes('완료') || c.includes('확인') || c.includes('DONE') ? 'check' : 'radio_button_unchecked'}
                        </span>
                      </div>
                      <p className="text-sm text-neutral-400 font-medium group-hover:text-neutral-200 transition-colors leading-relaxed">{c || "UNSPECIFIED_CRITERION"}</p>
                    </div>
                  )}
                </div>
              ))}
              {editedCriteria.length === 0 && (
                <div className="col-span-full py-16 text-center opacity-30 border-2 border-dashed border-neutral-800 rounded-3xl">
                   <span className="material-symbols-outlined text-4xl mb-2">inventory_2</span>
                   <p className="text-[10px] uppercase font-bold tracking-widest">No success criteria defined</p>
                </div>
              )}
            </div>
          </section>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-10 pt-12 border-t border-neutral-800/50 pb-10">
            {/* Architect's Summary Section */}
            <section className="space-y-4">
              <div className="flex items-center gap-2 px-1">
                <span className="material-symbols-outlined text-amber-500/60 text-lg">psychology</span>
                <label className="text-[10px] font-bold text-neutral-500 uppercase tracking-[0.2em]">{I18N.ArchitectSummary[language]}</label>
              </div>
              <div className="bg-neutral-900/30 border border-neutral-800/60 rounded-3xl p-8 shadow-inner group hover:border-amber-500/20 transition-all duration-500 min-h-[200px] flex flex-col">
                {isEditing ? (
                  <textarea 
                    value={editedDescription}
                    onChange={(e) => { setEditedDescription(e.target.value); setIsDirty(true); }}
                    placeholder="Enter detailed architect's summary..."
                    className="flex-1 w-full bg-transparent text-sm text-neutral-300 outline-none resize-none leading-relaxed font-mono custom-scrollbar"
                  />
                ) : (
                  <p className="text-sm text-neutral-500 leading-relaxed italic font-mono">
                    {editedDescription || "No detailed architect summary has been initialized for this node."}
                  </p>
                )}
              </div>
            </section>

            {/* Operational Dependencies Section */}
            <section className="space-y-4">
              <div className="flex items-center gap-2 px-1">
                <span className="material-symbols-outlined text-blue-500/60 text-lg">settings_suggest</span>
                <label className="text-[10px] font-bold text-neutral-500 uppercase tracking-[0.2em]">{I18N.TechDependencies[language]}</label>
              </div>
              <div className="bg-neutral-900/30 border border-neutral-800/60 rounded-3xl p-8 flex flex-wrap gap-3 items-start min-h-[200px]">
                {details.units?.map((u, i: number) => (
                  <div key={i} className="px-4 py-2.5 bg-neutral-950 border border-neutral-800 rounded-xl flex items-center gap-2 group hover:border-blue-500/40 transition-all cursor-default shadow-md">
                    <span className="w-1.5 h-1.5 rounded-full bg-blue-500 group-hover:animate-ping"></span>
                    <span className="text-[11px] text-neutral-400 font-bold font-mono uppercase tracking-tight group-hover:text-blue-400">
                      {typeof u === 'string' ? u : u.name}
                    </span>
                  </div>
                ))}
                {!details.units?.length && (
                  <div className="flex-1 flex flex-col items-center justify-center opacity-20 py-10">
                    <span className="material-symbols-outlined text-4xl mb-2">developer_board_off</span>
                    <p className="text-[9px] uppercase font-bold tracking-widest text-center leading-relaxed">No autonomous units<br/>bound to this circuit</p>
                  </div>
                )}
              </div>
            </section>
          </div>
        </div>
      </div>
    </div>
  );
};
