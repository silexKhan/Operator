"use client";

import React, { useEffect, useState, useRef } from "react";

interface LogEntry {
  timestamp: string;
  level: string;
  message: string;
  category: string;
}

export default function Home() {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [status, setStatus] = useState("DISCONNECTED");
  const logEndRef = useRef<HTMLDivElement>(null);
  const socketRef = useRef<WebSocket | null>(null);

  // 웹소켓 연결 및 데이터 수신
  useEffect(() => {
    // [사용자] 엔진 업링크 시도 (3001 Port)
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
          }].slice(-30)); // 최근 30개 기록 유지
        }
      } catch (e) {
        console.error("Signal parsing error:", e);
      }
    };

    return () => socket.close();
  }, []);

  // MCP 상태 요청 함수
  const requestMcpStatus = () => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      const command = {
        type: "COMMAND",
        action: "get_operator_status",
        timestamp: new Date().toISOString()
      };
      socketRef.current.send(JSON.stringify(command));
      
      // 요청 로그 즉시 추가 (낙관적 UI)
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

  // 로그 스크롤 자동 하단 이동
  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  return (
    <div className="flex flex-col min-h-screen text-on-surface bg-[#050505]">
      {/* TopAppBar */}
      <header className="fixed top-0 left-0 w-full z-50 flex justify-between items-center px-4 h-12 bg-black border-b border-green-900/30">
        <div className="text-lg font-black text-green-500 drop-shadow-[0_0_8px_rgba(0,255,65,0.4)] font-mono uppercase tracking-tighter flex items-center gap-2">
          <span className="material-symbols-outlined text-sm">terminal</span>
          NEBUCHADNEZZAR_OS_V2.5
        </div>
        <nav className="flex gap-6 font-mono uppercase tracking-tighter text-[10px]">
          <a className="text-green-400 border-b-2 border-green-500 pb-1" href="#">MULTI_NODE_GRID</a>
          <a className="text-neutral-600 hover:text-green-300 transition-all duration-75" href="#">SATELLITE_UPLINK</a>
          <a className="text-neutral-600 hover:text-green-300 transition-all duration-75" href="#">VOID_PROXY</a>
        </nav>
        <div className="flex items-center gap-4 text-green-500">
          <div className="text-[10px] font-mono mr-4 text-green-900 uppercase">UPLINK: {status}</div>
          <span className="material-symbols-outlined text-sm cursor-pointer hover:text-white transition-all">settings_input_component</span>
          <span className="material-symbols-outlined text-sm cursor-pointer hover:text-white transition-all">power_settings_new</span>
        </div>
      </header>

      {/* Main Grid Workspace */}
      <main className="mt-12 p-2 h-[calc(100vh-5.5rem)] grid grid-cols-12 grid-rows-6 gap-2 bg-black overflow-hidden">
        {/* Window 1: CORE_ACCESS */}
        <section className="col-span-4 row-span-3 flex flex-col terminal-window overflow-hidden">
          <div className="terminal-header px-2 py-1 flex justify-between items-center">
            <span className="text-[10px] font-mono text-green-500 crt-glow">CORE_ACCESS.sys</span>
            <div className="flex gap-1">
              <div className="w-2 h-2 rounded-full bg-green-900"></div>
              <div className="w-2 h-2 rounded-full bg-green-500"></div>
            </div>
          </div>
          <div className="flex-1 p-3 font-mono text-[10px] text-green-500/80 overflow-hidden telemetry-scroll flex flex-col">
            <div className="space-y-1">
              <p className="text-green-400 opacity-60">Initializing core handshake...</p>
              <p className="text-green-400 opacity-70">Bypassing mainframe firewall [SEC_LVL_9]</p>
              <p className="text-green-400 opacity-80">&gt; Decrypting packet 0x4F22... [OK]</p>
              <p className="text-green-400 opacity-90">&gt; Handshake established with main_node_0</p>
              <p className="text-green-400">Welcome, Operator. Awaiting instruction.</p>
              <p className="text-green-500 mt-4">_ROOT_PERMISSION_GRANTED</p>
              <button 
                onClick={requestMcpStatus}
                className="mt-4 px-3 py-1 border border-green-500 text-[10px] font-mono text-green-500 hover:bg-green-500 hover:text-black transition-all cursor-pointer flex items-center gap-2 uppercase"
              >
                <span className="material-symbols-outlined text-xs">analytics</span>
                Check MCP Status
              </button>
            </div>
          </div>
          <div className="bg-black/50 border-t border-green-900/30 p-2 flex items-center gap-2">
            <span className="text-green-600 font-mono text-[10px]">root@neb:~#</span>
            <input autoFocus className="bg-transparent border-none text-[10px] font-mono text-green-400 focus:ring-0 p-0 flex-1 outline-none" placeholder="execute --trace --force" type="text" />
            <span className="w-1.5 h-3 bg-green-500 cursor-blink"></span>
          </div>
        </section>

        {/* Window 2: RADAR_UPLINK */}
        <section className="col-span-5 row-span-4 flex flex-col terminal-window overflow-hidden">
          <div className="terminal-header px-2 py-1 flex justify-between items-center">
            <span className="text-[10px] font-mono text-green-500 crt-glow">RADAR_UPLINK.map</span>
            <span className="text-[9px] text-green-900 font-mono">LAT: 32.122 / LONG: -114.908</span>
          </div>
          <div className="flex-1 relative flex items-center justify-center p-4 bg-green-950/5">
            <img alt="3D tactical wireframe map" className="w-full h-full object-cover opacity-10 mix-blend-screen absolute" src="https://lh3.googleusercontent.com/aida-public/AB6AXuCxXrbq5q9X1NfJ1x-_3WVDQ2cKJKf3kdR2GmS_ZRrAQbA_oOqw8PNEGJ7ST0REQO4uQpxIO-S6uwB0OCWK4wd_4HVxdql-2Wk3maHZV7AwCvOOiS9h4bPQ2OfBHtov9S40jdUZKLWMUwYO9fpvyZy5w_09yZf1sm-EHut52_wARZsflLYvulymZws3KfRL-KCz2AFayo___m122Dj-VlKdtaTdtdsRLjOSc7ezbcSz5IfH4OBnwvpinoAAjXBSPTSWZvZ5aWaX9w" />
            <div className="w-[200px] h-[200px] border border-green-500/20 rounded-full flex items-center justify-center relative">
              <div className="w-[100px] h-[100px] border border-green-500/10 rounded-full"></div>
              <div className="absolute w-full h-[1px] bg-green-500/10"></div>
              <div className="absolute h-full w-[1px] bg-green-500/10"></div>
              <div className="w-1.5 h-1.5 bg-green-400 rounded-full absolute translate-x-10 -translate-y-12 animate-pulse"></div>
              <div className="w-1.5 h-1.5 bg-green-400 rounded-full absolute -translate-x-20 translate-y-4 animate-pulse"></div>
            </div>
            <div className="absolute bottom-4 left-4 font-mono text-[9px] text-green-500/60 leading-tight uppercase">
              TARGET_LOCKED: SENTINEL_01<br />
              RANGE: 0.42km<br />
              THREAT_LEVEL: OMEGA
            </div>
          </div>
          <div className="bg-black/50 border-t border-green-900/30 p-2 flex items-center gap-2">
            <span className="text-green-600 font-mono text-[10px]">scan@neb:~#</span>
            <input className="bg-transparent border-none text-[10px] font-mono text-green-400 focus:ring-0 p-0 flex-1 outline-none" placeholder="ping --freq 0.8hz" type="text" />
            <span className="w-1.5 h-3 bg-green-500 cursor-blink"></span>
          </div>
        </section>

        {/* Window 3: SYSTEM_LOGS (Real-time Linked) */}
        <section className="col-span-3 row-span-6 flex flex-col terminal-window overflow-hidden">
          <div className="terminal-header px-2 py-1 flex justify-between items-center">
            <span className="text-[10px] font-mono text-green-500 crt-glow">SYSTEM_LOGS.raw</span>
            <span className={`text-[9px] ${status === 'CONNECTED' ? 'text-green-500' : 'text-green-900'} animate-pulse`}>
              ● {status === 'CONNECTED' ? 'STREAMING' : 'OFFLINE'}
            </span>
          </div>
          <div className="flex-1 p-3 font-mono text-[9px] text-green-500/70 overflow-y-auto custom-scrollbar flex flex-col">
            <div className="space-y-1">
              {logs.length === 0 ? (
                <p className="opacity-50 italic">Awaiting telemetry downlink...</p>
              ) : (
                logs.map((log, i) => (
                  <p key={i} className="leading-tight">
                    <span className="text-green-900">[{log.timestamp}]</span>{' '}
                    <span className={log.level === 'END' ? 'text-blue-400' : 'text-green-400'}>
                      {log.category}: {log.message}
                    </span>
                  </p>
                ))
              )}
              <div ref={logEndRef} />
            </div>
          </div>
          <div className="bg-black/50 border-t border-green-900/30 p-2 flex items-center gap-2">
            <span className="text-green-600 font-mono text-[10px]">logs@neb:~#</span>
            <input className="bg-transparent border-none text-[10px] font-mono text-green-400 focus:ring-0 p-0 flex-1 outline-none" placeholder="tail -f /var/log/sys" type="text" />
            <span className="w-1.5 h-3 bg-green-500 cursor-blink"></span>
          </div>
        </section>

        {/* Window 4: SENTINEL_TRACKING */}
        <section className="col-span-4 row-span-3 flex flex-col terminal-window overflow-hidden">
          <div className="terminal-header px-2 py-1 flex justify-between items-center">
            <span className="text-[10px] font-mono text-green-500 crt-glow">SENTINEL_TRACKING.bin</span>
            <span className="material-symbols-outlined text-[10px] text-red-500 animate-ping">emergency</span>
          </div>
          <div className="flex-1 p-3 font-mono text-[9px] text-green-500/80 overflow-hidden flex flex-col">
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div className="border border-green-900/50 p-2 bg-green-500/5">
                <div className="text-[8px] text-green-900 mb-1">SIGNATURE_ALPHA</div>
                <div className="h-2 bg-black border border-green-900 relative">
                  <div className="h-full bg-green-500 w-[72%] shadow-[0_0_8px_rgba(0,255,65,0.4)]"></div>
                </div>
              </div>
              <div className="border border-green-900/50 p-2 bg-green-500/5">
                <div className="text-[8px] text-green-900 mb-1">INTERCEPT_PROB</div>
                <div className="h-2 bg-black border border-green-900 relative">
                  <div className="h-full bg-green-500 w-[12%]"></div>
                </div>
              </div>
            </div>
            <div className="flex-1 overflow-hidden opacity-40 leading-none">
              01100111 01101111 01100100 00100000 01101001 01110011 00100000 01100100 01100001 01100100 00101110 00100000 01110111 01100101 00100000 01101011 01100001 01110110 01100101 00100000 01101011 01101001 01101100 01101100 01100101 01100100 00100000 01101000 01101001 01101101
            </div>
          </div>
          <div className="bg-black/50 border-t border-green-900/30 p-2 flex items-center gap-2">
            <span className="text-green-600 font-mono text-[10px]">track@neb:~#</span>
            <input className="bg-transparent border-none text-[10px] font-mono text-green-400 focus:ring-0 p-0 flex-1 outline-none" placeholder="scramble --all" type="text" />
            <span className="w-1.5 h-3 bg-green-500 cursor-blink"></span>
          </div>
        </section>

        {/* Window 5: ZION_COMMS */}
        <section className="col-span-5 row-span-2 flex flex-col terminal-window overflow-hidden">
          <div className="terminal-header px-2 py-1 flex justify-between items-center">
            <span className="text-[10px] font-mono text-green-500 crt-glow">ZION_COMMS.ext</span>
            <div className="flex items-center gap-2">
              <span className="text-[8px] font-mono text-green-900">ENCRYPTION: 1024_RSA</span>
            </div>
          </div>
          <div className="flex-1 p-3 flex flex-col font-mono text-[10px]">
            <div className="flex gap-2 mb-2">
              <span className="text-green-900">[MORPHEUS]</span>
              <span className="text-green-400 italic">"We need the operator to pull the main sequence."</span>
            </div>
            <div className="flex gap-2">
              <span className="text-green-900">[TANK]</span>
              <span className="text-green-400 italic">"Loading the program now. Hold on."</span>
            </div>
          </div>
          <div className="bg-black/50 border-t border-green-900/30 p-2 flex items-center gap-2">
            <span className="text-green-600 font-mono text-[10px]">tank@neb:~#</span>
            <input className="bg-transparent border-none text-[10px] font-mono text-green-400 focus:ring-0 p-0 flex-1 outline-none" placeholder="say --voice morpheus 'Initiate exit'" type="text" />
            <span className="w-1.5 h-3 bg-green-500 cursor-blink"></span>
          </div>
        </section>
      </main>

      {/* Bottom Status Bar */}
      <footer className="fixed bottom-0 left-0 w-full z-50 flex justify-between items-center h-10 px-4 bg-black border-t border-green-900/30">
        <div className="flex gap-6">
          <div className="flex items-center gap-2 font-mono text-[9px] text-green-700">
            <span className={`w-2 h-2 rounded-full ${status === 'CONNECTED' ? 'bg-green-500 animate-pulse' : 'bg-red-900'}`}></span>
            LINK: {status}
          </div>
          <div className="flex items-center gap-2 font-mono text-[9px] text-green-700">
            <span className="material-symbols-outlined text-xs">memory</span>
            MEM: 82%
          </div>
        </div>
        <div className="font-mono text-[9px] text-green-500/40">
          SYSTEM_UPTIME: 44:12:09:01 // OPERATOR_ID: CYPHER_01
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
