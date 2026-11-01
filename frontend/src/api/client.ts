// API Client connecting to FastAPI backend with graceful fallback
export const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000/api";
export const authenticatedFetch = (url: string, options: RequestInit = {}) => {
  const token = sessionStorage.getItem('access_token');
  return fetch(url, { ...options, headers: { ...options.headers,
    ...(token ? { Authorization: `Bearer ${token}` } : {}) } });
};

export interface EvidenceItem {
  id?: string;
  category: string;
  severity: "critical" | "high" | "moderate" | "low" | "verified";
  evidence: string;
  source: string;
  confidence: number;
  explanation?: string;
  timestamp?: string;
  observed_value?: string;
  origin?: string;
  verification_status?: string;
  correlation_group?: string;
  related_entities?: string[];
  source_spans?: { start:number; end:number; text:string; kind:string }[];
}

export interface RiskIndicatorItem {
  name: string;
  description?: string;
  weight: number;
  is_positive: boolean;
}

export interface VerificationCheckItem {
  check_name: string;
  status: "passed" | "verified" | "warning" | "failed" | "unavailable" | "not_performed";
  details?: string;
}

export interface TimelineEvent {
  timestamp_str: string;
  step: string;
  status: "passed" | "warning" | "critical" | "info";
  details: string;
}

export interface ScanDetail {
  id: string;
  input_type: string;
  input_content: string;
  target_identifier?: string;
  status: string;
  trust_score: number;
  risk_level: string;
  analysis_confidence: number;
  summary?: string;
  created_at: string;
  is_demo?: boolean;
  evidence: EvidenceItem[];
  indicators: RiskIndicatorItem[];
  verification_results: VerificationCheckItem[];
  recommended_actions: string[];
  timeline: TimelineEvent[];
  threat_intel_details?: any;
  investigation?: Investigation;
}

export async function fetchDashboardData() {
  const res = await authenticatedFetch(`${API_BASE}/dashboard`);
  if (!res.ok) throw new Error('Dashboard unavailable');
  return await res.json();
}

export async function submitAnalyze(type: string, content: string, targetIdentifier?: string): Promise<ScanDetail> {
  const endpoint = `${API_BASE}/analyze/${type}`;
  const res = await authenticatedFetch(endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      input_type: type,
      content: content,
      target_identifier: targetIdentifier
    })
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Analysis failed" }));
    throw new Error(analysisErrorMessage(err.detail));
  }
  return await res.json();
}

export async function submitFileUpload(type: "screenshot" | "pdf", file: File, targetIdentifier?: string): Promise<ScanDetail> {
  const endpoint = `${API_BASE}/analyze/${type}`;
  const formData = new FormData();
  formData.append("file", file);
  if (targetIdentifier) {
    formData.append("target_identifier", targetIdentifier);
  }
  const res = await authenticatedFetch(endpoint, {
    method: "POST",
    body: formData
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "File upload analysis failed" }));
    throw new Error(analysisErrorMessage(err.detail));
  }
  return await res.json();
}

export async function getScanById(scanId: string): Promise<ScanDetail> {
  const res = await authenticatedFetch(`${API_BASE}/scans/${scanId}`);
  if (res.ok) {
    return await res.json();
  }
  // Try demo case fallback
  const demoRes = await authenticatedFetch(`${API_BASE}/demo/run/${scanId}`, { method: "POST" });
  if (demoRes.ok) {
    return await demoRes.json();
  }
  throw new Error("Scan record could not be loaded");
}

export async function askAIInvestigator(scanId: string, question: string) {
  const res = await authenticatedFetch(`${API_BASE}/ai/investigate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ scan_id: scanId, question })
  });
  if (res.ok) return await res.json();
  return {
    answer: "Unable to query the investigator assistant right now. Please verify the recorded evidence list.",
    grounded_in_evidence: true,
    evidence_referenced: [],
    confidence_note: "Local offline fallback"
  };
}

export async function fetchEmergencyGuidance(incidentType: string) {
  const res = await authenticatedFetch(`${API_BASE}/emergency/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ incident_type: incidentType })
  });
  if (res.ok) return await res.json();
  throw new Error("Could not retrieve emergency guidance");
}

export async function fetchCommunityReports() {
  const res = await authenticatedFetch(`${API_BASE}/community/reports`);
  if (res.ok) return await res.json();
  return [];
}

export async function submitCommunityReport(report: any) {
  const res = await authenticatedFetch(`${API_BASE}/community/reports`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(report)
  });
  if (res.ok) return await res.json();
  throw new Error("Could not submit community report");
}

export async function runDemoCase(caseId: string): Promise<ScanDetail> {
  const res = await authenticatedFetch(`${API_BASE}/demo/run/${caseId}`, { method: "POST" });
  if (res.ok) return await res.json();
  throw new Error("Failed to execute demo case");
}

