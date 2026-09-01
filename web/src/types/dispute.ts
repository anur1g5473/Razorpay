export type GroundTruth = 'win' | 'lose' | 'ambiguous';
export type Recommendation = 'CONTEST' | 'ABSTAIN' | 'ACCEPT' | 'REVIEW';

export interface EvidenceItemRequirement {
  item_id: string;
  name: string;
  weight: number;
  compelling_level: 'critical' | 'important' | 'supporting';
  required_fields: string[];
  strong_evidence_indicators: string[];
  weak_evidence_indicators: string[];
}

export interface DisputeCategoryRubric {
  category_id: string;
  title: string;
  description: string;
  reason_codes: string[];
  required_evidence: EvidenceItemRequirement[];
  abstention_triggers: string[];
  win_probability_thresholds: {
    high: number;
    medium: number;
  };
}

export interface DisputeCase {
  case_id: string;
  merchant_id: string;
  merchant_name: string;
  merchant_category: string;
  payment_id: string;
  dispute_amount: number;
  currency: string;
  payment_method: string;
  card_network: string;
  dispute_category: string;
  reason_code: string;
  reason_description: string;
  filed_date: string;
  due_date: string;
  ground_truth: GroundTruth;
  ground_truth_reasoning: string;
  auth_3ds?: any;
  delivery_tracking?: any;
  invoice_dispatch?: any;
  customer_communication?: any[];
  customer_account?: any;
  terms_acceptance?: any;
  service_usage?: any;
  product_specs?: any;
  qa_inspection?: any;
  refund_logs?: any;
  duplicate_transactions?: any[];
  price_breakdown?: any;
  subscription_mandate?: any;
  notes?: string;
  [key: string]: any;
}

export interface EvidenceItemScore {
  item_id: string;
  name: string;
  weight: number;
  score_awarded: number;
  max_score: number;
  present: boolean;
  compelling_level: 'critical' | 'important' | 'supporting';
  strengths: string[];
  weaknesses: string[];
  extracted_fields: Record<string, any>;
}

export interface ScoringResult {
  category_id: string;
  category_title: string;
  total_score: number;
  max_possible_score: number;
  confidence: 'HIGH' | 'MEDIUM' | 'LOW' | number;
  win_probability_estimate: number;
  recommendation: Recommendation;
  is_hard_abstention: boolean;
  abstention_reasons: string[];
  item_scores: EvidenceItemScore[];
  missing_critical_items: string[];
  missing_important_items?: string[];
  actionable_recommendations: string[];
  notes: string[];
}


export interface PipelineAnalysis {
  case_id: string;
  dispute_category: string;
  category_title: string;
  reason_code: string;
  decision: Recommendation;
  confidence: number;
  total_score: number;
  win_probability_estimate: number;
  retrieved_slices: Record<string, any>;
  scoring_result: ScoringResult;
  rebuttal_letter?: string | null;
  actionable_recommendations: string[];
  missing_critical_items: string[];
  ground_truth_label?: string;
  predicted_outcome?: string;
  is_correct_prediction?: boolean;
  elapsed_ms: number;
  llm_generated?: boolean;
}

export interface EvalSummary {
  timestamp: string;
  total_cases: number;
  overall_accuracy: number;
  macro_f1: number;
  precision_contest: number;
  recall_contest: number;
  dispute_prevention_savings_inr: number;
  net_financial_gain_inr: number;
  recovered_amount_inr: number;
  category_breakdown: Record<string, any>;
  confusion_matrix: {
    contest_actual_win: number;
    contest_actual_lose: number;
    contest_actual_ambiguous: number;
    accept_actual_win: number;
    accept_actual_lose: number;
    accept_actual_ambiguous: number;
    review_actual_win: number;
    review_actual_lose: number;
    review_actual_ambiguous: number;
  };
  latency: {
    mean_ms: number;
    median_ms: number;
    p95_ms: number;
    min_ms: number;
    max_ms: number;
  };
}
