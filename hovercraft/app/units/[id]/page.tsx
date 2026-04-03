'use client';

import { useParams, useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import ProtocolModal from '../../components/ProtocolModal';

/**
 * [사용자] 전문 기술 유닛의 핵심 정체성과 수칙을 관리하는 정밀 사령탑입니다. 
 * 서버와 클라이언트의 초기 렌더링 구조를 완벽히 일치시켜 Hydration 에러를 영구 봉쇄합니다.
 */
export default function UnitCommandPage() {
  const params = useParams();
  const router = useRouter();
  
  // 상태 관리
  const [rules, setRules] = useState<string[]>([]);
  const [unitPath, setUnitPath] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [mounted, setMounted] = useState(false);
  const [toast, setToast] = useState<{ message: string; visible: boolean }>({ message: '', visible: false });
  const [isProtocolModalOpen, setIsProtocolModalOpen] = useState(false);
  const [editingIdx, setEditingIdx] = useState<number | null>(null);

  // 파라미터 추출 (서버/클라이언트 공통)
  const unitId = (params?.id as string) || '';
  const displayUnitName = unitId.toUpperCase();

  useEffect(() => {
    setMounted(true);
    fetchData();
  }, [unitId]);

  const showToast = (msg: string) => {
    setToast({ message: msg, visible: true });
    setTimeout(() => setToast(prev => ({ ...prev, visible: false })), 3000);
  };

  const fetchData = async () => {
    if (!unitId) return;
    setLoading(true);
    try {
      const res = await fetch(`/api/mcp/units/protocols?unit=${unitId}`);
      const data = await res.json();
      setRules(data.rules || []);

      const unitsRes = await fetch('/api/mcp/units');
      const unitsData = await unitsRes.json();
      const currentUnit = unitsData.units?.find((u: any) => u.name.toLowerCase() === unitId.toLowerCase());
      if (currentUnit) setUnitPath(currentUnit.path);
    } catch (e) {
      console.error("Failed to fetch unit data", e);
    }
    setLoading(false);
  };

  const handleDeleteUnit = async () => {
    const confirmed = window.confirm(` [위험] 전문 유닛 '${displayUnitName}' 부대를 영구 해체하시겠습니까?`);
    if (!confirmed) return;

    setLoading(true);
    try {
      const res = await fetch('/api/mcp/units/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: unitId })
      });
      if (res.ok) {
        alert(` 전문 유닛 '${displayUnitName}' 부대가 해체되었습니다.`);
        router.push('/units');
      }
    } catch (e) {
      showToast(' 에러 발생');
    }
    setLoading(false);
  };

  const saveProtocols = async (updatedRules: string[]) => {
    setLoading(true);
    try {
      await fetch('/api/mcp/units/protocols', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: unitId, rules: updatedRules })
      });
      setRules(updatedRules);
      showToast(' 유닛 기술 수칙이 성공적으로 반영되었습니다.');
    } catch (e) {}
    setLoading(false);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem', position: 'relative' }} suppressHydrationWarning>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }} suppressHydrationWarning>
        <div style={{ display: 'flex', flexDirection: 'column' }} suppressHydrationWarning>
          <button 
            onClick={() => router.push('/units')} 
            style={{ alignSelf: 'flex-start', background: 'transparent', border: 'none', color: 'var(--cyber-pink)', cursor: 'pointer', marginBottom: '1rem', padding: 0 }}
          >
             BACK TO REGISTRY
          </button>
          <h2 className="neon-text" style={{ fontSize: '2.5rem', color: 'var(--cyber-pink)', textShadow: '0 0 20px rgba(255, 0, 255, 0.5)' }}>
            UNIT COMMAND: {displayUnitName}
          </h2>
          <p style={{ color: 'var(--text-dim)', marginTop: '0.5rem' }}>
            전문 부대의 독자적인 기술 규격과 물리 경로를 관리합니다.
          </p>
        </div>
        
        {mounted && !['mcp', 'python', 'swift', 'markdown'].includes(unitId?.toLowerCase()) && (
          <button 
            onClick={handleDeleteUnit}
            disabled={loading}
            style={{ 
              padding: '0.75rem 1.5rem', background: 'rgba(255, 0, 0, 0.1)', 
              border: '1px solid #ff4444', color: '#ff4444', 
              borderRadius: '4px', fontWeight: 'bold', cursor: 'pointer',
              transition: 'all 0.2s'
            }}
          >
            DECOMMISSION UNIT
          </button>
        )}
      </header>

      <section style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }} suppressHydrationWarning>
        <div className="card" style={{ borderLeft: '4px solid var(--cyber-pink)', background: 'rgba(255, 0, 255, 0.02)' }} suppressHydrationWarning>
          <h4 style={{ color: 'var(--cyber-pink)', marginBottom: '1.5rem' }}>UNIT OVERVIEW</h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            <div>
              <label style={{ display: 'block', color: 'var(--cyber-pink)', fontSize: '0.8rem', marginBottom: '0.5rem' }}>IDENTITY & MISSION</label>
              <div style={{ padding: '1.5rem', background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border-color)', color: 'white', borderRadius: '8px', fontSize: '1.1rem', lineHeight: '1.8' }}>
                이 유닛은 {displayUnitName} 기술 도메인의 정밀 감사를 수행합니다. 회선의 요청 시 배속되어 독자적인 기술 프로토콜을 강제합니다.
              </div>
            </div>
            <div>
              <label style={{ display: 'block', color: 'var(--cyber-amber)', fontSize: '0.8rem', marginBottom: '0.5rem' }}>BASE PATH (PHYSICAL)</label>
              <div style={{ padding: '1rem', background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border-color)', color: 'var(--cyber-amber)', borderRadius: '8px', fontFamily: 'monospace' }}>
                {unitPath || `units/${unitId?.toLowerCase()}`}
              </div>
            </div>
          </div>
        </div>

        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', borderLeft: '4px solid var(--cyber-pink)' }} suppressHydrationWarning>
          <h3 style={{ color: 'var(--cyber-pink)', borderBottom: '1px solid var(--border-color)', paddingBottom: '1rem' }}>UNIT SPECIAL PROTOCOLS</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(45%, 1fr))', gap: '1rem' }}>
            {rules.map((rule, idx) => (
              <button key={idx} onClick={() => { setEditingIdx(idx); setIsProtocolModalOpen(true); }} className="nav-item" style={{ textAlign: 'left', background: 'rgba(255,255,255,0.03)', padding: '1.5rem', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.1)', color: 'white', fontSize: '1rem', lineHeight: '1.5', cursor: 'pointer' }}>{rule}</button>
            ))}
            {mounted && (
              <button onClick={() => { const newRules = [...rules, `Protocol ${unitId?.charAt(0).toUpperCase()}-X (New): Description`]; setRules(newRules); setEditingIdx(newRules.length - 1); setIsProtocolModalOpen(true); }} style={{ textAlign: 'center', background: 'transparent', padding: '1.5rem', borderRadius: '8px', border: '1px dashed var(--text-dim)', color: 'var(--text-dim)', cursor: 'pointer' }}>+ ADD NEW RULE</button>
            )}
          </div>
          <div style={{ marginTop: '2rem', borderTop: '1px solid var(--border-color)', paddingTop: '2rem', display: 'flex', justifyContent: 'center' }}>
            <button onClick={() => saveProtocols(rules)} disabled={loading} style={{ padding: '1.2rem 4rem', background: 'var(--cyber-pink)', border: 'none', color: 'white', fontWeight: 'bold', fontSize: '1.2rem', cursor: 'pointer', borderRadius: '4px', boxShadow: '0 0 30px rgba(255, 0, 255, 0.4)', width: '100%', maxWidth: '500px' }}>
              {loading ? 'DEPLOYING...' : 'UPDATE UNIT RULES '}
            </button>
          </div>
        </div>
      </section>

      {toast.visible && (
        <div style={{ position: 'fixed', bottom: '2rem', left: '50%', transform: 'translateX(-50%)', padding: '1rem 2rem', background: 'rgba(0, 255, 255, 0.1)', backdropFilter: 'blur(10px)', border: '1px solid var(--cyber-pink)', borderRadius: '8px', color: 'var(--cyber-pink)', fontWeight: 'bold', fontSize: '0.9rem', zIndex: 3000, boxShadow: '0 0 20px rgba(255, 0, 255, 0.3)', animation: 'slideUp 0.3s ease' }}>{toast.message}</div>
      )}

      <ProtocolModal isOpen={isProtocolModalOpen} onClose={() => setIsProtocolModalOpen(false)} initialText={editingIdx !== null ? rules[editingIdx] : ''} onSave={(newText) => { if (editingIdx !== null) { const newRules = [...rules]; newRules[editingIdx] = newText; setRules(newRules); setIsProtocolModalOpen(false); } }} onDelete={() => { if (editingIdx !== null) { const newRules = rules.filter((_, i) => i !== editingIdx); setRules(newRules); setIsProtocolModalOpen(false); } }} />

      <style jsx>{` @keyframes slideUp { from { bottom: 0; opacity: 0; } to { bottom: 2rem; opacity: 1; } } `}</style>
    </div>
  );
}