export interface Fusion {
  assessment_mode: 'HEURISTIC' | 'BAYESIAN'; risk_level: string; risk_score: number | null;
  confidence: number; evidence_coverage: number; prior: number; unknowns: string[]; explanation: string[];
  evidence_updates: { evidence_id: string; correlation_group: string; included: boolean;
    heuristic_multiplier?: number; likelihood_ratio?: number; before: number; after: number; reason: string }[];
}
export interface ResearchSource {
  id: string; title: string; url: string; extracted_information: string; retrieved_at: string;
  source_type: string; relevance: number; claim: string; verification_status: string;
}
export interface Investigation {
  monetary_entities?: MonetaryEntity[];
  document_extraction?: {filename?:string; content_origin?:string; ocr_status?:string; user_corrected?:boolean};
  version: number; revision: number; status: string; claimed_organization?: string;
  entities: {id: string; type: string; value: string; provenance: string}[];
  evidence: EvidenceItem[]; fusion: Fusion; research_calls: number;
  research: {status: string; reason: string; query: string; sources: ResearchSource[]}[];
  language: {provider: string; mode: string; reason: string; interpretations: {text: string; evidence_ids: string[]}[]};
  recommendations: {action_id: string; title: string; reason: string; priority: string; ranking_score: number;
    execution_type: string; status: string; instructions: string; required_information: string[]; unavailable_reason?:string }[];
  graph: {nodes: {id: string; type: string; label: string; provenance: string; inconsistent?: boolean;
    evidence?: EvidenceItem; source?: ResearchSource; citations?:GraphCitation[]}[];
    edges: {id: string; source: string; target: string; relation: string; relationship_status?:string; verification_status?:string; evidence_ids?:string[];citations?:GraphCitation[]}[]; disclaimer: string; verification_scope?:string};
  history: {action_id: string; timestamp: string; status: string; details?: string}[];
  last_change?: {status?:string; reason: string; before: Fusion; after: Fusion; risk_score_changed: boolean};
}
export async function executeInvestigationAction(scanId: string, actionId: string, revision: number): Promise<Investigation> {
  const res = await authenticatedFetch(`${API_BASE}/investigations/${scanId}/actions/${actionId}`, {
    method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({expected_revision: revision}),
  });
  if (!res.ok) { const error = await res.json(); throw new Error(error.detail || 'Investigation failed'); }
  return await res.json();
}
export async function authenticate(mode: 'login' | 'register', email: string, password: string, full_name?: string) {
  const res = await fetch(`${API_BASE}/auth/${mode}`, {method: 'POST', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({email, password, full_name})});
  const data = await res.json();
  if (!res.ok) throw new Error(typeof data.detail === 'string' ? data.detail : 'Authentication failed');
  sessionStorage.setItem('access_token', data.access_token);
  return data.user;
}
export async function downloadReport(scanId: string) {
  const res = await authenticatedFetch(`${API_BASE}/reports/${scanId}/pdf`);
  if (!res.ok) throw new Error('Report download failed');
  const url = URL.createObjectURL(await res.blob());
  const a = document.createElement('a'); a.href = url; a.download = `investigation-${scanId}.pdf`; a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

export async function fetchJson(path: string) {
  const response = await authenticatedFetch(`${API_BASE}${path}`);
  const data = await response.json();
  if (!response.ok) throw new Error(typeof data.detail === 'string' ? data.detail : 'Request unavailable');
  return data;
}

export interface MonetaryEntity {
  raw:string; value:string; currency:string; role:string; category:string; period:string|null;
  start:number; end:number; context:string; ambiguity_reason?:string|null;
}
export interface ScreenshotExtraction {
  status:'SUCCESS'|'EMPTY'|'UNAVAILABLE'|'ERROR'; extracted_text:string; ocr_engine:string;
  character_count:number; error_code?:string; reason:string; review_token:string; filename:string;
}
export interface ReviewedScreenshot {content:string; review_token:string}
export function analysisErrorMessage(detail:unknown):string {
  if (typeof detail==='string') return detail;
  if (detail && typeof detail==='object' && 'message' in detail) {
    const d=detail as {stage?:string;code?:string;message:string};
    return `${d.stage||'analysis'}${d.code?` (${d.code})`:''}: ${d.message}`;
  }
  return 'Request validation or analysis failed. Review the submitted input.';
}
export async function extractScreenshot(file:File):Promise<ScreenshotExtraction> {
  const form=new FormData(); form.append('file',file);
  const response=await authenticatedFetch(`${API_BASE}/analyze/screenshot/extract`,{method:'POST',body:form});
  const data=await response.json();
  if (!response.ok) throw new Error(analysisErrorMessage(data.detail));
  return data;
}
export async function submitReviewedScreenshot(review:ReviewedScreenshot):Promise<ScanDetail> {
  const response=await authenticatedFetch(`${API_BASE}/analyze/screenshot/reviewed`,{method:'POST',
    headers:{'Content-Type':'application/json'},body:JSON.stringify(review)});
  const data=await response.json();
  if (!response.ok) throw new Error(analysisErrorMessage(data.detail));
  return data;
}

export interface GraphCitation {source_id:string;source_title:string;excerpt:string;field?:string;start?:number;end?:number;page?:number}
