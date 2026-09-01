'use client';

import React, { useState } from 'react';
import { DisputeCase, PipelineAnalysis } from '../types/dispute';

interface Props {
  disputeCase: DisputeCase | null;
  analysis: PipelineAnalysis | null;
  analyzing: boolean;
  onRunAnalysis: (useLlm: boolean) => void;
}

export const DisputeWorkspace: React.FC<Props> = ({
  disputeCase,
  analysis,
  analyzing,
  onRunAnalysis,
}) => {
  const [useLlm, setUseLlm] = useState(false);
  const [letterDraft, setLetterDraft] = useState<string>('');
  const [copied, setCopied] = useState(false);
  const [activeSliceTab, setActiveSliceTab] = useState('raw');

  React.useEffect(() => {
    if (analysis?.rebuttal_letter) {
      setLetterDraft(analysis.rebuttal_letter);
    }
  }, [analysis]);

  if (!disputeCase) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-12 text-center text-slate-400">
        <p className="text-base font-medium text-slate-300">No dispute selected for analysis.</p>
        <p className="text-xs text-slate-500 mt-1">Select a dispute from the Dispute Queue or load a custom case.</p>
      </div>
    );
  }

  const handleCopy = () => {
    if (letterDraft) {
      navigator.clipboard.writeText(letterDraft);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const decisionBadge = (rec?: string) => {
    switch (rec) {
      case 'CONTEST':
        return <span className="px-3 py-1 bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 rounded-lg font-bold text-sm">CONTEST (High Win Probability)</span>;
      case 'ACCEPT':
        return <span className="px-3 py-1 bg-rose-500/20 text-rose-400 border border-rose-500/30 rounded-lg font-bold text-sm">ACCEPT (Save Dispute Fee)</span>;
      case 'REVIEW':
      case 'ABSTAIN':
      default:
        return <span className="px-3 py-1 bg-amber-500/20 text-amber-400 border border-amber-500/30 rounded-lg font-bold text-sm">HUMAN REVIEW REQUIRED</span>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Case Header & Quick Run */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-lg">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-3">
              <span className="font-mono text-blue-400 font-bold text-lg">{disputeCase.case_id}</span>
              <span className="px-2 py-0.5 bg-slate-800 text-slate-300 rounded text-xs border border-slate-700">
                {disputeCase.merchant_name}
              </span>
              <span className="px-2 py-0.5 bg-indigo-500/20 text-indigo-400 rounded text-xs border border-indigo-500/30">
                {disputeCase.card_network} | {disputeCase.payment_method}
              </span>
            </div>
            <p className="text-sm font-semibold text-white mt-1">
              Reason: {disputeCase.reason_code} — {disputeCase.reason_description}
            </p>
            <p className="text-xs text-slate-400 mt-0.5">
              Category: <span className="text-slate-300 font-medium">{disputeCase.dispute_category.replace(/_/g, ' ')}</span> | Due Date: <span className="text-slate-300 font-medium">{disputeCase.due_date}</span>
            </p>
          </div>

          <div className="flex items-center gap-3">
            <div className="text-right mr-2">
              <p className="text-xs text-slate-400">Disputed Amount</p>
              <p className="text-2xl font-bold text-white font-mono">
                Rs {disputeCase.dispute_amount?.toLocaleString('en-IN')}
              </p>
            </div>
            <button
              disabled={analyzing}
              onClick={() => onRunAnalysis(useLlm)}
              className="px-5 py-2.5 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-700 text-white rounded-lg text-sm font-semibold shadow-md shadow-blue-600/30 transition-all flex items-center gap-2"
            >
              {analyzing ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  Analyzing...
                </>
              ) : (
                <>
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  Run Dispute Pipeline
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Pipeline Scoring & Evidence Analysis */}
      {analysis && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Column: Decision & Evidence Scoring */}
          <div className="lg:col-span-7 space-y-6">
            {/* Scorer Summary Card */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-lg">
              <div className="flex items-center justify-between pb-4 border-b border-slate-800">
                <div>
                  <h3 className="text-base font-bold text-white">Automated Dispute Decision</h3>
                  <p className="text-xs text-slate-400 mt-0.5">Dual-layer evaluation (Deterministic Scorer + LLM Drafter)</p>
                </div>
                {decisionBadge(analysis.decision || analysis.scoring_result?.recommendation)}
              </div>

              <div className="grid grid-cols-3 gap-4 my-5">
                <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800/80 text-center">
                  <span className="text-xs text-slate-400 font-medium">Win Probability</span>
                  <p className="text-2xl font-bold text-emerald-400 mt-1 font-mono">
                    {Math.round((analysis.win_probability_estimate ?? analysis.scoring_result?.win_probability_estimate ?? 0) * 100)}%
                  </p>
                </div>
                <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800/80 text-center">
                  <span className="text-xs text-slate-400 font-medium">Evidence Score</span>
                  <p className="text-2xl font-bold text-blue-400 mt-1 font-mono">
                    {analysis.total_score ?? analysis.scoring_result?.total_score ?? 0} <span className="text-xs text-slate-500 font-normal">/ 100</span>
                  </p>
                </div>
                <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800/80 text-center">
                  <span className="text-xs text-slate-400 font-medium">Confidence Level</span>
                  <p className="text-2xl font-bold text-purple-400 mt-1 font-mono">
                    {typeof analysis.scoring_result?.confidence === 'string'
                      ? analysis.scoring_result.confidence
                      : `${Math.round((analysis.confidence ?? 0) * 100)}%`}
                  </p>
                </div>
              </div>

              {/* Rationale */}
              <div className="bg-slate-950/40 p-4 rounded-lg border border-slate-800 text-xs text-slate-300">
                <span className="font-semibold text-slate-200">Decision Summary: </span>
                {analysis.scoring_result?.notes?.length
                  ? analysis.scoring_result.notes.join('; ')
                  : analysis.actionable_recommendations?.join('; ') || 'Analysis evaluated against scheme evidence rubric.'}
              </div>

              {/* Hard Abstention Warnings */}
              {(analysis.scoring_result?.abstention_reasons || []).length > 0 && (
                <div className="mt-4 p-3 bg-amber-500/10 border border-amber-500/30 rounded-lg text-xs text-amber-300">
                  <span className="font-bold">⚠️ Abstention Flags Detected:</span>
                  <ul className="list-disc list-inside mt-1 space-y-0.5 text-amber-200/80">
                    {analysis.scoring_result.abstention_reasons.map((trigger: string, idx: number) => (
                      <li key={idx}>{trigger}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            {/* Evidence Checklist Breakdown */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-lg">
              <h3 className="text-base font-bold text-white mb-1">Evidence Item Evaluation</h3>
              <p className="text-xs text-slate-400 mb-4">Rubric requirements mapped against merchant evidence</p>

              <div className="space-y-3">
                {(analysis.scoring_result?.item_scores || []).map((item, idx: number) => (
                  <div
                    key={idx}
                    className={`p-3.5 rounded-lg border text-xs ${
                      item.present
                        ? 'bg-slate-950/40 border-slate-800 text-slate-300'
                        : 'bg-rose-950/10 border-rose-900/30 text-rose-300'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center gap-2">
                        <span className={`w-2 h-2 rounded-full ${item.present ? 'bg-emerald-400' : 'bg-rose-400'}`} />
                        <span className="font-semibold text-white">{item.name}</span>
                        <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400">
                          Weight: {item.weight}% ({item.compelling_level})
                        </span>
                      </div>
                      <span className="font-mono font-bold text-slate-200">
                        {item.score_awarded} / {item.max_score ?? item.weight} pts
                      </span>
                    </div>

                    {item.strengths && item.strengths.length > 0 && (
                      <p className="text-emerald-400/90 mt-1">✓ {item.strengths.join('; ')}</p>
                    )}
                    {item.weaknesses && item.weaknesses.length > 0 && (
                      <p className="text-rose-400/90 mt-1">✗ {item.weaknesses.join('; ')}</p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Right Column: Rebuttal Drafter */}
          <div className="lg:col-span-5 space-y-6">
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-lg flex flex-col h-full">
              <div className="flex items-center justify-between pb-4 border-b border-slate-800">
                <div>
                  <h3 className="text-base font-bold text-white">Rebuttal Letter</h3>
                  <p className="text-xs text-slate-400">Card scheme compliant representations document</p>
                </div>
                <button
                  onClick={handleCopy}
                  className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded text-xs font-semibold border border-slate-700 transition-colors flex items-center gap-1.5"
                >
                  {copied ? '✓ Copied' : '📋 Copy Letter'}
                </button>
              </div>

              <div className="mt-4 flex-1">
                <textarea
                  value={letterDraft}
                  onChange={(e) => setLetterDraft(e.target.value)}
                  rows={20}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-4 font-mono text-xs text-slate-200 focus:outline-none focus:border-blue-500 resize-none leading-relaxed"
                  placeholder="Rebuttal letter draft will be generated here..."
                />
              </div>

              <div className="mt-3 flex items-center justify-between text-xs text-slate-500">
                <span>Word count: {letterDraft ? letterDraft.trim().split(/\s+/).length : 0} words</span>
                <span>Format: Card Scheme Representation Letter</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

