'use client';

import dynamic from 'next/dynamic';
import { useEffect, useRef, useState } from 'react';

// ForceGraph는 클라이언트 사이드에서만 렌더링되도록 dynamic import 처리합니다. 📞⚡️
const ForceGraph2D = dynamic(() => import('react-force-graph-2d'), { ssr: false });

/**
 * [대장님 🎯] 모든 Circuit 간의 의존성 및 연결 상태를 시각화하는 다이어그램입니다. 🛰️⚡️
 */
export default function CircuitMap({ graphData, onNodeClick }: { graphData: any, onNodeClick: (name: string) => void }) {
  const fgRef = useRef<any>();
  const [windowSize, setWindowSize] = useState({ width: 800, height: 500 });

  useEffect(() => {
    const handleResize = () => {
      setWindowSize({ width: window.innerWidth - 400, height: 400 });
    };
    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  if (!graphData) return null;

  return (
    <div className="card" style={{ padding: '1rem', position: 'relative', overflow: 'hidden', cursor: 'pointer' }}>
      <h5 className="neon-text" style={{ position: 'absolute', top: '1rem', left: '1rem', zIndex: 10 }}>
        🛰️ CIRCUIT ARCHITECTURE MAP
      </h5>
      
      <ForceGraph2D
        ref={fgRef}
        graphData={graphData}
        width={windowSize.width}
        height={windowSize.height}
        backgroundColor="#0a0a0a"
        onNodeClick={(node: any) => onNodeClick(node.id)}
        nodeLabel="id"
        nodeColor={(node: any) => node.group === 1 ? "#00f3ff" : node.group === 2 ? "#ffcc00" : "#ff3366"}
        nodeCanvasObject={(node: any, ctx: CanvasRenderingContext2D, globalScale: number) => {
          const label = node.id;
          const fontSize = 12 / globalScale;
          ctx.font = `${fontSize}px Inter`;
          const textWidth = ctx.measureText(label).width;
          const bckgDimensions = [textWidth, fontSize].map(n => n + fontSize * 0.8);

          ctx.fillStyle = 'rgba(10, 10, 10, 0.8)';
          ctx.fillRect(node.x - bckgDimensions[0] / 2, node.y - bckgDimensions[1] / 2, bckgDimensions[0], bckgDimensions[1]);
          
          ctx.strokeStyle = node.group === 1 ? "#00f3ff" : "#ffcc00";
          ctx.strokeRect(node.x - bckgDimensions[0] / 2, node.y - bckgDimensions[1] / 2, bckgDimensions[0], bckgDimensions[1]);

          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillStyle = node.group === 1 ? "#00f3ff" : "#ffcc00";
          ctx.fillText(label, node.x, node.y);
        }}
        linkColor={() => 'rgba(0, 243, 255, 0.2)'}
        linkDirectionalParticles={2}
        linkDirectionalParticleSpeed={0.005}
        linkDirectionalParticleWidth={2}
      />
      
      <div style={{ position: 'absolute', bottom: '1rem', right: '1rem', fontSize: '0.7rem', color: 'var(--text-dim)' }}>
        * Dynamic Circuit Interconnection Map | Scale: {windowSize.width}x{windowSize.height}
      </div>
    </div>
  );
}
