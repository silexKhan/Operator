"use client";

import React, { useState, useMemo } from "react";
import { CircuitDetails, CircuitOverview, I18nText, ProtocolRule } from "@/types/mcp";

interface CircuitDetailViewProps {
  name: string;
  details: CircuitDetails | null;
  allUnits?: string[];
  language: "ko" | "en";
  onBack: () => void;
  onUpdateOverview: (name: string, description: I18nText) => Promise<void>;
  onUpdateUnits: (name: string, units: string[]) => Promise<void>;
  onUpdateProtocols: (name: string, rules: ProtocolRule[]) => Promise<void>;
}

export const CircuitDetailView: React.FC<CircuitDetailViewProps> = ({ 
  name, details, allUnits = [], language, onBack, onUpdateOverview, onUpdateUnits, onUpdateProtocols 
}) => {
  const [activeModal, setActiveModal] = useState<"overview" | "units" | "protocol_edit" | "protocol_add" | "delete_confirm" | "unit_unlink_confirm" | null>(null);
  const [editDesc, setEditDesc] = useState<string>("");
  const [selectedUnits, setSelectedUnits] = useState<string[]>([]);
  const [targetProtocolIndex, setTargetProtocolIndex] = useState<number | null>(null);
  const [targetUnitName, setTargetUnitName] = useState<string>("");
  const [editProtocolText, setEditProtocolText] = useState<string>("");
  const [isSaving, setIsSaving] = useState(false);

  const overview: Partial<CircuitOverview> = details?.overview || {};
  const currentProtocols: ProtocolRule[] = details?.protocols && !Array.isArray(details.protocols) && 'RULES' in details.protocols ? details.protocols.RULES : (Array.isArray(details?.protocols) ? details.protocols : []);
  
  const currentUnits = useMemo(() => 
    (details?.units || []).map(u => typeof u === 'string' ? u : u.name),
    [details?.units]
  );

  const getI18nText = (data: unknown): string => {
    if (!data) return "";
    if (typeof data === 'string') return data;
    if (typeof data === 'object' && data !== null && !Array.isArray(data)) {
      const map = data as Record<string, unknown>;
      const value = map[language] || map.ko || map.en || map.name;
      return typeof value === "string" ? value : JSON.stringify(data);
    }
    return String(data);
  };

  const handleSaveOverview = async () => {
    setIsSaving(true);
    const newDesc: I18nText = typeof overview.description === 'object' && overview.description !== null ? { ...overview.description, [language]: editDesc } : editDesc;
    await onUpdateOverview(name, newDesc);
    setIsSaving(false);
    setActiveModal(null);
  };

  const handleSaveUnits = async () => {
    setIsSaving(true);
    await onUpdateUnits(name, selectedUnits);
    setIsSaving(false);
    setActiveModal(null);
  };

  const handleAddProtocol = async () => {
    setIsSaving(true);
    const newRules = [...currentProtocols, { [language]: editProtocolText }];
    await onUpdateProtocols(name, newRules);
    setIsSaving(false);
    setActiveModal(null);
    setEditProtocolText("");
  };

  const handleEditProtocol = async () => {
    if (targetProtocolIndex === null) return;
    setIsSaving(true);
    const newRules = [...currentProtocols];
    const originalRule = newRules[targetProtocolIndex];
    if (typeof originalRule === 'object') {
      newRules[targetProtocolIndex] = { ...originalRule, [language]: editProtocolText };
    } else {
      newRules[targetProtocolIndex] = editProtocolText;
    }
    await onUpdateProtocols(name, newRules);
    setIsSaving(false);
    setActiveModal(null);
  };

  const handleDeleteProtocol = async () => {
    if (targetProtocolIndex === null) return;
    setIsSaving(true);
    const newRules = currentProtocols.filter((_, i) => i !== targetProtocolIndex);
    await onUpdateProtocols(name, newRules);
    setIsSaving(false);
    setActiveModal(null);
  };

  const handleUnlinkUnit = async () => {
    if (!targetUnitName) return;
    setIsSaving(true);
    const newUnits = currentUnits.filter(u => u !== targetUnitName);
    await onUpdateUnits(name, newUnits);
    setIsSaving(false);
    setActiveModal(null);
  };

  const handleSubmit = () => {
    switch (activeModal) {
      case "overview": return handleSaveOverview();
      case "units": return handleSaveUnits();
      case "protocol_add": return handleAddProtocol();
      case "protocol_edit": return handleEditProtocol();
      case "delete_confirm": return handleDeleteProtocol();
      case "unit_unlink_confirm": return handleUnlinkUnit();
      default: return null;
    }
  };

  return (
    <div className="h-full flex flex-col animate-in fade-in slide-in-from-bottom-4 duration-500 font-sans pb-20 relative">
      {/* Header Area */}
      <div className="flex items-center justify-between mb-10 flex-shrink-0 px-2">
        <div className="flex items-center gap-6">
          <button onClick={onBack} className="p-3.5 bg-neutral-900 border border-neutral-800 hover:bg-neutral-800 text-neutral-400 hover:text-white rounded-2xl transition-all shadow-xl group">
            <span className="material-symbols-outlined group-hover:-translate-x-1 transition-transform">arrow_back</span>
          </button>
          <div>
            <div className="flex items-center gap-3 mb-1">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse shadow-[0_0_10px_rgba(16,185,129,0.5)]" />
              <h3 className="text-3xl font-black text-white uppercase tracking-tighter leading-none">{getI18nText(name)}</h3>
            </div>
            <p className="text-[10px] text-neutral-500 font-mono uppercase tracking-[0.4em] font-bold opacity-60">Circuit_Governance_Center</p>
          </div>
        </div>
        <div className="px-6 py-3 bg-neutral-900/50 border border-neutral-800 rounded-2xl text-center shadow-inner">
           <div className="text-[9px] font-bold text-neutral-600 uppercase tracking-widest mb-1">Integrity</div>
           <div className="text-xs font-black text-emerald-500 font-mono uppercase tracking-tighter">OPTIMAL</div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto custom-scrollbar space-y-12 pr-4">
        {/* Overview Section - Full Width */}
        <section className="space-y-4">
          <div className="flex items-center justify-between px-1">
            <label className="text-[10px] font-black text-neutral-500 uppercase tracking-[0.3em]">Node Strategic Overview</label>
            <button onClick={() => { setEditDesc(getI18nText(overview.description)); setActiveModal("overview"); }} className="flex items-center gap-1.5 px-3 py-1 bg-neutral-900 border border-neutral-800 rounded-lg text-[9px] font-bold text-neutral-500 hover:text-emerald-500 transition-all">
              <span className="material-symbols-outlined text-xs">edit_square</span> EDIT_DESCRIPTION
            </button>
          </div>
          <div className="p-10 bg-neutral-900/30 border border-neutral-800 rounded-[2.5rem] shadow-inner relative group">
             <p className="text-sm text-neutral-300 leading-relaxed font-medium max-w-4xl">{getI18nText(overview.description) || "No strategic overview defined."}</p>
             <div className="absolute top-10 right-10 opacity-5">
                <span className="material-symbols-outlined text-7xl">info</span>
             </div>
          </div>
        </section>

        {/* Protocols Section */}
        <section className="space-y-6">
           <div className="flex items-center justify-between px-1">
              <label className="text-[10px] font-black text-neutral-500 uppercase tracking-[0.3em]">Circuit Specific Protocols</label>
              <button onClick={() => { setEditProtocolText(""); setActiveModal("protocol_add"); }} className="flex items-center gap-1.5 px-4 py-1.5 bg-emerald-600 text-black rounded-xl text-[9px] font-black tracking-widest hover:bg-emerald-500 transition-all active:scale-95 shadow-lg">
                <span className="material-symbols-outlined text-xs font-black">add_circle</span> ADD_NODE
              </button>
           </div>
           <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {currentProtocols.map((rule, i) => (
                <div key={i} className="group p-6 bg-neutral-900/40 border border-neutral-800 rounded-2xl hover:border-emerald-500/30 transition-all flex justify-between gap-5 relative overflow-hidden">
                   <div className="flex gap-5 flex-1">
                      <span className="font-mono text-[10px] font-black text-neutral-700 mt-1">P{String(i+1).padStart(2, '0')}</span>
                      <p className="text-xs text-neutral-400 leading-relaxed font-medium group-hover:text-neutral-200 transition-colors">{getI18nText(rule)}</p>
                   </div>
                   <div className="flex flex-col gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button onClick={() => { setTargetProtocolIndex(i); setEditProtocolText(getI18nText(rule)); setActiveModal("protocol_edit"); }} className="p-2 bg-neutral-800 rounded-lg text-neutral-400 hover:text-emerald-500 transition-colors"><span className="material-symbols-outlined text-sm">edit</span></button>
                      <button onClick={() => { setTargetProtocolIndex(i); setActiveModal("delete_confirm"); }} className="p-2 bg-neutral-800 rounded-lg text-neutral-400 hover:text-rose-500 transition-colors"><span className="material-symbols-outlined text-sm">delete</span></button>
                   </div>
                </div>
              ))}
           </div>
        </section>

        {/* Units Section */}
        <section className="space-y-6 pb-20">
           <div className="flex items-center justify-between px-1">
              <label className="text-[10px] font-black text-neutral-500 uppercase tracking-[0.3em]">Neural Sub-Units (Imported)</label>
              <button onClick={() => { setSelectedUnits(currentUnits); setActiveModal("units"); }} className="flex items-center gap-1.5 px-3 py-1 bg-neutral-900 border border-neutral-800 rounded-lg text-[9px] font-bold text-neutral-500 hover:text-emerald-500 transition-all">
                <span className="material-symbols-outlined text-xs">link</span> UPDATE_LINKAGE
              </button>
           </div>
           <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
              {currentUnits.map((unit, i) => (
                <div key={i} className="p-5 bg-neutral-900/60 border border-neutral-800 rounded-2xl text-center shadow-lg group relative overflow-hidden">
                   <button 
                     onClick={() => { setTargetUnitName(unit); setActiveModal("unit_unlink_confirm"); }}
                     className="absolute top-2 right-2 p-1.5 bg-rose-500/10 text-rose-500/40 hover:text-rose-500 hover:bg-rose-500/20 rounded-lg opacity-0 group-hover:opacity-100 transition-all z-10"
                   >
                     <span className="material-symbols-outlined text-xs">link_off</span>
                   </button>
                   <span className="material-symbols-outlined text-2xl text-neutral-700 group-hover:text-emerald-500 transition-colors mb-3">settings_suggest</span>
                   <div className="text-[10px] font-black text-neutral-400 uppercase tracking-tighter truncate font-mono">{unit}</div>
                </div>
              ))}
           </div>
        </section>
      </div>

      {/* Modals */}
      {activeModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md animate-in fade-in duration-300 p-8">
          <div className="bg-neutral-900 border border-neutral-800 rounded-[2.5rem] w-full max-w-2xl shadow-[0_0_100px_rgba(0,0,0,0.5)] overflow-hidden flex flex-col max-h-[85vh]">
            <div className="px-10 py-8 border-b border-neutral-800 flex justify-between items-center bg-neutral-900/50">
              <div className="flex items-center gap-5">
                <div className={`p-3 rounded-2xl border ${activeModal.includes('confirm') ? 'bg-rose-500/10 text-rose-500 border-rose-500/20' : 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20'}`}>
                  <span className="material-symbols-outlined text-2xl">{activeModal.includes('protocol') ? 'rule' : activeModal.includes('unit') ? 'link_off' : 'info'}</span>
                </div>
                <div>
                  <h3 className="text-white font-black uppercase text-sm tracking-tight">{activeModal.replace(/_/g, ' ')}</h3>
                  <p className="text-[10px] text-neutral-500 font-mono mt-1 uppercase font-bold tracking-widest">{name}</p>
                </div>
              </div>
              <button onClick={() => setActiveModal(null)} className="text-neutral-600 hover:text-white"><span className="material-symbols-outlined text-3xl font-light">close</span></button>
            </div>

            <div className="flex-1 p-10 overflow-y-auto custom-scrollbar">
              {activeModal === "overview" && (
                <textarea value={editDesc} onChange={(e) => setEditDesc(e.target.value)} className="w-full bg-neutral-950 border border-neutral-800 rounded-3xl p-8 text-sm font-mono text-emerald-400 h-60 resize-none outline-none focus:ring-1 focus:ring-emerald-500/20 shadow-inner" />
              )}
              {activeModal === "units" && (
                <div className="grid grid-cols-2 gap-3">
                  {allUnits.map(u => (
                    <button key={u} onClick={() => setSelectedUnits(prev => prev.includes(u) ? prev.filter(x => x !== u) : [...prev, u])} className={`p-5 rounded-2xl border text-left flex items-center gap-4 transition-all ${selectedUnits.includes(u) ? "bg-emerald-500/10 border-emerald-500/40 text-emerald-400" : "bg-neutral-950 border-neutral-800 text-neutral-500"}`}>
                      <span className="material-symbols-outlined text-sm">{selectedUnits.includes(u) ? "check_circle" : "radio_button_unchecked"}</span>
                      <span className="text-[10px] font-black uppercase font-mono">{u}</span>
                    </button>
                  ))}
                </div>
              )}
              {activeModal.includes('protocol') && activeModal !== 'delete_confirm' && (
                <textarea value={editProtocolText} onChange={(e) => setEditProtocolText(e.target.value)} className="w-full bg-neutral-950 border border-neutral-800 rounded-3xl p-8 text-sm font-mono text-emerald-400 h-40 resize-none outline-none focus:ring-1 focus:ring-emerald-500/20 shadow-inner" placeholder="Enter protocol text..." />
              )}
              {activeModal === "delete_confirm" && (
                <div className="text-center py-10">
                   <p className="text-neutral-400 text-sm leading-relaxed mb-6 font-medium">이 규약 노드를 회선에서 영구적으로 제외하시겠습니까?</p>
                   <div className="p-6 bg-rose-500/5 border border-rose-500/20 rounded-2xl text-rose-500/60 font-mono text-[10px]">{currentProtocols[targetProtocolIndex!] ? getI18nText(currentProtocols[targetProtocolIndex!]) : ""}</div>
                </div>
              )}
              {activeModal === "unit_unlink_confirm" && (
                <div className="text-center py-10">
                   <p className="text-neutral-400 text-sm leading-relaxed mb-6 font-medium">유닛 [ {targetUnitName} ]의 링크를 해제하시겠습니까?</p>
                   <div className="p-4 bg-rose-500/10 border border-rose-500/20 rounded-xl inline-block text-rose-500 font-black text-xs tracking-widest uppercase px-8 py-3">Link_Termination_Warning</div>
                </div>
              )}
            </div>

            <div className="px-10 py-8 bg-neutral-900/80 border-t border-neutral-800 flex justify-end gap-6">
              <button onClick={() => setActiveModal(null)} className="text-[10px] font-black text-neutral-600 hover:text-white uppercase tracking-widest">Abort</button>
              <button onClick={handleSubmit} disabled={isSaving} className={`px-10 py-3.5 rounded-2xl text-[10px] font-black uppercase tracking-widest active:scale-95 transition-all ${activeModal.includes('confirm') ? 'bg-rose-600 hover:bg-rose-500 text-white' : 'bg-emerald-600 hover:bg-emerald-500 text-black'}`}>
                {isSaving ? "Syncing..." : activeModal.includes('confirm') ? "Confirm_Action" : "Apply_Commit"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
