'use client';

import { useState, useEffect } from 'react';

interface DependencyModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (selected: string[]) => void;
  allCircuits: string[];
  initialSelected: string[];
}

/**
 * [사용자] 수많은 회선 중 필요한 연결 고리를 정밀하게 선택하는 전용 지휘창입니다. 
 */
export default function DependencyModal({ isOpen, onClose, onSave, allCircuits, initialSelected }: DependencyModalProps) {
  const [selected, setSelected] = useState<string[]>(initialSelected);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    setSelected(initialSelected);
  }, [initialSelected, isOpen]);

  if (!isOpen) return null;

  const filteredCircuits = allCircuits.filter(c => 
    c.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const toggleItem = (name: string) => {
    const lowerName = name.toLowerCase();
    if (selected.includes(lowerName)) {
      setSelected(selected.filter(s => s !== lowerName));
    } else {
      setSelected([...selected, lowerName]);
    }
  };

  return (
    <div 
      onClick={onClose}
      style={{
        position: 'fixed', top: 0, left: 0, width: '100%', height: '100%',
        background: 'rgba(0,0,0,0.9)', backdropFilter: 'blur(10px)',
        display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 2000
      }}
    >
      <div 
        onClick={(e) => e.stopPropagation()}
        className="card" 
        style={{ width: '500px', border: '1px solid var(--cyber-cyan)', boxShadow: '0 0 40px rgba(0, 229, 255, 0.2)' }}
      >
        <h3 className="neon-text" style={{ marginBottom: '1.5rem' }}> MANAGE LINE CONNECTIONS</h3>
        
        {/* Search Bar  */}
        <input 
          placeholder="회선 이름 검색..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          style={{ 
            width: '100%', padding: '0.75rem 1rem', background: 'rgba(255,255,255,0.05)', 
            border: '1px solid var(--border-color)', color: 'white', borderRadius: '4px',
            marginBottom: '1rem', outline: 'none'
          }}
        />

        {/* Circuit List */}
        <div style={{ maxHeight: '300px', overflowY: 'auto', background: 'rgba(0,0,0,0.2)', borderRadius: '8px', padding: '0.5rem' }}>
          {filteredCircuits.map(name => {
            const isChecked = selected.includes(name.toLowerCase());
            return (
              <div 
                key={name}
                onClick={() => toggleItem(name)}
                style={{ 
                  padding: '0.75rem 1rem', display: 'flex', alignItems: 'center', gap: '1rem',
                  cursor: 'pointer', borderBottom: '1px solid rgba(255,255,255,0.02)',
                  background: isChecked ? 'rgba(0, 229, 255, 0.05)' : 'transparent',
                  transition: 'all 0.2s'
                }}
              >
                <div style={{ 
                  width: '18px', height: '18px', border: `2px solid ${isChecked ? 'var(--cyber-cyan)' : 'var(--text-dim)'}`,
                  borderRadius: '3px', background: isChecked ? 'var(--cyber-cyan)' : 'transparent',
                  display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '12px', color: 'black'
                }}>
                  {isChecked && ''}
                </div>
                <span style={{ color: isChecked ? 'var(--cyber-cyan)' : 'var(--text-main)', fontWeight: isChecked ? 'bold' : 'normal' }}>
                  {name.toUpperCase()}
                </span>
              </div>
            );
          })}
          {filteredCircuits.length === 0 && (
            <p style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-dim)' }}>검색 결과가 없습니다.</p>
          )}
        </div>

        <div style={{ marginTop: '2rem', display: 'flex', justifyContent: 'flex-end', gap: '1rem' }}>
          <button onClick={onClose} style={{ padding: '0.75rem 1.5rem', background: 'transparent', border: '1px solid var(--border-color)', color: 'white', cursor: 'pointer' }}>CANCEL</button>
          <button 
            onClick={() => { onSave(selected); onClose(); }}
            style={{ padding: '0.75rem 2rem', background: 'var(--cyber-cyan)', border: 'none', color: 'black', fontWeight: 'bold', borderRadius: '4px', cursor: 'pointer' }}
          >
            CONFIRM CONNECTIONS
          </button>
        </div>
      </div>
    </div>
  );
}
