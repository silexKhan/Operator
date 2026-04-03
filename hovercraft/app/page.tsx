'use client';

import { useEffect, useState } from 'react';
import CircuitMap from './components/CircuitMap';

/**
 * [사용자] 모든 Circuit의 가동 상태를 조망하는 통합 상황실입니다. 
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
            <p style={{ color: 'var(--text-dim)' }}>Initializing Architecture Map... </p>
          </div>
        )}
      </section>

      {/* Summary Cards */}
      <section style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
        <div className="card">
          <h3 style={{ fontSize: '0.9rem', color: 'var(--text-dim)', marginBottom: '1rem' }}>
            {mounted ? 'ACTIVE CIRCUITS' : 'CIRC_DISCOVERY'}
          </h3>
          <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>
            {mounted && data?.registered_circuits ? data.registered_circuits.join(', ').toUpperCase() : 'SEARCHING...'}
          </div>
          <div style={{ marginTop: '0.5rem', color: 'var(--cyber-cyan)', fontSize: '0.8rem' }}>
             Domain Isolation Lines Established
          </div>
        </div>
        
        <div className="card">
          <h3 style={{ fontSize: '0.9rem', color: 'var(--text-dim)', marginBottom: '1rem' }}>SYSTEM LOAD</h3>
          <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>0.02ms</div>
          <div style={{ marginTop: '0.5rem', color: 'var(--cyber-amber)', fontSize: '0.8rem' }}>Low Latency Architecture</div>
        </div>
      </section>

      {/* Domain Details (Vertical Stack for Mobile ) */}
      {mounted && data && (
        <section style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          {/* CIRCUITS REGISTRY */}
          <div className="card">
            <h5 className="neon-text" style={{ marginBottom: '1.5rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem' }}>
               CIRCUITS REGISTRY
            </h5>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem' }}>
              {data.registered_circuits?.length > 0 ? data.registered_circuits.map((name: string) => (
                <div 
                  key={name} 
                  onClick={() => handleNodeClick(name)}
                  style={{ 
                    padding: '1rem 2rem', 
                    background: 'rgba(255, 204, 0, 0.05)', 
                    border: '1px solid var(--cyber-amber)', 
                    color: 'var(--cyber-amber)',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    fontWeight: 'bold',
                    textAlign: 'center',
                    minWidth: '150px'
                  }}>
                  {name.toUpperCase()}
                </div>
              )) : <p style={{color:'var(--text-dim)'}}>No registered circuits found.</p>}
            </div>
          </div>

          {/* OPERATIONAL UNITS (3-Line Scrollable Section) */}
          <div className="card">
            <h5 className="neon-text" style={{ marginBottom: '1.5rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem' }}>
               OPERATIONAL UNITS
            </h5>
            <div style={{ 
              display: 'flex', 
              flexWrap: 'wrap', 
              gap: '0.75rem', 
              maxHeight: '180px', 
              overflowY: 'auto',
              paddingRight: '0.5rem'
            }}>
              {data.active_units?.length > 0 ? data.active_units.map((unit: string) => (
                <div 
                  key={unit} 
                  style={{ 
                    padding: '0.75rem 1.5rem', 
                    background: 'rgba(0, 243, 255, 0.05)', 
                    border: '1px solid var(--cyber-cyan)', 
                    color: 'var(--cyber-cyan)',
                    borderRadius: '4px',
                    fontSize: '0.85rem',
                    fontWeight: 'bold',
                    textTransform: 'uppercase'
                  }}>
                  {unit} UNIT
                </div>
              )) : <p style={{color:'var(--text-dim)'}}>No operational units detected.</p>}
            </div>
          </div>
        </section>
      )}
    </div>
  );
}
