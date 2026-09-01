'use client';

import React, { useState, useEffect } from 'react';
import { fetchRubrics } from '../lib/api';

export const RubricViewer: React.FC = () => {
  const [rubrics, setRubrics] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(true);
  const [selectedCat, setSelectedCat] = useState<string>('fraudulent_unauthorized');

  useEffect(() => {
    async function load() {
      try {
        const res = await fetchRubrics();
        setRubrics(res.categories || {});
      } catch (e) {
        console.warn('Loading rubric fallback');
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const catKeys = Object.keys(rubrics);
  const active = rubrics[selectedCat] || (catKeys.length > 0 ? rubrics[catKeys[0]] : null);

  if (loading) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-8 text-center text-slate-400">
        <p className="animate-pulse">Loading Evidence Rubrics...</p>
      </div>
    );
  }

  if (!active) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-8 text-center text-slate-400">
        <p>No rubrics loaded.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-lg">
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <span>Evidence Evaluation Rubrics</span>
          <span className="text-xs bg-blue-500/20 text-blue-400 border border-blue-500/30 px-2.5 py-0.5 rounded-full font-mono">
            {catKeys.length} Categories
          </span>
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Deterministic scoring rules for Visa, Mastercard, RuPay, Amex, and UPI dispute representment.
        </p>

        <div className="flex flex-wrap gap-2 mt-4 pt-4 border-t border-slate-800">
          {catKeys.map((k) => (
            <button
              key={k}
              onClick={() => setSelectedCat(k)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                selectedCat === k
                  ? 'bg-blue-600 text-white shadow-md shadow-blue-500/20'
                  : 'bg-slate-800 text-slate-300 hover:bg-slate-700 hover:text-white'
              }`}
            >
              {rubrics[k].title?.split('/')[0]?.trim() || k}
            </button>
          ))}
        </div>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-lg space-y-6">
        <div>
          <div className="flex flex-wrap items-center justify-between gap-2">
            <h3 className="text-lg font-bold text-white">{active.title}</h3>
            <span className="text-xs font-mono text-blue-400 bg-blue-900/30 px-2 py-0.5 rounded border border-blue-800">
              Reason Codes: {active.reason_codes?.join(', ')}
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">{active.description}</p>
        </div>

        <div>
          <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-3">
            Required Evidence Items & Weights (Max 100)
          </h4>
          <div className="space-y-2.5">
            {active.required_evidence?.map((item: any, idx: number) => (
              <div key={idx} className="bg-slate-950/60 border border-slate-800 rounded-lg p-3 flex flex-col md:flex-row md:items-center justify-between gap-3">
                <div className="flex items-start md:items-center gap-3">
                  <span className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded border shrink-0 ${
                    item.compelling_level === 'critical'
                      ? 'bg-red-500/10 text-red-400 border-red-500/30'
                      : item.compelling_level === 'important'
                      ? 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                      : 'bg-blue-500/10 text-blue-400 border-blue-500/30'
                  }`}>
                    {item.compelling_level}
                  </span>
                  <div>
                    <p className="text-sm font-medium text-white">{item.name}</p>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {item.required_fields?.map((f: string) => (
                        <span key={f} className="text-[10px] bg-slate-800 text-slate-400 px-1.5 py-0.5 rounded font-mono">
                          {f}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
                <div className="text-right shrink-0">
                  <span className="text-sm font-bold text-blue-400 font-mono">{item.weight} pts</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {active.abstention_triggers?.length > 0 && (
          <div>
            <h4 className="text-xs font-semibold text-amber-400 uppercase tracking-wider mb-3 flex items-center gap-1.5">
              Abstention / Human Review Triggers
            </h4>
            <div className="bg-amber-950/20 border border-amber-800/40 rounded-lg p-4 space-y-2">
              {active.abstention_triggers.map((abs: string, idx: number) => (
                <div key={idx} className="flex items-start gap-2 text-xs text-amber-300/90">
                  <span className="text-amber-500 font-bold">•</span>
                  <span>{abs}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
