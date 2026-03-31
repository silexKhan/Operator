'use client';

import { useEffect, useState } from 'react';
import CircuitMap from './components/CircuitMap';

/**
 * [대장님 🎯] 모든 Circuit의 가동 상태를 조망하는 통합 상황실입니다. 🛡️⚡️
 */
export default function Home() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    fetchBlueprint();
  }, []);

  const fetchBlueprint = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/mcp');
      const json = await res.json();
      setData(json);
    } catch (e) {
      console.error("Failed to fetch blueprint", e);
    }
    setLoading(false);
  };

  const handleNodeClick = (name: string) => {
    window.location.href = `/circuits/${name.toLowerCase()}`;
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
        <div>
          <h2 className="neon-text" style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>
            MISSION DASHBOARD
          </h2>
          <p style={{ color: 'var(--text-dim)' }}>
            실시간 프로젝트 아키텍처 관측 및 AI 행동 규약 제어
          </p>
        </div>
        <button 
          onClick={fetchBlueprint}
          disabled={loading}
          style={{ 
            padding: '0.75rem 1.5rem', 
            background: loading ? 'transparent' : 'var(--cyber-cyan)', 
            border: '1px solid var(--cyber-cyan)', 
            color: loading ? 'var(--cyber-cyan)' : 'var(--bg-dark)',
            cursor: 'pointer',
            borderRadius: '4px',
            fontWeight: 'bold'
          }}>
          {loading ? 'RE-SCANNING...' : 'SYSTEM RE-SCAN'}
        </button>
      </header>

      {/* Visual Architecture Map */}
      <section>
        {mounted && data?.dependency_graph ? (
          <CircuitMap graphData={data.dependency_graph} onNodeClick={handleNodeClick} />
        ) : (
          <div className="card" style={{ height: '400px', display: 'flex', alignItems: 'center', justifyContent: 'center', borderStyle: 'dashed' }}>
            <p style={{ color: 'var(--text-dim)' }}>Initializing Architecture Map... 📡</p>
          </div>
        )}
      </section>

      {/* Summary Cards */}
      <section style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem' }}>
        <div className="card">
          <h3 style={{ fontSize: '0.9rem', color: 'var(--text-dim)', marginBottom: '1rem' }}>ACTIVE CIRCUITS</h3>
          <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>
            {mounted && data ? (data.registered_circuits?.length || 0) : '0'} Lines
          </div>
          <div style={{ marginTop: '0.5rem', color: 'var(--cyber-cyan)', fontSize: '0.8rem' }}>
            {data ? '🟢 Connection Stable' : '⚪ Standby'}
          </div>
        </div>
        
        <div className="card">
          <h3 style={{ fontSize: '0.9rem', color: 'var(--text-dim)', marginBottom: '1rem' }}>SYSTEM LOAD</h3>
          <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>0.02ms</div>
          <div style={{ marginTop: '0.5rem', color: 'var(--cyber-amber)', fontSize: '0.8rem' }}>Low Latency</div>
        </div>

        <div className="card">
          <h3 style={{ fontSize: '0.9rem', color: 'var(--text-dim)', marginBottom: '1rem' }}>MODULES SCANNED</h3>
          <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>
            {mounted && data ? (Object.keys(data.core?.files || {}).length + Object.keys(data.circuits?.files || {}).length) : '0'} Units
          </div>
          <div style={{ marginTop: '0.5rem', color: 'var(--cyber-cyan)', fontSize: '0.8rem' }}>AST Discovery Complete</div>
        </div>
      </section>

      {/* Domain Details (Vertical Stack for Mobile 📱) */}
      {mounted && data && (
        <section style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          {/* CORE Domain */}
          <div className="card">
            <h5 className="neon-text" style={{ marginBottom: '1.5rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem' }}>
              📂 CORE ENGINE
            </h5>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {data.core?.files ? Object.entries(data.core.files).map(([path, info]: [string, any]) => (
                <div key={path} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)', paddingBottom: '1rem' }}>
                  <span style={{ color: 'var(--cyber-amber)', fontWeight: 'bold' }}>📄 {path}</span>
                  <div style={{ marginTop: '0.5rem', display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                    {Object.keys(info.classes || {}).map(c => <span key={c} style={{ fontSize: '0.7rem', padding: '2px 6px', background: 'rgba(0, 243, 255, 0.1)', color: 'var(--cyber-cyan)', borderRadius: '4px' }}>{c}</span>)}
                  </div>
                </div>
              )) : <p style={{color:'var(--text-dim)'}}>No core modules found.</p>}
            </div>
          </div>

          {/* CIRCUITS Domain */}
          <div className="card">
            <h5 className="neon-text" style={{ marginBottom: '1.5rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem' }}>
              🏢 CIRCUITS REGISTRY
            </h5>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {data.circuits?.files ? Object.entries(data.circuits.files).map(([path, info]: [string, any]) => (
                <div key={path} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)', paddingBottom: '1rem' }}>
                  <span style={{ color: 'var(--cyber-amber)', fontWeight: 'bold' }}>📄 {path}</span>
                  <div style={{ marginTop: '0.5rem', display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                    {Object.keys(info.classes || {}).map(c => <span key={c} style={{ fontSize: '0.7rem', padding: '2px 6px', background: 'rgba(255, 204, 0, 0.1)', color: 'var(--cyber-amber)', borderRadius: '4px' }}>{c}</span>)}
                  </div>
                </div>
              )) : <p style={{color:'var(--text-dim)'}}>No circuits found in registry.</p>}
            </div>
          </div>
        </section>
      )}
    </div>
  );
}
