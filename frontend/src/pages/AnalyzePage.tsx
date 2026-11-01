import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Globe, 
  FileText, 
  Image as ImageIcon, 
  FileUp, 
  Mail, 
  Phone, 
  Building2, 
  ArrowRight, 
  Sparkles, 
  CheckCircle2, 
  AlertTriangle, 
  Loader2,
  Terminal,
  ShieldCheck,
  Zap,
  Lock,
  UploadCloud,
  FileCheck,
  Clipboard,
  X
} from 'lucide-react';
import {CaseIntake} from '../components/cases/CaseIntake';
import type {CaseDetail} from '../api/cases';
import { ScreenshotReview } from '../components/common/ScreenshotReview';
import { submitReviewedScreenshot, type ReviewedScreenshot, submitAnalyze, submitFileUpload, ScanDetail } from '../api/client';

export const AnalyzePage: React.FC = () => {
  const navigate = useNavigate();
  const [multi,setMulti]=useState(false),[multiBusy,setMultiBusy]=useState(false),[multiError,setMultiError]=useState('');
  const runMulti=async(operation:()=>Promise<CaseDetail>)=>{setMultiBusy(true);setMultiError('');try{const result=await operation();navigate(`/cases/${result.case_id}`);return result;}catch(e){setMultiError(e instanceof Error?e.message:'Evidence processing failed');}finally{setMultiBusy(false);}};
  const [searchParams] = useSearchParams();
  const initialTab = searchParams.get('tab') || 'url';

  const [activeTab, setActiveTab] = useState<'url' | 'text' | 'screenshot' | 'pdf' | 'email' | 'phone' | 'org'>(
    (initialTab as any) || 'url'
  );
  
  // Inputs state
  const [urlInput, setUrlInput] = useState('');
  const [textInput, setTextInput] = useState('');
  const [emailInput, setEmailInput] = useState('');
  const [phoneInput, setPhoneInput] = useState('');
  const [orgInput, setOrgInput] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [screenshotReview, setScreenshotReview] = useState<ReviewedScreenshot | null>(null);
  useEffect(() => { setScreenshotReview(null); }, [selectedFile]);
  const [isDragOver, setIsDragOver] = useState(false);

  // Analysis Progress State
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [progressStepIndex, setProgressStepIndex] = useState(0);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const analysisSteps = [
    { label: "Investigating submitted content; completed checks appear in results…", icon: FileText },
  ];

  // Pre-fill from query params on mount
  useEffect(() => {
    const q = searchParams.get('q');
    const preset = searchParams.get('preset');
    const tabParam = searchParams.get('tab');

    if (tabParam && ['url', 'text', 'screenshot', 'pdf', 'email', 'phone', 'org'].includes(tabParam)) {
      setActiveTab(tabParam as any);
    }

    if (preset) {
      loadPreset(preset);
    } else if (q) {
      if (q.startsWith('http://') || q.startsWith('https://')) {
        setActiveTab('url');
        setUrlInput(q);
      } else {
        setActiveTab('text');
        setTextInput(q);
      }
    }
  }, [searchParams]);

  // Pre-fill sample opportunities
  const loadPreset = (type: string) => {
    setErrorMsg(null);
    if (type === 'fake_internship') {
      setActiveTab('text');
      setTextInput(
        "Congratulations! You have been officially selected for the Microsoft AI Summer Internship 2026.\n" +
        "Role: Junior AI & ML Research Intern\n" +
        "Stipend: ₹45,000 / month (2 hours/day, No experience required)\n" +
        "Registration Fee: Pay ₹999 mandatory refundable laptop security deposit.\n" +
        "Official Portal: https://microsoft-careers-india.xyz/apply/onboarding\n" +
        "Payment UPI: microsoft.careers@okhdfcbank\n" +
        "Required Documents: Submit Aadhaar Card, PAN Card, and Bank Account details.\n" +
        "Immediate confirmation required. Offer expires today."
      );
    } else if (type === 'genuine_tcs') {
      setActiveTab('url');
      setUrlInput("https://nextstep.tcs.com/campus/#/register");
    } else if (type === 'phishing_link') {
      setActiveTab('url');
      setUrlInput("https://google.com.security-check.example.xyz/login.php");
    }
  };

  const handlePasteClipboard = async (setter: (val: string) => void) => {
    try {
      const text = await navigator.clipboard.readText();
      if (text) setter(text);
    } catch {
      // Clipboard permissions denied
    }
  };

  const handleCreateMockSampleFile = (type: 'pdf' | 'screenshot') => {
    if (type === 'pdf') {
      const sampleText = "OFFER LETTER - MICROSOFT INTERNSHIP PROGRAM 2026\nMandatory Security Deposit: ₹999 via UPI";
      const blob = new Blob([sampleText], { type: 'application/pdf' });
      const file = new File([blob], "Sample_Microsoft_Internship_Offer.pdf", { type: 'application/pdf' });
      setSelectedFile(file);
    } else {
      const canvas = document.createElement('canvas');
      canvas.width = 400;
      canvas.height = 200;
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.fillStyle = '#111c34';
        ctx.fillRect(0, 0, 400, 200);
        ctx.fillStyle = '#00f2fe';
        ctx.font = '16px monospace';
        ctx.fillText('Job Offer: Pay ₹999 fee', 20, 100);
      }
      canvas.toBlob((blob) => {
        if (blob) {
          const file = new File([blob], "whatsapp_recruiter_screenshot.png", { type: 'image/png' });
          setSelectedFile(file);
        }
      });
    }
  };

  const handleStartScan = async () => {
    setErrorMsg(null);
    setIsAnalyzing(true);
    setProgressStepIndex(0);

    // Progress simulation loop
    const interval = setInterval(() => {
      setProgressStepIndex((prev) => {
        if (prev < analysisSteps.length - 1) {
          return prev + 1;
        }
        return prev;
      });
    }, 380);

    try {
      let result: ScanDetail;
      if (activeTab === 'url') {
        if (!urlInput.trim()) throw new Error("Please enter a valid URL to analyze.");
        result = await submitAnalyze('url', urlInput.trim());
      } else if (activeTab === 'text') {
        if (!textInput.trim()) throw new Error("Please paste message or opportunity text.");
        result = await submitAnalyze('text', textInput.trim());
      } else if (activeTab === 'email') {
        if (!emailInput.trim()) throw new Error("Please enter email text or headers.");
        result = await submitAnalyze('email', emailInput.trim());
      } else if (activeTab === 'phone') {
        if (!phoneInput.trim()) throw new Error("Please enter a phone number.");
        result = await submitAnalyze('phone', phoneInput.trim());
      } else if (activeTab === 'org') {
        if (!orgInput.trim()) throw new Error("Please enter an organization name.");
        result = await submitAnalyze('organization', orgInput.trim());
      } else if (activeTab === 'screenshot') {
        if (!selectedFile || !screenshotReview?.content.trim()) throw new Error('Extract and review the screenshot text before investigating.');
        result = await submitReviewedScreenshot(screenshotReview);
      } else if (activeTab === 'pdf') {
        if (!selectedFile) throw new Error(`Please upload a ${activeTab === 'pdf' ? 'PDF' : 'screenshot'} file.`);
        result = await submitFileUpload(activeTab, selectedFile);
      } else {
        throw new Error("Invalid input tab");
      }

      clearInterval(interval);
      setProgressStepIndex(analysisSteps.length - 1);
      // Brief pause on final 100% state before navigation
      setTimeout(() => {
        navigate(`/scan/${result.id}`);
      }, 700);

    } catch (err: any) {
      clearInterval(interval);
      setIsAnalyzing(false);
      setErrorMsg(err.message || "Failed to complete scan. Please try again.");
    }
  };

  return (
    <div className="min-h-screen py-12 px-4 sm:px-6 lg:px-8 max-w-5xl mx-auto space-y-8">
      
      {/* Page Header */}
      <div className="text-center">
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-xs font-mono mb-3">
          <Terminal className="w-3.5 h-3.5" />
          <span>MULTI-MODAL FORENSIC INGESTION</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-black text-white tracking-tight">
          Unified Digital Trust Scanner
        </h1>
        <p className="text-sm text-slate-300 mt-2 max-w-xl mx-auto leading-relaxed">
          Submit any URL, screenshot, offer letter, or message. Our multi-layer forensic engine
          inspects submitted claims, available domain evidence and risk signals before you take action.
        </p>

        {/* Quick Demo Presets */}
        <div className="mt-5 flex flex-wrap items-center justify-center gap-2">
          <span className="text-xs text-slate-400 font-mono">Quick Benchmarks:</span>
          <button
            type="button"
            onClick={() => loadPreset('fake_internship')}
            className="text-xs px-3 py-1.5 rounded-lg bg-rose-950/60 border border-rose-500/50 text-rose-300 hover:bg-rose-900/60 transition-colors flex items-center space-x-1.5 cursor-pointer font-medium"
          >
            <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />
            <span>Fake Microsoft Internship (₹999 Fee)</span>
          </button>
          <button
            type="button"
            onClick={() => loadPreset('genuine_tcs')}
            className="text-xs px-3 py-1.5 rounded-lg bg-emerald-950/60 border border-emerald-500/50 text-emerald-300 hover:bg-emerald-900/60 transition-colors flex items-center space-x-1.5 cursor-pointer font-medium"
          >
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            <span>TCS careers reference (unverified offer)</span>
          </button>
          <button
            type="button"
            onClick={() => loadPreset('phishing_link')}
            className="text-xs px-3 py-1.5 rounded-lg bg-amber-950/60 border border-amber-500/50 text-amber-300 hover:bg-amber-900/60 transition-colors flex items-center space-x-1.5 cursor-pointer font-medium"
          >
            <Zap className="w-3.5 h-3.5 text-amber-400" />
            <span>Lookalike Phishing URL</span>
          </button>
        </div>
      </div>

      <section className="glass-card rounded-2xl p-5 space-y-3" aria-label="Multi-source investigation">
        <h2 className="font-bold text-lg">Investigate one opportunity with multiple sources</h2><p className="text-sm text-slate-400">Combine optional text, links, PDFs and up to five screenshots in the existing Cases workspace. Single-format scans remain below.</p>
        <button onClick={()=>setMulti(v=>!v)} disabled={multiBusy} className="bg-cyan-300 text-slate-950 rounded-lg px-4 py-2 text-sm font-bold">{multi?'Hide multi-source inputs':'Add multiple sources'}</button>
        {multiError&&<p role="alert" className="text-rose-300 text-sm">{multiError}</p>}
        {multi&&<CaseIntake busy={multiBusy} onSubmit={runMulti} onCancel={()=>setMulti(false)}/>}
      </section>
      {/* Main Scanner Container */}
      <div className="glass-card rounded-3xl p-6 sm:p-8 shadow-2xl relative overflow-hidden border border-cyber-border">
        
        {/* Navigation Tabs */}
        <div className="grid grid-cols-4 sm:grid-cols-7 gap-1.5 p-1.5 rounded-2xl bg-cyber-bg border border-cyber-border mb-6">
          {[
            { id: 'url', label: 'URL', icon: Globe },
            { id: 'text', label: 'Text', icon: FileText },
            { id: 'screenshot', label: 'Screenshot', icon: ImageIcon },
            { id: 'pdf', label: 'PDF Letter', icon: FileUp },
            { id: 'email', label: 'Email', icon: Mail },
            { id: 'phone', label: 'Phone', icon: Phone },
            { id: 'org', label: 'Org Verify', icon: Building2 },
          ].map((tab) => {
            const Icon = tab.icon;
            const isSel = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                type="button"
                onClick={() => {
                  setActiveTab(tab.id as any);
                  setErrorMsg(null);
                }}
                className={`flex flex-col sm:flex-row items-center justify-center space-y-1 sm:space-y-0 sm:space-x-1.5 py-2.5 px-2 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                  isSel 
                    ? 'bg-gradient-to-r from-cyan-500/20 to-blue-600/20 text-cyan-300 border border-cyber-cyan shadow-[0_0_15px_rgba(6,182,212,0.25)]'
                    : 'text-slate-400 hover:text-white hover:bg-cyber-surface/60'
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${isSel ? 'text-cyber-cyan' : 'text-slate-400'}`} />
                <span className="truncate">{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* Input Bodies */}
        <div className="space-y-4">
          
          {/* URL Tab */}
          {activeTab === 'url' && (
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="block text-xs font-mono uppercase text-slate-300 font-semibold">
                  Target Website / Opportunity URL
                </label>
                <button
                  type="button"
                  onClick={() => handlePasteClipboard(setUrlInput)}
                  className="text-[11px] text-cyber-cyan hover:underline flex items-center space-x-1 cursor-pointer font-mono"
                >
                  <Clipboard className="w-3 h-3" />
                  <span>Paste from clipboard</span>
                </button>
              </div>
              <div className="relative">
                <Globe className="w-5 h-5 text-cyber-cyan absolute left-3.5 top-3.5" />
                <input
                  type="url"
                  value={urlInput}
                  onChange={(e) => setUrlInput(e.target.value)}
                  placeholder="https://microsoft-careers-india.xyz or https://nextstep.tcs.com"
                  className="w-full bg-cyber-bg border border-cyber-border rounded-xl pl-11 pr-4 py-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-cyber-cyan focus:ring-1 focus:ring-cyber-cyan font-mono transition-all"
                />
              </div>
              <p className="text-[11px] text-slate-400 mt-2 font-mono flex items-center space-x-1.5">
                <ShieldCheck className="w-3.5 h-3.5 text-cyber-cyan" />
                <span>Hardened against SSRF, redirects, brand lookalikes, punycode, and newly created domains.</span>
              </p>
            </div>
          )}

          {/* Text Tab */}
          {activeTab === 'text' && (
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="block text-xs font-mono uppercase text-slate-300 font-semibold">
                  Paste Opportunity / Recruiter Message Content
                </label>
                <button
                  type="button"
                  onClick={() => handlePasteClipboard(setTextInput)}
                  className="text-[11px] text-cyber-cyan hover:underline flex items-center space-x-1 cursor-pointer font-mono"
                >
                  <Clipboard className="w-3 h-3" />
                  <span>Paste from clipboard</span>
                </button>
              </div>
              <textarea
                rows={6}
                value={textInput}
                onChange={(e) => setTextInput(e.target.value)}
                placeholder="Paste internship letter, WhatsApp message, Telegram task offer, or freelance proposal..."
                className="w-full bg-cyber-bg border border-cyber-border rounded-xl p-3.5 text-xs sm:text-sm text-white placeholder-slate-500 focus:outline-none focus:border-cyber-cyan focus:ring-1 focus:ring-cyber-cyan leading-relaxed transition-all font-sans"
              />
              <p className="text-[11px] text-slate-400 mt-2 font-mono flex items-center space-x-1.5">
                <ShieldCheck className="w-3.5 h-3.5 text-cyber-cyan" />
                <span>Audits language pressure, upfront fees, sensitive data requests (Aadhaar/PAN/OTP), and salary anomalies.</span>
              </p>
            </div>
          )}

          {/* Screenshot Upload Tab */}
          {activeTab === 'screenshot' && (
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="block text-xs font-mono uppercase text-slate-300 font-semibold">
                  Upload Opportunity Screenshot (PNG, JPG, WEBP)
                </label>
                <button
                  type="button"
                  onClick={() => handleCreateMockSampleFile('screenshot')}
                  className="text-[11px] text-cyber-cyan hover:underline flex items-center space-x-1 cursor-pointer font-mono"
                >
                  <Sparkles className="w-3 h-3" />
                  <span>Load Sample Screenshot</span>
                </button>
              </div>
              
              <div
                onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
                onDragLeave={() => setIsDragOver(false)}
                onDrop={(e) => {
                  e.preventDefault();
                  setIsDragOver(false);
                  if (e.dataTransfer.files?.[0]) setSelectedFile(e.dataTransfer.files[0]);
                }}
                className={`border-2 border-dashed rounded-2xl p-8 text-center transition-all ${
                  isDragOver 
                    ? 'border-cyber-cyan bg-cyan-950/20 shadow-[0_0_20px_rgba(6,182,212,0.2)]'
                    : 'border-cyber-border hover:border-cyber-cyan/50 bg-cyber-bg/60'
                }`}
              >
                {selectedFile ? (
                  <div className="flex items-center justify-center space-x-3 p-3 rounded-xl bg-cyber-surface border border-cyber-cyan/40 max-w-md mx-auto">
                    <FileCheck className="w-8 h-8 text-cyber-cyan flex-shrink-0" />
                    <div className="text-left flex-1 truncate">
                      <p className="text-sm font-bold text-white truncate">{selectedFile.name}</p>
                      <p className="text-[11px] text-slate-400 font-mono">{(selectedFile.size / 1024).toFixed(1)} KB • Ready for OCR</p>
                    </div>
                    <button
                      type="button"
                      onClick={() => setSelectedFile(null)}
                      className="p-1.5 rounded-lg hover:bg-rose-950/60 text-slate-400 hover:text-rose-400 transition-colors"
                      title="Remove file"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                ) : (
                  <div>
                    <ImageIcon className="w-10 h-10 text-cyber-cyan mx-auto mb-2" />
                    <p className="text-sm font-bold text-slate-200">
                      Drag & drop recruiter screenshot or click to browse
                    </p>
                    <p className="text-xs text-slate-400 mt-1">
                      Extract real OCR text, inspect it and correct any errors before investigation
                    </p>
                    <label className="mt-4 inline-block px-5 py-2 rounded-xl bg-cyber-card border border-cyber-cyan/40 text-cyber-cyan hover:bg-cyan-950/30 font-bold text-xs cursor-pointer transition-colors">
                      Browse Files
                      <input
                        type="file"
                        accept="image/png,image/jpeg,image/webp"
                        onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                        className="hidden"
                      />
                    </label>
                  </div>
                )}
              </div>
              {selectedFile && <ScreenshotReview file={selectedFile} onChange={setScreenshotReview} />}
            </div>
          )}

          {/* PDF Upload Tab */}
          {activeTab === 'pdf' && (
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="block text-xs font-mono uppercase text-slate-300 font-semibold">
                  Upload Offer Letter / Contract (PDF)
                </label>
                <button
                  type="button"
                  onClick={() => handleCreateMockSampleFile('pdf')}
                  className="text-[11px] text-cyber-cyan hover:underline flex items-center space-x-1 cursor-pointer font-mono"
                >
                  <Sparkles className="w-3 h-3" />
                  <span>Load Sample Offer Letter</span>
                </button>
              </div>

              <div
                onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
                onDragLeave={() => setIsDragOver(false)}
                onDrop={(e) => {
                  e.preventDefault();
                  setIsDragOver(false);
                  if (e.dataTransfer.files?.[0]) setSelectedFile(e.dataTransfer.files[0]);
                }}
                className={`border-2 border-dashed rounded-2xl p-8 text-center transition-all ${
                  isDragOver 
                    ? 'border-cyber-cyan bg-cyan-950/20 shadow-[0_0_20px_rgba(6,182,212,0.2)]'
                    : 'border-cyber-border hover:border-cyber-cyan/50 bg-cyber-bg/60'
                }`}
              >
                {selectedFile ? (
                  <div className="flex items-center justify-center space-x-3 p-3 rounded-xl bg-cyber-surface border border-cyber-cyan/40 max-w-md mx-auto">
                    <FileCheck className="w-8 h-8 text-cyber-cyan flex-shrink-0" />
                    <div className="text-left flex-1 truncate">
                      <p className="text-sm font-bold text-white truncate">{selectedFile.name}</p>
                      <p className="text-[11px] text-slate-400 font-mono">{(selectedFile.size / 1024).toFixed(1)} KB • PDF Parsable</p>
                    </div>
                    <button
                      type="button"
                      onClick={() => setSelectedFile(null)}
                      className="p-1.5 rounded-lg hover:bg-rose-950/60 text-slate-400 hover:text-rose-400 transition-colors"
                      title="Remove file"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                ) : (
                  <div>
                    <FileUp className="w-10 h-10 text-cyber-cyan mx-auto mb-2" />
                    <p className="text-sm font-bold text-slate-200">
                      Drag & drop PDF document or click to browse
                    </p>
                    <p className="text-xs text-slate-400 mt-1">
                      Inspects document creation metadata, toolkits, links, and text tampering signals
                    </p>
                    <label className="mt-4 inline-block px-5 py-2 rounded-xl bg-cyber-card border border-cyber-cyan/40 text-cyber-cyan hover:bg-cyan-950/30 font-bold text-xs cursor-pointer transition-colors">
                      Browse Files
                      <input
                        type="file"
                        accept="application/pdf"
                        onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                        className="hidden"
                      />
                    </label>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Email Tab */}
          {activeTab === 'email' && (
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="block text-xs font-mono uppercase text-slate-300 font-semibold">
                  Email Message or RFC 822 Headers
                </label>
                <button
                  type="button"
                  onClick={() => handlePasteClipboard(setEmailInput)}
                  className="text-[11px] text-cyber-cyan hover:underline flex items-center space-x-1 cursor-pointer font-mono"
                >
                  <Clipboard className="w-3 h-3" />
                  <span>Paste from clipboard</span>
                </button>
              </div>
              <textarea
                rows={5}
                value={emailInput}
                onChange={(e) => setEmailInput(e.target.value)}
                placeholder="From: Google Careers HR <recruiter99@gmail.com>&#10;Subject: Selected for Software Engineer Internship&#10;Reply-To: security.jobs@mail.xyz"
                className="w-full bg-cyber-bg border border-cyber-border rounded-xl p-3.5 text-xs sm:text-sm text-white placeholder-slate-500 focus:outline-none focus:border-cyber-cyan focus:ring-1 focus:ring-cyber-cyan font-mono leading-relaxed"
              />
              <p className="text-[11px] text-slate-400 mt-2 font-mono flex items-center space-x-1.5">
                <ShieldCheck className="w-3.5 h-3.5 text-cyber-cyan" />
                <span>Detects display name spoofing (e.g. Google HR via gmail.com) and SPF/DKIM flags.</span>
              </p>
            </div>
          )}

          {/* Phone Tab */}
          {activeTab === 'phone' && (
            <div>
              <label className="block text-xs font-mono uppercase text-slate-300 font-semibold mb-1.5">
                Recruiter / Opportunity Contact Phone Number
              </label>
              <div className="relative">
                <Phone className="w-5 h-5 text-cyber-cyan absolute left-3.5 top-3.5" />
                <input
                  type="text"
                  value={phoneInput}
                  onChange={(e) => setPhoneInput(e.target.value)}
                  placeholder="+91 98765 43210"
                  className="w-full bg-cyber-bg border border-cyber-border rounded-xl pl-11 pr-4 py-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-cyber-cyan focus:ring-1 focus:ring-cyber-cyan font-mono"
                />
              </div>
              <p className="text-[11px] text-slate-400 mt-2 font-mono flex items-center space-x-1.5">
                <ShieldCheck className="w-3.5 h-3.5 text-cyber-cyan" />
                <span>Checks VoIP virtual routing indicators and community abuse complaints.</span>
              </p>
            </div>
          )}

          {/* Organization Verify Tab */}
          {activeTab === 'org' && (
            <div>
              <label className="block text-xs font-mono uppercase text-slate-300 font-semibold mb-1.5">
                Company / Institution Name
              </label>
              <div className="relative">
                <Building2 className="w-5 h-5 text-cyber-cyan absolute left-3.5 top-3.5" />
                <input
                  type="text"
                  value={orgInput}
                  onChange={(e) => setOrgInput(e.target.value)}
                  placeholder="Microsoft, Tata Consultancy Services, Infosys, ISRO..."
                  className="w-full bg-cyber-bg border border-cyber-border rounded-xl pl-11 pr-4 py-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-cyber-cyan focus:ring-1 focus:ring-cyber-cyan"
                />
              </div>
              <p className="text-[11px] text-slate-400 mt-2 font-mono flex items-center space-x-1.5">
                <ShieldCheck className="w-3.5 h-3.5 text-cyber-cyan" />
                <span>Resolves official corporate domains, MCA/corporate identifiers, and authentic careers portals.</span>
              </p>
            </div>
          )}
        </div>

        {/* Error message */}
        {errorMsg && (
          <div className="mt-4 p-3.5 rounded-xl bg-rose-950/60 border border-rose-500/60 text-rose-300 text-xs flex items-center space-x-2">
            <AlertTriangle className="w-4 h-4 text-rose-400 flex-shrink-0" />
            <span className="font-medium">{errorMsg}</span>
          </div>
        )}

        {/* Submit Button */}
        <div className="mt-6 flex justify-end">
          <button
            type="button"
            onClick={handleStartScan}
            disabled={isAnalyzing || (activeTab === 'screenshot' && !screenshotReview?.content.trim())}
            className="w-full sm:w-auto px-8 py-3.5 rounded-xl bg-gradient-to-r from-cyan-500 via-sky-400 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-black text-sm tracking-wider uppercase shadow-[0_0_25px_rgba(6,182,212,0.4)] transition-all flex items-center justify-center space-x-2 disabled:opacity-50 cursor-pointer"
          >
            {isAnalyzing ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin text-slate-950" />
                <span>Running Multi-Layer Scan...</span>
              </>
            ) : (
              <>
                <span>Execute Deep Verification</span>
                <ArrowRight className="w-4 h-4 text-slate-950" />
              </>
            )}
          </button>
        </div>

        {/* Animated Scanning Sequence Overlay */}
        <AnimatePresence>
          {isAnalyzing && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mt-8 pt-6 border-t border-cyber-border"
            >
              <div className="p-5 rounded-2xl bg-cyber-bg border border-cyber-cyan/50 font-mono text-xs relative overflow-hidden shadow-[0_0_30px_rgba(6,182,212,0.15)]">
                {/* Cyber Scan Beam Animation */}
                <div className="scan-beam pointer-events-none" />

                <div className="flex items-center justify-between pb-3 border-b border-cyber-border/70 mb-4">
                  <div className="flex items-center space-x-2 text-cyber-cyan">
                    <Terminal className="w-4 h-4 text-cyber-cyan animate-pulse" />
                    <span className="font-bold tracking-wider">FORENSIC AUDIT SEQUENCE ACTIVE</span>
                  </div>
                  <div className="flex items-center space-x-3 text-slate-300">
                    <span className="text-[11px] font-mono text-cyber-cyan font-bold">
                      Awaiting backend results
                    </span>
                    <span className="text-[11px] text-slate-400">
                      Check availability is reported after completion
                    </span>
                  </div>
                </div>

                {/* Progress Bar */}
                <div className="w-full h-1.5 bg-slate-800 rounded-full mb-4 overflow-hidden">
                  <motion.div 
                    className="h-full bg-gradient-to-r from-cyan-500 to-emerald-400 rounded-full"
                    animate={{ width: ['20%', '80%', '20%'] }}
                    transition={{ duration: 2, repeat: Infinity }}
                  />
                </div>

                <div className="space-y-2">
                  {analysisSteps.slice(0, progressStepIndex + 1).map((step, idx) => {
                    const isLatest = idx === progressStepIndex;
                    const Icon = step.icon;
                    return (
                      <motion.div
                        key={idx}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        className={`flex items-center space-x-2.5 p-1.5 rounded-lg transition-colors ${
                          isLatest 
                            ? 'bg-cyan-950/40 text-cyber-cyan font-bold border border-cyan-500/30' 
                            : 'text-slate-300'
                        }`}
                      >
                        {isLatest ? (
                          <Loader2 className="w-3.5 h-3.5 animate-spin text-cyber-cyan flex-shrink-0" />
                        ) : (
                          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
                        )}
                        <span className="truncate">{step.label}</span>
                      </motion.div>
                    );
                  })}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

      </div>
    </div>
  );
};
