import Image from 'next/image';
import Link from 'next/link';

export default function MasterLandingPage() {
  return (
    <main className="flex min-h-[calc(100vh-80px)] flex-col items-center justify-center p-6 relative z-10 overflow-hidden font-sans">
      
      {/* Background Glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-gradient-to-tr from-brand-cyan/10 to-brand-purple/10 blur-[120px] rounded-full -z-10 animate-[pulse_6s_ease-in-out_infinite]"></div>

      {/* Hero Section */}
      <div className="relative mb-16 flex flex-col items-center text-center mt-8">
        <Image src="/logo.png" alt="AI5K Logo" width={160} height={160} priority className="mb-6 drop-shadow-[0_0_30px_rgba(196,136,251,0.3)]" />
        <h1 className="text-5xl md:text-6xl font-bold tracking-tight text-white font-outfit mb-4">
          Welcome to <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-purple to-brand-cyan">AI5K</span>
        </h1>
        <p className="text-lg text-gray-300 max-w-2xl">
          The organization-first, evidence-based AI capability platform. 
          Select an intelligence engine below to begin.
        </p>
      </div>

      {/* Portal Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 w-full max-w-5xl mb-12">
        
        {/* Profile Engine */}
        <Link href="/profile" className="group p-8 rounded-2xl border border-white/10 bg-[#141419]/60 backdrop-blur-xl hover:bg-white/5 hover:border-brand-purple/50 transition-all duration-300 shadow-xl hover:shadow-[0_0_30px_rgba(196,136,251,0.2)]">
          <div className="w-12 h-12 rounded-lg bg-brand-purple/20 flex items-center justify-center text-brand-purple mb-6 group-hover:scale-110 transition-transform">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>
          </div>
          <h2 className="text-2xl font-bold text-white mb-3 font-outfit group-hover:text-brand-purple transition-colors">Profile Intelligence</h2>
          <p className="text-sm text-gray-400">Assess individual talent readiness, verify capabilities, and generate dimensional radar scores based on historical evidence.</p>
        </Link>

        {/* Opportunity Engine */}
        <Link href="/opportunity" className="group p-8 rounded-2xl border border-white/10 bg-[#141419]/60 backdrop-blur-xl hover:bg-white/5 hover:border-brand-cyan/50 transition-all duration-300 shadow-xl hover:shadow-[0_0_30px_rgba(80,223,251,0.2)]">
          <div className="w-12 h-12 rounded-lg bg-brand-cyan/20 flex items-center justify-center text-brand-cyan mb-6 group-hover:scale-110 transition-transform">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path></svg>
          </div>
          <h2 className="text-2xl font-bold text-white mb-3 font-outfit group-hover:text-brand-cyan transition-colors">Opportunity Intelligence</h2>
          <p className="text-sm text-gray-400">Parse complex job descriptions and automatically map them against proven talent pools to find the perfect capability intersection.</p>
        </Link>

        {/* Teaming Engine */}
        <Link href="/teaming" className="group p-8 rounded-2xl border border-white/10 bg-[#141419]/60 backdrop-blur-xl hover:bg-white/5 hover:border-brand-success/50 transition-all duration-300 shadow-xl hover:shadow-[0_0_30px_rgba(33,254,169,0.2)]">
          <div className="w-12 h-12 rounded-lg bg-brand-success/20 flex items-center justify-center text-brand-success mb-6 group-hover:scale-110 transition-transform">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path></svg>
          </div>
          <h2 className="text-2xl font-bold text-white mb-3 font-outfit group-hover:text-brand-success transition-colors">Organization Teaming</h2>
          <p className="text-sm text-gray-400">Assemble dynamic delivery pods across timezones, balancing budget constraints with verified historical delivery evidence.</p>
        </Link>

        {/* Proposal Workbench */}
        <Link href="/proposal" className="group p-8 rounded-2xl border border-white/10 bg-[#141419]/60 backdrop-blur-xl hover:bg-white/5 hover:border-brand-blue/50 transition-all duration-300 shadow-xl hover:shadow-[0_0_30px_rgba(91,152,247,0.2)]">
          <div className="w-12 h-12 rounded-lg bg-brand-blue/20 flex items-center justify-center text-brand-blue mb-6 group-hover:scale-110 transition-transform">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
          </div>
          <h2 className="text-2xl font-bold text-white mb-3 font-outfit group-hover:text-brand-blue transition-colors">Proposal Workbench</h2>
          <p className="text-sm text-gray-400">Generate high-converting, XML-tagged proposals injecting real verified claims and past case studies.</p>
        </Link>

      </div>
    </main>
  );
}
