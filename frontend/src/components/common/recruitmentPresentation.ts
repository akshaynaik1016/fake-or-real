export interface CitedClaim {id:string;source_id:string;claim_type:string;value:unknown;excerpt:string;location:{field:string;start:number;end:number;page?:number};extraction_method:string;verification_status:string}
export function groupClaims(claims:CitedClaim[]) {
 const groups=new Map<string,{claim:CitedClaim;references:CitedClaim[]}>();
 for(const claim of claims){const value=claim.value&&typeof claim.value==='object'?JSON.stringify(claim.value,Object.keys(claim.value).filter(k=>k!=='amount_role').sort()):String(claim.value);const key=claim.claim_type+':'+value;
  if(!groups.has(key))groups.set(key,{claim,references:[]});groups.get(key)!.references.push(claim);}
 return [...groups.values()];
}
export function claimValue(value:unknown):string {
 if(typeof value==='string')return /^[A-Z_]+$/.test(value)&&value.includes('_')?value.replaceAll('_',' ').toLowerCase():value;
 if(typeof value==='number')return String(value);
 if(!value||typeof value!=='object')return String(value??'Unresolved');
 const v=value as Record<string,unknown>;
 if(v.currency&&v.value)return `${v.currency} ${v.value}${v.period?'/'+v.period:''}${v.category?' · '+String(v.category).replaceAll('_',' ').toLowerCase():''}`;
 if(v.base&&v.total)return `${v.currency} ${v.base} + stated GST → ${v.currency} ${v.total}`;
 return Object.entries(v).filter(([,x])=>x!==null).map(([k,x])=>`${k.replaceAll('_',' ')}: ${x}`).join(' · ');
}
export function groupedResults<T extends {claim_type:string;value:unknown;status:string}>(results:T[]):T[]{
 const groups=new Map<string,T>();
 for(const r of results){const key=r.claim_type+':'+JSON.stringify(r.value)+':'+r.status,previous=groups.get(key);
  if(previous&&'citations' in previous&&'citations' in r&&Array.isArray(previous.citations)&&Array.isArray(r.citations)){
   groups.set(key,{...previous,citations:[...new Map([...previous.citations,...r.citations].map(c=>[JSON.stringify(c),c])).values()]});
  }else if(!previous)groups.set(key,r);
 }
 return [...groups.values()];
}
