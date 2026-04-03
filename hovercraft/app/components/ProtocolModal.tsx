'use client';

import { useState, useEffect } from 'react';

interface ProtocolModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (newText: string) => void;
  onDelete: () => void;
  initialText: string;
}

/**
 * [사용자] 개별 AI 행동 규약을 정밀 수정하거나 삭제하는 작전 창입니다. 
 * 배경(Dimmed Area) 클릭 시 자동으로 닫히는 인터랙션이 추가되었습니다. 
 */
export default function ProtocolModal({ isOpen, onClose, onSave, onDelete, initialText }: ProtocolModalProps) {
  const [text, setText] = useState(initialText);

  useEffect(() => {
    setText(initialText);
  }, [initialText, isOpen]);

  if (!isOpen) return null;

  return (
    <div 
      onClick={onClose} // [사용자] 배경 클릭 시 창을 닫습니다. 
      style={{
        position: 'fixed', top: 0, left: 0, width: '100%', height: '100%',
        background: 'rgba(0,0,0,0.85)', backdropFilter: 'blur(8px)',
        display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000,
        cursor: 'zoom-out' // 밖을 누르면 닫힌다는 시각적 힌트
      }}
    >
      <div 
        onClick={(e) => e.stopPropagation()} // [사용자] 내부 클릭 시 이벤트 전파를 차단하여 창이 닫히지 않게 합니다. 
        className="card" 
        style={{ 
          width: '600px', 
          border: '1px solid var(--cyber-cyan)', 
          boxShadow: '0 0 30px rgba(0, 243, 255, 0.2)',
          cursor: 'default' // 내부는 일반 커서 유지
        }}
      >
        <h3 className="neon-text" style={{ marginBottom: '1.5rem' }}> EDIT PROTOCOL</h3>
        
        <div style={{ marginBottom: '2rem' }}>
          <label style={{ display: 'block', color: 'var(--text-dim)', fontSize: '0.8rem', marginBottom: '0.5rem' }}>규약 내용 (Protocol Content)</label>
          <textarea 
            value={text}
            onChange={(e) => setText(e.target.value)}
            style={{ 
              width: '100%', minHeight: '150px', padding: '1rem', background: 'rgba(255,255,255,0.02)', 
              border: '1px solid var(--border-color)', color: 'white', borderRadius: '8px',
              fontSize: '1.1rem', lineHeight: '1.6', outline: 'none'
            }}
          />
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <button 
            onClick={() => {
              if(confirm('이 규약을 영구적으로 삭제하시겠습니까? ')) {
                onDelete();
                onClose();
              }
            }} 
            style={{ padding: '0.75rem 1.5rem', background: 'transparent', border: '1px solid var(--cyber-red)', color: 'var(--cyber-red)', cursor: 'pointer', borderRadius: '4px', fontWeight: 'bold' }}
          >
            DELETE
          </button>
          
          <div style={{ display: 'flex', gap: '1rem' }}>
            <button onClick={onClose} style={{ padding: '0.75rem 1.5rem', background: 'transparent', border: '1px solid var(--border-color)', color: 'white', cursor: 'pointer', borderRadius: '4px' }}>
              CANCEL
            </button>
            <button 
              onClick={() => onSave(text)}
              style={{ 
                padding: '0.75rem 2rem', background: 'var(--cyber-cyan)', border: 'none', 
                color: 'var(--bg-dark)', fontWeight: 'bold', cursor: 'pointer', borderRadius: '4px' 
              }}
            >
              SAVE CHANGES
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
