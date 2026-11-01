export interface SourceCounts {screenshot:number;pdf:number;url:number;total:number}
export function intakeError(counts:SourceCounts,urls:string[],text:string,files:{name:string}[],limits={url:10,pdf:10}) {
 const supplied=urls.filter(x=>x.trim());
 if(!supplied.length&&!text.trim()&&!files.length)return 'Add at least one URL, message or file.';
 const pdf=files.filter(f=>f.name.toLowerCase().endsWith('.pdf')).length;
 const images=files.length-pdf;
 if(counts.screenshot+images>5)return 'An opportunity supports at most 5 screenshots. Remove a selected or existing image.';
 if(counts.pdf+pdf>limits.pdf)return `An opportunity supports at most ${limits.pdf} PDFs.`;
 if(counts.url+supplied.length>limits.url)return `An opportunity supports at most ${limits.url} URLs.`;
 if(counts.total+supplied.length+(text.trim()?1:0)+files.length>25)return 'An opportunity supports at most 25 active sources.';
 return '';
}
export function sourceStatus(source:{processing_status:string;extraction_status:string}) {
 if(source.processing_status==='READY')return source.extraction_status==='UNAVAILABLE'?'Partially processed — page unavailable':'Processed';
 return ({NEEDS_REVIEW:'Extracted — review required',FAILED:'Unavailable — processing failed',PROCESSING:'Processing',REMOVED:'Removed'} as Record<string,string>)[source.processing_status]||'Pending';
}
