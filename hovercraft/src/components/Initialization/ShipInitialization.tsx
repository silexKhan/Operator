"use client";

import React, { useState } from 'react';

interface ShipInitializationProps {
  onComplete: (shipName: string, captainName: string) => void;
}

export const ShipInitialization: React.FC<ShipInitializationProps> = ({ onComplete }) => {
  const [shipName, setShipName] = useState('');
  const [captainName, setCaptainName] = useState('');
  const [isSubmitting, setIsComplete] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!shipName || !captainName) return;

    setIsComplete(true);
    try {
      const res = await fetch('/api/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ shipName, captainName }),
      });

      if (res.ok) {
        onComplete(shipName, captainName);
      }
    } catch (error) {
      console.error('Failed to initialize ship:', error);
      setIsComplete(false);
    }
  };

  return (
    <div className="fixed inset-0 z-[100] bg-black flex items-center justify-center p-4">
      <div className="w-full max-w-md border border-green-500 p-8 bg-black shadow-[0_0_20px_rgba(34,197,94,0.2)]">
        <h1 className="text-green-500 font-mono text-xl mb-8 uppercase tracking-widest border-b border-green-900 pb-2">
          System_Initialization.exe
        </h1>
        
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-green-900 font-mono text-[10px] uppercase mb-1">Ship Designation</label>
            <input
              autoFocus
              type="text"
              value={shipName}
              onChange={(e) => setShipName(e.target.value.toUpperCase())}
              placeholder="e.g. NEBUCHADNEZZAR"
              className="w-full bg-transparent border border-green-900 p-2 text-green-400 font-mono text-sm focus:border-green-500 outline-none transition-all"
              required
            />
          </div>
          
          <div>
            <label className="block text-green-900 font-mono text-[10px] uppercase mb-1">Captain ID</label>
            <input
              type="text"
              value={captainName}
              onChange={(e) => setCaptainName(e.target.value)}
              placeholder="e.g. MORPHEUS"
              className="w-full bg-transparent border border-green-900 p-2 text-green-400 font-mono text-sm focus:border-green-500 outline-none transition-all"
              required
            />
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full border border-green-500 py-2 text-green-500 font-mono text-sm hover:bg-green-500 hover:text-black transition-all disabled:opacity-50"
          >
            {isSubmitting ? 'ESTABLISHING LINK...' : 'AUTHORIZE ACCESS'}
          </button>
        </form>
        
        <div className="mt-8 text-[9px] text-green-900 font-mono leading-tight">
          WARNING: Identity data will be stored locally. <br />
          Unauthorized access to this terminal is punishable by system expulsion.
        </div>
      </div>
    </div>
  );
};
