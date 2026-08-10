export interface PipelineInput {
  cv_text?: string;
  cv_pdf_bytes?: string;
  github_username?: string;
  upwork_url?: string;
  rate_desired?: number;
  niche?: string;
  version?: string;
}

export interface PipelineStatus {
  run_id: string;
  status: 'pending' | 'extracting' | 'benchmarking' | 'assigning' | 'scoring' | 'ranking' | 'generating' | 'completed' | 'failed';
  progress: number;
  message: string;
  error?: string;
  result?: PipelineResult;
}

export interface PipelineResult {
  claims: Claim[];
  readiness_score: ReadinessScore;
  gap_actions: GapAction[];
  generated_assets: GeneratedAssets;
  org_score?: number;
  match_score?: OpportunityMatchScore;
}

export interface Claim {
  id: string;
  text: string;
  tier: string; // T1 - T8
  source: string;
  date?: string;
  verified: boolean;
}

export interface ReadinessScore {
  overall_readiness_score: number;
  dimensions: {
    positioning_alignment: number;
    evidence_quality: number;
    keyword_coverage: number;
    portfolio_strength: number;
    profile_completeness: number;
  };
  overview_blocked_by_evidence_tier: boolean;
}

export interface GapAction {
  action_type: string;
  priority: string;
  description: string;
  effort_hours: number;
  score_gain: number;
}

export interface GeneratedAssets {
  proposal?: string;
  profile_summary?: string;
}

export interface OpportunityMatchScore {
  overall_match_score: number;
  factors: {
    skill_fit: number;
    evidence_quality: number;
    industry_fit: number;
    timezone_compatibility: number;
    budget_fit: number;
  };
  requirements_intersection: {
    matched: any[];
    missing: any[];
  };
}
