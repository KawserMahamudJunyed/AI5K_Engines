"use client";

import { useState } from 'react';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import PipelinePoller from '@/components/pipeline-poller';
import ReadinessGauge from '@/components/charts/readiness-gauge';
import DimensionRadar from '@/components/charts/dimension-radar';
import ClaimsStackedBar from '@/components/charts/claims-stacked-bar';
import GapScatterPlot from '@/components/charts/gap-scatter-plot';

export default function ProfileEngine() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [cvText, setCvText] = useState('');
  const [githubUrl, setGithubUrl] = useState('');
  const [upworkUrl, setUpworkUrl] = useState('');
  const [niche, setNiche] = useState('');
  const [rate, setRate] = useState('');
  const [version, setVersion] = useState('1.0');
  
  const [status, setStatus] = useState<'idle' | 'polling' | 'complete'>('idle');
  const [runId, setRunId] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState('');
  const [result, setResult] = useState<any>(null);

  const API_URL = "https://ai5k-engines.onrender.com";

  const handleUpload = async () => {
    setErrorMsg('');

    try {
      const formData = new FormData();
      if (file) formData.append('cv_file', file);
      if (cvText) formData.append('cv_text', cvText);
      if (githubUrl) formData.append('github_username', githubUrl);
      if (upworkUrl) formData.append('upwork_url', upworkUrl);
      if (niche) formData.append('niche', niche);
      if (rate) formData.append('rate_desired', rate);
      if (version) formData.append('version', version);

      const startRes = await fetch(`${API_URL}/analyze`, {
        method: 'POST',
        body: formData,
      });

      if (!startRes.ok) throw new Error("Failed to start analysis pipeline");
      
      const data = await startRes.json();
      setRunId(data.run_id);
      setStatus('polling');
    } catch (err: any) {
      setErrorMsg(err.message);
    }
  };

  const handlePipelineComplete = (resultData: any) => {
    setResult(resultData);
    setStatus('complete');
  };

  const handleReset = () => {
    setStatus('idle');
    setResult(null);
    setRunId(null);
  };

  if (status === 'polling' && runId) {
    return (
      <main className="flex min-h-[calc(100vh-80px)] flex-col items-center justify-center p-6 relative z-10 transition-opacity duration-1000">
        <PipelinePoller runId={runId} onComplete={handlePipelineComplete} />
      </main>
    );
  }

  if (status === 'complete' && result) {
    const scores = result.scoring || {};
    const finalScore = scores.final_score || 0;
    const lockActive = finalScore < 30; // Just as an example visual trigger

    return (
      <main className="flex min-h-screen flex-col items-center p-6 relative z-10 font-sans w-full max-w-7xl mx-auto">
        <header className="mb-12 mt-8 text-center w-full flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold font-outfit text-white tracking-widest uppercase">Profile Intelligence Report</h1>
            <p className="text-gray-400 mt-2">Target Niche: <span className="text-brand-purple font-mono">{result.niche || niche || 'Unknown'}</span></p>
          </div>
          <button onClick={handleReset} className="px-6 py-2 border border-white/20 text-white rounded hover:bg-white/10 transition-colors font-mono text-sm uppercase">Run New Analysis</button>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 w-full mb-8">
          {/* Gauge Chart */}
          <div className="p-6 rounded-2xl border border-white/10 bg-[#141419]/80 backdrop-blur-md shadow-2xl flex flex-col items-center">
            <h3 className="text-sm font-bold text-gray-400 uppercase tracking-widest mb-6 w-full text-left">Readiness Baseline</h3>
            <div className="relative w-full h-[300px]">
              <ReadinessGauge score={finalScore} />
              {lockActive && (
                <div className="absolute inset-0 flex items-center justify-center bg-black/60 rounded-xl backdrop-blur-sm z-10">
                  <div className="text-brand-danger text-center font-mono">
                    <svg className="w-12 h-12 mx-auto mb-2 opacity-80" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path></svg>
                    CRITICAL: INSUFFICIENT EVIDENCE
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Radar Chart */}
          <div className="p-6 rounded-2xl border border-white/10 bg-[#141419]/80 backdrop-blur-md shadow-2xl lg:col-span-2 flex flex-col">
            <h3 className="text-sm font-bold text-gray-400 uppercase tracking-widest mb-6 w-full text-left">7-Dimension Cyber Radar</h3>
            <div className="flex-1 w-full flex items-center justify-center min-h-[300px]">
              <DimensionRadar dimensions={scores.dimensions || {}} />
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 w-full">
          {/* Claims Stacked Bar */}
          <div className="p-6 rounded-2xl border border-white/10 bg-[#141419]/80 backdrop-blur-md shadow-2xl">
             <h3 className="text-sm font-bold text-gray-400 uppercase tracking-widest mb-6">Evidence Provenance</h3>
             <div className="w-full h-[300px]">
               <ClaimsStackedBar claims={result.claims || []} />
             </div>
          </div>

          {/* Gap Actions */}
          <div className="p-6 rounded-2xl border border-white/10 bg-[#141419]/80 backdrop-blur-md shadow-2xl">
             <h3 className="text-sm font-bold text-gray-400 uppercase tracking-widest mb-6">Remediation Scatter Plot</h3>
             <div className="w-full h-[300px]">
               <GapScatterPlot gaps={result.gaps || []} />
             </div>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="flex min-h-screen flex-col items-center p-6 relative z-10 overflow-hidden font-sans">
      
      {/* Centered Logo with Header */}
      <div className="relative mb-12 flex flex-col items-center mt-12">
        <Image src="/logo.png" alt="AI5K Logo" width={120} height={120} priority className="mb-4" />
        <h1 className="text-4xl font-bold tracking-tight text-white flex items-center gap-2 font-outfit">
          AI5K <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-purple to-brand-cyan">Intelligence Engine</span>
        </h1>
        <p className="mt-2 text-gray-300 font-medium text-sm">
          Real-time profile assessment and dimensional scoring.
        </p>
      </div>

      {/* Input Glass Panel */}
      <div className="p-8 w-full max-w-4xl flex flex-col mb-12 rounded-2xl border border-white/5 bg-[#141419]/60 backdrop-blur-xl shadow-2xl">
        <h2 className="text-2xl font-bold text-white mb-6 font-outfit">Run Analysis</h2>
        
        {/* Row 1: 3 Columns */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <div className="flex flex-col gap-2">
            <label className="text-sm font-medium text-gray-400">Target Niche</label>
            <input 
              type="text" 
              placeholder="ai-ml-engineer" 
              value={niche}
              onChange={(e) => setNiche(e.target.value)}
              className="w-full bg-black/30 border border-white/10 rounded-lg px-4 py-3 text-gray-200 focus:outline-none focus:border-brand-purple transition-colors"
            />
          </div>
          <div className="flex flex-col gap-2">
            <label className="text-sm font-medium text-gray-400">Benchmark Version</label>
            <input 
              type="text" 
              placeholder="1.0" 
              value={version}
              onChange={(e) => setVersion(e.target.value)}
              className="w-full bg-black/30 border border-white/10 rounded-lg px-4 py-3 text-gray-200 focus:outline-none focus:border-brand-purple transition-colors"
            />
          </div>
          <div className="flex flex-col gap-2">
            <label className="text-sm font-medium text-gray-400">Desired Hourly Rate ($)</label>
            <input 
              type="number" 
              placeholder="120" 
              value={rate}
              onChange={(e) => setRate(e.target.value)}
              className="w-full bg-black/30 border border-white/10 rounded-lg px-4 py-3 text-gray-200 focus:outline-none focus:border-brand-purple transition-colors"
            />
          </div>
        </div>

        {/* Row 2: Full Width */}
        <div className="flex flex-col gap-2 mb-6">
          <label className="text-sm font-medium text-gray-400">Upload CV (PDF)</label>
          <div 
            className={`w-full border-2 border-dashed rounded-xl p-8 flex flex-col items-center justify-center cursor-pointer transition-all ${
              file ? 'border-brand-success bg-brand-success/5' : 'border-white/20 hover:border-brand-purple hover:bg-white/5'
            }`}
            onClick={() => document.getElementById('cv-upload')?.click()}
            onDragOver={(e) => { e.preventDefault(); e.currentTarget.classList.add('border-brand-purple', 'bg-white/5'); }}
            onDragLeave={(e) => { e.preventDefault(); e.currentTarget.classList.remove('border-brand-purple', 'bg-white/5'); }}
            onDrop={(e) => {
              e.preventDefault();
              e.currentTarget.classList.remove('border-brand-purple', 'bg-white/5');
              const droppedFile = e.dataTransfer.files[0];
              if (droppedFile?.type === 'application/pdf') {
                setFile(droppedFile);
              } else {
                setErrorMsg('Please drop a valid PDF file.');
              }
            }}
          >
            <input 
              id="cv-upload"
              type="file" 
              accept=".pdf"
              className="hidden"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
            />
            {file ? (
              <div className="flex flex-col items-center text-brand-success">
                <svg className="w-8 h-8 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                <span className="font-mono text-sm">{file.name}</span>
              </div>
            ) : (
              <div className="flex flex-col items-center text-gray-400">
                <svg className="w-8 h-8 mb-2 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path></svg>
                <span className="font-medium text-sm">Click to upload or drag and drop</span>
                <span className="text-xs text-gray-500 mt-1">PDF (MAX. 10MB)</span>
              </div>
            )}
          </div>
        </div>

        {/* Row 3: 2 Columns */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div className="flex flex-col gap-2">
            <label className="text-sm font-medium text-gray-400">GitHub Profile URL</label>
            <input 
              type="text" 
              placeholder="https://github.com/username" 
              value={githubUrl}
              onChange={(e) => setGithubUrl(e.target.value)}
              className="w-full bg-black/30 border border-white/10 rounded-lg px-4 py-3 text-gray-200 focus:outline-none focus:border-brand-purple transition-colors"
            />
          </div>
          <div className="flex flex-col gap-2">
            <label className="text-sm font-medium text-gray-400">Upwork Profile URL</label>
            <input 
              type="text" 
              placeholder="https://upwork.com/freelancers/..." 
              value={upworkUrl}
              onChange={(e) => setUpworkUrl(e.target.value)}
              className="w-full bg-black/30 border border-white/10 rounded-lg px-4 py-3 text-gray-200 focus:outline-none focus:border-brand-purple transition-colors"
            />
          </div>
        </div>

        {/* Row 4: Full Width Textarea */}
        <div className="flex flex-col gap-2 mb-8">
          <label className="text-sm font-medium text-gray-400">CV / Resume Text (Fallback)</label>
          <textarea 
            rows={3}
            placeholder="Senior Machine Learning Engineer with 10 years of experience..." 
            value={cvText}
            onChange={(e) => setCvText(e.target.value)}
            className="w-full bg-black/30 border border-white/10 rounded-lg px-4 py-3 text-gray-200 focus:outline-none focus:border-brand-purple transition-colors resize-y"
          />
        </div>

        <button 
          onClick={handleUpload}
          className="w-full bg-gradient-to-r from-brand-purple to-brand-cyan text-white font-bold py-4 rounded-lg shadow-lg hover:-translate-y-0.5 hover:shadow-[0_0_20px_rgba(196,136,251,0.4)] transition-all duration-200"
        >
          Analyze Profile
        </button>

        {errorMsg && <div className="w-full text-red-400 text-sm font-medium mt-4 p-4 bg-red-400/10 border-l-4 border-red-400 rounded-r-lg">{errorMsg}</div>}
      </div>
    </main>
  );
}
