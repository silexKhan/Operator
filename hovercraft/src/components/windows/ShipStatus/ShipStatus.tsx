"use client";

import React, { useState, useEffect, useCallback } from "react";

const MetricBar: React.FC<{ label: string; value: number; max: number; color?: string }> = ({ label, value, max, color = "bg-green-500" }) => (
  <div className="space-y-1">
    <div className="flex justify-between text-[8px] uppercase tracking-tighter">
      <span className="text-neutral-500 font-bold">{label}</span>
      <span className="text-neutral-400 font-mono">{value.toFixed(1)} / {max}</span>
    </div>
    <div className="h-1 w-full bg-neutral-800 rounded-full overflow-hidden">
      <div 
        className={`h-full transition-all duration-500 ease-out ${color}`} 
        style={{ width: `${(value / max) * 100}%` }}
      ></div>
    </div>
  </div>
);

export const ShipStatus: React.FC = () => {
  const [mounted, setMounted] = useState(false);
  const [metrics, setMetrics] = useState({
    fuel: 84.2,
    engineTemp: 210.5,
    shields: 100
  });

  const simulateMetrics = useCallback(() => {
    setMetrics(prev => ({
      fuel: Math.max(0, prev.fuel - 0.01),
      engineTemp: 210 + (Math.random() * 5),
      shields: prev.shields
    }));
  }, []);

  useEffect(() => {
    // 동기 호출 방지를 위해 마운트 후에만 실행되도록 분리
    const timeout = setTimeout(() => setMounted(true), 0);
    return () => clearTimeout(timeout);
  }, []);

  useEffect(() => {
    if (!mounted) return;
    const interval = setInterval(simulateMetrics, 3000);
    return () => clearInterval(interval);
  }, [mounted, simulateMetrics]);

  if (!mounted) {
    return <div className="col-span-3 row-span-3 bg-neutral-900 border border-neutral-800 rounded-xl" />;
  }

  return (
    <section className="col-span-3 row-span-3 flex flex-col bg-neutral-900 border border-neutral-800 rounded-xl overflow-hidden shadow-sm">
      <div className="px-4 py-3 border-b border-neutral-800 bg-neutral-900/50 flex items-center gap-3">
        <div className="p-1.5 bg-green-500/10 rounded">
          <span className="material-symbols-outlined text-green-500 text-sm">rocket_launch</span>
        </div>
        <h3 className="text-[10px] font-bold text-white uppercase tracking-widest">Vessel Core Status</h3>
      </div>

      <div className="p-4 flex-1 flex flex-col justify-center">
        <div className="space-y-3">
          <MetricBar label="Core Fuel Reserves" value={metrics.fuel} max={100} />
          <MetricBar 
            label="Engine Temperature (K)" 
            value={metrics.engineTemp} 
            max={300} 
            color={metrics.engineTemp > 250 ? "bg-red-500 shadow-[0_0_8px_#ef4444]" : "bg-green-500"} 
          />
          <MetricBar label="Oxygen Levels" value={99.4} max={100} />
        </div>

        <div className="mt-4 pt-3 border-t border-neutral-800">
          <div className="flex justify-between items-center">
            <span className="text-[8px] text-neutral-500 uppercase font-bold tracking-tighter">Shield Buffer</span>
            <span className="text-[10px] text-blue-400 font-mono font-bold">{metrics.shields}%</span>
          </div>
          <div className="mt-1 grid grid-cols-10 gap-0.5">
            {[...Array(10)].map((_, i) => (
              <div key={i} className={`h-1.5 rounded-sm ${i < 8 ? 'bg-blue-500/40' : 'bg-neutral-800'}`} />
            ))}
          </div>
        </div>
      </div>

      <div className="px-4 py-2 bg-neutral-950/50 border-t border-neutral-800">
        <div className="flex items-center gap-2">
          <span className="w-1 h-1 rounded-full bg-green-500 animate-pulse" />
          <span className="text-[8px] text-neutral-600 font-mono uppercase tracking-widest">Propulsion_Stable</span>
        </div>
      </div>
    </section>
  );
};
