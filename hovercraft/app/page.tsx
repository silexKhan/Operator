"use client";

import React, { useEffect, useState, useRef, useCallback } from "react";
import dynamic from "next/dynamic";

// 하이드레이션 오류 방지를 위해 SSR 제외 임포트
const CoreAccess = dynamic(() => import("@/components/windows/CoreAccess/CoreAccess").then(mod => mod.CoreAccess), { ssr: false });
const MissionSpecs = dynamic(() => import("@/components/windows/MissionSpecs/MissionSpecs").then(mod => mod.MissionSpecs), { ssr: false });
const AuditSecurity = dynamic(() => import("@/components/windows/AuditSecurity/AuditSecurity").then(mod => mod.AuditSecurity), { ssr: false });
const UnitProtocols = dynamic(() => import("@/components/windows/UnitProtocols/UnitProtocols").then(mod => mod.UnitProtocols), { ssr: false });
const ResourceMonitor = dynamic(() => import("@/components/windows/ResourceMonitor/ResourceMonitor").then(mod => mod.ResourceMonitor), { ssr: false });
const SystemLogs = dynamic(() => import("@/components/windows/SystemLogs/SystemLogs").then(mod => mod.SystemLogs), { ssr: false });

import { ShipInitialization } from "@/components/Initialization/ShipInitialization";
import { I18N } from "@/constants/i18n";
import { SystemStatus, LogEntry, CircuitDetails, Unit } from "@/types/mcp";

type TabType = "Overview" | "Protocols" | "Units" | "Circuits" | "Monitor";

