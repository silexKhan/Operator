'use client';

import { useEffect, useState } from 'react';

/**
 * [사용자] 모든 Circuits가 상속받는 최상위 행동 규약(Protocols)을 관리하는 구역입니다. 
 * 용어 정규화: Axiom -> Protocol 전면 적용 완료. 
 */
export default function ProtocolsRepositoryPage() {
  const [globalProtocols, setGlobalProtocols] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchInheritedProtocols = async () => {
    setLoading(true);
    // [사용자] core/protocols.py 에 정의된 조직의 근본 규약들입니다. 
    const topLevelRules = [
      { id: "0-1", name: "Mechanical Integrity", rule: "코드나 문서 내에 '...' 또는 '중략' 금지. 완전한 텍스트 의무화.", emoji: "" },
      { id: "0-2", name: "Content Preservation", rule: "기존의 유효한 정보, 섹션, 예시를 임의로 삭제하지 않음.", emoji: "" },
      { id: "0-4", name: "Security First", rule: "비밀번호, API Key 등 보안 정보 노출 절대 금지.", emoji: "" },
      { id: "0-5", name: "Single Responsibility", rule: "하나의 기능이나 문서는 하나의 책임만 가짐 (KISS 원칙).", emoji: "" },
      { id: "0-6", name: "Explain Before Acting", rule: "모든 작업 시작 전 의도와 전략을 선제 보고함.", emoji: "" },
      { id: "0-8", name: "Proactive Specification", rule: "모든 제안은 구체적인 예시와 기대 효과를 포함함.", emoji: "" }
    ];
    setGlobalProtocols(topLevelRules);
    setLoading(false);
  };

  useEffect(() => {
    fetchInheritedProtocols();
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <header>
        <h2 className="neon-text" style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>
          PROTOCOLS
        </h2>
        <p style={{ color: 'var(--text-dim)' }}>
          모든 Circuits가 공통으로 상속받아 준수해야 할 최상위 절대 규약입니다.
        </p>
      </header>

      {/* Inherited Top-Level Rules */}
      <section className="card" style={{ borderLeft: '4px solid var(--cyber-amber)' }}>
        <h3 style={{ color: 'var(--cyber-amber)', marginBottom: '2rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
           GLOBAL CONSTITUTION
        </h3>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {globalProtocols.map((item) => (
            <div key={item.id} style={{ 
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
                  {item.emoji} Protocol {item.id} ({item.name})
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
