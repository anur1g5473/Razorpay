'use client';
import React, { useState } from 'react';
import { DisputeCase } from '../types/dispute';

interface Props {
  cases: DisputeCase[];
  selectedCaseId: string | null;
  onSelectCase: (id: string) => void;
  loading: boolean;
}

export const DisputeQueue: React.FC<Props> = ({ cases, selectedCaseId, onSelectCase, loading }) => {
  const [cat, setCat] = useState('all');
  const [outcome, setOutcome] = useState('all');
  const [search, setSearch] = useState('');

  const filtered = cases.filter((c) => {
    if (cat !== 'all' && c.dispute_category !== cat) return false;
    if (outcome !== 'all' && c.ground_truth !== outcome) return false;
    if (search) {
      const q = search.toLowerCase();
      if (!c.case_id.toLowerCase().includes(q) && !c.merchant_name.toLowerCase().includes(q) && !c.reason_code.toLowerCase().includes(q)) return false;
    }
    return true;
  });

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-lg font-bold text-white">Dispute Ingestion Queue</h2>
            <span className="bg-blue-600/20 text-blue-400 text-xs px-2 py-0.5 rounded-full border border-blue-500/30 font-mono">
              {filtered.length} / {cases.length} cases
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">Synthetic dataset modeled after Razorpay dispute webhooks across 6 card networks & UPI</p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <input
            type="text"
            placeholder="Search Case ID, Merchant..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white placeholder-slate-400 focus:outline-none focus:border-blue-500"
          />
          <select
            value={cat}
            onChange={(e) => setCat(e.target.value)}
            className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none"
          >
            <option value="all">All Categories</option>
            <option value="fraudulent_unauthorized">Fraud</option>
            <option value="product_service_not_received">PNR</option>
            <option value="product_unacceptable_defective">Defective</option>
            <option value="credit_refund_not_processed">Refund</option>
            <option value="duplicate_incorrect_amount">Duplicate</option>
            <option value="subscription_recurring_cancellation">Subscription</option>
          </select>
          <select
            value={outcome}
            onChange={(e) => setOutcome(e.target.value)}
            className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none"
          >
            <option value="all">All Truths</option>
            <option value="win">Win</option>
            <option value="lose">Lose</option>
            <option value="ambiguous">Ambiguous</option>
          </select>
        </div>
      </div>
      <div className="mt-4 overflow-x-auto max-h-[560px] overflow-y-auto">
        {loading ? (
          <div className="text-center py-12 text-slate-400">Loading synthetic disputes...</div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-12 text-slate-400">No matching disputes found.</div>
        ) : (
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/60 text-slate-400 font-semibold uppercase sticky top-0">
              <tr>
                <th className="py-2.5 px-3">Case ID</th>
                <th className="py-2.5 px-3">Merchant</th>
                <th className="py-2.5 px-3">Amount</th>
                <th className="py-2.5 px-3">Reason</th>
                <th className="py-2.5 px-3">Category</th>
                <th className="py-2.5 px-3">Truth</th>
                <th className="py-2.5 px-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {filtered.map((c) => (
                <tr
                  key={c.case_id}
                  onClick={() => onSelectCase(c.case_id)}
                  className={`cursor-pointer transition-colors ${
                    selectedCaseId === c.case_id ? 'bg-blue-600/15 border-l-2 border-blue-500' : 'hover:bg-slate-800/40 text-slate-300'
                  }`}
                >
                  <td className="py-3 px-3 font-mono font-medium text-blue-400">{c.case_id}</td>
                  <td className="py-3 px-3 font-medium text-white">{c.merchant_name}</td>
                  <td className="py-3 px-3 font-semibold text-slate-200">Rs {c.dispute_amount?.toLocaleString('en-IN') || 0}</td>
                  <td className="py-3 px-3 font-mono text-slate-300">{c.reason_code}</td>
                  <td className="py-3 px-3 text-slate-400">{c.dispute_category.replace(/_/g, ' ')}</td>
                  <td className="py-3 px-3">
                    <span className={`px-2 py-0.5 text-[11px] font-semibold rounded ${
                      c.ground_truth === 'win' ? 'bg-emerald-500/20 text-emerald-400' :
                      c.ground_truth === 'lose' ? 'bg-rose-500/20 text-rose-400' : 'bg-amber-500/20 text-amber-400'
                    }`}>
                      {c.ground_truth.toUpperCase()}
                    </span>
                  </td>
                  <td className="py-3 px-3 text-right">
                    <button
                      onClick={(e) => { e.stopPropagation(); onSelectCase(c.case_id); }}
                      className="px-2.5 py-1 bg-blue-600 hover:bg-blue-500 text-white rounded text-xs font-semibold"
                    >
                      Analyze
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};
