'use client';

import React from 'react';

interface HeaderProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  caseCount: number;
}

export const Header: React.FC<HeaderProps> = ({ activeTab, setActiveTab, caseCount }) => {
  const navItems = [
    { id: 'queue', label: 'Dispute Queue', badge: caseCount },
    { id: 'workspace', label: 'Analysis & Rebuttal Workspace' },
    { id: 'custom', label: 'Custom Case Simulator' },
    { id: 'benchmark', label: 'Benchmark & ROI Hub' },
    { id: 'rubric', label: 'Evidence Rubric (6 Rules)' },
  ];

  return (
    <header className="bg-slate-900 border-b border-slate-800 sticky top-0 z-50 text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand Logo & Title */}
          <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setActiveTab('queue')}>
            <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center shadow-lg shadow-blue-500/30">
              <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-lg tracking-tight text-white">DisputeShield</span>
                <span className="text-[10px] uppercase font-semibold px-2 py-0.5 bg-blue-500/20 text-blue-400 rounded-full border border-blue-500/30">
                  Razorpay AI
                </span>
              </div>
              <p className="text-xs text-slate-400">Autonomous Chargeback Representation & Evidence Rubric Engine</p>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="flex space-x-1 sm:space-x-2">
            {navItems.map((item) => {
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`px-3 py-2 rounded-lg text-sm font-medium transition-all duration-150 flex items-center space-x-1.5 ${
                    isActive
                      ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30'
                      : 'text-slate-300 hover:text-white hover:bg-slate-800/80'
                  }`}
                >
                  <span>{item.label}</span>
                  {item.badge !== undefined && (
                    <span className={`text-xs px-1.5 py-0.2 rounded-full font-mono ${isActive ? 'bg-blue-800 text-white' : 'bg-slate-800 text-slate-400'}`}>
                      {item.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>
        </div>
      </div>
    </header>
  );
};
