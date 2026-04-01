'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

interface CircuitInfo {
  name: string;
  units: string[];
}

/**
 * [사용자] 햄버거 메뉴로 여닫을 수 있는 세련된 사이드바 지휘 메뉴입니다. 
 * 활성 회선과 등록된 모든 유닛을 실시간으로 감시하는 기능이 통합되었습니다.
 */
export default function Sidebar() {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [mounted, setMounted] = useState(false);
  const [circuits, setCircuits] = useState<CircuitInfo[]>([]);
  const [availableUnits, setAvailableUnits] = useState<any[]>([]); // 유닛 객체 리스트 
  const pathname = usePathname();

  useEffect(() => {
    setMounted(true);
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      // 1. 등록된 회선 및 상세 정보 가져오기
      const res = await fetch('/api/mcp');
      const data = await res.json();
      
      if (data.registered_circuits) {
        const details = await Promise.all(
          data.registered_circuits.map(async (name: string) => {
            const detailRes = await fetch(`/api/mcp/protocols?circuit=${name}`);
            const detailData = await detailRes.json();
            return {
              name,
              units: detailData.briefing?.units || []
            };
          })
        );
        setCircuits(details);
      }

      // 2. 등록된 전체 유닛 리스트 가져오기 ({name, path} 구조) 
      const unitRes = await fetch('/api/mcp/units');
      const unitData = await unitRes.json();
      setAvailableUnits(unitData.units || []);

    } catch (e) {
      console.error("Failed to fetch sidebar data", e);
    }
  };

  const getUnitIcon = (unitName: string) => {
    const u = unitName.toLowerCase();
    if (u.includes('python')) return '';
    if (u.includes('swift')) return '';
    if (u.includes('markdown')) return '';
    return '';
  };

  const menuItems = [
    { name: 'Dashboard', path: '/', icon: '' },
    { name: 'Circuits Registry', path: '/circuits', icon: '' },
    { name: 'Units Registry', path: '/units', icon: '' },
    { name: 'Global Protocols', path: '/protocols', icon: '' },
    { name: 'System Status', path: '/core', icon: '' },
  ];

  const sidebarBaseClass = "sidebar";
  const sidebarClass = isCollapsed ? `${sidebarBaseClass} collapsed` : sidebarBaseClass;

  return (
    <aside className={sidebarClass} suppressHydrationWarning>
      <div className="sidebar-header" suppressHydrationWarning>
        {(!isCollapsed && mounted) && (
          <div suppressHydrationWarning>
            <h1 className="neon-text" style={{ fontSize: '1.2rem', fontWeight: 'bold' }}> OPERATOR</h1>
            <p style={{ fontSize: '0.6rem', color: 'var(--text-dim)' }}>CONTROL CENTER v1.5</p>
          </div>
        )}
        <button 
          className="toggle-btn" 
          onClick={() => setIsCollapsed(!isCollapsed)}
        >
          {mounted ? (isCollapsed ? '' : '') : ''}
        </button>
      </div>
      
      <nav style={{ flex: 1, padding: '1rem 0.5rem', display: 'flex', flexDirection: 'column', gap: '2rem', overflowY: 'auto' }} suppressHydrationWarning>
        {/* Main Menu */}
        <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.5rem' }} suppressHydrationWarning>
          {menuItems.map((item) => {
            const isActive = pathname === item.path || (item.path !== '/' && pathname.startsWith(item.path));
            const navItemClass = isActive ? "nav-item active" : "nav-item";
            
            return (
              <li key={item.path} suppressHydrationWarning>
                <Link 
                  href={item.path}
                  className={navItemClass}
                  style={{ 
                    textDecoration: 'none', 
                    display: 'flex', 
                    alignItems: 'center',
                    gap: isCollapsed ? '0' : '1rem',
                    justifyContent: isCollapsed ? 'center' : 'flex-start',
                    padding: isCollapsed ? '0.75rem 1rem' : '0.75rem 1rem'
                  }}
                >
                  <span style={{ fontSize: '1.2rem', display: 'flex' }} suppressHydrationWarning>{item.icon}</span>
                  {(!isCollapsed && mounted) && (
                    <span suppressHydrationWarning>
                      {item.name}
                    </span>
                  )}
                </Link>
              </li>
            );
          })}
        </ul>

        {/* Active Circuits Section */}
        {mounted && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }} suppressHydrationWarning>
            {!isCollapsed && (
              <h5 style={{ 
                padding: '0 1rem', fontSize: '0.7rem', color: 'var(--cyber-pink)', 
                letterSpacing: '0.1rem', marginBottom: '0.5rem' 
              }}>
                ACTIVE CIRCUITS
              </h5>
            )}
            <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
              {circuits.map((circuit) => {
                const isActive = pathname === `/circuits/${circuit.name}`;
                return (
                  <li key={circuit.name}>
                    <Link 
                      href={`/circuits/${circuit.name}`}
                      style={{ 
                        textDecoration: 'none', 
                        display: 'flex', 
                        alignItems: 'center',
                        gap: isCollapsed ? '0' : '1rem',
                        justifyContent: isCollapsed ? 'center' : 'flex-start',
                        padding: '0.5rem 1rem',
                        background: isActive ? 'rgba(255, 0, 255, 0.05)' : 'transparent',
                        borderLeft: isActive ? '2px solid var(--cyber-pink)' : '2px solid transparent',
                        color: isActive ? 'var(--cyber-pink)' : 'var(--text-dim)',
                        fontSize: '0.85rem',
                        transition: 'all 0.2s'
                      }}
                    >
                      {isCollapsed ? (
                        <span style={{ fontSize: '0.8rem' }}>●</span>
                      ) : (
                        <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%', alignItems: 'center' }}>
                          <span style={{ fontWeight: isActive ? 'bold' : 'normal' }}>{circuit.name.toUpperCase()}</span>
                          <div style={{ display: 'flex', gap: '0.2rem' }}>
                            {circuit.units.map((unitName, i) => (
                              <span key={i} title={unitName}>{getUnitIcon(unitName)}</span>
                            ))}
                          </div>
                        </div>
                      )}
                    </Link>
                  </li>
                );
              })}
            </ul>
          </div>
        )}

        {/* Units Section  */}
        {mounted && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }} suppressHydrationWarning>
            {!isCollapsed && (
              <h5 style={{ 
                padding: '0 1rem', fontSize: '0.7rem', color: 'var(--cyber-cyan)', 
                letterSpacing: '0.1rem', marginBottom: '0.5rem' 
              }}>
                REGISTERED UNITS
              </h5>
            )}
            <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
              {availableUnits.map((unit) => {
                const name = unit.name;
                return (
                  <li key={name}>
                    <Link
                      href={`/units/${name.toLowerCase()}`}
                      style={{ 
                        textDecoration: 'none',
                        display: 'flex', 
                        alignItems: 'center',
                        gap: isCollapsed ? '0' : '1rem',
                        justifyContent: isCollapsed ? 'center' : 'flex-start',
                        padding: '0.5rem 1rem',
                        color: 'var(--text-dim)',
                        fontSize: '0.85rem',
                        transition: 'all 0.2s'
                      }}
                    >
                      {isCollapsed ? (
                        <span style={{ fontSize: '1rem' }}>{getUnitIcon(name)}</span>
                      ) : (
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                          <span style={{ fontSize: '1rem' }}>{getUnitIcon(name)}</span>
                          <span>{name.toUpperCase()}</span>
                        </div>
                      )}
                    </Link>
                  </li>
                );
              })}
            </ul>
          </div>
        )}
      </nav>

      <div style={{ padding: '1rem', borderTop: '1px solid var(--border-color)', fontSize: '0.8rem' }} suppressHydrationWarning>
        {mounted && (
          !isCollapsed ? (
            <div className="status-badge" style={{ textAlign: 'center' }} suppressHydrationWarning>
              ● ONLINE
            </div>
          ) : (
            <div style={{ textAlign: 'center', color: 'var(--cyber-cyan)' }} suppressHydrationWarning>
              ●
            </div>
          )
        )}
      </div>
    </aside>
  );
}
