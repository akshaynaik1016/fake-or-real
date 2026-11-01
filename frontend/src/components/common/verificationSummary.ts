export function checkStatus(value:string):string {
  if(['passed','verified'].includes(value))return 'completed';
  return ['warning','failed','unavailable','not_performed','completed'].includes(value)?value:'unavailable';
}
export function summarizeVerification(checks:{status:string}[]) {
 const counts={verified:0,failed:0,warning:0,unavailable:0,not_performed:0,completed:0};
 for(const c of checks)counts[checkStatus(c.status) as keyof typeof counts]++;
 const unresolved=counts.warning+counts.unavailable+counts.not_performed+counts.completed;
 return {...counts,unresolved,text:`${counts.failed} failed · ${unresolved} unresolved · ${counts.verified} independently verified`};
}
