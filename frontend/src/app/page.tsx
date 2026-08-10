"use client";

import { useState } from 'react';
import { 
  Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend
} from 'recharts';

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [githubUrl, setGithubUrl] = useState('');
  const [upworkUrl, setUpworkUrl] = useState('');
  
  const [status, setStatus] = useState<string>('idle'); // idle, analyzing, success, error
  const [progress, setProgress] = useState(0);
  const [resultData, setResultData] = useState<any>(null);
  const [errorMsg, setErrorMsg] = useState('');

  const API_URL = "https://ai5k-engines.onrender.com";

  const handleUpload = async () => {
    if (!file && !githubUrl && !upworkUrl) {
      setErrorMsg("Please provide at least a CV, GitHub URL, or Upwork URL");
      return;
    }
    
    setStatus('analyzing');
    setProgress(10);
    setErrorMsg('');

    try {
      const formData = new FormData();
      if (file) formData.append('cv_file', file);
      if (githubUrl) formData.append('github_username', githubUrl);
      if (upworkUrl) formData.append('upwork_url', upworkUrl);
      formData.append('niche', 'backend');

      const startRes = await fetch(`${API_URL}/analyze`, {
        method: 'POST',
        body: formData,
      });

      if (!startRes.ok) throw new Error("Failed to start analysis");
      
      const { run_id } = await startRes.json();
      pollStatus(run_id);
    } catch (err: any) {
      setStatus('error');
      setErrorMsg(err.message);
    }
  };

  const pollStatus = async (runId: string) => {
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`${API_URL}/analyze/${runId}/status`);
        if (!res.ok) return;
        const data = await res.json();
        
        if (data.status === 'completed') {
          clearInterval(interval);
          setProgress(100);
          fetchResult(runId);
        } else if (data.status === 'failed') {
          clearInterval(interval);
          setStatus('error');
          setErrorMsg(data.error || "Analysis failed");
        } else {
          setProgress(Math.min(90, progress + 15));
        }
      } catch (err) {
        console.error("Polling error", err);
      }
    }, 2000);
  };

  const fetchResult = async (runId: string) => {
    try {
      const res = await fetch(`${API_URL}/analyze/${runId}/result`);
      if (!res.ok) throw new Error("Failed to fetch final results");
      const data = await res.json();
      setResultData(data);
      setStatus('success');
    } catch (err: any) {
      setStatus('error');
      setErrorMsg(err.message);
    }
  };

  // Safe fallback data for charts
  const radarData = resultData?.result?.readiness_score?.dimensions ? [
    { subject: 'Positioning', A: resultData.result.readiness_score.dimensions.positioning_alignment, fullMark: 100 },
    { subject: 'Evidence Q.', A: resultData.result.readiness_score.dimensions.evidence_quality, fullMark: 100 },
    { subject: 'Keyword Cov.', A: resultData.result.readiness_score.dimensions.keyword_coverage, fullMark: 100 },
    { subject: 'Portfolio', A: resultData.result.readiness_score.dimensions.portfolio_strength, fullMark: 100 },
    { subject: 'Completeness', A: resultData.result.readiness_score.dimensions.profile_completeness, fullMark: 100 },
  ] : [
    { subject: 'Positioning', A: 0, fullMark: 100 }, { subject: 'Evidence Q.', A: 0, fullMark: 100 }, { subject: 'Keyword Cov.', A: 0, fullMark: 100 }, { subject: 'Portfolio', A: 0, fullMark: 100 }, { subject: 'Completeness', A: 0, fullMark: 100 }
  ];

  const overallScore = resultData?.result?.readiness_score?.overall_readiness_score || 0;

  const barData = resultData?.result?.claims ? [
    { 
      name: 'Claims', 
      T1_T2: resultData.result.claims.filter((c:any) => c.tier === 'T1' || c.tier === 'T2').length,
      T3_T4: resultData.result.claims.filter((c:any) => c.tier === 'T3' || c.tier === 'T4').length,
      T5_T6: resultData.result.claims.filter((c:any) => c.tier === 'T5' || c.tier === 'T6').length,
      T7_T8: resultData.result.claims.filter((c:any) => c.tier === 'T7' || c.tier === 'T8').length,
    }
  ] : [{ name: 'Claims', T1_T2: 0, T3_T4: 0, T5_T6: 0, T7_T8: 0 }];

  return (
    <main className="container mx-auto px-6 py-8">
      
      <header className="mb-8 flex justify-between items-end">
        <div>
          <h2 className="text-3xl font-bold text-white">Layer 1: Profile Intelligence</h2>
          <p className="text-gray-400 mt-2">Verified Capability Ingestion & 7-Dimension Analytics</p>
        </div>
      </header>

      {/* Input Section */}
      <div className="glass-panel p-6 mb-8 flex flex-wrap gap-4 items-center">
        <div className="flex-1 min-w-[250px]">
            <label className="block text-xs text-cyber-primary uppercase tracking-wider mb-2">Upload PDF CV</label>
            <input 
                type="file" 
                accept=".pdf"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                className="w-full text-sm text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-cyber-primary/20 file:text-cyber-primary hover:file:bg-cyber-primary/30"
            />
        </div>
        <div className="flex-1 min-w-[250px]">
            <label className="block text-xs text-cyber-secondary uppercase tracking-wider mb-2">GitHub Username</label>
            <input 
                type="text" 
                placeholder="e.g. torvalds" 
                value={githubUrl}
                onChange={(e) => setGithubUrl(e.target.value)}
                className="w-full bg-black/50 border border-white/10 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-cyber-secondary"
            />
        </div>
        <div className="w-full md:w-auto flex items-end">
            <button 
                onClick={handleUpload}
                disabled={status === 'analyzing'}
                className="w-full md:w-auto bg-gradient-to-r from-cyber-primary to-cyber-secondary text-black font-bold py-3 px-8 rounded-lg shadow-[0_0_15px_rgba(0,240,255,0.3)] hover:shadow-[0_0_25px_rgba(0,240,255,0.5)] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
                {status === 'analyzing' ? `ANALYZING [${progress}%]` : 'INITIALIZE PIPELINE'}
            </button>
        </div>
        {errorMsg && <div className="w-full text-cyber-danger text-sm mt-2">{errorMsg}</div>}
      </div>

      {status === 'success' && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            
            {/* Overall Readiness */}
            <div className="glass-panel p-6 flex flex-col items-center justify-center relative">
              <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4 w-full text-left">Overall Readiness</h3>
              <div className="relative w-[150px] h-[150px] rounded-full flex items-center justify-center" style={{ background: `conic-gradient(var(--color-cyber-primary) ${overallScore}%, rgba(255,255,255,0.05) 0)` }}>
                <div className="w-[130px] h-[130px] rounded-full bg-cyber-bg flex items-center justify-center flex-col shadow-inner">
                  <span className="text-4xl font-bold text-white">{overallScore}<span className="text-lg text-gray-500">/100</span></span>
                </div>
              </div>
            </div>

            {/* 7-Dimension Radar */}
            <div className="glass-panel p-6 md:col-span-2">
              <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">7-Dimension Vector Plot</h3>
              <div className="h-[250px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart cx="50%" cy="50%" outerRadius="80%" data={radarData}>
                    <PolarGrid stroke="rgba(255,255,255,0.1)" />
                    <PolarAngleAxis dataKey="subject" tick={{ fill: '#94a3b8', fontSize: 11 }} />
                    <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                    <Radar name="Current Profile" dataKey="A" stroke="var(--color-cyber-secondary)" strokeWidth={2} fill="var(--color-cyber-secondary)" fillOpacity={0.2} dot={{ fill: 'var(--color-cyber-primary)', r: 3 }} />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Evidence Hierarchy */}
            <div className="glass-panel p-6">
              <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">Evidence Hierarchy (T1-T8)</h3>
              <div className="h-[200px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={barData} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" horizontal={false} />
                    <XAxis type="number" hide />
                    <YAxis dataKey="name" type="category" hide />
                    <Tooltip cursor={{fill: 'rgba(255,255,255,0.05)'}} contentStyle={{ backgroundColor: 'rgba(10,10,15,0.9)', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '8px', color: '#fff' }} />
                    <Legend iconType="circle" wrapperStyle={{ fontSize: '12px', color: '#94a3b8' }} />
                    <Bar dataKey="T1_T2" stackId="a" fill="var(--color-cyber-success)" name="T1-T2 (Verified Code)" radius={[0, 0, 0, 0]} />
                    <Bar dataKey="T3_T4" stackId="a" fill="var(--color-cyber-primary)" name="T3-T4 (References)" radius={[0, 0, 0, 0]} />
                    <Bar dataKey="T5_T6" stackId="a" fill="var(--color-cyber-secondary)" name="T5-T6 (Self-Reported)" radius={[0, 0, 0, 0]} />
                    <Bar dataKey="T7_T8" stackId="a" fill="#334155" name="T7-T8 (Weak/None)" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
            
            {/* Gap Actions */}
            <div className="glass-panel p-6 overflow-y-auto max-h-[300px]">
              <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">Priority Gap Actions</h3>
              <ul className="space-y-3">
                {resultData.result.gap_actions?.map((gap: any, i: number) => (
                  <li key={i} className="p-4 bg-white/5 border border-white/10 rounded-lg hover:border-cyber-primary/50 transition-colors">
                    <div className="flex justify-between items-start mb-2">
                      <span className="font-bold text-cyber-primary text-sm">{gap.action_type}</span>
                      <span className={`text-xs px-2 py-1 rounded border ${gap.priority === 'High' ? 'text-cyber-danger bg-cyber-danger/10 border-cyber-danger/30' : 'text-cyber-warning bg-cyber-warning/10 border-cyber-warning/30'}`}>
                        {gap.priority} PRIORITY
                      </span>
                    </div>
                    <p className="text-sm text-gray-300">{gap.description}</p>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </>
      )}
    </main>
  );
}
