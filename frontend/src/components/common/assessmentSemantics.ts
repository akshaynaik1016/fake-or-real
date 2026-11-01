// Historical low/unknown states abstain; completion never means authenticity.
export function assessmentLabel(level:string|undefined):'Elevated concern'|'Undetermined' {
  return /ELEVATED|HIGH|CRITICAL/i.test(level||'')?'Elevated concern':'Undetermined';
}
export function riskIndex(trust:number|null|undefined,level:string):string {
  return assessmentLabel(level)==='Elevated concern' && typeof trust==='number'?`${100-trust}/100`:'Undetermined';
}
export function researchLabel(status:string):string {
  return status==='COMPLETED'?'Context retrieved · offer verification unresolved':'Research unavailable or not performed · verification unresolved';
}

export function concernIndex(trust:number|null|undefined,level:string):string {const value=riskIndex(trust,level);return value==='Undetermined'?'Not scored':value;}
