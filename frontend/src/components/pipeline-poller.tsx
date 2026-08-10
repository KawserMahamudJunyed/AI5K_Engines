"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Loader2 } from 'lucide-react';
import { PipelineStatus } from '../types';

export default function PipelinePoller({ runId, onComplete }: { runId: string, onComplete: (data: any) => void }) {
  const [status, setStatus] = useState<PipelineStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const API_URL = "https://ai5k-engines.onrender.com";
  
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`${API_URL}/analyze/${runId}/status`);
        if (!res.ok) return;
        const data = await res.json() as PipelineStatus;
        setStatus(data);
        
        if (data.status === 'completed') {
          clearInterval(interval);
          
          // Fetch results
          const resultRes = await fetch(`${API_URL}/analyze/${runId}/result`);
          if (resultRes.ok) {
              const resultData = await resultRes.json();
              onComplete(resultData);
          } else {
              setError("Failed to fetch final results");
          }
        } else if (data.status === 'failed') {
          clearInterval(interval);
          setError(data.error || "Analysis failed");
        }
      } catch (err: any) {
        console.error("Polling error", err);
      }
    }, 1500); // 1.5 seconds per prompt v2 requirements

    return () => clearInterval(interval);
  }, [runId, onComplete]);

  return (
    <div className="flex flex-col items-center justify-center p-12 glass-panel w-full max-w-lg mx-auto">
      <Loader2 className="w-16 h-16 text-[--color-brand-purple] animate-spin mb-6" />
      <h3 className="text-xl font-bold font-mono tracking-widest text-white mb-2">PIPELINE ACTIVE</h3>
      <p className="text-[--color-brand-cyan] font-mono text-sm uppercase mb-6">
        {status ? `STAGE: ${status.status.toUpperCase()}` : "INITIALIZING..."}
      </p>
      
      <div className="w-full bg-black/50 rounded-full h-2 mb-2">
        <div 
          className="h-2 rounded-full bg-gradient-to-r from-[--color-brand-purple] to-[--color-brand-cyan] transition-all duration-500"
          style={{ width: `${status?.progress || 10}%` }}
        ></div>
      </div>
      
      {error && <p className="text-[--color-brand-danger] text-sm mt-4">{error}</p>}
    </div>
  );
}
