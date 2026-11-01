import { API_BASE,authenticatedFetch,analysisErrorMessage,type EvidenceItem,type Fusion,type Investigation } from './client';
export interface Citation {source_id:string;source_title:string;source_type?:string;claim_id?:string;excerpt:string;field?:string;start?:number;end?:number;page?:number}
export interface CaseClaim {id:string;source_id:string;claim_type:string;value:unknown;excerpt:string;location:{field:string;start:number;end:number;page?:number};extraction_method:string;verification_status:string}
export interface CaseSource {id:string;title:string;input_type:string;filename?:string;submitted_content:string;extracted_text:string;processing_status:string;extraction_status:string;error_code?:string;error_message?:string;scan_id?:string;analysis:Investigation;metadata_json:Record<string,unknown>}
export interface CaseFinding {id:string;kind:string;classification:string;severity:string;description:string;citations:Citation[]}
export interface CaseDetail {case_id:string;title:string;revision:number;status:string;fusion:Fusion;sources:CaseSource[];claims:CaseClaim[];cross_source_findings:CaseFinding[];evidence:EvidenceItem[];missing_information:string[];duplicate_sources:Record<string,string>;distinct_content_count:number;recommendations:Investigation['recommendations'];graph:Investigation['graph'];research:Investigation['research'];research_calls:number;last_action?:{action_id:string;status:string;message:string}}
export interface CaseRevision {revision:number;event:string;created_at:string;fusion:Fusion}
export interface CaseListItem {id:string;title:string;status:string;revision:number;fusion:Fusion;source_count:number;updated_at:string}
async function request<T>(path:string,options:RequestInit={}):Promise<T>{
  const response=await authenticatedFetch(`${API_BASE}/cases${path}`,options);const data=await response.json();
  if(!response.ok)throw new Error(analysisErrorMessage(data.detail));return data;
}
const body=(value:unknown,method='POST'):RequestInit=>({method,headers:{'Content-Type':'application/json'},body:JSON.stringify(value)});
export const listCases=()=>request<CaseListItem[]>('');
export const createCase=(title:string)=>request<CaseDetail>('',body({title}));
export const getCase=(id:string)=>request<CaseDetail>(`/${id}`);
export const renameCase=(id:string,title:string,revision:number)=>request<CaseDetail>(`/${id}`,body({title,expected_revision:revision},'PATCH'));
export const addCaseSource=(id:string,revision:number,input_type:string,content:string,title?:string)=>request<CaseDetail>(`/${id}/sources`,body({input_type,content,title:title||undefined,expected_revision:revision}));
export async function uploadCaseSource(id:string,revision:number,file:File,input_type:string,title?:string){
  const form=new FormData();form.append('file',file);form.append('input_type',input_type);form.append('expected_revision',String(revision));if(title)form.append('title',title);
  return request<CaseDetail>(`/${id}/sources/upload`,{method:'POST',body:form});
}
export const reviewCaseSource=(id:string,source:string,content:string,revision:number)=>request<CaseDetail>(`/${id}/sources/${source}/review`,body({content,expected_revision:revision}));
export const removeCaseSource=(id:string,source:string,revision:number)=>request<CaseDetail>(`/${id}/sources/${source}`,body({expected_revision:revision},'DELETE'));
export const getCaseRevisions=(id:string)=>request<CaseRevision[]>(`/${id}/revisions`);
export const getCaseRevision=(id:string,revision:number)=>request<CaseDetail>(`/${id}/revisions/${revision}`);
export const runCaseAction=(id:string,action:string,revision:number)=>request<CaseDetail>(`/${id}/actions/${encodeURIComponent(action)}`,body({expected_revision:revision}));
export function claimText(value:unknown):string {
  if(typeof value==='string')return value;
  if(value&&typeof value==='object')return Object.entries(value).filter(([,v])=>v!==null).map(([k,v])=>`${k}: ${v}`).join(' · ');
  return String(value);
}
