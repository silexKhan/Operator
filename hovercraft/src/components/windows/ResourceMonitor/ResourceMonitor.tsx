"use client";

import React, { useState, useEffect } from "react";

interface ResourceMonitorProps {
  systemStatus: any;
}

export const ResourceMonitor: React.FC<ResourceMonitorProps> = ({ systemStatus }) => {
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
    } catch (e) {
      console.error("Failed to fetch thresholds:", e);
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
    } catch (e) {
      alert("Failed to save thresholds.");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="bg-neutral-900 border border-neutral-800 rounded-xl overflow-hidden flex flex-col shadow-sm">
      {/* Header */}
      <div className="px-6 py-4 border-b border-neutral-800 flex justify-between items-center bg-neutral-900/50">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-blue-500/10 rounded-lg text-blue-500">
            <span className="material-symbols-outlined text-xl">speed</span>
          </div>
          <div>
            <h3 className="text-white font-medium">System Resources</h3>
            <p className="text-[11px] text-neutral-500 font-mono uppercase tracking-wider">Neural_Compute_Load</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {!isEditing ? (
            <button 
              onClick={() => setIsEditing(true)}
              className="flex items-center gap-2 px-3 py-1.5 bg-neutral-800 hover:bg-neutral-700 text-neutral-200 text-xs rounded-md transition-colors"
            >
              <span className="material-symbols-outlined text-sm">settings</span>
              Thresholds
            </button>
          ) : (
            <div className="flex items-center gap-2">
              <button 
                onClick={handleSave}
                disabled={isSaving}
                className="flex items-center gap-2 px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white text-xs rounded-md transition-colors font-medium"
              >
                <span className="material-symbols-outlined text-sm">save</span>
                {isSaving ? "Saving..." : "Save Config"}
              </button>
              <button 
                onClick={() => setIsEditing(false)}
                className="flex items-center gap-2 px-3 py-1.5 bg-neutral-800 hover:bg-neutral-700 text-neutral-400 text-xs rounded-md transition-colors"
              >
                Cancel
              </button>
            </div>
          )}
        </div>
      </div>

      <div className="p-6 space-y-8 flex-1">
        {isEditing ? (
          /* Configuration View */
          <div className="space-y-8 max-w-md mx-auto py-4 animate-in fade-in duration-300">
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <label className="text-xs font-bold text-neutral-400 uppercase tracking-widest">CPU Warning Limit</label>
                <span className="text-sm font-mono text-blue-400 font-bold">{thresholds.cpu}%</span>
              </div>
              <input 
                type="range" min="10" max="95" value={thresholds.cpu}
                onChange={(e) => setThresholds({...thresholds, cpu: parseInt(e.target.value)})}
                className="w-full h-1.5 bg-neutral-800 rounded-lg appearance-none cursor-pointer accent-blue-500"
              />
            </div>

            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <label className="text-xs font-bold text-neutral-400 uppercase tracking-widest">Memory Alert Point</label>
                <span className="text-sm font-mono text-blue-400 font-bold">{thresholds.mem}%</span>
              </div>
              <input 
                type="range" min="10" max="95" value={thresholds.mem}
                onChange={(e) => setThresholds({...thresholds, mem: parseInt(e.target.value)})}
                className="w-full h-1.5 bg-neutral-800 rounded-lg appearance-none cursor-pointer accent-blue-500"
              />
            </div>

            <p className="text-[10px] text-neutral-600 italic text-center mt-4">
              * Real-time alerts will trigger when resources exceed these thresholds.
            </p>
          </div>
        ) : (
          /* Monitoring View */
          <>
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-neutral-950 border border-neutral-800 rounded-xl p-4">
                <p className="text-[10px] text-neutral-500 uppercase font-bold tracking-widest mb-1">Uplink Strength</p>
                <div className="flex items-end gap-2">
                  <span className="text-2xl font-bold text-white font-mono">{isConnected ? "98.2" : "0.0"}</span>
                  <span className="text-xs text-neutral-500 mb-1">%</span>
                </div>
              </div>
              <div className="bg-neutral-950 border border-neutral-800 rounded-xl p-4">
                <p className="text-[10px] text-neutral-500 uppercase font-bold tracking-widest mb-1">Latency</p>
                <div className="flex items-end gap-2">
                  <span className="text-2xl font-bold text-white font-mono">{isConnected ? "12" : "---"}</span>
                  <span className="text-xs text-neutral-500 mb-1">ms</span>
                </div>
              </div>
            </div>

            <div className="space-y-6">
              <div className="space-y-3">
                <div className="flex justify-between items-end">
                  <label className="text-[10px] font-bold text-neutral-500 uppercase tracking-widest">Neural CPU Load</label>
                  <span className="text-sm font-mono text-neutral-400">{isConnected ? "14.2%" : "0.0%"}</span>
                </div>
                <div className="h-2 w-full bg-neutral-800 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-blue-500 transition-all duration-1000 ease-out" 
                    style={{ width: isConnected ? "14.2%" : "0%" }}
                  ></div>
                </div>
              </div>

              <div className="space-y-3">
                <div className="flex justify-between items-end">
                  <label className="text-[10px] font-bold text-neutral-500 uppercase tracking-widest">Core Memory Usage</label>
                  <span className="text-sm font-mono text-neutral-400">{isConnected ? "65.8%" : "0.0%"}</span>
                </div>
                <div className="h-2 w-full bg-neutral-800 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-blue-500 transition-all duration-1000 ease-out" 
                    style={{ width: isConnected ? "65.8%" : "0%" }}
                  ></div>
                </div>
              </div>
            </div>
          </>
        )}
      </div>

      {/* Footer / Status */}
      {!isEditing && (
        <div className="px-6 py-4 bg-neutral-950/50 border-t border-neutral-800 flex justify-between items-center">
          <div className="flex items-center gap-2 text-[10px] text-neutral-600 font-mono uppercase tracking-widest">
            <span className={`w-1.5 h-1.5 rounded-full ${isConnected ? 'bg-emerald-500' : 'bg-rose-500 animate-pulse'}`} />
            Operator_Node: {isConnected ? "Online" : "Awaiting_Connection"}
          </div>
          <span className="text-[10px] text-neutral-700 font-mono">v2.5.0-STABLE</span>
        </div>
      )}
    </div>
  );
};
