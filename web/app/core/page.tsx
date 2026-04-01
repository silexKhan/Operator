'use client';

import { useEffect, useState } from 'react';

/**
 * [사용자] MCP 오퍼레이터 엔진의 가동 현황을 모니터링하는 관제실입니다. 
 */
export default function CoreStatusPage() {
  const [status, setStatus] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const fetchStatus = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/mcp');
      const data = await res.json();
      setStatus(data);
    } catch (e) {
      console.error("Failed to fetch engine status", e);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 className="neon-text" style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>
            SYSTEM STATUS
          </h2>
          <p style={{ color: 'var(--text-dim)' }}>
            MCP 오퍼레이터 엔진의 가동 현황 및 실시간 상태를 모니터링합니다.
          </p>
        </div>
        <button 
          onClick={fetchStatus}
          style={{ padding: '0.5rem 1rem', background: 'transparent', border: '1px solid var(--cyber-cyan)', color: 'var(--cyber-cyan)', borderRadius: '4px', cursor: 'pointer' }}
        >
          FORCE PING
        </button>
      </header>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '2rem' }}>
        {/* Connection Health */}
        <section className="card" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <h3 style={{ color: 'var(--cyber-cyan)', fontSize: '1.1rem' }}>ENGINE PULSE</h3>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <div className="status-badge" style={{ animation: 'pulse 2s infinite' }}>ACTIVE</div>
            <span style={{ color: 'var(--text-main)' }}>연결 상태: 안정적</span>
          </div>
          <div style={{ fontSize: '0.9rem', color: 'var(--text-dim)' }}>
             작업 공간을 자동으로 감지합니다.
          </div>
        </section>

        {/* Module Health */}
        <section className="card" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <h3 style={{ color: 'var(--cyber-amber)', fontSize: '1.1rem' }}>LOADED UNITS</h3>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span>Core Units:</span>
            <span style={{ color: 'var(--cyber-cyan)', fontWeight: 'bold' }}>
              {status?.core?.files ? Object.keys(status.core.files).length : '0'}
            </span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span>Active Circuits:</span>
            <span style={{ color: 'var(--cyber-cyan)', fontWeight: 'bold' }}>
              {/* [사용자] 정규화된 키값 'registered_circuits'를 사용합니다!  */}
              {status?.registered_circuits ? status.registered_circuits.length : '0'}
            </span>
          </div>
        </section>
      </div>

      {/* Engine Log Preview */}
      <section className="card" style={{ background: '#000', border: '1px solid #1a1a1a' }}>
        <h4 style={{ color: 'var(--text-dim)', marginBottom: '1rem', fontSize: '0.8rem' }}> RECENT ENGINE LOGS</h4>
        <div style={{ fontFamily: 'monospace', fontSize: '0.8rem', color: '#00ff00', lineHeight: '1.5' }}>
          <div>[INFO] MCP Server initialized on stdio...</div>
          <div>[INFO] Dynamic Discovery: found {status?.registered_circuits ? status.registered_circuits.length : '...'} circuits.</div>
          <div>[INFO] Protocol Reflection: Global constitution loaded.</div>
          <div style={{ color: 'var(--cyber-cyan)' }}>[INFO] Hot-swap capability: ENABLED </div>
          <div style={{ opacity: 0.5 }}>[WAIT] Waiting for incoming commands...</div>
        </div>
      </section>

      <style jsx>{`
        @keyframes pulse {
          0% { box-shadow: 0 0 0 0 rgba(0, 243, 255, 0.4); }
          70% { box-shadow: 0 0 0 10px rgba(0, 243, 255, 0); }
          100% { box-shadow: 0 0 0 0 rgba(0, 243, 255, 0); }
        }
      `}</style>
    </div>
  );
}
