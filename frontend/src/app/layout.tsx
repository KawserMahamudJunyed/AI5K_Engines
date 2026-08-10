import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI5K Trinity Dashboard",
  description: "Organization-first, evidence-based AI capability platform",
};

import Link from 'next/link';
import Image from 'next/image';

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="font-sans min-h-screen overflow-x-hidden selection:bg-[--color-brand-cyan] selection:text-black text-gray-200">
        
        {/* Global Top Navigation */}
        <nav className="sticky top-0 z-50 border-b border-white/10 px-6 py-4 flex justify-between items-center bg-[#0a0e1a]/80 backdrop-blur-md">
          <Link href="/" className="flex items-center group">
            <Image src="/logo.png" alt="AI5K Logo" width={64} height={64} className="group-hover:scale-105 transition-transform" />
          </Link>
          <div className="flex gap-6">
            <Link href="/profile" className="text-sm font-medium text-gray-300 hover:text-white transition-colors">Profile Intelligence</Link>
            <Link href="/opportunity" className="text-sm font-medium text-gray-300 hover:text-white transition-colors">Opportunity Intelligence</Link>
            <Link href="/teaming" className="text-sm font-medium text-gray-300 hover:text-white transition-colors">Organization Teaming</Link>
            <Link href="/proposal" className="text-sm font-medium text-gray-300 hover:text-white transition-colors">Proposal Workbench</Link>
          </div>
          <div className="flex items-center gap-3">
            <div className="w-2 h-2 rounded-full bg-brand-success animate-pulse shadow-[0_0_8px_rgba(33,254,169,0.8)]"></div>
            <span className="text-xs text-brand-success tracking-wider uppercase font-mono">System Online</span>
          </div>
        </nav>

        {children}
      </body>
    </html>
  );
}