export default function Home() {
  const [activeTab, setActiveTab] = useState<TabType>("Overview");
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [status, setStatus] = useState("DISCONNECTED");
  const [systemStatus, setSystemStatus] = useState<SystemStatus>({ active_circuit: "None", circuits: [] });
  const [shipConfig, setShipConfig] = useState<{ shipName: string; captainName: string } | null>(null);
  const [isInitializing, setIsInitializing] = useState(true);
  const [mounted, setMounted] = useState(false);
  const [selectedCircuit, setSelectedCircuit] = useState<string | null>(null);
  const [circuitDetails, setCircuitDetails] = useState<CircuitDetails | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [language, setLanguage] = useState<"ko" | "en">("ko");
  const [isEditingCircuit, setIsEditingCircuit] = useState(false);
  const [editingCircuitData, setEditingCircuitData] = useState<CircuitDetails | null>(null);
  const [selectedCircuitRuleIndex, setSelectedCircuitRuleIndex] = useState<number | null>(null);
  const [editedCircuitRule, setEditedCircuitRule] = useState("");
  const [isGlobalProtocolsExpanded, setIsGlobalProtocolsExpanded] = useState(false);
  const logEndRef = useRef<HTMLDivElement>(null);

  const [isCreatingCircuit, setIsCreatingCircuit] = useState(false);
  const [newCircuitName, setNewCircuitName] = useState("");
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [pollingRate, setPollingRate] = useState(3000);
  const [logLimit, setLogLimit] = useState(50);

  const requestMcpStatus = useCallback(() => {
    setLogs((prev) => [...prev, {
      timestamp: new Date().toLocaleTimeString(),
      level: "INFO",
      message: "Syncing MCP Status...",
      category: "OPERATOR"
    }].slice(-logLimit));
  }, [logLimit]);

  const handleCreateCircuit = async () => {
    if (!newCircuitName.trim()) return;
    setIsSaving(true);
    try {
      const res = await fetch("/api/mcp/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          target: "circuit", 
          name: newCircuitName.toLowerCase().trim()
        })
      });
      if (res.ok) {
        setIsCreatingCircuit(false);
        setNewCircuitName("");
        requestMcpStatus();
      } else {
        alert("Failed to create circuit.");
      }
    } catch (e) {
      console.error("Circuit creation error:", e);
    } finally {
      setIsSaving(false);
    }
  };

  useEffect(() => {
    setMounted(true);
    const fetchConfig = async () => {
      try {
        const configRes = await fetch("/api/config");
        if (configRes.ok) {
          const configData = await configRes.json();
          setShipConfig(configData);
        }

        const stateRes = await fetch("/api/mcp/state");
        if (stateRes.ok) {
          const stateData = await stateRes.json();
          setSystemStatus({
            active_circuit: stateData.active_circuit || "None",
            circuits: stateData.registered_circuits || stateData.circuits || [],
            details: stateData.active_circuit_details
          });
          if (stateData.lang) {
            setLanguage(stateData.lang);
          }
        }
      } catch (e) {
        console.error("Initial config/state fetch error:", e);
      } finally {
        setIsInitializing(false);
      }
    };
    fetchConfig();
  }, []);

  const fetchCircuitDetails = useCallback((name: string) => {
    fetch(`/api/mcp/protocols?type=circuit_full&name=${name}`)
      .then(res => res.json())
      .then(data => {
        setCircuitDetails(data);
      })
      .catch(err => console.error("Failed to fetch circuit details", err));
  }, []);

  useEffect(() => {
    if (selectedCircuit) {
      fetchCircuitDetails(selectedCircuit);
    } else {
      setCircuitDetails(null);
      setSelectedCircuitRuleIndex(null);
    }
  }, [selectedCircuit, language, fetchCircuitDetails]);

  useEffect(() => {
    if (!mounted) return;

    const eventSource = new EventSource("/api/mcp/events");

    eventSource.onopen = () => setStatus("CONNECTED");
    eventSource.onerror = () => setStatus("DISCONNECTED");

    eventSource.addEventListener("state", (event: MessageEvent) => {
      try {
        const payload = JSON.parse(event.data);
        setSystemStatus({
          active_circuit: payload.active_circuit || "None",
          circuits: payload.registered_circuits || payload.circuits || [],
          details: payload.active_circuit_details
        });
        
        if (payload.lang && (payload.lang === "ko" || payload.lang === "en")) {
          setLanguage(payload.lang);
        }
      } catch (e) {
        console.error("Failed to parse SSE state data", e);
      }
    });

    eventSource.addEventListener("log", (event: MessageEvent) => {
      try {
        const log = JSON.parse(event.data);
        setLogs((prev) => [...prev, {
          timestamp: new Date(log.timestamp || Date.now()).toLocaleTimeString(),
          level: log.level || "INFO",
          message: log.message,
          category: log.category || "ENGINE"
        }].slice(-logLimit));
      } catch (e) {
        console.error("Failed to parse SSE log data", e);
      }
    });

    return () => eventSource.close();
  }, [mounted, logLimit]);

  const requestSwitchCircuit = async (name: string) => {
    try {
      await fetch("/api/mcp/update", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          target: "state",
          data: { active_circuit: name }
        })
      });
      setSelectedCircuit(name);
    } catch (e) {
      console.error("Switch circuit error:", e);
    }
  };

  const handleEditCircuit = async (name: string) => {
    try {
      const res = await fetch(`/api/mcp/protocols?type=circuit_full&name=${name}`);
      if (res.ok) {
        const data = await res.json();
        setEditingCircuitData(data.overview || { name, description: "", mission: { objective: "", criteria: [] } });
        setIsEditingCircuit(true);
      }
    } catch (e) {
      console.error("Failed to fetch circuit for editing", e);
    }
  };

  const handleSaveCircuitOverview = async () => {
    if (!editingCircuitData) return;
    setIsSaving(true);
    try {
      const res = await fetch("/api/mcp/update", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          target: "overview",
          name: editingCircuitData.name,
          data: editingCircuitData
        })
      });

      if (res.ok) {
        setIsEditingCircuit(false);
        setEditingCircuitData(null);
        requestMcpStatus();
      } else {
        alert("Failed to save circuit overview.");
      }
    } catch (e) {
      console.error("Circuit save error:", e);
    } finally {
      setIsSaving(false);
    }
  };

  const handleSaveIndividualCircuitRule = async () => {
    if (selectedCircuitRuleIndex === null || !selectedCircuit || !circuitDetails) return;
    setIsSaving(true);
    
    let newRules: string[] = [];
    if (Array.isArray(circuitDetails.protocols)) {
      newRules = [...circuitDetails.protocols];
    } else if (circuitDetails.protocols && typeof circuitDetails.protocols === 'object' && 'RULES' in circuitDetails.protocols) {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      newRules = [...(circuitDetails.protocols as any).RULES];
    }

    newRules[selectedCircuitRuleIndex] = editedCircuitRule;

    try {
      const res = await fetch("/api/mcp/update", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          target: "protocol",
          name: selectedCircuit,
          data: { rules: newRules }
        })
      });

      if (res.ok) {
        setSelectedCircuitRuleIndex(null);
        fetchCircuitDetails(selectedCircuit);
      } else {
        alert("Failed to update circuit protocol.");
      }
    } catch (e) {
      console.error("Protocol update error:", e);
    } finally {
      setIsSaving(false);
    }
  };

  const handleLanguageChange = async (newLang: "ko" | "en") => {
    setLanguage(newLang);
    try {
      await fetch("/api/mcp/update", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          target: "state",
          data: { lang: newLang }
        })
      });
    } catch (e) {
      console.error("Language switch error:", e);
    }
  };

  if (!mounted) return <div className="h-screen bg-neutral-950" />;

  const displayShipName = shipConfig?.shipName || "NEBUCHADNEZZAR";

  return (
    <div className="flex h-screen bg-neutral-950 text-neutral-200 font-sans overflow-hidden">
      {!shipConfig && !isInitializing && (
        <ShipInitialization onComplete={(shipName, captainName) => setShipConfig({ shipName, captainName })} />
      )}

      {/* Sidebar */}
      <aside className="w-64 border-r border-neutral-800 bg-neutral-900/50 flex flex-col flex-shrink-0">
        <div className="p-6 border-b border-neutral-800">
          <div className="flex items-center gap-2 mb-1">
            <span className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_#10b981]" />
            <h1 className="text-sm font-bold tracking-tight text-white uppercase">{displayShipName}</h1>
          </div>
          <p className="text-[11px] text-neutral-500 font-mono">OPERATOR_OS: 2.0</p>
        </div>

        <nav className="flex-1 p-4 space-y-1 overflow-y-auto custom-scrollbar">
          <div className="px-3 py-2 text-[10px] font-bold text-neutral-500 uppercase tracking-widest">Main Channels</div>
          {[
            { id: "Overview", icon: "dashboard", label: I18N.Overview[language] },
            { id: "Protocols", icon: "rule", label: I18N.Protocols[language] },
            { id: "Circuits", icon: "hub", label: I18N.Circuits[language] },
            { id: "Units", icon: "memory", label: I18N.Units[language] },
            { id: "Monitor", icon: "monitoring", label: I18N.Monitor[language] },
          ].map((item) => (
            <button
              key={item.id}
              onClick={() => {
                setActiveTab(item.id as TabType);
                if (item.id !== "Circuits") setSelectedCircuit(null);
              }}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all ${
                activeTab === item.id 
                  ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20" 
                  : "text-neutral-500 hover:bg-neutral-800/50 hover:text-neutral-200 border border-transparent"
              }`}
            >
              <span className={`material-symbols-outlined text-lg ${activeTab === item.id ? 'text-emerald-500' : ''}`}>{item.icon}</span>
              <span className="font-medium">{item.label}</span>
            </button>
          ))}
        </nav>

        <div className="p-4 border-t border-neutral-800">
          <div className="bg-neutral-950 rounded-xl p-4 border border-neutral-800 shadow-inner">
            <div className="text-[9px] font-bold text-neutral-600 uppercase tracking-[0.2em] mb-2">Active Link</div>
            <div className="text-xs text-emerald-500 font-mono truncate font-bold">
              {systemStatus.active_circuit}
            </div>
          </div>
        </div>
      </aside>

      {/* Main Body */}
      <main className="flex-1 flex flex-col min-w-0 bg-neutral-950 relative overflow-hidden">
        {/* Header */}
        <header className="h-14 border-b border-neutral-800 flex items-center justify-between px-8 bg-neutral-900/40 backdrop-blur-md z-20 flex-shrink-0">
          <div className="flex items-center gap-4">
            <h2 className="text-sm font-bold text-white uppercase tracking-widest">
              {selectedCircuit ? `CIRCUIT_NODE // ${selectedCircuit}` : `SYSTEM_CHANNEL // ${activeTab}`}
            </h2>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-1 bg-neutral-950 border border-neutral-800 rounded-lg p-1 shadow-inner">
              <button 
                onClick={() => handleLanguageChange("ko")}
                className={`px-2.5 py-1 text-[9px] font-bold rounded-md transition-all ${language === "ko" ? "bg-neutral-800 text-emerald-500 shadow-sm" : "text-neutral-600 hover:text-neutral-400"}`}
              >
                KO
              </button>
              <button 
                onClick={() => handleLanguageChange("en")}
                className={`px-2.5 py-1 text-[9px] font-bold rounded-md transition-all ${language === "en" ? "bg-neutral-800 text-emerald-500 shadow-sm" : "text-neutral-600 hover:text-neutral-400"}`}
              >
                EN
              </button>
            </div>
            <button 
              onClick={() => setIsSettingsOpen(true)}
              className="p-2 text-neutral-500 hover:text-white transition-all active:scale-90"
            >
              <span className="material-symbols-outlined text-xl">settings</span>
            </button>
          </div>
        </header>

        {/* Dynamic Content Area (Fills space between header and logs) */}
        <div className="flex-1 overflow-hidden flex flex-col relative">
          <div className="flex-1 overflow-y-auto p-8 custom-scrollbar">
            <div className="max-w-[1400px] mx-auto h-full flex flex-col">
              
              {activeTab === "Overview" && (
                <div className="h-full overflow-y-auto pr-2 custom-scrollbar pb-10">
                  <MissionSpecs systemStatus={systemStatus} language={language} />
                </div>
              )}

              {activeTab === "Protocols" && (
                <div className="h-full overflow-hidden flex flex-col">
                  <UnitProtocols systemStatus={systemStatus} language={language} />
                </div>
              )}

              {activeTab === "Circuits" && !selectedCircuit && (
                <div className="bg-neutral-900/30 border border-neutral-800 rounded-2xl p-8 shadow-2xl animate-in fade-in zoom-in-98 duration-500">
                  <div className="flex justify-between items-center mb-10">
                    <div className="flex items-center gap-4">
                      <div className="p-3 bg-emerald-500/5 rounded-2xl border border-emerald-500/20 shadow-inner text-emerald-500">
                        <span className="material-symbols-outlined text-3xl font-light">hub</span>
                      </div>
                      <div>
                        <h3 className="text-lg font-bold text-white tracking-tight uppercase leading-none">Circuit Orchestration</h3>
                        <p className="text-[10px] text-neutral-500 font-mono mt-2 uppercase tracking-[0.2em]">Matrix Control Interface</p>
                      </div>
                    </div>
                    <button 
                      onClick={() => setIsCreatingCircuit(true)}
                      className="px-6 py-2.5 bg-emerald-600 text-black text-[10px] font-black rounded-xl uppercase tracking-widest hover:bg-emerald-500 transition-all active:scale-95 shadow-lg shadow-emerald-900/20"
                    >
                      Initialize Node
                    </button>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                      {systemStatus.circuits.filter(name => name !== "__pycache__").map((name: string) => (
                        <div key={name} className="group relative">
                          <button
                            onClick={() => requestSwitchCircuit(name)}
                            className={`w-full p-8 rounded-3xl border text-left transition-all duration-500 ${
                              systemStatus.active_circuit === name 
                              ? "bg-emerald-500/5 border-emerald-500/40 text-emerald-400 shadow-[0_0_40px_rgba(16,185,129,0.08)]" 
                              : "bg-neutral-900/40 border-neutral-800/60 text-neutral-500 hover:border-neutral-600 hover:bg-neutral-900/60"
                            }`}
                          >
                            <div className="flex items-center justify-between mb-6">
                              <span className={`material-symbols-outlined text-2xl transition-all duration-700 ${systemStatus.active_circuit === name ? 'rotate-180 text-emerald-500' : 'text-neutral-700'}`}>{systemStatus.active_circuit === name ? 'hub' : 'settings_input_component'}</span>
                              {systemStatus.active_circuit === name && (
                                <div className="flex items-center gap-1.5 px-2 py-1 bg-emerald-500 text-black rounded-lg font-black text-[8px] uppercase tracking-tighter shadow-lg shadow-emerald-900/40">
                                  <div className="w-1 h-1 bg-black rounded-full animate-ping"></div>
                                  Active
                                </div>
                              )}
                            </div>
                            <div className="font-bold text-xs uppercase font-mono tracking-tight leading-none truncate">{name}</div>
                          </button>
                          <button 
                            onClick={(e: React.MouseEvent) => { e.stopPropagation(); handleEditCircuit(name); }}
                            className="absolute top-4 right-4 p-2.5 bg-neutral-800/80 backdrop-blur-sm text-neutral-400 rounded-xl opacity-0 group-hover:opacity-100 hover:text-white hover:bg-neutral-700 transition-all z-10 shadow-2xl border border-neutral-700/50"
                          >
                            <span className="material-symbols-outlined text-sm">edit</span>
                          </button>
                        </div>
                      ))}
                  </div>
                </div>
              )}

              {activeTab === "Circuits" && selectedCircuit && (
                <div className="h-full flex flex-col animate-in fade-in slide-in-from-bottom-4 duration-500">
                  <div className="flex items-center gap-5 mb-8 flex-shrink-0">
                    <button 
                      onClick={() => setSelectedCircuit(null)}
                      className="p-3 bg-neutral-900 border border-neutral-800 hover:bg-neutral-800 text-neutral-400 hover:text-white rounded-2xl transition-all active:scale-90 shadow-lg"
                    >
                      <span className="material-symbols-outlined">arrow_back</span>
                    </button>
                    <div>
                      <h3 className="text-2xl font-bold text-white uppercase tracking-tighter leading-none">{selectedCircuit}</h3>
                      <p className="text-[10px] text-emerald-500/60 font-mono mt-2 uppercase tracking-[0.3em] font-bold">Node_Status: Fully_Functional</p>
                    </div>
                  </div>

                  <div className="flex-1 overflow-y-auto pr-4 custom-scrollbar pb-10 space-y-8">
                    {/* Circuit Details content here */}
                    <div className="p-8 bg-neutral-900/30 border border-neutral-800 rounded-3xl">
                       <p className="text-sm text-neutral-400 leading-relaxed italic">
                         {circuitDetails?.overview?.description ? (typeof circuitDetails.overview.description === 'string' ? circuitDetails.overview.description : (circuitDetails.overview.description as any)[language]) : "System configuration for this node is being processed..."}
                       </p>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === "Units" && (
                <div className="h-full overflow-hidden flex flex-col">
                  <CoreAccess 
                    requestMcpStatus={requestMcpStatus} 
                    systemStatus={systemStatus} 
                    language={language}
                  />
                </div>
              )}
              
              {activeTab === "Monitor" && (
                <div className="h-full overflow-y-auto pr-2 custom-scrollbar pb-10">
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    <ResourceMonitor systemStatus={systemStatus} language={language} />
                    <AuditSecurity logs={logs} systemStatus={systemStatus} language={language} />
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Modals - constrained to space above log panel */}
        {isEditingCircuit && editingCircuitData && (
          <div className="fixed inset-x-0 top-0 bottom-48 z-50 flex items-start justify-center bg-black/70 backdrop-blur-md p-8 pt-24 overflow-hidden animate-in fade-in duration-300">
            <div className="bg-neutral-900 border border-neutral-800 rounded-3xl w-full max-w-3xl shadow-[0_0_100px_rgba(0,0,0,0.5)] flex flex-col h-full max-h-[calc(100%-40px)] animate-in zoom-in-98 duration-300">
              <div className="px-8 py-6 border-b border-neutral-800 flex justify-between items-center bg-neutral-900/50 flex-shrink-0">
                <div className="flex items-center gap-4">
                  <div className="p-3 bg-emerald-500/10 rounded-2xl text-emerald-500 border border-emerald-500/20 shadow-inner">
                    <span className="material-symbols-outlined text-2xl">settings_input_component</span>
                  </div>
                  <div>
                    <h3 className="text-white font-bold uppercase tracking-tight text-sm">Configure Circuit Node</h3>
                    <p className="text-[10px] text-neutral-500 font-mono mt-1 uppercase tracking-widest">{editingCircuitData.name}</p>
                  </div>
                </div>
                <button onClick={() => setIsEditingCircuit(false)} className="text-neutral-500 hover:text-white p-2 transition-all active:scale-90"><span className="material-symbols-outlined">close</span></button>
              </div>
              <div className="p-8 space-y-8 overflow-y-auto flex-1 custom-scrollbar">
                <div className="space-y-3">
                  <label className="text-[10px] font-bold text-neutral-600 uppercase tracking-[0.2em] px-1">Description</label>
                  <textarea 
                    value={editingCircuitData.description ? (typeof editingCircuitData.description === 'string' ? editingCircuitData.description : (editingCircuitData.description as any)[language]) : ""}
                    onChange={(e) => {
                      if (editingCircuitData) {
                        const newDesc = typeof editingCircuitData.description === 'object' ? { ...editingCircuitData.description, [language]: e.target.value } : e.target.value;
                        setEditingCircuitData({ ...editingCircuitData, description: newDesc });
                      }
                    }}
                    className="w-full bg-neutral-950 border border-neutral-800 rounded-2xl p-5 text-sm text-neutral-300 h-28 outline-none focus:border-emerald-500/40 focus:ring-1 focus:ring-emerald-500/20 transition-all resize-none shadow-inner leading-relaxed"
                  />
                </div>
              </div>
              <div className="px-8 py-6 bg-neutral-900/80 border-t border-neutral-800 flex justify-end gap-4 flex-shrink-0">
                <button onClick={() => setIsEditingCircuit(false)} className="px-6 py-2.5 text-[10px] font-bold text-neutral-500 hover:text-white uppercase tracking-widest transition-colors">Discard</button>
                <button onClick={handleSaveCircuitOverview} disabled={isSaving} className="px-8 py-2.5 bg-emerald-600 text-black text-[10px] font-black rounded-xl uppercase tracking-widest hover:bg-emerald-500 shadow-lg shadow-emerald-900/20 active:scale-95 transition-all">
                  {isSaving ? "Syncing..." : "Apply Config"}
                </button>
              </div>
            </div>
          </div>
        )}

        {isCreatingCircuit && (
          <div className="fixed inset-x-0 top-0 bottom-48 z-50 flex items-start justify-center bg-black/70 backdrop-blur-md p-8 pt-24 overflow-hidden animate-in fade-in duration-300">
             <div className="bg-neutral-900 border border-neutral-800 rounded-3xl w-full max-w-md shadow-2xl animate-in zoom-in-98 duration-300 flex flex-col h-fit max-h-[80%]">
                {/* Create Circuit Form */}
                <div className="p-8 space-y-8">
                   <div className="flex items-center gap-4">
                      <div className="p-3 bg-emerald-500/10 rounded-2xl text-emerald-500"><span className="material-symbols-outlined text-2xl">add_circle</span></div>
                      <h3 className="text-sm font-bold text-white uppercase tracking-widest">Initialize Node</h3>
                   </div>
                   <input 
                      type="text" value={newCircuitName} onChange={(e) => setNewCircuitName(e.target.value)}
                      placeholder="Enter system identifier..."
                      className="w-full bg-neutral-950 border border-neutral-800 rounded-xl p-4 text-xs text-emerald-400 font-mono outline-none focus:border-emerald-500/40"
                   />
                   <div className="flex justify-end gap-3">
                      <button onClick={() => setIsCreatingCircuit(false)} className="px-4 py-2 text-[10px] text-neutral-500 uppercase font-bold">Cancel</button>
                      <button onClick={handleCreateCircuit} className="px-6 py-2 bg-emerald-600 text-black text-[10px] font-black rounded-lg uppercase tracking-widest">Execute</button>
                   </div>
                </div>
             </div>
          </div>
        )}

        {isSettingsOpen && (
          <div className="fixed inset-x-0 top-0 bottom-48 z-50 flex items-start justify-center bg-black/70 backdrop-blur-md p-8 pt-24 overflow-hidden animate-in fade-in duration-300">
             <div className="bg-neutral-900 border border-neutral-800 rounded-3xl w-full max-w-md shadow-2xl flex flex-col h-fit max-h-[80%]">
                <div className="p-8 space-y-8">
                   <h3 className="text-sm font-bold text-white uppercase tracking-widest">System Engine Settings</h3>
                   <div className="space-y-4">
                      <div className="flex justify-between items-center bg-neutral-950 p-4 rounded-xl border border-neutral-800">
                         <span className="text-[10px] text-neutral-500 uppercase font-bold">Link Latency</span>
                         <span className="text-xs text-emerald-500 font-mono">2.4ms</span>
                      </div>
                      <button onClick={() => handleLanguageChange(language === "ko" ? "en" : "ko")} className="w-full py-3 bg-neutral-800 border border-neutral-700 rounded-xl text-[10px] font-bold uppercase text-neutral-300 hover:text-white transition-all">
                         Switch Language ({language.toUpperCase()})
                      </button>
                   </div>
                   <button onClick={() => setIsSettingsOpen(false)} className="w-full py-3 bg-neutral-950 border border-neutral-800 rounded-xl text-[10px] font-bold text-neutral-500 uppercase tracking-widest hover:text-white">Close Interface</button>
                </div>
             </div>
          </div>
        )}

        {/* System Telemetry Console (Fixed Bottom) */}
        <div className="h-48 border-t border-neutral-800 bg-neutral-900/60 backdrop-blur-xl z-30 flex-shrink-0">
          <SystemLogs logs={logs} status={status} logEndRef={logEndRef} />
        </div>
      </main>
    </div>
  );
}
