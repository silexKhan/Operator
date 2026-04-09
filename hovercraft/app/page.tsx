"use client";

import React, { useEffect, useState, useRef } from "react";
import dynamic from "next/dynamic";

// 하이드레이션 오류 방지를 위해 SSR 제외 임포트
const CoreAccess = dynamic(() => import("@/components/windows/CoreAccess/CoreAccess").then(mod => mod.CoreAccess), { ssr: false });
const MissionSpecs = dynamic(() => import("@/components/windows/MissionSpecs/MissionSpecs").then(mod => mod.MissionSpecs), { ssr: false });
const AuditSecurity = dynamic(() => import("@/components/windows/AuditSecurity/AuditSecurity").then(mod => mod.AuditSecurity), { ssr: false });
const UnitProtocols = dynamic(() => import("@/components/windows/UnitProtocols/UnitProtocols").then(mod => mod.UnitProtocols), { ssr: false });
const ResourceMonitor = dynamic(() => import("@/components/windows/ResourceMonitor/ResourceMonitor").then(mod => mod.ResourceMonitor), { ssr: false });
const SystemLogs = dynamic(() => import("@/components/windows/SystemLogs/SystemLogs").then(mod => mod.SystemLogs), { ssr: false });

import { ShipInitialization } from "@/components/Initialization/ShipInitialization";

interface LogEntry {
  timestamp: string;
  level: string;
  message: string;
  category: string;
}

type TabType = "Overview" | "Protocols" | "Units" | "Circuits" | "Monitor";

