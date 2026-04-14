"use client";

import React, { useState, useEffect } from "react";
import { I18N } from "@/constants/i18n";
import { SystemStatus } from "@/types/mcp";

interface ResourceMonitorProps {
  systemStatus: SystemStatus;
  language: "ko" | "en";
}

export const ResourceMonitor: React.FC<ResourceMonitorProps> = ({ systemStatus, language }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [thresholds, setThresholds] = useState({ cpu: 80, mem: 85 });
  const [isSaving, setIsSaving] = useState(false);

  const isConnected = systemStatus.active_circuit !== "None";

  const fetchThresholds = async () => {
    try {
      const res = await fetch("/api/mcp/protocols?type=resource");
      if (res.ok) {
        const data = await res.json();
        setThresholds(data.thresholds || { cpu: 80, mem: 85 });
      }
    } catch {
      // ignore
    }
  };

  useEffect(() => {
    if (isEditing) fetchThresholds();
  }, [isEditing]);

  const handleSave = async () => {
    setIsSaving(true);
    try {
      const response = await fetch("/api/mcp/update", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          target: "resource_monitor",
          data: { thresholds, last_updated: new Date().toISOString() }
        })
      });
      if (response.ok) setIsEditing(false);
    } catch {
      alert("Failed to save thresholds.");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="bg-neutral-900 border border-neutral-800 rounded-2xl overflow-hidden flex flex-col h-full shadow-2xl animate-in fade-in slide-in-from-left-4 duration-500">
      {/* Header */}
      <div className="px-8 py-5 border-b border-neutral-800 flex justify-between items-center bg-neutral-900/80 backdrop-blur-md z-10 flex-shrink-0">
        <div className="flex items-center gap-4">
          <div className="p-2.5 bg-blue-500/10 rounded-xl border border-blue-500/20 shadow-inner text-blue-500">
            <span className="material-symbols-outlined text-2xl font-light">speed</span>
          </div>
          <div>
            <h3 className="text-white font-bold tracking-tight uppercase text-sm">Neural Resource Monitor</h3>
            <p className="text-[10px] text-neutral-500 font-mono mt-0.5 tracking-wider uppercase">System_Compute_Load</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          {!isEditing ? (
            <button 
              onClick={() => setIsEditing(true)}
              className="flex items-center gap-2 px-4 py-2 bg-neutral-800 hover:bg-neutral-700 text-white text-[10px] font-black rounded-xl transition-all active:scale-95 border border-neutral-700 uppercase tracking-widest shadow-lg"
            >
              <span className="material-symbols-outlined text-sm">settings</span>
              Thresholds
            </button>
          ) : (
            <div className="flex items-center gap-3 animate-in fade-in slide-in-from-right-4 duration-300">
              <button 
                onClick={handleSave}
                disabled={isSaving}
                className="flex items-center gap-2 px-6 py-2 bg-blue-600 hover:bg-blue-500 text-black text-[10px] font-black rounded-xl transition-all active:scale-95 uppercase tracking-widest shadow-lg shadow-blue-900/20"
              >
                <span className="material-symbols-outlined text-sm">save</span>
                {isSaving ? "Syncing..." : "Apply Changes"}
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

      <div className="flex-1 overflow-y-auto p-10 custom-scrollbar bg-neutral-950/20">
        <div className="max-w-xl mx-auto space-y-10 animate-in fade-in zoom-in-98 duration-500">
          {isEditing ? (
            /* Configuration View */
            <div className="space-y-10 py-4">
              <div className="bg-neutral-900/40 border border-neutral-800/60 rounded-3xl p-8 space-y-6 shadow-inner">
                <div className="flex justify-between items-center mb-2">
                  <div className="flex items-center gap-2">
                    <span className="material-symbols-outlined text-blue-500/60 text-lg">cpu</span>
                    <label className="text-[10px] font-bold text-neutral-400 uppercase tracking-[0.2em]">CPU Warning Limit</label>
                  </div>
                  <span className="text-sm font-mono text-blue-400 font-black">{thresholds.cpu}%</span>
                </div>
                <input 
                  type="range" min="10" max="95" value={thresholds.cpu}
                  onChange={(e) => setThresholds({...thresholds, cpu: parseInt(e.target.value)})}
                  className="w-full h-1.5 bg-neutral-800 rounded-full appearance-none cursor-pointer accent-blue-500 shadow-inner"
                />
              </div>

              <div className="bg-neutral-900/40 border border-neutral-800/60 rounded-3xl p-8 space-y-6 shadow-inner">
                <div className="flex justify-between items-center mb-2">
                  <div className="flex items-center gap-2">
                    <span className="material-symbols-outlined text-blue-500/60 text-lg">memory</span>
                    <label className="text-[10px] font-bold text-neutral-400 uppercase tracking-[0.2em]">Memory Alert Point</label>
                  </div>
                  <span className="text-sm font-mono text-blue-400 font-black">{thresholds.mem}%</span>
                </div>
                <input 
                  type="range" min="10" max="95" value={thresholds.mem}
                  onChange={(e) => setThresholds({...thresholds, mem: parseInt(e.target.value)})}
                  className="w-full h-1.5 bg-neutral-800 rounded-full appearance-none cursor-pointer accent-blue-500 shadow-inner"
                />
              </div>

              <div className="p-6 bg-blue-500/5 border border-blue-500/20 rounded-2xl flex gap-3 items-start">
                 <span className="material-symbols-outlined text-blue-500 text-lg mt-0.5">info</span>
                 <p className="text-[11px] text-neutral-500 leading-relaxed font-mono uppercase tracking-tighter">
                   Operational Safety: Thresholds defined here will trigger high-priority alerts across the neural interface when reached.
                 </p>
              </div>
            </div>
          ) : (
            /* Monitoring View */
            <div className="space-y-12">
              <div className="grid grid-cols-2 gap-6">
                <div className="bg-neutral-900/40 border border-neutral-800/60 rounded-3xl p-6 shadow-inner group hover:border-blue-500/30 transition-all duration-500">
                  <p className="text-[10px] text-neutral-600 uppercase font-black tracking-[0.2em] mb-3 group-hover:text-blue-500/60 transition-colors px-1">Uplink Strength</p>
                  <div className="flex items-end gap-2 px-1">
                    <span className="text-4xl font-black text-white font-mono tracking-tighter">{isConnected ? "98.2" : "0.0"}</span>
                    <span className="text-[11px] text-neutral-600 font-mono mb-1 uppercase font-bold tracking-widest">%</span>
                  </div>
                </div>
                <div className="bg-neutral-900/40 border border-neutral-800/60 rounded-3xl p-6 shadow-inner group hover:border-blue-500/30 transition-all duration-500">
                  <p className="text-[10px] text-neutral-600 uppercase font-black tracking-[0.2em] mb-3 group-hover:text-blue-500/60 transition-colors px-1">Neural Latency</p>
                  <div className="flex items-end gap-2 px-1">
                    <span className="text-4xl font-black text-white font-mono tracking-tighter">{isConnected ? "12" : "---"}</span>
                    <span className="text-[11px] text-neutral-600 font-mono mb-1 uppercase font-bold tracking-widest">ms</span>
                  </div>
                </div>
              </div>

              <div className="space-y-10">
                <div className="space-y-4 px-1">
                  <div className="flex justify-between items-end">
                    <div className="flex items-center gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse"></span>
                      <label className="text-[10px] font-bold text-neutral-400 uppercase tracking-[0.2em]">Neural CPU Consumption</label>
                    </div>
                    <span className="text-xs font-mono font-black text-white">{isConnected ? "14.2%" : "0.0%"}</span>
                  </div>
                  <div className="h-3 w-full bg-neutral-900/80 border border-neutral-800 rounded-full overflow-hidden shadow-inner p-0.5">
                    <div 
                      className="h-full bg-gradient-to-r from-blue-600 to-blue-400 rounded-full transition-all duration-1000 ease-out shadow-[0_0_15px_rgba(59,130,246,0.3)]" 
                      style={{ width: isConnected ? "14.2%" : "0%" }}
                    ></div>
                  </div>
                </div>

                <div className="space-y-4 px-1">
                  <div className="flex justify-between items-end">
                    <div className="flex items-center gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse"></span>
                      <label className="text-[10px] font-bold text-neutral-400 uppercase tracking-[0.2em]">Core Memory Allocation</label>
                    </div>
                    <span className="text-xs font-mono font-black text-white">{isConnected ? "65.8%" : "0.0%"}</span>
                  </div>
                  <div className="h-3 w-full bg-neutral-900/80 border border-neutral-800 rounded-full overflow-hidden shadow-inner p-0.5">
                    <div 
                      className="h-full bg-gradient-to-r from-blue-600 to-blue-400 rounded-full transition-all duration-1000 ease-out shadow-[0_0_15px_rgba(59,130,246,0.3)]" 
                      style={{ width: isConnected ? "65.8%" : "0%" }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Footer / Status */}
      {!isEditing && (
        <div className="px-8 py-5 bg-neutral-900/80 backdrop-blur-sm border-t border-neutral-800 flex justify-between items-center flex-shrink-0">
          <div className="flex items-center gap-3 text-[10px] text-neutral-600 font-mono uppercase tracking-[0.2em] font-bold">
            <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]' : 'bg-rose-500 animate-pulse shadow-[0_0_8px_rgba(244,63,94,0.5)]'}`} />
            OPERATOR_NODE: {isConnected ? "SYNC_ACTIVE" : "AWAITING_UPLINK"}
          </div>
          <span className="text-[10px] text-neutral-700 font-mono font-bold tracking-widest uppercase italic">V2.5.0_COMMAND_LINK</span>
        </div>
      )}
    </div>
  );
};
