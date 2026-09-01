'use client';

import React from 'react';
import { EvalSummary } from '../types/dispute';
import { FALLBACK_EVAL_SUMMARY } from '../lib/fallbackData';

interface Props {
  summary?: EvalSummary | null;
}

export const BenchmarkHub: React.FC<Props> = ({ summary: propSummary }) => {
  const summary = propSummary || FALLBACK_EVAL_SUMMARY;
  const cm = summary.confusion_matrix;

  return (
    <div className="space-y-6">
      {/* Benchmark Summary Header */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-lg">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <span>Benchmark & Financial ROI Hub</span>
              <span className="text-xs bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 px-2.5 py-0.5 rounded-full font-mono">
                100 / 100 Synthesized Cases
              </span>
            </h2>
            <p className="text-xs text-slate-400 mt-1 max-w-2xl">
              Systematic evaluation of DisputeShield across 6 card & UPI categories. Evaluates accuracy, macro F1, and financial gains.
            </p>
          </div>
          <div className="text-right">
            <span className="text-xs text-slate-400">Net Financial Gain</span>
            <p className="text-2xl font-bold text-indigo-400 font-mono">
              Rs {summary.net_financial_gain_inr?.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
            </p>
          </div>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <p className="text-xs text-slate-400 font-medium">Overall Accuracy</p>
          <p className="text-2xl font-bold text-emerald-400 mt-1 font-mono">
            {(summary.overall_accuracy * 100).toFixed(1)}%
          </p>
          <p className="text-[11px] text-slate-500 mt-0.5">90 / 100 exact match</p>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <p className="text-xs text-slate-400 font-medium">Macro F1 Score</p>
          <p className="text-2xl font-bold text-blue-400 mt-1 font-mono">
            {summary.macro_f1.toFixed(3)}
          </p>
          <p className="text-[11px] text-slate-500 mt-0.5">3-class balanced metric</p>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <p className="text-xs text-slate-400 font-medium">Contest Recall</p>
          <p className="text-2xl font-bold text-emerald-400 mt-1 font-mono">
            {(summary.recall_contest * 100).toFixed(1)}%
          </p>
          <p className="text-[11px] text-slate-500 mt-0.5">0 winnable disputes missed</p>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <p className="text-xs text-slate-400 font-medium">Dispute Fee Savings</p>
          <p className="text-2xl font-bold text-amber-400 mt-1 font-mono">
            Rs {summary.dispute_prevention_savings_inr?.toLocaleString('en-IN')}
          </p>
          <p className="text-[11px] text-slate-500 mt-0.5">Avoided fee on 40 losses</p>
        </div>
      </div>
    </div>
  );
};
