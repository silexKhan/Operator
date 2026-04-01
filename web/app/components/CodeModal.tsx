'use client';

import { useState, useEffect } from 'react';

interface CodeModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  initialCode: string;
  onSave: (code: string) => void;
}

/**
 * [사용자] 전문 유닛의 핵심 엔진(Auditor.py) 소스 코드를 정밀 분석하고 수정하는 코드 에디터입니다. 
 */
export default function CodeModal({ isOpen, onClose, title, initialCode, onSave }: CodeModalProps) {
  const [code, setCode] = useState(initialCode);

  useEffect(() => {
    setCode(initialCode);
  }, [initialCode, isOpen]);

  if (!isOpen) return null;

  return (
    <div style={{
      position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh',
      background: 'rgba(0,0,0,0.85)', backdropFilter: 'blur(10px)',
      display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 7000
    }}>
      <div className="card" style={{
        width: '90%', maxWidth: '1000px', height: '80vh', background: 'var(--bg-dark)',
        border: '1px solid var(--cyber-cyan)', display: 'flex', flexDirection: 'column',
        boxShadow: '0 0 50px rgba(0, 243, 255, 0.2)', padding: '2rem', borderRadius: '12px'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
          <div>
            <h3 style={{ color: 'var(--cyber-cyan)', margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
               ENGINE INSIGHT: {title}
            </h3>
            <p style={{ color: 'var(--text-dim)', fontSize: '0.8rem', marginTop: '0.3rem' }}>
              유닛의 핵심 감사 로직(Auditor.py)을 정밀 제어합니다. 파이썬 문법을 준수하십시오.
            </p>
          </div>
          <button 
            onClick={onClose}
            style={{ background: 'transparent', border: 'none', color: 'var(--text-dim)', fontSize: '1.5rem', cursor: 'pointer' }}
          >
            
          </button>
        </div>

        <div style={{ flex: 1, position: 'relative', marginBottom: '1.5rem', overflow: 'hidden', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
          <textarea
            value={code}
            onChange={(e) => setCode(e.target.value)}
            spellCheck={false}
            style={{
              width: '100%', height: '100%', background: 'rgba(0,0,0,0.3)',
              color: '#d4d4d4', fontFamily: 'monospace', fontSize: '1rem',
              padding: '1.5rem', border: 'none', outline: 'none', resize: 'none',
              lineHeight: '1.6', whiteSpace: 'pre', tabSize: 4
            }}
          />
        </div>

        <div style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end' }}>
          <button 
            onClick={onClose}
            style={{ padding: '0.8rem 2rem', background: 'transparent', border: '1px solid var(--border-color)', color: 'white', borderRadius: '6px', cursor: 'pointer' }}
          >
            CANCEL
          </button>
          <button 
            onClick={() => onSave(code)}
            style={{ 
              padding: '0.8rem 3rem', background: 'var(--cyber-cyan)', 
              border: 'none', color: 'var(--bg-dark)', fontWeight: '900', 
              borderRadius: '6px', cursor: 'pointer',
              boxShadow: '0 0 20px rgba(0, 243, 255, 0.3)'
            }}
          >
            OVERWRITE ENGINE 
          </button>
        </div>
      </div>
    </div>
  );
}
