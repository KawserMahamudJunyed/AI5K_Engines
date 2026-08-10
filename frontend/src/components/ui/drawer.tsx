"use client";

import React from 'react';
import { X } from 'lucide-react';

interface DrawerProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
}

export function Drawer({ isOpen, onClose, title, children }: DrawerProps) {
  return (
    <>
      {/* Backdrop */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 transition-opacity"
          onClick={onClose}
        ></div>
      )}
      
      {/* Drawer Panel */}
      <div 
        className={`fixed top-0 right-0 h-full w-[400px] glass-panel z-50 transform transition-transform duration-300 ease-in-out border-r-0 rounded-r-none ${
          isOpen ? 'translate-x-0' : 'translate-x-full'
        }`}
      >
        <div className="flex justify-between items-center p-6 border-b border-white/10">
          <h2 className="text-lg font-bold text-white font-mono">{title}</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-white transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>
        <div className="p-6 overflow-y-auto h-[calc(100vh-80px)]">
          {children}
        </div>
      </div>
    </>
  );
}
