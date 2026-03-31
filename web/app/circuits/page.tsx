'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';

/**
 * [대장님 🎯] 오퍼레이터 시스템에 등록된 모든 Circuits를 관리하는 허브입니다. 🛡️⚡️
 */
export default function CircuitsRegistryPage() {
  const [circuits, setCircuits] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [newCircuitName, setNewCircuitName] = useState('');
  const [inheritGlobal, setInheritGlobal] = useState(true); // 상속 여부 상태 추가 🛡️
  const [showAddForm, setShowAddForm] = useState(false);

  const fetchCircuits = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/mcp');
      const data = await res.json();
      setCircuits(data.registered_circuits || []);
    } catch (e) {
      console.error("Failed to fetch Circuits", e);
    }
    setLoading(false);
  };

  const handleCreateCircuit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newCircuitName) return;

    setLoading(true);
    try {
      const res = await fetch('/api/mcp/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: newCircuitName, role: 'development', inherit_global: inheritGlobal })
      });
      if (res.ok) {
        alert(`✅ Circuit '${newCircuitName}' established! 🛡️⚡️\nInheritance: ${inheritGlobal ? 'ON' : 'OFF'}`);
        setNewCircuitName('');
        setInheritGlobal(true);
        setShowAddForm(false);
        fetchCircuits();
      }
    } catch (e) {
      alert("Failed to create Circuit.");
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchCircuits();
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 className="neon-text" style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>
            CIRCUITS REGISTRY
          </h2>
          <p style={{ color: 'var(--text-dim)' }}>
            오퍼레이터 시스템에 연결된 물리적 Circuit 목록입니다.
          </p>
        </div>
        <button 
          onClick={() => setShowAddForm(!showAddForm)}
          style={{ 
            padding: '0.75rem 1.5rem', 
            background: 'var(--cyber-cyan)', 
            border: 'none', 
            color: 'var(--bg-dark)',
            cursor: 'pointer',
            borderRadius: '4px',
            fontWeight: 'bold',
            fontSize: '1.2rem'
          }}>
          {showAddForm ? 'CANCEL' : '＋ NEW CIRCUIT'}
        </button>
      </header>

      {showAddForm && (
        <section className="card" style={{ border: '1px solid var(--cyber-cyan)', animation: 'fadeIn 0.3s ease' }}>
          <form onSubmit={handleCreateCircuit} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
              <input 
                type="text" 
                placeholder="Enter New Circuit Name..." 
                value={newCircuitName}
                onChange={(e) => setNewCircuitName(e.target.value)}
                style={{ 
                  flex: 1, padding: '1rem', background: 'rgba(255,255,255,0.05)', 
                  border: '1px solid var(--border-color)', color: 'white', borderRadius: '4px' 
                }}
              />
              <button 
                type="submit" 
                disabled={loading}
                style={{ 
                  padding: '1rem 2rem', background: 'var(--cyber-cyan)', 
                  border: 'none', color: 'var(--bg-dark)', fontWeight: 'bold', 
                  cursor: 'pointer', borderRadius: '4px' 
                }}>
                {loading ? 'ESTABLISHING...' : 'ESTABLISH LINE 🚀'}
              </button>
            </div>
            
            {/* [대장님 🎯] 상위 규약 상속 토글 UI 🛡️⚡️ */}
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', cursor: 'pointer', color: 'var(--cyber-amber)' }}>
              <input 
                type="checkbox" 
                checked={inheritGlobal} 
                onChange={(e) => setInheritGlobal(e.target.checked)}
                style={{ width: '1.2rem', height: '1.2rem', accentColor: 'var(--cyber-amber)' }}
              />
              <span style={{ fontSize: '0.9rem', fontWeight: 'bold' }}>Inherit Global Protocols (상위 전사 규약 상속)</span>
            </label>
          </form>
        </section>
      )}

      <section style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1.5rem' }}>
        {loading && !circuits.length ? (
          <p style={{ color: 'var(--text-dim)' }}>Scanning lines... 🕵️‍♂️</p>
        ) : (
          circuits.map(name => (
            <Link key={name} href={`/circuits/${name.toLowerCase()}`} style={{ textDecoration: 'none' }}>
              <div className="card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer' }}>
                <div>
                  <h4 style={{ color: 'var(--cyber-cyan)', marginBottom: '0.2rem' }}>{name.toUpperCase()}</h4>
                  <p style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>Status: Active | Scope: Circuit Line</p>
                </div>
                <div className="status-badge">ONLINE</div>
              </div>
            </Link>
          ))
        )}
      </section>

      {circuits.length === 0 && !loading && (
        <div className="card" style={{ borderStyle: 'dashed', textAlign: 'center', padding: '4rem' }}>
          <p style={{ color: 'var(--text-dim)' }}>No Circuits found. Establish your first line! 🛡️⚡️</p>
        </div>
      )}
    </div>
  );
}
