'use client';

import { useState, useEffect } from 'react';

interface UnitModalProps {
  isOpen: boolean;
  onClose: () => void;
  allUnits: string[];
  initialSelected: string[];
  onSave: (selected: string[]) => void;
}

/**
 * [사용자] 회선에 투입할 전문 기술 유닛(Unit)을 정밀 선택하는 모달입니다. 
 */
export default function UnitModal({ isOpen, onClose, allUnits, initialSelected, onSave }: UnitModalProps) {
  const [selected, setSelected] = useState<string[]>(initialSelected);

  useEffect(() => {
    setSelected(initialSelected);
  }, [initialSelected, isOpen]);

  if (!isOpen) return null;

  const toggleUnit = (unit: string) => {
    setSelected(prev => 
      prev.includes(unit) ? prev.filter(u => u !== unit) : [...prev, unit]
    );
  };

  const getUnitIcon = (unit: string) => {
    if (unit.includes('python')) return '';
    if (unit.includes('swift')) return '';
    if (unit.includes('markdown')) return '';
    return '';
  };

  return (
    <div className="modal-overlay" style={{
      position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh',
      background: 'rgba(0,0,0,0.8)', backdropFilter: 'blur(5px)',
      display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 5000
    }}>
      <div className="modal-content card" style={{
        width: '100%', maxWidth: '500px', background: 'var(--bg-dark)',
        border: '1px solid var(--cyber-pink)', padding: '2rem', borderRadius: '12px',
        boxShadow: '0 0 40px rgba(255, 0, 255, 0.2)'
      }}>
        <h3 style={{ color: 'var(--cyber-pink)', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
           MANAGE SPECIAL UNITS
        </h3>
        
        <p style={{ color: 'var(--text-dim)', fontSize: '0.9rem', marginBottom: '2rem' }}>
          회선에 투입할 전문 기술 유닛을 선택하십시오. 배속된 유닛의 프로토콜이 즉시 적용됩니다.
        </p>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', maxHeight: '400px', overflowY: 'auto', marginBottom: '2rem', paddingRight: '0.5rem' }}>
          {allUnits.map(unit => {
            const isSelected = selected.includes(unit);
            return (
              <div 
                key={unit}
                onClick={() => toggleUnit(unit)}
                style={{
                  padding: '1rem',
                  background: isSelected ? 'rgba(255, 0, 255, 0.1)' : 'rgba(255,255,255,0.02)',
                  border: `1px solid ${isSelected ? 'var(--cyber-pink)' : 'var(--border-color)'}`,
                  borderRadius: '8px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                  <span style={{ fontSize: '1.5rem' }}>{getUnitIcon(unit)}</span>
                  <span style={{ 
                    fontWeight: 'bold', 
                    color: isSelected ? 'var(--cyber-pink)' : 'rgba(255,255,255,0.7)',
                    textShadow: isSelected ? '0 0 10px rgba(255, 0, 255, 0.5)' : 'none',
                    fontSize: '1.1rem'
                  }}>
                    {unit.toUpperCase()}
                  </span>
                </div>
                <div style={{ 
                  width: '24px', height: '24px', borderRadius: '6px',
                  border: `2px solid ${isSelected ? 'var(--cyber-pink)' : 'rgba(255,255,255,0.2)'}`,
                  background: isSelected ? 'var(--cyber-pink)' : 'rgba(255,255,255,0.05)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  boxShadow: isSelected ? '0 0 10px var(--cyber-pink)' : 'none',
                  transition: 'all 0.2s'
                }}>
                  {isSelected && <span style={{ color: 'white', fontSize: '1rem', fontWeight: 'bold' }}></span>}
                </div>
              </div>
            );
          })}
        </div>

        <div style={{ display: 'flex', gap: '1rem' }}>
          <button 
            onClick={onClose}
            style={{ flex: 1, padding: '1rem', background: 'transparent', border: '1px solid var(--border-color)', color: 'white', borderRadius: '6px', cursor: 'pointer' }}
          >
            CANCEL
          </button>
          <button 
            onClick={() => onSave(selected)}
            style={{ 
              flex: 2, padding: '1rem', background: 'var(--cyber-pink)', 
              border: 'none', color: 'white', fontWeight: '900', 
              borderRadius: '6px', cursor: 'pointer',
              fontSize: '1rem', letterSpacing: '0.05rem',
              textShadow: '0 1px 3px rgba(0,0,0,0.5)',
              boxShadow: '0 0 20px rgba(255, 0, 255, 0.3)'
            }}
          >
            DEPLOY UNITS 
          </button>
        </div>
      </div>
    </div>
  );
}
