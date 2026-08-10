"use client";

import { useState, useRef, useEffect } from 'react';
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
    <main style={{ padding: '32px', maxWidth: '1200px', margin: '0 auto' }}>
      <header style={{ marginBottom: '32px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontSize: '28px', fontWeight: 'bold' }}>Layer 1: Profile Intelligence</h2>
          <p style={{ color: 'var(--text-secondary)', marginTop: '8px' }}>Verified Capability Ingestion & Analytics</p>
        </div>
      </header>

      {/* Input Section */}
      <div className="glass-panel" style={{ padding: '24px', marginBottom: '32px', display: 'flex', gap: '16px', alignItems: 'center', flexWrap: 'wrap' }}>
        <input 
          type="file" 
          accept=".pdf"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
          style={{ padding: '8px', background: 'rgba(255,255,255,0.05)', borderRadius: '4px', border: '1px solid var(--border-color)', color: 'white' }} 
        />
        <input 
          type="text" 
          placeholder="GitHub Username" 
          value={githubUrl}
          onChange={(e) => setGithubUrl(e.target.value)}
          style={{ padding: '10px 16px', background: 'rgba(255,255,255,0.05)', borderRadius: '4px', border: '1px solid var(--border-color)', color: 'white', minWidth: '200px' }} 
        />
        <button 
          onClick={handleUpload}
          disabled={status === 'analyzing'}
          style={{ background: 'var(--primary-color)', color: 'black', padding: '10px 24px', border: 'none', borderRadius: '4px', fontWeight: 'bold', cursor: status === 'analyzing' ? 'not-allowed' : 'pointer' }}
        >
          {status === 'analyzing' ? `Analyzing (${progress}%)` : 'Run Pipeline'}
        </button>
        {errorMsg && <span style={{ color: 'var(--danger-color, #ff003c)' }}>{errorMsg}</span>}
      </div>

      {status === 'success' && (
        <>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '24px', marginBottom: '24px' }}>
            
            {/* Overall Readiness */}
            <div className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <h3 style={{ fontSize: '14px', textTransform: 'uppercase', letterSpacing: '0.1em', color: 'var(--text-secondary)', marginBottom: '16px', width: '100%' }}>Overall Readiness</h3>
              <div style={{ position: 'relative', width: '150px', height: '150px', borderRadius: '50%', background: `conic-gradient(var(--primary-color) ${overallScore}%, rgba(255,255,255,0.05) 0)`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <div style={{ width: '130px', height: '130px', borderRadius: '50%', backgroundColor: 'var(--surface-color)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column' }}>
                  <span style={{ fontSize: '36px', fontWeight: 'bold' }}>{overallScore}<span style={{ fontSize: '16px', color: 'var(--text-secondary)' }}>/100</span></span>
                </div>
              </div>
            </div>

            {/* 7-Dimension Radar */}
            <div className="glass-panel" style={{ padding: '24px' }}>
              <h3 style={{ fontSize: '14px', textTransform: 'uppercase', letterSpacing: '0.1em', color: 'var(--text-secondary)', marginBottom: '16px' }}>Performance Vector Plot</h3>
              <div style={{ height: '300px', width: '100%' }}>
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart cx="50%" cy="50%" outerRadius="80%" data={radarData}>
                    <PolarGrid stroke="rgba(255,255,255,0.1)" />
                    <PolarAngleAxis dataKey="subject" tick={{ fill: '#94a3b8', fontSize: 12 }} />
                    <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                    <Radar name="Score" dataKey="A" stroke="var(--secondary-color)" fill="var(--secondary-color)" fillOpacity={0.4} />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
            {/* Evidence Hierarchy */}
            <div className="glass-panel" style={{ padding: '24px' }}>
              <h3 style={{ fontSize: '14px', textTransform: 'uppercase', letterSpacing: '0.1em', color: 'var(--text-secondary)', marginBottom: '16px' }}>Evidence Hierarchy (T1-T8)</h3>
              <div style={{ height: '200px', width: '100%' }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={barData} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" horizontal={false} />
                    <XAxis type="number" hide />
                    <YAxis dataKey="name" type="category" hide />
                    <Tooltip contentStyle={{ backgroundColor: 'rgba(10,10,15,0.9)', borderColor: 'rgba(255,255,255,0.1)' }} />
                    <Legend />
                    <Bar dataKey="T1_T2" stackId="a" fill="var(--success-color)" name="T1-T2 (Verified Code)" />
                    <Bar dataKey="T3_T4" stackId="a" fill="var(--primary-color)" name="T3-T4 (References)" />
                    <Bar dataKey="T5_T6" stackId="a" fill="var(--secondary-color)" name="T5-T6 (Self-Reported)" />
                    <Bar dataKey="T7_T8" stackId="a" fill="#333" name="T7-T8 (Weak/None)" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
            
            {/* Gap Actions */}
            <div className="glass-panel" style={{ padding: '24px', overflowY: 'auto', maxHeight: '300px' }}>
              <h3 style={{ fontSize: '14px', textTransform: 'uppercase', letterSpacing: '0.1em', color: 'var(--text-secondary)', marginBottom: '16px' }}>Priority Gap Actions</h3>
              <ul style={{ listStyle: 'none', padding: 0 }}>
                {resultData.result.gap_actions?.map((gap: any, i: number) => (
                  <li key={i} style={{ padding: '12px', borderBottom: '1px solid var(--border-color)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ fontWeight: 'bold', color: 'var(--primary-color)' }}>{gap.action_type}</span>
                      <span style={{ fontSize: '12px', color: gap.priority === 'High' ? 'var(--danger-color, #ff003c)' : 'var(--text-secondary)' }}>{gap.priority} Priority</span>
                    </div>
                    <p style={{ fontSize: '14px', marginTop: '4px' }}>{gap.description}</p>
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
