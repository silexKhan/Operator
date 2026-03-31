'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import ProtocolModal from '../components/ProtocolModal';

interface UnitInfo {
  name: string;
  icon: string;
}

/**
 * [대장님 🎯] 지휘소에 등록된 전문 기술 유닛(Units)을 관리하는 허브입니다. 🛡️⚡️
 * 각 유닛 카드를 클릭하면 정밀 지휘 화면으로 이동합니다.
 */
export default function UnitRegistryPage() {
  const [units, setUnits] = useState<UnitInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [mounted, setMounted] = useState(false);
  
  // 창설 제어 상태
  const [showAddForm, setShowAddForm] = useState(false);
  const [newUnitName, setNewUnitName] = useState('');

  useEffect(() => {
    setMounted(true);
    fetchUnits();
  }, []);

  const fetchUnits = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/mcp/units');
      const data = await res.json();
      
      // [대장님 🎯] unit이 이제 {name, path} 구조이므로 name을 정확히 타격합니다. 🕵️‍♂️
      const unitDetails = data.units.map((unit: any) => ({
        name: unit.name,
        icon: getUnitIcon(unit.name)
      }));
      
      setUnits(unitDetails);
    } catch (e) {
      console.error("Failed to fetch units", e);
    }
    setLoading(false);
  };

  const getUnitIcon = (unit: string) => {
    const u = unit.toLowerCase();
    if (u.includes('python')) return '🐍';
    if (u.includes('swift')) return '🍎';
    if (u.includes('markdown')) return '📝';
    return '🛠️';
  };

  const handleCreateUnit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newUnitName) return;
    
    setLoading(true);
    try {
      const res = await fetch('/api/mcp/units/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: newUnitName.toLowerCase() })
      });
      if (res.ok) {
        alert(`🆕 전문 유닛 '${newUnitName.toUpperCase()}' 부대가 창설되었습니다! 🛡️⚡️`);
        setNewUnitName('');
        setShowAddForm(false);
        fetchUnits();
      }
    } catch (e) {
      alert("유닛 창설에 실패했습니다.");
    }
    setLoading(false);
  };

  if (!mounted) return null;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 className="neon-text" style={{ fontSize: '2.5rem', marginBottom: '0.5rem', color: 'var(--cyber-pink)', textShadow: '0 0 20px rgba(255, 0, 255, 0.5)' }}>
            UNITS REGISTRY
          </h2>
          <p style={{ color: 'var(--text-dim)' }}>
            지휘소에 배속된 전문 기술 부대(Units)들의 목록과 상태를 관리합니다.
          </p>
        </div>
        <button 
          onClick={() => setShowAddForm(!showAddForm)}
          style={{ 
            padding: '0.75rem 1.5rem', background: 'var(--cyber-pink)', 
            border: 'none', color: 'white', cursor: 'pointer',
            borderRadius: '4px', fontWeight: 'bold', fontSize: '1.2rem',
            boxShadow: '0 0 20px rgba(255, 0, 255, 0.3)'
          }}>
          {showAddForm ? 'CANCEL' : '＋ NEW UNIT'}
        </button>
      </header>

      {showAddForm && (
        <section className="card" style={{ border: '1px solid var(--cyber-pink)', animation: 'fadeIn 0.3s ease', background: 'rgba(255, 0, 255, 0.02)' }}>
          <form onSubmit={handleCreateUnit} style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
            <input 
              type="text" 
              placeholder="Enter New Unit Name (e.g. golang, rust)..." 
              value={newUnitName}
              onChange={(e) => setNewUnitName(e.target.value)}
              style={{ 
                flex: 1, padding: '1rem', background: 'rgba(255,255,255,0.05)', 
                border: '1px solid var(--border-color)', color: 'white', borderRadius: '4px',
                fontSize: '1.1rem', outline: 'none'
              }}
              autoFocus
            />
            <button 
              type="submit" 
              disabled={loading}
              style={{ 
                padding: '1rem 2rem', background: 'var(--cyber-pink)', 
                border: 'none', color: 'white', fontWeight: 'bold', 
                cursor: 'pointer', borderRadius: '4px' 
              }}>
              {loading ? 'CREATING...' : 'ESTABLISH UNIT 🚀'}
            </button>
          </form>
        </section>
      )}

      <section style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: '1.5rem' }}>
        {loading && !units.length ? (
          <p style={{ color: 'var(--text-dim)' }}>Scanning Tactical Units... 🕵️‍♂️</p>
        ) : (
          units.map(unit => (
            <Link key={unit.name} href={`/units/${unit.name.toLowerCase()}`} style={{ textDecoration: 'none' }}>
              <div className="card" style={{ 
                display: 'flex', justifyContent: 'space-between', alignItems: 'center', 
                borderLeft: `4px solid ${unit.name === 'mcp' ? 'var(--cyber-cyan)' : 'var(--cyber-pink)'}`,
                background: 'rgba(255, 255, 255, 0.01)',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
              onMouseOver={(e) => e.currentTarget.style.transform = 'translateY(-2px)'}
              onMouseOut={(e) => e.currentTarget.style.transform = 'translateY(0)'}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                  <span style={{ fontSize: '2.5rem' }}>{unit.icon}</span>
                  <div>
                    <h4 style={{ color: 'white', margin: 0, fontSize: '1.2rem' }}>{unit.name.toUpperCase()}</h4>
                    <p style={{ fontSize: '0.7rem', color: 'var(--text-dim)', marginTop: '0.2rem' }}>TACTICAL UNIT ACTIVE</p>
                  </div>
                </div>
                <div className="status-badge" style={{ background: 'rgba(255, 0, 255, 0.1)', color: 'var(--cyber-pink)', border: '1px solid var(--cyber-pink)' }}>
                  COMMAND
                </div>
              </div>
            </Link>
          ))
        )}
      </section>

      {units.length === 0 && !loading && (
        <div className="card" style={{ borderStyle: 'dashed', textAlign: 'center', padding: '4rem', borderColor: 'var(--cyber-pink)' }}>
          <p style={{ color: 'var(--text-dim)' }}>No Tactical Units found. Establish your first unit! 🛡️⚡️</p>
        </div>
      )}
    </div>
  );
}
