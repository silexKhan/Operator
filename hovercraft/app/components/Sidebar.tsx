'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

interface CircuitInfo {
  name: string;
  units: string[];
}

/**
 * [사용자] 통합 API를 통해 실시간 지휘소 정보를 출력하는 고성능 사이드바입니다. 
 * McpClient 기반의 Batching API를 활용하여 로딩 속도를 최적화했습니다.
 */
export default function Sidebar() {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [mounted, setMounted] = useState(false);
  const [circuits, setCircuits] = useState<CircuitInfo[]>([]);
  const [availableUnits, setAvailableUnits] = useState<string[]>([]); 
  const pathname = usePathname();

  useEffect(() => {
    setMounted(true);
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      // [사용자] 통합 API(/api/mcp)로부터 모든 정보를 한 번에 가져옵니다.
      const res = await fetch('/api/mcp');
      const data = await res.json();
      
      if (data.registered_circuits) {
        const details = data.registered_circuits.map((name: string) => ({
          name,
          units: data.circuit_details?.[name]?.units || []
        }));
        setCircuits(details);
      }

      setAvailableUnits(data.active_units || []);

    } catch (e) {
      console.error("Failed to fetch sidebar data", e);
    }
  };

  const getUnitIcon = (unitName: string) => {
    const u = unitName.toLowerCase();
    const iconMap: { [key: string]: string } = {
      'python': '🐍',
      'swift': '🍎',
      'markdown': '📝',
      'sentinel': '🛡️',
      'logic': '⚙️',
      'design': '🎨'
    };
    return iconMap[u] || '🔹';
  };

  const menuItems = [
    { name: 'Dashboard', path: '/', icon: '📊' },
    { name: 'Circuits Registry', path: '/circuits', icon: '⚡' },
    { name: 'Units Registry', path: '/units', icon: '🧩' },
    { name: 'Global Protocols', path: '/protocols', icon: '📜' },
    { name: 'System Status', path: '/core', icon: '🖥️' },
  ];

  const sidebarBaseClass = "sidebar";
  const sidebarClass = isCollapsed ? `${sidebarBaseClass} collapsed` : sidebarBaseClass;

  return (
    <aside className={sidebarClass} suppressHydrationWarning>
      <div className="sidebar-header" suppressHydrationWarning>
        {(!isCollapsed && mounted) && (
          <div suppressHydrationWarning>
            <h1 className="neon-text" style={{ fontSize: '1.2rem', fontWeight: 'bold' }}> OPERATOR</h1>
            <p style={{ fontSize: '0.6rem', color: 'var(--text-dim)' }}>CONTROL CENTER v2.0</p>
          </div>
        )}
        <button 
          className="toggle-btn" 
          onClick={() => setIsCollapsed(!isCollapsed)}
          style={{ cursor: 'pointer' }}
        >
          {mounted ? (isCollapsed ? '▶' : '◀') : ''}
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
                    padding: '0.75rem 1rem'
                  }}
                >
                  <span style={{ fontSize: '1.2rem' }}>{item.icon}</span>
                  {(!isCollapsed && mounted) && <span>{item.name}</span>}
                </Link>
              </li>
            );
          })}
        </ul>

        {/* Active Circuits Section */}
        {mounted && circuits.length > 0 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {!isCollapsed && (
              <h5 style={{ padding: '0 1.2rem', fontSize: '0.7rem', color: 'var(--cyber-pink)', letterSpacing: '0.1rem' }}>
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
                        fontSize: '0.85rem'
                      }}
                    >
                      {isCollapsed ? (
                        <span>●</span>
                      ) : (
                        <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%', alignItems: 'center' }}>
                          <span>{circuit.name.toUpperCase()}</span>
                          <div style={{ display: 'flex', gap: '0.2rem' }}>
                            {circuit.units.map((u, i) => <span key={i}>{getUnitIcon(u)}</span>)}
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

        {/* Registered Units Section */}
        {mounted && availableUnits.length > 0 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {!isCollapsed && (
              <h5 style={{ padding: '0 1.2rem', fontSize: '0.7rem', color: 'var(--cyber-cyan)', letterSpacing: '0.1rem' }}>
                REGISTERED UNITS
              </h5>
            )}
            <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
              {availableUnits.map((unit) => (
                <li key={unit}>
                  <Link
                    href={`/units/${unit.toLowerCase()}`}
                    style={{ 
                      textDecoration: 'none',
                      display: 'flex', 
                      alignItems: 'center',
                      gap: isCollapsed ? '0' : '1rem',
                      justifyContent: isCollapsed ? 'center' : 'flex-start',
                      padding: '0.5rem 1rem',
                      color: 'var(--text-dim)',
                      fontSize: '0.85rem'
                    }}
                  >
                    <span>{getUnitIcon(unit)}</span>
                    {!isCollapsed && <span>{unit.toUpperCase()}</span>}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        )}
      </nav>

      <div style={{ padding: '1rem', borderTop: '1px solid var(--border-color)', fontSize: '0.8rem' }} suppressHydrationWarning>
        {mounted && (
          !isCollapsed ? (
            <div className="status-badge" style={{ textAlign: 'center' }}>● ONLINE</div>
          ) : (
            <div style={{ textAlign: 'center', color: 'var(--cyber-cyan)' }}>●</div>
          )
        )}
      </div>
    </aside>
  );
}
