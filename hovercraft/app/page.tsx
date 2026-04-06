"use client";

import React, { useEffect, useState, useRef } from "react";
import { CoreAccess } from "@/components/windows/CoreAccess/CoreAccess";
import { RadarUplink } from "@/components/windows/RadarUplink/RadarUplink";
import { SystemLogs } from "@/components/windows/SystemLogs/SystemLogs";
import { SentinelTracking } from "@/components/windows/SentinelTracking/SentinelTracking";
import { ZionComms } from "@/components/windows/ZionComms/ZionComms";
import { ShipStatus } from "@/components/windows/ShipStatus/ShipStatus";
import { ShipInitialization } from "@/components/Initialization/ShipInitialization";

interface LogEntry {
  timestamp: string;
  level: string;
  message: string;
  category: string;
}

export default function Home() {
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
  const logEndRef = useRef<HTMLDivElement>(null);
  const socketRef = useRef<WebSocket | null>(null);

  // 함선 설정 로드 및 마운트 체크
  useEffect(() => {
    setMounted(true);
    const fetchConfig = async () => {
      try {
        const res = await fetch("/api/config");
        if (res.ok) {
          const data = await res.json();
          setShipConfig(data);
        }
      } catch (e) {
        console.error("Config fetch error:", e);
      } finally {
        setIsInitializing(false);
      }
    };
    fetchConfig();
  }, []);

  // 웹소켓 연결 및 데이터 수신
  useEffect(() => {
    if (!mounted) return;
    const socket = new WebSocket("ws://localhost:3001");
    socketRef.current = socket;

    socket.onopen = () => setStatus("CONNECTED");
    socket.onclose = () => setStatus("DISCONNECTED");
    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === "LOG") {
          setLogs((prev) => [...prev, {
            timestamp: new Date(data.timestamp).toLocaleTimeString(),
            level: data.level,
            message: data.message,
            category: data.category
          }].slice(-30));
        } else if (data.type === "INIT" || data.type === "STATUS_UPDATE") {
          // [사용자] 엔진 상태 데이터 동기화 (다양한 패킷 구조 대응)
          const active = data.active_circuit || data.data?.active_circuit || "None";
          const circuits = data.registered_circuits || data.circuits || data.data?.circuits || [];
          const details = data.active_circuit_details || data.data?.active_circuit_details;
          
          setSystemStatus({
            active_circuit: active,
            circuits: circuits,
            details: details
          });
        }
      } catch (e) {
        console.error("Signal parsing error:", e);
      }
    };

    return () => socket.close();
  }, [mounted]);

  const requestMcpStatus = () => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      const command = { type: "COMMAND", action: "get_operator_status", timestamp: new Date().toISOString() };
      socketRef.current.send(JSON.stringify(command));
      setLogs((prev) => [...prev, {
        timestamp: new Date().toLocaleTimeString(),
        level: "INFO",
        message: "Requesting MCP Status via Uplink...",
        category: "OPERATOR"
      }].slice(-30));
    } else {
      alert("Uplink not connected.");
    }
  };

  const requestSwitchCircuit = (name: string) => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      const command = {
        type: "COMMAND",
        action: "set_active_circuit",
        name: name,
        timestamp: new Date().toISOString()
      };
      socketRef.current.send(JSON.stringify(command));
      
      setLogs((prev) => [...prev, {
        timestamp: new Date().toLocaleTimeString(),
        level: "INFO",
        message: `Requesting direct switch to circuit: ${name}`,
        category: "UPLINK"
      }].slice(-30));
    }
  };

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  // [중요] 하이드레이션 오류 방지를 위해 마운트 전에는 정적 기본값만 출력
  const displayShipName = (mounted && shipConfig?.shipName) ? shipConfig.shipName : "NEBUCHADNEZZAR";
  const displayCaptainName = (mounted && shipConfig?.captainName) ? shipConfig.captainName.toUpperCase() : "CYPHER_01";
  const uplinkStatusText = status === 'CONNECTED' ? 'SECURE' : 'TERMINATED';
  const uplinkStatusClass = status === 'CONNECTED' ? 'text-green-400 font-bold' : 'text-red-600';

  return (
    <div className="flex flex-col min-h-screen text-on-surface bg-[#050505]">
      {mounted && !shipConfig && !isInitializing && (
        <ShipInitialization onComplete={(shipName, captainName) => setShipConfig({ shipName, captainName })} />
      )}

      {/* TopAppBar */}
      <header className="fixed top-0 left-0 w-full z-50 flex justify-between items-center px-4 h-12 bg-black border-b border-green-900/30">
        <div className="text-lg font-black text-green-500 drop-shadow-[0_0_8px_rgba(0,255,65,0.4)] font-mono uppercase tracking-tighter flex items-center gap-2">
          <span className="material-symbols-outlined text-sm">terminal</span>
          {`${displayShipName}_OS_V2.5`}
        </div>
        <nav className="flex gap-6 font-mono uppercase tracking-tighter text-[10px]">
          <a className="text-green-400 border-b-2 border-green-500 pb-1" href="#">MULTI_NODE_GRID</a>
          <a className="text-neutral-600 hover:text-green-300 transition-all duration-75" href="#">SATELLITE_UPLINK</a>
          <a className="text-neutral-600 hover:text-green-300 transition-all duration-75" href="#">VOID_PROXY</a>
        </nav>
        <div className="flex items-center gap-4 text-green-500">
          <div className={`text-[10px] font-mono mr-4 ${uplinkStatusClass} uppercase tracking-widest`}>
            {`UPLINK: ${uplinkStatusText}`}
          </div>
          <span className="material-symbols-outlined text-sm cursor-pointer hover:text-white transition-all">settings_input_component</span>
          <span className="material-symbols-outlined text-sm cursor-pointer hover:text-white transition-all">power_settings_new</span>
        </div>
      </header>

      {/* Main Grid Workspace */}
      <main className="mt-12 p-2 h-[calc(100vh-5.5rem)] grid grid-cols-12 grid-rows-6 gap-2 bg-black overflow-hidden">
        <CoreAccess 
          requestMcpStatus={requestMcpStatus} 
          requestSwitchCircuit={requestSwitchCircuit}
          systemStatus={systemStatus} 
        />
        <RadarUplink />
        <SystemLogs logs={logs} status={status} logEndRef={logEndRef} />
        <SentinelTracking />
        <ZionComms />
        <ShipStatus />
      </main>

      {/* Bottom Status Bar */}
      <footer className="fixed bottom-0 left-0 w-full z-50 flex justify-between items-center h-10 px-4 bg-black border-t border-green-900/30">
        <div className="flex gap-6">
          <div className="flex items-center gap-2 font-mono text-[9px] text-green-700">
            <span className={`w-2 h-2 rounded-full ${status === 'CONNECTED' ? 'bg-green-500 animate-pulse shadow-[0_0_8px_#22c55e]' : 'bg-red-600 shadow-[0_0_8px_#dc2626]'}`}></span>
            {`OPERATOR: ${status === 'CONNECTED' ? 'ONLINE' : 'OFFLINE'}`}
          </div>
          <div className="flex items-center gap-2 font-mono text-[9px] text-green-700">
            <span className="material-symbols-outlined text-xs">memory</span>
            MEM: 82%
          </div>
        </div>
        <div className="font-mono text-[9px] text-green-500/40">
          {`SYSTEM_UPTIME: 44:12:09:01 // OPERATOR_ID: ${displayCaptainName}`}
        </div>
        <div className="flex gap-4 items-center">
          <div className="h-2 w-24 bg-green-950 border border-green-900 relative">
            <div className="h-full bg-green-500 w-[65%]"></div>
          </div>
          <span className="material-symbols-outlined text-sm text-green-500 cursor-pointer">notifications_active</span>
        </div>
      </footer>
    </div>
  );
}
