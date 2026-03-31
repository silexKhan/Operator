'use client';

import { useParams, useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import ProtocolModal from '../../components/ProtocolModal';
import PathBrowserModal from '../../components/PathBrowserModal';
import DependencyModal from '../../components/DependencyModal';
import UnitModal from '../../components/UnitModal';

/**
 * [대장님 🎯] 각 Circuit의 모든 면모를 지휘하는 통합 사령탑입니다. 🛡️⚡️
 */
export default function CircuitCommandPage() {
  const params = useParams();
  const router = useRouter();
  const [rules, setRules] = useState<string[]>([]);
  const [globalRules, setGlobalRules] = useState<string[]>([]);
  const [description, setDescription] = useState<string>('');
  const [projectPath, setProjectPath] = useState<string>('');
  const [dependencies, setDependencies] = useState<string[]>([]);
  const [units, setUnits] = useState<string[]>([]);
  const [availableUnits, setAvailableUnits] = useState<string[]>([]); // 이름 리스트로 관리 🛡️
  const [allCircuits, setAllCircuits] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [mounted, setMounted] = useState(false);
  
  const [toast, setToast] = useState<{ message: string; visible: boolean }>({ message: '', visible: false });

  const [isProtocolModalOpen, setIsProtocolModalOpen] = useState(false);
  const [isBrowserOpen, setIsBrowserOpen] = useState(false);
  const [isDependencyModalOpen, setIsDependencyModalOpen] = useState(false);
  const [isUnitModalOpen, setIsUnitModalOpen] = useState(false);
  const [isGlobalVisible, setIsGlobalVisible] = useState(false);
  const [editingIdx, setEditingIdx] = useState<number | null>(null);

  const circuitName = params?.id as string;

  useEffect(() => {
    setMounted(true);
    fetchData();
    fetchAllCircuits();
    fetchAvailableUnits();
  }, [circuitName]);

  const showToast = (msg: string) => {
    setToast({ message: msg, visible: true });
    setTimeout(() => setToast(prev => ({ ...prev, visible: false })), 3000);
  };

  const fetchData = async () => {
    if (!circuitName) return;
    setLoading(true);
    try {
      const res = await fetch(`/api/mcp/protocols?circuit=${circuitName}`);
      const data = await res.json();
      setRules(data.rules || []);
      setGlobalRules(data.globalRules || []);
      setDescription(data.briefing?.description || '');
      setProjectPath(data.briefing?.path || '');
      setDependencies(data.briefing?.dependencies || []);
      setUnits(data.briefing?.units || []);
    } catch (e) {
      console.error("Failed to fetch circuit data", e);
    }
    setLoading(false);
  };

  const fetchAvailableUnits = async () => {
    try {
      const res = await fetch('/api/mcp/units');
      const data = await res.json();
      // [대장님 🎯] 객체 리스트에서 이름만 추출하여 가용 유닛 목록을 구성합니다. 🕵️‍♂️
      const unitNames = (data.units || []).map((u: any) => u.name);
      setAvailableUnits(unitNames);
    } catch (e) {
      console.error("Failed to fetch available units", e);
    }
  };

  const fetchAllCircuits = async () => {
    try {
      const res = await fetch('/api/mcp');
      const data = await res.json();
      setAllCircuits(data.registered_circuits?.filter((c: string) => c.toLowerCase() !== circuitName.toLowerCase()) || []);
    } catch (e) {}
  };

  const handleDeleteCircuit = async () => {
    const confirmed = window.confirm(`⚠️ [위험] 회선 '${circuitName.toUpperCase()}'을 영구 삭제하시겠습니까?\n이 작업은 물리적 소스 코드를 삭제하며 복구가 불가능합니다.`);
    if (!confirmed) return;

    setLoading(true);
    try {
      const res = await fetch('/api/mcp/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: circuitName })
      });
      if (res.ok) {
        alert(`🔥 회선 '${circuitName.toUpperCase()}'이 성공적으로 폐기되었습니다.`);
        router.push('/circuits');
      } else {
        showToast('❌ 삭제 권한이 없거나 실패했습니다.');
      }
    } catch (e) {
      showToast('❌ 에러 발생');
    }
    setLoading(false);
  };

  const saveProtocols = async (updatedRules: string[]) => {
    setLoading(true);
    try {
      await fetch('/api/mcp/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ circuit_name: circuitName, rules: updatedRules })
      });
      showToast('✅ 규약(Protocols)이 성공적으로 반영되었습니다.');
      fetchData();
    } catch (e) {
      showToast('❌ 반영 실패');
    }
    setLoading(false);
  };

  const handleUpdateOverview = async (updatedDeps?: string[]) => {
    const finalDeps = updatedDeps || dependencies;
    setLoading(true);
    try {
      await fetch('/api/mcp/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          circuit_name: circuitName, 
          description, 
          project_path: projectPath,
          dependencies: finalDeps,
          action: 'OVERVIEW_UPDATE'
        })
      });
      showToast(updatedDeps ? '🔗 회선 연결망 업데이트 완료' : '✅ 개요 및 경로 저장 완료');
      fetchData();
    } catch (e) {
      showToast('❌ 업데이트 실패');
    }
    setLoading(false);
  };

  const saveUnits = async (newUnits: string[]) => {
    setLoading(true);
    try {
      await fetch('/api/mcp/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          circuit_name: circuitName, 
          units: newUnits,
          action: 'UNITS_UPDATE'
        })
      });
      setUnits(newUnits);
      setIsUnitModalOpen(false);
      showToast('🛡️ 전문 유닛 배속 정보가 갱신되었습니다.');
    } catch (e) {
      showToast('❌ 유닛 갱신 실패');
    }
    setLoading(false);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem', position: 'relative' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
        <div style={{ display: 'flex', flexDirection: 'column' }}>
          <button onClick={() => router.push('/circuits')} style={{ alignSelf: 'flex-start', background: 'transparent', border: 'none', color: 'var(--cyber-cyan)', cursor: 'pointer', marginBottom: '1rem', padding: 0 }}>
            {mounted ? '← BACK TO REGISTRY' : '←'}
          </button>
          <h2 className="neon-text" style={{ fontSize: '2.5rem' }}>
            {mounted ? `CIRCUIT COMMAND: ${circuitName?.toUpperCase()}` : 'CIRCUIT COMMAND'}
          </h2>
          <p style={{ color: 'var(--text-dim)', marginTop: '0.5rem' }}>
            해당 회선의 정체성, 경로, 의존성, 유닛, 규약을 통합 관리합니다.
          </p>
        </div>
        
        {mounted && circuitName !== 'mcp' && (
          <button 
            onClick={handleDeleteCircuit}
            disabled={loading}
            style={{ 
              padding: '0.75rem 1.5rem', background: 'rgba(255, 0, 0, 0.1)', 
              border: '1px solid #ff4444', color: '#ff4444', 
              borderRadius: '4px', fontWeight: 'bold', cursor: 'pointer',
              transition: 'all 0.2s'
            }}
          >
            🗑️ DELETE CIRCUIT
          </button>
        )}
      </header>

      {mounted ? (
        <section style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          <div className="card" style={{ borderLeft: '4px solid var(--cyber-amber)', background: 'rgba(255, 179, 0, 0.02)' }}>
            <div onClick={() => setIsGlobalVisible(!isGlobalVisible)} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer' }}>
              <h4 style={{ color: 'var(--cyber-amber)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>🏛️ INHERITED GLOBAL CONSTITUTION</h4>
              <span style={{ color: 'var(--cyber-amber)', fontWeight: 'bold' }}>{isGlobalVisible ? '▼ CLOSE' : '▶ VIEW'}</span>
            </div>
            {isGlobalVisible && (
              <div style={{ marginTop: '1.5rem', display: 'flex', flexDirection: 'column', gap: '0.75rem', animation: 'fadeIn 0.3s ease' }}>
                {globalRules.map((rule, idx) => (
                  <div key={idx} style={{ padding: '1rem', background: 'rgba(255, 179, 0, 0.05)', border: '1px solid rgba(255, 179, 0, 0.1)', borderRadius: '6px', fontSize: '0.9rem' }}>{rule}</div>
                ))}
              </div>
            )}
          </div>

          <div className="card" style={{ borderLeft: '4px solid var(--cyber-pink)', background: 'rgba(255, 0, 255, 0.02)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
              <h4 style={{ color: 'var(--cyber-pink)' }}>🛠️ ASSIGNED SPECIAL UNITS</h4>
              <button 
                onClick={() => setIsUnitModalOpen(true)}
                disabled={loading}
                style={{ 
                  padding: '0.5rem 1.5rem', background: 'transparent', 
                  border: '1px dashed var(--cyber-pink)', color: 'var(--cyber-pink)', 
                  borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold'
                }}
              >
                ＋ MANAGE UNITS
              </button>
            </div>
            
            <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
              {units.map(unit => (
                <div
                  key={unit}
                  style={{
                    padding: '0.75rem 1.5rem',
                    background: 'rgba(255, 0, 255, 0.1)',
                    border: '1px solid var(--cyber-pink)',
                    color: 'var(--cyber-pink)',
                    borderRadius: '8px',
                    fontSize: '0.9rem',
                    fontWeight: 'bold',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem'
                  }}
                >
                  {unit.includes('python') ? '🐍' : unit.includes('swift') ? '🍎' : unit.includes('markdown') ? '📝' : '🛠️'} {unit.toUpperCase()}
                </div>
              ))}
              {units.length === 0 && (
                <div style={{ color: 'var(--text-dim)', fontSize: '0.9rem', padding: '1rem 0' }}>
                  배속된 전문 유닛이 없습니다. 유닛을 추가하여 특수 수칙을 활성화하십시오.
                </div>
              )}
            </div>
          </div>

          <div className="card" style={{ borderLeft: '4px solid var(--cyber-cyan)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
              <h4 style={{ color: 'var(--cyber-cyan)' }}>🔍 OVERVIEW & LINE CONNECTIONS</h4>
              <button onClick={() => handleUpdateOverview()} disabled={loading} style={{ padding: '0.5rem 1.5rem', background: 'var(--cyber-cyan)', border: 'none', color: 'var(--bg-dark)', fontWeight: 'bold', borderRadius: '4px', cursor: 'pointer' }}>SAVE CHANGES</button>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              <div>
                <label style={{ display: 'block', color: 'var(--cyber-cyan)', fontSize: '0.8rem', marginBottom: '0.5rem' }}>DESCRIPTION</label>
                <textarea value={description} onChange={(e) => setDescription(e.target.value)} style={{ width: '100%', minHeight: '150px', padding: '1.5rem', background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border-color)', color: 'white', borderRadius: '8px', fontSize: '1.1rem', lineHeight: '1.8', resize: 'vertical', outline: 'none' }} />
              </div>
              <div>
                <label style={{ display: 'block', color: 'var(--cyber-cyan)', fontSize: '0.8rem', marginBottom: '0.5rem' }}>🔗 CONNECTED CIRCUITS (DEPENDENCIES)</label>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem', alignItems: 'center' }}>
                  {dependencies.map(name => (
                    <span key={name} style={{ padding: '0.4rem 1rem', background: 'rgba(0, 243, 255, 0.1)', border: '1px solid var(--cyber-cyan)', color: 'var(--cyber-cyan)', borderRadius: '20px', fontSize: '0.8rem', fontWeight: 'bold' }}>{name.toUpperCase()}</span>
                  ))}
                  {dependencies.length === 0 && <span style={{ color: 'var(--text-dim)', fontSize: '0.8rem' }}>연결된 회선이 없습니다.</span>}
                  <button onClick={() => setIsDependencyModalOpen(true)} style={{ marginLeft: '0.5rem', padding: '0.4rem 1rem', background: 'transparent', border: '1px dashed var(--cyber-cyan)', color: 'var(--cyber-cyan)', borderRadius: '20px', fontSize: '0.8rem', cursor: 'pointer' }}>＋ MANAGE CONNECTIONS</button>
                </div>
              </div>
              <div>
                <label style={{ display: 'block', color: 'var(--cyber-amber)', fontSize: '0.8rem', marginBottom: '0.5rem' }}>PROJECT PATH</label>
                <div style={{ display: 'flex', gap: '1rem' }}>
                  <input value={projectPath} onChange={(e) => setProjectPath(e.target.value)} style={{ flex: 1, padding: '1rem', background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border-color)', color: 'var(--cyber-amber)', borderRadius: '8px', fontFamily: 'monospace' }} />
                  <button onClick={() => setIsBrowserOpen(true)} style={{ padding: '0 2rem', background: 'transparent', border: '1px solid var(--cyber-amber)', color: 'var(--cyber-amber)', borderRadius: '4px', fontWeight: 'bold', cursor: 'pointer' }}>SET PATH</button>
                </div>
              </div>
            </div>
          </div>

          <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            <h3 style={{ color: 'var(--cyber-cyan)', borderBottom: '1px solid var(--border-color)', paddingBottom: '1rem' }}>📜 ACTIVE PROTOCOLS</h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(45%, 1fr))', gap: '1rem' }}>
              {rules.map((rule, idx) => (
                <button key={idx} onClick={() => { setEditingIdx(idx); setIsProtocolModalOpen(true); }} className="nav-item" style={{ textAlign: 'left', background: 'rgba(255,255,255,0.03)', padding: '1.5rem', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.1)', color: 'white', fontSize: '1rem', lineHeight: '1.5', cursor: 'pointer' }}>{rule}</button>
              ))}
              <button onClick={() => { const newRules = [...rules, "Protocol P-X (New): Description"]; setRules(newRules); setEditingIdx(newRules.length - 1); setIsProtocolModalOpen(true); }} style={{ textAlign: 'center', background: 'transparent', padding: '1.5rem', borderRadius: '8px', border: '1px dashed var(--text-dim)', color: 'var(--text-dim)', cursor: 'pointer' }}>+ ADD NEW PROTOCOL</button>
            </div>
            <div style={{ marginTop: '2rem', borderTop: '1px solid var(--border-color)', paddingTop: '2rem', display: 'flex', justifyContent: 'center' }}>
              <button onClick={() => saveProtocols(rules)} disabled={loading} style={{ padding: '1.2rem 4rem', background: 'var(--cyber-cyan)', border: 'none', color: 'var(--bg-dark)', fontWeight: 'bold', fontSize: '1.2rem', cursor: 'pointer', borderRadius: '4px', boxShadow: '0 0 30px rgba(0, 243, 255, 0.4)', width: '100%', maxWidth: '500px' }}>{loading ? 'DEPLOYING...' : 'DEPLOY PROTOCOLS TO AI 🚀'}</button>
            </div>
          </div>
        </section>
      ) : (
        <div className="card" style={{ height: '200px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}><p style={{ color: 'var(--text-dim)' }}>Loading Exchange Center...</p></div>
      )}

      {toast.visible && (
        <div style={{ position: 'fixed', bottom: '2rem', left: '50%', transform: 'translateX(-50%)', padding: '1rem 2rem', background: 'rgba(0, 229, 255, 0.1)', backdropFilter: 'blur(10px)', border: '1px solid var(--cyber-cyan)', borderRadius: '8px', color: 'var(--cyber-cyan)', fontWeight: 'bold', fontSize: '0.9rem', zIndex: 3000, boxShadow: '0 0 20px rgba(0, 243, 255, 0.3)', animation: 'slideUp 0.3s ease' }}>{toast.message}</div>
      )}

      <ProtocolModal isOpen={isProtocolModalOpen} onClose={() => setIsProtocolModalOpen(false)} initialText={editingIdx !== null ? rules[editingIdx] : ''} onSave={(newText) => { if (editingIdx !== null) { const newRules = [...rules]; newRules[editingIdx] = newText; setRules(newRules); setIsProtocolModalOpen(false); } }} onDelete={() => { if (editingIdx !== null) { const newRules = rules.filter((_, i) => i !== editingIdx); setRules(newRules); setIsProtocolModalOpen(false); } }} />
      <PathBrowserModal isOpen={isBrowserOpen} onClose={() => setIsBrowserOpen(false)} initialPath={projectPath} onSelect={(selectedPath) => setProjectPath(selectedPath)} />
      <DependencyModal isOpen={isDependencyModalOpen} onClose={() => setIsDependencyModalOpen(false)} allCircuits={allCircuits} initialSelected={dependencies} onSave={(selected) => { setDependencies(selected); handleUpdateOverview(selected); }} />
      <UnitModal isOpen={isUnitModalOpen} onClose={() => setIsUnitModalOpen(false)} allUnits={availableUnits} initialSelected={units} onSave={saveUnits} />

      <style jsx>{` @keyframes slideUp { from { bottom: 0; opacity: 0; } to { bottom: 2rem; opacity: 1; } } `}</style>
    </div>
  );
}
