import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI5K Trinity Dashboard",
  description: "Organization-first, evidence-based AI capability platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        {/* Glowing Background Effect */}
        <div className="bg-glow-1"></div>
        <div className="bg-glow-2"></div>
        
        {/* Navigation */}
        <nav className="glass-panel" style={{ position: 'sticky', top: 0, zIndex: 50, borderBottom: '1px solid rgba(255,255,255,0.1)', padding: '16px 24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: 'linear-gradient(to top right, var(--primary-color), var(--secondary-color))', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold', color: 'black' }}>A5</div>
            <h1 style={{ fontSize: '20px', fontWeight: 'bold', letterSpacing: '0.1em' }}>AI5K <span style={{ color: 'var(--primary-color)', fontSize: '14px', fontWeight: 'normal' }}>TRINITY</span></h1>
          </div>
          <div style={{ display: 'flex', gap: '16px' }}>
            <button className="nav-btn active">Profile Intel</button>
            <button className="nav-btn">Opp Matcher</button>
            <button className="nav-btn">Pod Teaming</button>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: 'var(--success-color)' }}></div>
            <span style={{ fontSize: '12px', color: 'var(--success-color)', letterSpacing: '0.1em', textTransform: 'uppercase' }}>System Online</span>
          </div>
        </nav>

        {children}
      </body>
    </html>
  );
}
