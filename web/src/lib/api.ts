import { DisputeCase, PipelineAnalysis, EvalSummary, DisputeCategoryRubric } from '../types/dispute';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000';

export async function fetchCases(params?: { category?: string; outcome?: string; search?: string }): Promise<{ cases: DisputeCase[]; total_count: number; categories: string[]; outcomes: string[] }> {
  try {
    const url = new URL(`${API_BASE}/api/cases`);
    if (params?.category && params.category !== 'all') url.searchParams.append('category', params.category);
    if (params?.outcome && params.outcome !== 'all') url.searchParams.append('expected_outcome', params.outcome);
    if (params?.search) url.searchParams.append('search', params.search);

    const res = await fetch(url.toString(), { cache: 'no-store' });
    if (!res.ok) throw new Error(`Failed to fetch cases: ${res.statusText}`);
    return await res.json();
  } catch (err) {
    console.warn('Backend API not reachable for /api/cases, using fallback generator or empty set.', err);
    throw err;
  }
}

export async function fetchCaseById(caseId: string): Promise<DisputeCase> {
  const res = await fetch(`${API_BASE}/api/cases/${caseId}`, { cache: 'no-store' });
  if (!res.ok) throw new Error(`Case ${caseId} not found`);
  return await res.json();
}

export async function analyzeCase(caseId: string, useLlm: boolean = false): Promise<PipelineAnalysis> {
  const res = await fetch(`${API_BASE}/api/analyze/${caseId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ use_llm: useLlm }),
  });
  if (!res.ok) throw new Error(`Analysis failed: ${res.statusText}`);
  return await res.json();
}

export async function analyzeCustomDispute(payload: any): Promise<PipelineAnalysis> {
  const res = await fetch(`${API_BASE}/api/analyze/custom/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`Custom analysis failed: ${res.statusText}`);
  return await res.json();
}

export async function fetchEvalSummary(): Promise<EvalSummary> {
  const res = await fetch(`${API_BASE}/api/eval/summary`, { cache: 'no-store' });
  if (!res.ok) throw new Error(`Failed to fetch evaluation summary: ${res.statusText}`);
  return await res.json();
}

export async function fetchRubric(): Promise<{ categories: Record<string, DisputeCategoryRubric> }> {
  const res = await fetch(`${API_BASE}/api/rubric`, { cache: 'no-store' });
  if (!res.ok) throw new Error(`Failed to fetch rubric: ${res.statusText}`);
  return await res.json();
}

export const fetchRubrics = fetchRubric;
