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
    <html lang="en" className="dark">
      <body className="bg-cyber-bg text-gray-200 font-sans min-h-screen overflow-x-hidden selection:bg-cyber-primary selection:text-black">
        
        {/* Glowing Background Effect */}
        <div className="fixed top-0 left-0 w-full h-full overflow-hidden -z-10 pointer-events-none">
          <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-cyber-secondary opacity-20 blur-[120px]"></div>
          <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] rounded-full bg-cyber-primary opacity-10 blur-[150px]"></div>
        </div>
        
        {/* Navigation */}
        <nav className="glass-panel sticky top-0 z-50 border-b border-white/10 px-6 py-4 flex justify-between items-center rounded-none border-x-0 border-t-0">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-cyber-primary to-cyber-secondary flex items-center justify-center font-bold text-black">A5</div>
            <h1 className="text-xl font-bold tracking-widest text-white">AI5K <span className="text-cyber-primary text-sm font-normal">TRINITY</span></h1>
          </div>
          <div className="flex gap-4">
            <button className="nav-btn active">Profile Intel</button>
            <button className="nav-btn">Opp Matcher</button>
            <button className="nav-btn">Pod Teaming</button>
          </div>
          <div className="flex items-center gap-3">
            <div className="w-2 h-2 rounded-full bg-cyber-success animate-pulse"></div>
            <span className="text-xs text-cyber-success tracking-wider uppercase">System Online</span>
          </div>
        </nav>

        {children}
      </body>
    </html>
  );
}
