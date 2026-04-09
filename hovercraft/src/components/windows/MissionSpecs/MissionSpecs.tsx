"use client";

import React, { useState, useEffect } from "react";

interface MissionSpecsProps {
  systemStatus: any;
}

export const MissionSpecs: React.FC<MissionSpecsProps> = ({ systemStatus }) => {
  const details = systemStatus.details;
  
  const [isEditing, setIsEditing] = useState(false);
  const [editedObjective, setEditedObjective] = useState("");
  const [editedCriteria, setEditedCriteria] = useState<string[]>([]);
  const [editedDescription, setEditedDescription] = useState("");
  const [isDirty, setIsDirty] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    if (details) {
      setEditedObjective(details.mission?.objective || "");
      setEditedCriteria(details.mission?.criteria || []);
      setEditedDescription(details.description || "");
    }
  }, [details, isEditing]);

  const handleSave = async () => {
    setIsSaving(true);
    try {
      const response = await fetch("/api/mcp/update", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          target: "circuit_overview",
          name: systemStatus.active_circuit,
          data: {
            name: systemStatus.active_circuit,
            description: editedDescription,
            units: details?.units || [],
            mission: {
              objective: editedObjective,
              criteria: editedCriteria
            }
          }
        })
      });

      if (response.ok) {
        setIsEditing(false);
        setIsDirty(false);
      } else {
        alert("Failed to save mission specs.");
      }
    } catch (error) {
      console.error("Error saving mission specs:", error);
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    setIsEditing(false);
    setIsDirty(false);
  };

  const addCriteria = () => {
    setEditedCriteria([...editedCriteria, ""]);
    setIsDirty(true);
  };

  const updateCriteria = (index: number, value: string) => {
    const newCriteria = [...editedCriteria];
    newCriteria[index] = value;
    setEditedCriteria(newCriteria);
    setIsDirty(true);
  };

  const removeCriteria = (index: number) => {
    setEditedCriteria(editedCriteria.filter((_, i) => i !== index));
    setIsDirty(true);
  };

  if (!details) {
    return (
      <div className="bg-neutral-900 border border-neutral-800 rounded-xl p-12 flex flex-col items-center justify-center text-neutral-500">
        <span className="material-symbols-outlined text-4xl mb-4 animate-pulse">hourglass_empty</span>
        <p className="text-sm">Awaiting detailed mission specifications...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Main Header Card */}
      <div className="bg-neutral-900 border border-neutral-800 rounded-xl overflow-hidden shadow-sm">
        <div className="px-6 py-4 border-b border-neutral-800 flex justify-between items-center bg-neutral-900/50">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-500/10 rounded-lg">
              <span className="material-symbols-outlined text-blue-500 text-xl">assignment</span>
            </div>
            <div>
              <h3 className="text-white font-medium">Mission & Objectives</h3>
              <p className="text-[11px] text-neutral-500 font-mono uppercase tracking-wider">Circuit: {systemStatus.active_circuit}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {!isEditing ? (
              <button 
                onClick={() => setIsEditing(true)}
                className="flex items-center gap-2 px-3 py-1.5 bg-neutral-800 hover:bg-neutral-700 text-neutral-200 text-xs rounded-md transition-colors"
              >
                <span className="material-symbols-outlined text-sm">edit</span>
                Modify Mission
              </button>
            ) : (
              <div className="flex items-center gap-2">
                <button 
                  onClick={handleSave}
                  disabled={!isDirty || isSaving}
                  className={`flex items-center gap-2 px-3 py-1.5 text-white text-xs rounded-md transition-colors font-medium ${
                    isDirty && !isSaving ? "bg-emerald-600 hover:bg-emerald-500" : "bg-neutral-800 text-neutral-500 cursor-not-allowed"
                  }`}
                >
                  <span className="material-symbols-outlined text-sm">save</span>
                  {isSaving ? "Syncing..." : "Save Changes"}
                </button>
                <button 
                  onClick={handleCancel}
                  className="flex items-center gap-2 px-3 py-1.5 bg-neutral-800 hover:bg-neutral-700 text-neutral-400 text-xs rounded-md transition-colors"
                >
                  Cancel
                </button>
              </div>
            )}
          </div>
        </div>

        <div className="p-8">
          <div className="max-w-3xl space-y-8">
            {/* Objective Section */}
            <section>
              <label className="text-[10px] font-bold text-neutral-500 uppercase tracking-widest mb-3 block">Primary Objective</label>
              {isEditing ? (
                <input 
                  value={editedObjective}
                  onChange={(e) => { setEditedObjective(e.target.value); setIsDirty(true); }}
                  placeholder="Enter mission objective..."
                  className="w-full bg-neutral-950 border border-neutral-800 rounded-lg px-4 py-3 text-white text-lg font-medium outline-none focus:border-blue-500/50 transition-colors"
                />
              ) : (
                <h4 className="text-2xl font-semibold text-white tracking-tight leading-tight">
                  {details.mission?.objective || "No objective defined."}
                </h4>
              )}
            </section>

            {/* Criteria Section */}
            <section>
              <div className="flex justify-between items-center mb-4">
                <label className="text-[10px] font-bold text-neutral-500 uppercase tracking-widest">Success Criteria</label>
                {isEditing && (
                  <button 
                    onClick={addCriteria}
                    className="text-xs text-blue-400 hover:text-blue-300 transition-colors flex items-center gap-1"
                  >
                    <span className="material-symbols-outlined text-sm">add</span> Add Criterion
                  </button>
                )}
              </div>
              
              <div className="space-y-3">
                {isEditing ? (
                  editedCriteria.map((item, idx) => (
                    <div key={idx} className="flex gap-2 items-center">
                      <input 
                        value={item}
                        onChange={(e) => updateCriteria(idx, e.target.value)}
                        placeholder={`Success criterion #${idx + 1}`}
                        className="flex-1 bg-neutral-950 border border-neutral-800 rounded-lg px-3 py-2 text-sm text-neutral-200 outline-none focus:border-blue-500/50"
                      />
                      <button onClick={() => removeCriteria(idx)} className="p-2 text-neutral-600 hover:text-red-500 transition-colors">
                        <span className="material-symbols-outlined text-lg">delete</span>
                      </button>
                    </div>
                  ))
                ) : (
                  details.mission?.criteria?.map((item: string, idx: number) => {
                    const isDone = item.includes("완료") || item.includes("확인") || item.includes("배치 완료") || item.includes("제거 완료");
                    return (
                      <div key={idx} className="flex items-center gap-3 p-3 bg-neutral-950/50 border border-neutral-800/50 rounded-lg">
                        <span className={`material-symbols-outlined text-xl ${isDone ? 'text-emerald-500' : 'text-neutral-700'}`}>
                          {isDone ? 'check_circle' : 'radio_button_unchecked'}
                        </span>
                        <span className={`text-sm ${isDone ? 'text-neutral-200' : 'text-neutral-500'}`}>{item}</span>
                      </div>
                    );
                  })
                )}
              </div>
            </section>

            {/* Architect's Summary Section */}
            <section>
              <label className="text-[10px] font-bold text-neutral-500 uppercase tracking-widest mb-3 block">Architect's Summary</label>
              <div className="bg-neutral-950 border border-neutral-800 rounded-lg p-4">
                {isEditing ? (
                  <textarea 
                    value={editedDescription}
                    onChange={(e) => { setEditedDescription(e.target.value); setIsDirty(true); }}
                    placeholder="Provide a detailed description of the circuit node's purpose..."
                    className="w-full h-32 bg-transparent text-sm text-neutral-300 outline-none resize-none leading-relaxed"
                  />
                ) : (
                  <p className="text-sm text-neutral-400 leading-relaxed italic">
                    {details.description || "No description provided for this circuit node."}
                  </p>
                )}
              </div>
            </section>

            {/* Operational Dependencies Section */}
            <section>
              <label className="text-[10px] font-bold text-neutral-500 uppercase tracking-widest mb-3 block">Technology Dependencies</label>
              <div className="flex flex-wrap gap-2">
                {details.units?.map((u: any, i: number) => (
                  <span key={i} className="px-2 py-1 bg-neutral-800 border border-neutral-700 rounded text-[10px] text-neutral-400 font-mono uppercase">
                    {u.name}
                  </span>
                ))}
              </div>
            </section>
          </div>
        </div>
      </div>

      {/* System Health / Footer */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-neutral-900 border border-neutral-800 rounded-xl p-4 flex items-center gap-4">
          <div className="p-2 bg-emerald-500/10 rounded-lg text-emerald-500">
            <span className="material-symbols-outlined">hub</span>
          </div>
          <div>
            <p className="text-[10px] text-neutral-500 uppercase font-bold tracking-widest">Circuit Node Status</p>
            <p className="text-sm text-white font-medium">READY / SYNCED</p>
          </div>
        </div>
        <div className="bg-neutral-900 border border-neutral-800 rounded-xl p-4 flex items-center gap-4">
          <div className="p-2 bg-blue-500/10 rounded-lg text-blue-500">
            <span className="material-symbols-outlined">memory</span>
          </div>
          <div>
            <p className="text-[10px] text-neutral-500 uppercase font-bold tracking-widest">Unit Count</p>
            <p className="text-sm text-white font-medium">{details.units?.length || 0} Units</p>          </div>
        </div>
        <div className="bg-neutral-900 border border-neutral-800 rounded-xl p-4 flex items-center gap-4">
          <div className="p-2 bg-neutral-800 rounded-lg text-neutral-400">
            <span className="material-symbols-outlined">folder</span>
          </div>
          <div>
            <p className="text-[10px] text-neutral-500 uppercase font-bold tracking-widest">Active Specs</p>
            <p className="text-sm text-white font-medium">{details.actions?.length || 0} Operational Files</p>
          </div>
        </div>
      </div>
    </div>
  );
};