export default function Home() {
  const [activeTab, setActiveTab] = useState<TabType>("Overview");
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [status, setStatus] = useState("DISCONNECTED");
  const [systemStatus, setSystemStatus] = useState<{ 
    active_circuit: string; 
    circuits: string[];
    details?: {
      name: string;
      protocols: string[];
      units: { name: string; mission: string; rules: string[] }[];
      actions: { name: string; description: string }[];
    }
  }>({ active_circuit: "None", circuits: [] });
  const [shipConfig, setShipConfig] = useState<{ shipName: string; captainName: string } | null>(null);
  const [isInitializing, setIsInitializing] = useState(true);
  const [mounted, setMounted] = useState(false);
  const [selectedCircuit, setSelectedCircuit] = useState<string | null>(null);
  const [circuitDetails, setCircuitDetails] = useState<any>(null);
  const [isEditingProtocols, setIsEditingProtocols] = useState(false);
  const [editedProtocols, setEditedProtocols] = useState("");
  const [isSaving, setIsSaving] = useState(false);
  const [language, setLanguage] = useState<"ko" | "en">("ko");
  const [isEditingCircuit, setIsEditingCircuit] = useState(false);
  const [editingCircuitData, setEditingCircuitData] = useState<any>(null);
  const [selectedCircuitRuleIndex, setSelectedCircuitRuleIndex] = useState<number | null>(null);
  const [editedCircuitRule, setEditedCircuitRule] = useState("");
  const [isGlobalProtocolsExpanded, setIsGlobalProtocolsExpanded] = useState(false);
  const logEndRef = useRef<HTMLDivElement>(null);

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

  const fetchCircuitDetails = (name: string) => {
    fetch(`/api/mcp/protocols?type=circuit_full&name=${name}`)
      .then(res => res.json())
      .then(data => {
        setCircuitDetails(data);
        setEditedProtocols(JSON.stringify(data.protocols || {}, null, 2));
      })
      .catch(err => console.error("Failed to fetch circuit details", err));
  };

  useEffect(() => {
    if (selectedCircuit) {
      fetchCircuitDetails(selectedCircuit);
    } else {
      setCircuitDetails(null);
      setIsEditingProtocols(false);
      setSelectedCircuitRuleIndex(null);
    }
  }, [selectedCircuit, language]);

  useEffect(() => {
    if (!mounted) return;

    const eventSource = new EventSource("/api/mcp/events");

    eventSource.onopen = () => setStatus("CONNECTED");
    eventSource.onerror = () => setStatus("DISCONNECTED");

    eventSource.addEventListener("state", (event: any) => {
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

    eventSource.addEventListener("log", (event: any) => {
      try {
        const log = JSON.parse(event.data);
        setLogs((prev) => [...prev, {
          timestamp: new Date(log.timestamp || Date.now()).toLocaleTimeString(),
          level: log.level || "INFO",
          message: log.message,
          category: log.category || "ENGINE"
        }].slice(-50));
      } catch (e) {
        console.error("Failed to parse SSE log data", e);
      }
    });

    return () => eventSource.close();
  }, [mounted]);

  const requestMcpStatus = () => {
    setLogs((prev) => [...prev, {
      timestamp: new Date().toLocaleTimeString(),
      level: "INFO",
      message: "Syncing MCP Status...",
      category: "OPERATOR"
    }].slice(-50));
  };

  const requestSwitchCircuit = (name: string) => {
    setSelectedCircuit(name);
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
          target: "circuit_overview",
          name: editingCircuitData.name,
          data: editingCircuitData
        })
      });

      if (res.ok) {
        setIsEditingCircuit(false);
        setEditingCircuitData(null);
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
    if (selectedCircuitRuleIndex === null || !selectedCircuit) return;
    setIsSaving(true);
    
    let newRules: string[] = [];
    if (Array.isArray(circuitDetails?.protocols)) {
      newRules = [...circuitDetails.protocols];
    } else if (circuitDetails?.protocols?.RULES) {
      newRules = [...circuitDetails.protocols.RULES];
    }

    newRules[selectedCircuitRuleIndex] = editedCircuitRule;

    try {
      const res = await fetch("/api/mcp/update", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          target: "circuit_protocols",
          name: selectedCircuit,
          data: { RULES: newRules }
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

  if (!mounted) return <div className="min-h-screen bg-neutral-950" />;

  const displayShipName = shipConfig?.shipName || "NEBUCHADNEZZAR";

  return (
    <div className="flex h-screen bg-neutral-950 text-neutral-200 font-sans overflow-hidden">
      {!shipConfig && !isInitializing && (
        <ShipInitialization onComplete={(shipName, captainName) => setShipConfig({ shipName, captainName })} />
      )}

      {/* Sidebar */}
      <aside className="w-64 border-r border-neutral-800 bg-neutral-900/50 flex flex-col">
        <div className="p-6 border-b border-neutral-800">
          <div className="flex items-center gap-2 mb-1">
            <span className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_#10b981]" />
            <h1 className="text-sm font-bold tracking-tight text-white uppercase">{displayShipName}</h1>
          </div>
          <p className="text-[11px] text-neutral-500 font-mono">SYSTEM_VERSION: 2.5</p>
        </div>

        <nav className="flex-1 p-4 space-y-1">
          <div className="px-3 py-2 text-[10px] font-bold text-neutral-500 uppercase tracking-widest">Navigation</div>
          {[
            { id: "Overview", icon: "dashboard", label: "Overview" },
            { id: "Protocols", icon: "rule", label: "Protocols" },
            { id: "Circuits", icon: "hub", label: "Circuits" },
            { id: "Units", icon: "memory", label: "Units" },
            { id: "Monitor", icon: "monitoring", label: "Monitor & Security" },
          ].map((item) => (
            <button
              key={item.id}
              onClick={() => {
                setActiveTab(item.id as TabType);
                if (item.id !== "Circuits") setSelectedCircuit(null);
              }}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors ${
                activeTab === item.id 
                  ? "bg-neutral-800 text-white" 
                  : "text-neutral-400 hover:bg-neutral-800/50 hover:text-neutral-200"
              }`}
            >
              <span className="material-symbols-outlined text-lg">{item.icon}</span>
              {item.label}
            </button>
          ))}
        </nav>

        <div className="p-4 border-t border-neutral-800">
          <div className="bg-neutral-950 rounded-lg p-3 border border-neutral-800">
            <div className="text-[10px] font-bold text-neutral-500 uppercase mb-2">Active Circuit</div>
            <div className="text-sm text-emerald-400 font-mono truncate">
              {systemStatus.active_circuit}
            </div>
            <div className="mt-2 flex items-center justify-between text-[10px] text-neutral-500">
              <span>Status</span>
              <span className={status === "CONNECTED" ? "text-emerald-500" : "text-red-500"}>
                {status}
              </span>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col min-w-0 bg-neutral-950">
        <header className="h-14 border-b border-neutral-800 flex items-center justify-between px-8 bg-neutral-900/20">
          <h2 className="text-lg font-medium text-white">{selectedCircuit ? `Circuit Detail: ${selectedCircuit}` : activeTab}</h2>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-1 bg-neutral-900 border border-neutral-800 rounded-lg p-1">
              <button 
                onClick={() => handleLanguageChange("ko")}
                className={`px-2 py-0.5 text-[10px] font-bold rounded ${language === "ko" ? "bg-emerald-600 text-white" : "text-neutral-500 hover:text-neutral-300"}`}
              >
                KO
              </button>
              <button 
                onClick={() => handleLanguageChange("en")}
                className={`px-2 py-0.5 text-[10px] font-bold rounded ${language === "en" ? "bg-emerald-600 text-white" : "text-neutral-500 hover:text-neutral-300"}`}
              >
                EN
              </button>
            </div>
            <button className="p-2 text-neutral-400 hover:text-white transition-colors">
              <span className="material-symbols-outlined text-xl">settings</span>
            </button>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto p-8">
          <div className="max-w-6xl mx-auto space-y-6">
            {activeTab === "Overview" && <MissionSpecs systemStatus={systemStatus} />}
            {activeTab === "Protocols" && <UnitProtocols systemStatus={systemStatus} />}
            
            {activeTab === "Circuits" && !selectedCircuit && (
              <div className="bg-neutral-900 border border-neutral-800 rounded-xl p-6">
                <div className="flex justify-between items-center mb-6">
                  <div>
                    <h3 className="text-xl font-bold text-white">Circuit Orchestration</h3>
                    <p className="text-sm text-neutral-500">Select a circuit to manage its operational metadata and configurations.</p>
                  </div>
                  <button 
                    onClick={() => {
                      const name = prompt("Enter new circuit name:");
                      if (name) {
                        fetch("/api/mcp/update", {
                          method: "POST",
                          headers: { "Content-Type": "application/json" },
                          body: JSON.stringify({ target: "circuit_overview", name: name.toLowerCase(), data: { name: name.toLowerCase(), description: "New Circuit", units: [], mission: { objective: "New Mission", criteria: [] } } })
                        }).then(res => res.ok && alert("Circuit created."));
                      }
                    }}
                    className="flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-sm rounded-lg transition-colors font-medium"
                  >
                    <span className="material-symbols-outlined text-sm">add</span>
                    Create New Circuit
                  </button>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4">
                  {systemStatus.circuits.filter(name => name !== "__pycache__").map((name) => (
                    <div key={name} className="group relative">
                      <button
                        onClick={() => requestSwitchCircuit(name)}
                        className={`w-full p-4 rounded-xl border text-left transition-all ${
                          systemStatus.active_circuit === name 
                          ? "bg-emerald-500/10 border-emerald-500 text-emerald-400 shadow-[0_0_15px_rgba(16,185,129,0.1)]" 
                          : "bg-neutral-950 border-neutral-800 text-neutral-400 hover:border-neutral-700 hover:text-neutral-200"
                        }`}
                      >
                        <div className="flex items-center justify-between mb-2">
                          <span className="material-symbols-outlined text-xl">{systemStatus.active_circuit === name ? 'hub' : 'settings_input_component'}</span>
                          {systemStatus.active_circuit === name && <span className="text-[10px] bg-emerald-500 text-black px-1.5 py-0.5 rounded font-bold uppercase">Active</span>}
                        </div>
                        <div className="font-bold text-sm uppercase font-mono truncate">{name}</div>
                      </button>
                      <button 
                        onClick={(e) => { e.stopPropagation(); handleEditCircuit(name); }}
                        className="absolute top-2 right-2 p-1.5 bg-neutral-800 text-neutral-400 rounded-md opacity-0 group-hover:opacity-100 hover:text-white hover:bg-neutral-700 transition-all z-10"
                      >
                        <span className="material-symbols-outlined text-sm">edit</span>
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {activeTab === "Circuits" && selectedCircuit && (
              <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-300">
                <div className="flex items-center gap-4 mb-2">
                  <button 
                    onClick={() => setSelectedCircuit(null)}
                    className="p-2 bg-neutral-800 hover:bg-neutral-700 text-neutral-400 hover:text-white rounded-lg transition-colors"
                  >
                    <span className="material-symbols-outlined">arrow_back</span>
                  </button>
                  <div>
                    <h3 className="text-xl font-bold text-white uppercase tracking-tight">{selectedCircuit}</h3>
                    <p className="text-[10px] text-neutral-500 font-mono">{circuitDetails?.overview?.description || "Circuit_Detail_Explorer"}</p>
                  </div>
                </div>

                <div className="space-y-6">
                  {/* Global Protocol Section (Foldable) */}
                  {circuitDetails?.global_protocols && (
                    <div className="bg-neutral-900 border border-neutral-800 rounded-xl overflow-hidden transition-all duration-300 shadow-sm">
                      <button 
                        onClick={() => setIsGlobalProtocolsExpanded(!isGlobalProtocolsExpanded)}
                        className="w-full px-6 py-4 flex items-center justify-between hover:bg-neutral-800/50 transition-colors bg-neutral-900/50"
                      >
                        <div className="flex items-center gap-2">
                          <span className="material-symbols-outlined text-emerald-500 text-lg">verified_user</span>
                          <h4 className="text-sm font-bold text-white uppercase tracking-widest">
                            {circuitDetails.global_protocols.title}
                          </h4>
                          <span className="ml-2 px-1.5 py-0.5 bg-emerald-500/10 text-[9px] text-emerald-500 rounded font-mono border border-emerald-500/20">INHERITED</span>
                        </div>
                        <span className={`material-symbols-outlined text-neutral-500 transition-transform duration-300 ${isGlobalProtocolsExpanded ? 'rotate-180' : ''}`}>
                          expand_more
                        </span>
                      </button>
                      
                      <div className={`overflow-hidden transition-all duration-500 ease-in-out ${isGlobalProtocolsExpanded ? 'max-h-[1000px] border-t border-neutral-800 p-6' : 'max-h-0'}`}>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          {circuitDetails.global_protocols.rules?.map((rule: string, idx: number) => (
                            <div key={idx} className="p-4 bg-neutral-950 border border-neutral-800 rounded-lg flex gap-3 items-start hover:border-emerald-500/30 transition-all">
                              <span className="text-emerald-500/60 font-mono text-[10px] mt-0.5">{String(idx + 1).padStart(2, '0')}</span>
                              <p className="text-xs text-neutral-300 leading-relaxed">{rule}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}

                  <div className="bg-neutral-900 border border-neutral-800 rounded-xl p-6">
                    <div className="flex justify-between items-center mb-6">
                      <div className="flex items-center gap-2">
                        <span className="material-symbols-outlined text-emerald-500">description</span>
                        <h4 className="text-sm font-bold text-white uppercase tracking-widest">Circuit-Specific Protocols</h4>
                      </div>
                    </div>
                    
                    <div className="space-y-3">
                      {Array.isArray(circuitDetails?.protocols) ? (
                        circuitDetails.protocols.map((rule: string, idx: number) => (
                          <div key={idx} className="group">
                            {selectedCircuitRuleIndex === idx ? (
                              <div className="p-4 bg-neutral-950 border border-emerald-500/50 rounded-xl space-y-3">
                                <textarea
                                  value={editedCircuitRule}
                                  onChange={(e) => setEditedCircuitRule(e.target.value)}
                                  className="w-full h-24 bg-transparent text-xs text-emerald-400 font-mono outline-none resize-none leading-relaxed"
                                  autoFocus
                                />
                                <div className="flex justify-end gap-2">
                                  <button onClick={() => setSelectedCircuitRuleIndex(null)} className="px-3 py-1 text-[10px] text-neutral-500 font-bold uppercase">Cancel</button>
                                  <button onClick={handleSaveIndividualCircuitRule} className="px-4 py-1 bg-emerald-600 text-black text-[10px] font-bold rounded uppercase">Apply Change</button>
                                </div>
                              </div>
                            ) : (
                              <button onClick={() => { setSelectedCircuitRuleIndex(idx); setEditedCircuitRule(rule); }} className="w-full p-5 bg-neutral-950 border border-neutral-800 rounded-xl text-left transition-all hover:border-emerald-500/30 group/item">
                                <div className="flex gap-4 items-start">
                                  <span className="text-emerald-500/40 font-mono text-[10px] mt-0.5">{String(idx + 1).padStart(2, '0')}</span>
                                  <p className="flex-1 text-xs text-neutral-300 leading-relaxed group-hover/item:text-emerald-400">{rule}</p>
                                  <span className="material-symbols-outlined text-sm text-neutral-700 opacity-0 group-hover/item:opacity-100 transition-opacity">edit</span>
                                </div>
                              </button>
                            )}
                          </div>
                        ))
                      ) : (
                        <p className="text-xs text-neutral-500 italic">No specific protocols defined.</p>
                      )}
                    </div>
                  </div>

                  <div className="bg-neutral-900 border border-neutral-800 rounded-xl p-6">
                    <div className="flex items-center gap-2 mb-6">
                      <span className="material-symbols-outlined text-blue-500">task</span>
                      <h4 className="text-sm font-bold text-white uppercase tracking-widest">Global Mission</h4>
                    </div>
                    <div className="p-4 bg-neutral-950 border border-neutral-800 rounded-lg">
                      <p className="text-sm text-emerald-400 font-medium">{circuitDetails?.mission?.objective || "No mission objective set."}</p>
                      <div className="mt-4 space-y-2">
                        {circuitDetails?.mission?.criteria?.map((c: string, idx: number) => (
                          <div key={idx} className="flex items-start gap-2 text-xs text-neutral-500">
                            <span className="text-emerald-500 mt-0.5">●</span>
                            {c}
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  <div className="bg-neutral-900 border border-neutral-800 rounded-xl p-6">
                    <div className="flex items-center gap-2 mb-6">
                      <span className="material-symbols-outlined text-amber-500">memory</span>
                      <h4 className="text-sm font-bold text-white uppercase tracking-widest">Assigned Units</h4>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
                      {circuitDetails?.units?.length > 0 ? (
                        circuitDetails.units.map((unit: any, idx: number) => (
                          <div key={idx} className="flex items-center justify-between p-3 bg-neutral-950 border border-neutral-800 rounded-lg hover:border-emerald-500/30 transition-colors">
                            <span className="text-xs font-bold text-neutral-300 font-mono uppercase truncate">{unit.name}</span>
                            <span className="material-symbols-outlined text-emerald-500 text-sm">verified</span>
                          </div>
                        ))
                      ) : (
                        <p className="text-xs text-neutral-500 italic text-center py-4 col-span-full">No units assigned.</p>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === "Units" && (
              <CoreAccess 
                requestMcpStatus={requestMcpStatus} 
                systemStatus={systemStatus} 
                language={language}
              />
            )}
            
            {activeTab === "Monitor" && (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <ResourceMonitor systemStatus={systemStatus} />
                <AuditSecurity logs={logs} systemStatus={systemStatus} />
              </div>
            )}
          </div>
        </div>

        {/* Circuit Edit Modal */}
        {isEditingCircuit && editingCircuitData && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
            <div className="bg-neutral-900 border border-neutral-800 rounded-2xl w-full max-w-2xl shadow-2xl overflow-hidden">
              <div className="px-6 py-4 border-b border-neutral-800 flex justify-between items-center bg-neutral-900/50">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-emerald-500/10 rounded-lg text-emerald-500">
                    <span className="material-symbols-outlined">settings_input_component</span>
                  </div>
                  <h3 className="text-white font-bold uppercase tracking-tight">Configure Circuit: {editingCircuitData.name}</h3>
                </div>
                <button onClick={() => setIsEditingCircuit(false)} className="text-neutral-500 hover:text-white"><span className="material-symbols-outlined">close</span></button>
              </div>
              <div className="p-6 space-y-6 max-h-[70vh] overflow-y-auto">
                <div className="space-y-2">
                  <label className="text-[10px] font-bold text-neutral-500 uppercase tracking-widest">Description</label>
                  <textarea 
                    value={typeof editingCircuitData.description === 'object' ? editingCircuitData.description[language] : editingCircuitData.description}
                    onChange={(e) => setEditingCircuitData({ ...editingCircuitData, description: typeof editingCircuitData.description === 'object' ? { ...editingCircuitData.description, [language]: e.target.value } : e.target.value })}
                    className="w-full bg-neutral-950 border border-neutral-800 rounded-lg p-3 text-sm text-neutral-200 h-20 outline-none"
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-[10px] font-bold text-neutral-500 uppercase tracking-widest">Objective</label>
                  <input 
                    value={typeof editingCircuitData.mission?.objective === 'object' ? editingCircuitData.mission.objective[language] : editingCircuitData.mission?.objective}
                    onChange={(e) => setEditingCircuitData({ ...editingCircuitData, mission: { ...editingCircuitData.mission, objective: typeof editingCircuitData.mission?.objective === 'object' ? { ...editingCircuitData.mission.objective, [language]: e.target.value } : e.target.value } })}
                    className="w-full bg-neutral-950 border border-neutral-800 rounded-lg px-3 py-2 text-sm text-white"
                  />
                </div>
                <div className="space-y-3">
                  <div className="flex justify-between items-center"><label className="text-[10px] font-bold text-neutral-500 uppercase tracking-widest">Criteria</label><button onClick={() => setEditingCircuitData({ ...editingCircuitData, mission: { ...editingCircuitData.mission, criteria: [...(editingCircuitData.mission?.criteria || []), language === "ko" ? { ko: "", en: "" } : { ko: "", en: "" }] } })} className="text-[10px] text-emerald-400 font-bold uppercase">+ Add</button></div>
                  <div className="space-y-2">
                    {(editingCircuitData.mission?.criteria || []).map((c: any, i: number) => (
                      <div key={i} className="flex gap-2">
                        <input value={typeof c === 'object' ? c[language] : c} onChange={(e) => { const newCriteria = [...editingCircuitData.mission.criteria]; newCriteria[i] = typeof c === 'object' ? { ...c, [language]: e.target.value } : e.target.value; setEditingCircuitData({ ...editingCircuitData, mission: { ...editingCircuitData.mission, criteria: newCriteria } }); }} className="flex-1 bg-neutral-950 border border-neutral-800 rounded-lg px-3 py-2 text-xs text-neutral-300" />
                        <button onClick={() => setEditingCircuitData({ ...editingCircuitData, mission: { ...editingCircuitData.mission, criteria: editingCircuitData.mission.criteria.filter((_: any, idx: number) => idx !== i) } })} className="text-neutral-600 hover:text-red-500"><span className="material-symbols-outlined text-sm">delete</span></button>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
              <div className="px-6 py-4 bg-neutral-900/80 border-t border-neutral-800 flex justify-end gap-3">
                <button onClick={() => setIsEditingCircuit(false)} className="px-4 py-2 text-xs font-bold text-neutral-500 uppercase tracking-widest">Cancel</button>
                <button onClick={handleSaveCircuitOverview} disabled={isSaving} className="px-6 py-2 bg-emerald-600 text-black text-xs font-bold rounded-lg uppercase tracking-widest">{isSaving ? "Syncing..." : "Save"}</button>
              </div>
            </div>
          </div>
        )}

        {/* Bottom Log Panel */}
        <div className="h-48 border-t border-neutral-800 bg-neutral-900/50">
          <SystemLogs logs={logs} status={status} logEndRef={logEndRef} />
        </div>
      </main>
    </div>
  );
}
