'use client';

import { useState, useEffect } from 'react';

interface PathBrowserModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelect: (path: string) => void;
  initialPath: string;
}

export default function PathBrowserModal({ isOpen, onClose, initialPath, onSelect }: PathBrowserModalProps) {
  const [currentPath, setCurrentPath] = useState(initialPath || '.');
  const [folders, setFolders] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchFolders = async (path: string) => {
    setLoading(true);
    try {
      const res = await fetch(`/api/mcp/browser?path=${encodeURIComponent(path)}`);
      const data = await res.json();
      if (data.folders) {
        setFolders(data.folders);
        setCurrentPath(data.current);
      }
    } catch (e) {
      console.error("Failed to browse", e);
    }
    setLoading(false);
  };

  useEffect(() => {
    if (isOpen) fetchFolders(currentPath);
  }, [isOpen]);

  const goUp = () => {
    const parent = currentPath.substring(0, currentPath.lastIndexOf('/')) || '/';
    fetchFolders(parent);
  };

  if (!isOpen) return null;

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
        style={{ width: '700px', border: '1px solid var(--cyber-amber)', boxShadow: '0 0 40px rgba(255, 179, 0, 0.2)' }}
      >
        <h3 style={{ color: 'var(--cyber-amber)', marginBottom: '1.5rem' }}> PROJECT PATH EXPLORER</h3>
        
        <div style={{ marginBottom: '1rem', display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <button onClick={goUp} style={{ padding: '0.5rem', background: 'rgba(255,255,255,0.1)', border: 'none', color: 'white', borderRadius: '4px', cursor: 'pointer' }}> UP</button>
          <div style={{ flex: 1, padding: '0.5rem', background: 'rgba(0,0,0,0.3)', borderRadius: '4px', fontFamily: 'monospace', fontSize: '0.8rem', color: 'var(--cyber-cyan)', overflow: 'hidden', textOverflow: 'ellipsis' }}>
            {currentPath}
          </div>
        </div>

        <div style={{ height: '350px', overflowY: 'auto', background: 'rgba(0,0,0,0.2)', borderRadius: '8px', padding: '1rem', display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))', gap: '0.5rem' }}>
          {loading ? (
            <p style={{ color: 'var(--text-dim)' }}>Scanning directories... </p>
          ) : (
            folders.map(folder => (
              <div 
                key={folder}
                onClick={() => fetchFolders(`${currentPath}/${folder}`.replace('//', '/'))}
                style={{ 
                  padding: '0.75rem', background: 'rgba(255,255,255,0.03)', borderRadius: '4px', 
                  fontSize: '0.9rem', cursor: 'pointer', border: '1px solid transparent',
                  transition: 'all 0.2s ease', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis'
                }}
                onMouseEnter={(e) => e.currentTarget.style.borderColor = 'var(--cyber-amber)'}
                onMouseLeave={(e) => e.currentTarget.style.borderColor = 'transparent'}
              >
                 {folder}
              </div>
            ))
          )}
        </div>

        <div style={{ marginTop: '2rem', display: 'flex', justifyContent: 'flex-end', gap: '1rem' }}>
          <button onClick={onClose} style={{ padding: '0.75rem 1.5rem', background: 'transparent', border: '1px solid var(--border-color)', color: 'white', cursor: 'pointer' }}>CANCEL</button>
          <button 
            onClick={() => { onSelect(currentPath); onClose(); }}
            style={{ padding: '0.75rem 2rem', background: 'var(--cyber-amber)', border: 'none', color: 'black', fontWeight: 'bold', borderRadius: '4px', cursor: 'pointer' }}
          >
            SELECT THIS FOLDER
          </button>
        </div>
      </div>
    </div>
  );
}
