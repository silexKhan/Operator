'use client';

import { useEffect, useState } from 'react';

/**
 * [사용자] 모든 Circuits가 상속받는 최상위 행동 규약(Protocols)을 관리하는 구역입니다. 
 * 하드코딩된 데이터를 제거하고, 실시간 API(SSOT) 연동 체계로 전면 전환하였습니다.
 */
export default function ProtocolsRepositoryPage() {
  const [globalProtocols, setGlobalProtocols] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchInheritedProtocols = async () => {
    setLoading(true);
    try {
      // [사용자] 리팩토링된 MCP Bridge API를 통해 실제 물리적 JSON 데이터를 가져옵니다.
      const res = await fetch('/api/mcp/protocols?circuit=mcp');
      const data = await res.json();
      
      if (data.globalRules && Array.isArray(data.globalRules)) {
        // "Protocol 0-X (Name): Description" 형식을 파싱하여 객체화
        const parsedRules = data.globalRules.map((ruleStr: string) => {
          const match = ruleStr.match(/Protocol\s+([\d-]+)\s+\((.*?)\):\s*(.*)/);
          if (match) {
            return {
              id: match[1],
              name: match[2],
              rule: match[3]
            };
          }
          return { id: '?', name: 'Unknown', rule: ruleStr };
        });
        setGlobalProtocols(parsedRules);
      }
    } catch (error) {
      console.error('Failed to fetch global protocols:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInheritedProtocols();
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <header>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h2 className="neon-text" style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>
              PROTOCOLS
            </h2>
            <p style={{ color: 'var(--text-dim)' }}>
              모든 Circuits가 공통으로 상속받아 준수해야 할 최상위 절대 규약입니다.
            </p>
          </div>
          <button 
            onClick={fetchInheritedProtocols}
            className="status-badge" 
            style={{ cursor: 'pointer', background: 'rgba(0, 243, 255, 0.1)', padding: '0.5rem 1rem' }}
          >
            {loading ? 'SYNCING...' : 'FORCE RELOAD'}
          </button>
        </div>
      </header>

      {/* Inherited Top-Level Rules */}
      <section className="card" style={{ borderLeft: '4px solid var(--cyber-amber)' }}>
        <h3 style={{ color: 'var(--cyber-amber)', marginBottom: '2rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
           GLOBAL CONSTITUTION
        </h3>
        
        {loading && <p style={{ textAlign: 'center', color: 'var(--cyber-cyan)' }}>지휘소 데이터 동기화 중...</p>}
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {globalProtocols.map((item, index) => (
            <div key={index} style={{ 
              padding: '1.5rem', 
              background: 'rgba(255, 204, 0, 0.02)', 
              border: '1px solid rgba(255, 204, 0, 0.1)', 
              borderRadius: '8px',
              display: 'flex',
              flexDirection: 'column',
              gap: '0.5rem'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ color: 'var(--cyber-amber)', fontWeight: 'bold', fontSize: '1.1rem' }}>
                  Protocol {item.id} ({item.name})
                </span>
                <div className="status-badge" style={{ borderColor: 'var(--cyber-amber)', color: 'var(--cyber-amber)', background: 'transparent' }}>
                  CORE MANDATE
                </div>
              </div>
              <p style={{ fontSize: '1rem', color: 'var(--text-main)', lineHeight: '1.6' }}>
                {item.rule}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* Logic explanation for Non-developers */}
      <div className="card" style={{ background: 'rgba(0, 243, 255, 0.02)', borderStyle: 'dashed' }}>
        <h4 style={{ color: 'var(--cyber-cyan)', marginBottom: '1rem' }}> 지휘 계통 안내</h4>
        <p style={{ color: 'var(--text-dim)', fontSize: '0.9rem', lineHeight: '1.8' }}>
          위 규칙들은 시스템의 <strong>'헌법'</strong>과 같습니다. 모든 개별 Circuit은 자신의 특수 수칙을 만들기 전,<br /> 
          이 상위 규약들을 자동으로 물려받아 AI의 기본 소양으로 삼습니다. 
        </p>
      </div>
    </div>
  );
}
