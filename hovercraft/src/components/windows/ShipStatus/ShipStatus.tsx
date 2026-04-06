"use client";

import React, { useEffect, useState } from "react";

export const ShipStatus: React.FC = () => {
  const [mounted, setMounted] = useState(false);
  const [metrics, setMetrics] = useState({
    fuel: 85,
    engineTemp: 182,
    shieldEnergy: 100,
    hullIntegrity: 98,
  });

  useEffect(() => {
    setMounted(true);
    // 실시간 데이터 시뮬레이션
    const interval = setInterval(() => {
      setMetrics(prev => ({
        ...prev,
        fuel: Math.max(0, prev.fuel - 0.01),
        engineTemp: 180 + Math.random() * 5,
        shieldEnergy: 95 + Math.random() * 5,
      }));
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  if (!mounted) {
    return (
      <section className="col-span-3 row-span-3 flex flex-col terminal-window overflow-hidden animate-pulse">
        <div className="terminal-header px-2 py-1 flex justify-between items-center">
          <span className="text-[10px] font-mono text-green-500 crt-glow">SHIP_STATUS.sys</span>
        </div>
        <div className="flex-1 p-3 font-mono text-[10px] text-green-500/30">
          Loading ship telemetry...
        </div>
      </section>
    );
  }

  const MetricBar: React.FC<{ label: string; value: number; max: number; color?: string }> = ({ label, value, max, color = "bg-green-500" }) => (
    <div className="space-y-1">
      <div className="flex justify-between text-[8px] uppercase tracking-tighter">
        <span className="text-green-700">{label}</span>
        <span className="text-green-500">{value.toFixed(1)} / {max}</span>
      </div>
      <div className="h-1.5 w-full bg-green-950 border border-green-900/30 overflow-hidden">
        <div 
          className={`h-full ${color} transition-all duration-1000`} 
          style={{ width: `${(value / max) * 100}%` }}
        ></div>
      </div>
    </div>
  );

  return (
    <section className="col-span-3 row-span-3 flex flex-col terminal-window overflow-hidden">
      <div className="terminal-header px-2 py-1 flex justify-between items-center bg-green-500/5">
        <div className="flex items-center gap-2">
          <span className="material-symbols-outlined text-[10px] text-green-500">monitoring</span>
          <span className="text-[10px] font-mono text-green-500 crt-glow">SHIP_STATUS.sys</span>
        </div>
        <div className="flex gap-1">
          <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse shadow-[0_0_8px_#22c55e]"></div>
        </div>
      </div>
      
      <div className="flex-1 p-3 font-mono text-[10px] space-y-4 overflow-y-auto telemetry-scroll">
        <div className="grid grid-cols-2 gap-4">
          <div className="p-2 border border-green-900/30 bg-green-500/5 flex flex-col items-center justify-center">
            <span className="text-[18px] font-black text-green-400">{metrics.hullIntegrity}%</span>
            <span className="text-[8px] text-green-900 uppercase">Hull Integrity</span>
          </div>
          <div className="p-2 border border-green-900/30 bg-green-500/5 flex flex-col items-center justify-center">
            <span className="text-[18px] font-black text-green-400">{metrics.shieldEnergy.toFixed(0)}%</span>
            <span className="text-[8px] text-green-900 uppercase">Shield Power</span>
          </div>
        </div>

        <div className="space-y-3">
          <MetricBar label="Core Fuel Reserves" value={metrics.fuel} max={100} />
          <MetricBar label="Engine Temperature (K)" value={metrics.engineTemp} max={300} color={metrics.engineTemp > 250 ? "bg-red-500 shadow-[0_0_8px_#ef4444]" : "bg-green-500"} />
          <MetricBar label="Oxygen Levels" value={99.4} max={100} />
        </div>

        <div className="mt-4 pt-3 border-t border-green-900/30">
          <p className="text-[8px] text-green-900 uppercase mb-2">Sub-system Diagnostics</p>
          <div className="space-y-1">
            <div className="flex justify-between items-center text-[9px]">
              <span className="text-green-700">├ Navigation Array</span>
              <span className="text-green-400">NOMINAL</span>
            </div>
            <div className="flex justify-between items-center text-[9px]">
              <span className="text-green-700">├ Weapon Systems</span>
              <span className="text-orange-500 font-bold">LOCKED</span>
            </div>
            <div className="flex justify-between items-center text-[9px]">
              <span className="text-green-700">└ External Uplink</span>
              <span className="text-green-400 font-bold">SECURE</span>
            </div>
          </div>
        </div>
      </div>

      <div className="p-2 bg-green-950/20 flex justify-between items-center border-t border-green-900/30">
        <button className="px-2 py-0.5 border border-green-900 text-[8px] text-green-700 uppercase hover:bg-green-500 hover:text-black transition-all">
          Emergency Purge
        </button>
        <span className="text-[8px] text-green-900 font-mono italic">Nebuchadnezzar-Class // Hovercraft</span>
      </div>
    </section>
  );
};
