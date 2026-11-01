import { useEffect, useRef, useState } from 'react';
import { extractScreenshot, type ScreenshotExtraction, type ReviewedScreenshot } from '../../api/client';
export function ScreenshotReview({file,onChange}:{file:File;onChange:(value:ReviewedScreenshot|null)=>void}) {
  const [extraction,setExtraction]=useState<ScreenshotExtraction|null>(null);
  const [text,setText]=useState(''); const [busy,setBusy]=useState(false); const [error,setError]=useState('');
  const generation=useRef(0);
  useEffect(()=>{ generation.current++; setExtraction(null);setText('');setError('');setBusy(false);onChange(null); },[file,onChange]);
  const extract=async()=>{
    const current=++generation.current; setBusy(true);setError('');setExtraction(null);onChange(null);
    try { const result=await extractScreenshot(file); if (current!==generation.current) return;
      setExtraction(result);setText(result.extracted_text);onChange({content:result.extracted_text,review_token:result.review_token});
    } catch(e) { if(current===generation.current)setError(e instanceof Error?e.message:'OCR request failed'); }
    finally { if(current===generation.current)setBusy(false); }
  };
  return <section className="mt-4 rounded-xl border border-slate-600 bg-slate-950/50 p-4 space-y-3" aria-label="Screenshot text review">
    <h3 className="text-sm font-bold text-cyan-300">Review screenshot text before investigation</h3>
    <p className="text-xs text-slate-400">The filename is metadata only. Investigators use the text you review below.</p>
    <button type="button" onClick={extract} disabled={busy} className="rounded-lg px-4 py-2 bg-cyan-300 text-slate-950 text-xs font-bold disabled:opacity-50">{busy?'Extracting text…':'Extract text for review'}</button>
    {error&&<p role="alert" className="text-rose-300 text-xs">{error}</p>}
    {extraction&&<><p role="status" className={`text-xs ${extraction.status==='SUCCESS'?'text-emerald-300':'text-amber-200'}`}>OCR: {extraction.status} {extraction.error_code?`(${extraction.error_code})`:''} · {extraction.reason}</p>
      <label className="block text-xs text-slate-300" htmlFor="reviewed-screenshot-text">Extracted text — inspect and correct before investigating</label>
      <textarea id="reviewed-screenshot-text" aria-label="Extracted screenshot text" value={text} rows={9} maxLength={50000}
        className="w-full rounded-lg bg-slate-900 border border-slate-600 p-3 text-sm text-slate-100"
        onChange={e=>{setText(e.target.value);onChange({content:e.target.value,review_token:extraction.review_token});}}/>
      <p className="text-xs text-slate-400">{text.length} characters. {text.trim()?'Use the investigation button below when ready.':'Enter readable text to enable investigation. Original OCR status remains recorded.'}</p>
    </>}
  </section>;
}
