"use client";

import React, { useEffect, useState } from "react";

interface CoreAccessProps {
  requestMcpStatus: () => void;
  systemStatus: any;
  language: "ko" | "en";
}

export const CoreAccess: React.FC<CoreAccessProps> = ({ requestMcpStatus, systemStatus, language }) => {
  const [mounted, setMounted] = useState(false);
  const [availableUnits, setAvailableUnits] = useState<string[]>([]);
  const [selectedUnit, setSelectedUnit] = useState<string | null>(null);
  const [selectedUnitData, setSelectedUnitData] = useState<any>(null);
  const [selectedRuleIndex, setSelectedRuleIndex] = useState<number | null>(null);
  const [editedRuleText, setEditedRuleText] = useState("");
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    setMounted(true);
    fetchAvailableUnits();
  }, []);

  // 유닛이나 언어가 변경되면 정보를 다시 가져옴
  useEffect(() => {
    if (selectedUnit) {
      fetchUnitDetails(selectedUnit);
    }
  }, [selectedUnit, language]);

  const fetchAvailableUnits = async () => {
    try {
      const res = await fetch("/api/mcp/protocols?type=units_list");
      if (res.ok) {
        const data = await res.json();
        setAvailableUnits(data.units);
      }
    } catch (e) {
      console.error("Failed to fetch units list:", e);
    }
  };

  const fetchUnitDetails = async (unitName: string) => {
    try {
      const res = await fetch(`/api/mcp/protocols?type=unit&name=${unitName}`);
      if (res.ok) {
        const data = await res.json();
        setSelectedUnitData(data);
        setSelectedUnit(unitName);
        setSelectedRuleIndex(null);
      } else {
        console.error("Unit details fetch failed:", await res.text());
      }
    } catch (e) {
      console.error("Failed to fetch unit details:", e);
    }
  };

  const handleSaveUnitRule = async () => {
    if (!selectedUnit || !selectedUnitData || selectedRuleIndex === null) return;
    setIsSaving(true);

    const newRules = [...(selectedUnitData.RULES || [])];
    newRules[selectedRuleIndex] = editedRuleText;

    try {
      const res = await fetch("/api/mcp/update", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          target: "unit_protocols",
          name: selectedUnit,
          data: { ...selectedUnitData, RULES: newRules }
        })
      });
      if (res.ok) {
        fetchUnitDetails(selectedUnit);
      }
    } catch (e) {
      alert("Failed to save unit protocol.");
    } finally {
      setIsSaving(false);
    }
  };

  const handleSaveUnitOverview = async (newOverview: string) => {
    if (!selectedUnit || !selectedUnitData) return;
    setIsSaving(true);
    try {
      const res = await fetch("/api/mcp/update", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          target: "unit_protocols",
          name: selectedUnit,
          data: { ...selectedUnitData, OVERVIEW: newOverview }
        })
      });
      if (res.ok) {
        fetchUnitDetails(selectedUnit);
      }
    } catch (e) {
      alert("Failed to update unit overview.");
    } finally {
      setIsSaving(false);
    }
  };

  if (!mounted) return null;

  return (
    <div className="bg-neutral-900 border border-neutral-800 rounded-xl overflow-hidden flex flex-col h-[650px] shadow-sm">
      <div className="px-6 py-4 border-b border-neutral-800 flex justify-between items-center bg-neutral-900/50">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-emerald-500/10 rounded-lg"><span className="material-symbols-outlined text-emerald-500 text-xl">memory</span></div>
          <div>
            <h3 className="text-white font-medium">Technology Unit Explorer</h3>
            <p className="text-[11px] text-neutral-500 font-mono uppercase tracking-wider">Registry_Management_Core</p>
          </div>
        </div>
      </div>

      <div className="flex-1 flex overflow-hidden">
        <div className="w-72 border-r border-neutral-800 bg-neutral-950/20 overflow-y-auto">
          <div className="p-4 space-y-2">
            <label className="text-[10px] font-bold text-neutral-500 uppercase tracking-widest px-2 mb-2 block">Available Units</label>
            {availableUnits.map(unit => (
              <button
                key={unit}
                onClick={() => setSelectedUnit(unit)}
                className={`w-full text-left px-4 py-3 rounded-xl border transition-all flex items-center justify-between group ${
                  selectedUnit === unit ? "bg-emerald-500/10 border-emerald-500/50 text-emerald-400" : "bg-neutral-900/50 border-neutral-800 text-neutral-400 hover:border-neutral-700"
                }`}
              >
                <div className="flex items-center gap-3">
                  <span className={`material-symbols-outlined text-sm ${selectedUnit === unit ? 'text-emerald-500' : 'text-neutral-600'}`}>{selectedUnit === unit ? 'radio_button_checked' : 'radio_button_unchecked'}</span>
                  <span className="text-xs font-bold uppercase font-mono">{unit}</span>
                </div>
                <span className="material-symbols-outlined text-xs opacity-0 group-hover:opacity-100 transition-opacity">chevron_right</span>
              </button>
            ))}
          </div>
        </div>

        <div className="flex-1 bg-neutral-950 flex flex-col overflow-hidden">
          {selectedUnit && selectedUnitData ? (
            <div className="flex-1 flex flex-col p-8 overflow-y-auto space-y-8 w-full">
              <div className="space-y-1">
                <h2 className="text-2xl font-bold text-white uppercase tracking-tight">{selectedUnit}</h2>
                <p className="text-xs text-neutral-500 font-mono">TYPE: OPERATIONAL_UNIT | STATUS: ACTIVE</p>
              </div>

              <section className="space-y-3">
                <label className="text-[10px] font-bold text-neutral-500 uppercase tracking-widest block">Unit Mission Overview</label>
                <div className="bg-neutral-900 border border-neutral-800 rounded-xl p-1 focus-within:border-emerald-500/50 transition-colors">
                  <textarea 
                    value={selectedUnitData.OVERVIEW || ""}
                    onChange={(e) => setSelectedUnitData({ ...selectedUnitData, OVERVIEW: e.target.value })}
                    onBlur={(e) => handleSaveUnitOverview(e.target.value)}
                    className="w-full bg-transparent text-sm text-neutral-300 p-4 outline-none resize-none h-24 leading-relaxed"
                  />
                </div>
              </section>

              <section className="space-y-4">
                <div className="flex justify-between items-center">
                  <label className="text-[10px] font-bold text-neutral-500 uppercase tracking-widest">Protocol Ruleset</label>
                  <button onClick={() => setSelectedUnitData({ ...selectedUnitData, RULES: [...(selectedUnitData.RULES || []), "New rule..."] })} className="text-[10px] text-emerald-400 font-bold uppercase hover:text-emerald-300">+ Add Rule</button>
                </div>
                <div className="space-y-3">
                  {(selectedUnitData.RULES || []).map((rule: any, idx: number) => (
                    <div key={idx} className="group">
                      {selectedRuleIndex === idx ? (
                        <div className="p-4 bg-neutral-900 border border-emerald-500/50 rounded-xl space-y-3">
                          <textarea value={editedRuleText} onChange={(e) => setEditedRuleText(e.target.value)} className="w-full bg-transparent text-xs text-emerald-400 font-mono outline-none resize-none h-20" autoFocus />
                          <div className="flex justify-end gap-2">
                            <button onClick={() => setSelectedRuleIndex(null)} className="px-3 py-1 text-[10px] text-neutral-500 font-bold uppercase">Cancel</button>
                            <button onClick={handleSaveUnitRule} disabled={isSaving} className="px-4 py-1 bg-emerald-600 text-black text-[10px] font-bold rounded uppercase">{isSaving ? "..." : "Update"}</button>
                          </div>
                        </div>
                      ) : (
                        <button onClick={() => { setSelectedRuleIndex(idx); setEditedRuleText(String(rule)); }} className="w-full p-5 bg-neutral-900/50 border border-neutral-800 rounded-xl text-left hover:border-emerald-500/30 transition-all flex gap-4">
                          <span className="text-emerald-500/40 font-mono text-[10px] mt-0.5">{String(idx + 1).padStart(2, '0')}</span>
                          <p className="flex-1 text-xs text-neutral-300 leading-relaxed">{String(rule)}</p>
                          <span className="material-symbols-outlined text-sm text-neutral-700 opacity-0 group-hover:opacity-100">edit</span>
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              </section>
            </div>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center opacity-40"><span className="material-symbols-outlined text-6xl mb-4">memory</span><h4 className="text-white font-bold uppercase tracking-widest">Select a Unit</h4></div>
          )}
        </div>
      </div>
    </div>
  );
};
