interface Item {id:string;type:string;label:string;provenance?:string}
interface Relation {id:string;source:string;target:string;relation:string;relationship_status?:string}
export function graphOverview<N extends Item,E extends Relation>(nodes:N[],edges:E[],expanded:string[]=[]){
 const program=nodes.some(n=>n.type==='program');
 const core=new Set(['offer','case','organization','program','domain','payment_policy','partnership','verification']);
 const details=program?nodes.filter(n=>!core.has(n.type)):[];
 const expandedDetails=expanded.includes('program_details')||expanded.includes('*');
 const display=details.length&&!expandedDetails?nodes.filter(n=>core.has(n.type)):nodes;
 const buckets=new Map<string,N[]>();display.forEach(n=>buckets.set(n.type,[...(buckets.get(n.type)||[]),n]));
 const visible:(N & {members?:string[]})[]=[],mapping=new Map<string,string>();
 for(const [type,items] of buckets){
  if(items.length<=3||expanded.includes(type)||expanded.includes('*')){items.forEach(n=>{visible.push(n);mapping.set(n.id,n.id);});continue;}
  const id=`overview:${type}`;items.forEach(n=>mapping.set(n.id,id));
  visible.push({id,type,label:`${items.length} ${type.replaceAll('_',' ')} records`,provenance:'Grouped view of recorded nodes; expand to inspect every original record.',members:items.map(n=>n.id)} as N&{members:string[]});
 }
 if(details.length&&!expandedDetails){
  const id='overview:program_details';details.forEach(n=>mapping.set(n.id,id));
  visible.push({id,type:'program_details',label:`Details & sources (${details.length})`,provenance:'Grouped source, claim and finding records; expand for every original record.',members:details.map(n=>n.id)} as N&{members:string[]});
 }
 const relations=new Map<string,E>();
 for(const edge of edges){
  const source=mapping.get(edge.source),target=mapping.get(edge.target);if(!source||!target||source===target)continue;
  const key=[source,target,edge.relation,edge.relationship_status||'UNRESOLVED'].join('|');
  if(!relations.has(key))relations.set(key,{...edge,id:edge.id,source,target});
 }
 return {nodes:visible,edges:[...relations.values()]};
}
