import React, { useState, useEffect } from 'react';
import { Users, AlertTriangle, Send, ThumbsUp, ShieldAlert, Plus, CheckCircle2, Filter, Search, Check } from 'lucide-react';
import { fetchCommunityReports, submitCommunityReport } from '../api/client';

export const CommunityPage: React.FC = () => {
  const [reports, setReports] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const [selectedFilter, setSelectedFilter] = useState('all');
  const [upvotedIds, setUpvotedIds] = useState<Record<string, boolean>>({});

  // Form inputs
  const [scamCategory, setScamCategory] = useState('fake_internship');
  const [orgName, setOrgName] = useState('');
  const [targetDomain, setTargetDomain] = useState('');
  const [targetPhone, setTargetPhone] = useState('');
  const [description, setDescription] = useState('');
  const [evidenceText, setEvidenceText] = useState('');

  useEffect(() => {
    fetchCommunityReports().then((data) => {
      setReports(data);
      setLoading(false);
    });
  }, []);

  const handleUpvote = (id: string) => {
    if (upvotedIds[id]) return;
    setUpvotedIds(prev => ({ ...prev, [id]: true }));
    setReports(prev => prev.map(r => r.id === id ? { ...r, upvotes: (r.upvotes || 1) + 1 } : r));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!description.trim()) return;

    setFormError(null);
    try {
      const newReport = await submitCommunityReport({
        scam_category: scamCategory,
        organization_name: orgName || undefined,
        target_domain: targetDomain || undefined,
        target_phone: targetPhone || undefined,
        description: description,
        evidence_text: evidenceText || undefined
      });
      setReports([newReport, ...reports]);
      setSubmitSuccess(true);
      setShowForm(false);
      setDescription('');
      setEvidenceText('');
      setOrgName('');
      setTargetDomain('');
      setTargetPhone('');
      setTimeout(() => setSubmitSuccess(false), 4000);
    } catch (e: any) {
      setFormError(`Submission error: ${e.message}`);
    }
  };

  const filteredReports = reports.filter(r => {
    if (selectedFilter === 'all') return true;
    return r.scam_category === selectedFilter;
  });

  return (
    <div className="min-h-screen py-10 px-4 sm:px-6 lg:px-8 max-w-5xl mx-auto space-y-8">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-cyber-border gap-4">
        <div>
          <div className="flex items-center space-x-2 text-cyber-cyan mb-1">
            <Users className="w-5 h-5" />
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white">Community Scam Intelligence</h1>
          </div>
          <p className="text-xs sm:text-sm text-slate-400">
            Crowdsourced alerts from students and job seekers across India. Report fraudulent opportunities to protect peers.
          </p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-400 to-blue-500 hover:from-cyan-300 hover:to-blue-400 text-slate-950 font-black text-xs tracking-wide uppercase transition-all flex items-center space-x-1.5 shadow-[0_0_15px_rgba(6,182,212,0.3)] w-fit"
        >
          <Plus className="w-4 h-4 stroke-[3]" />
          <span>{showForm ? "Cancel Form" : "Report Fraudulent Offer"}</span>
        </button>
      </div>

      {/* Mandatory Community Disclaimer Banner */}
      <div className="p-4 rounded-xl bg-cyber-surface/70 border border-cyber-border text-xs text-slate-300 flex items-start space-x-3">
        <AlertTriangle className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
        <div className="leading-relaxed">
          <span className="font-bold text-amber-300">Community Evidence Principle:</span> Community-generated reports 
          reflect individual user experiences and undergo multi-signal forensic cross-checks before contributing to reputation weighting.
          Personal identifiers and private keys are never stored.
        </div>
      </div>

      {submitSuccess && (
        <div className="p-4 rounded-xl bg-emerald-950/70 border border-emerald-500/60 text-emerald-300 text-xs flex items-center space-x-2 shadow-[0_0_15px_rgba(16,185,129,0.2)]">
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          <span>Report submitted successfully! Thank you for protecting the student community.</span>
        </div>
      )}

      {/* Submission Form Drawer */}
      {showForm && (
        <form onSubmit={handleSubmit} className="p-6 rounded-2xl glass-card border border-cyber-cyan/50 space-y-4 shadow-[0_0_30px_rgba(6,182,212,0.15)]">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-white text-base">Submit Anonymous Scam Report</h3>
            <span className="text-[10px] font-mono text-cyber-cyan uppercase">End-to-End Anonymized</span>
          </div>
          <p className="text-xs text-slate-400">Please provide observable evidence (claimed organization, suspicious domain, UPI ID or fee demand).</p>

          {formError && (
            <div className="p-3 rounded-lg bg-rose-950/60 border border-rose-500/50 text-rose-300 text-xs">
              {formError}
            </div>
          )}

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div>
              <label className="block font-mono uppercase text-slate-400 mb-1">Scam Category</label>
              <select
                value={scamCategory}
                onChange={(e) => setScamCategory(e.target.value)}
                className="w-full bg-cyber-bg border border-cyber-border rounded-xl p-2.5 text-white focus:outline-none focus:border-cyber-cyan"
              >
                <option value="fake_internship">Fake Internship Offer</option>
                <option value="job_scam">Job / Recruitment Scam</option>
                <option value="fake_scholarship">Fake Scholarship Scheme</option>
                <option value="phishing_website">Phishing Website / Portal</option>
                <option value="payment_scam">Upfront Deposit / Task Scam</option>
                <option value="fake_recruiter">Fake Recruiter Impersonation</option>
              </select>
            </div>

            <div>
              <label className="block font-mono uppercase text-slate-400 mb-1">Impersonated Organization (if any)</label>
              <input
                type="text"
                value={orgName}
                onChange={(e) => setOrgName(e.target.value)}
                placeholder="e.g. Microsoft, Google, TCS"
                className="w-full bg-cyber-bg border border-cyber-border rounded-xl p-2.5 text-white focus:outline-none focus:border-cyber-cyan"
              />
            </div>

            <div>
              <label className="block font-mono uppercase text-slate-400 mb-1">Suspicious Domain / URL</label>
              <input
                type="text"
                value={targetDomain}
                onChange={(e) => setTargetDomain(e.target.value)}
                placeholder="e.g. microsoft-careers-india.xyz"
                className="w-full bg-cyber-bg border border-cyber-border rounded-xl p-2.5 text-white focus:outline-none focus:border-cyber-cyan font-mono"
              />
            </div>

            <div>
              <label className="block font-mono uppercase text-slate-400 mb-1">Recruiter Phone / WhatsApp</label>
              <input
                type="text"
                value={targetPhone}
                onChange={(e) => setTargetPhone(e.target.value)}
                placeholder="e.g. +91 98765 43210"
                className="w-full bg-cyber-bg border border-cyber-border rounded-xl p-2.5 text-white focus:outline-none focus:border-cyber-cyan font-mono"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-mono uppercase text-slate-400 mb-1">What happened? (Incident Summary)</label>
            <textarea
              rows={3}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Describe the interview process, monetary fee request, urgency pressure, or suspicious offer..."
              className="w-full bg-cyber-bg border border-cyber-border rounded-xl p-3 text-xs text-white focus:outline-none focus:border-cyber-cyan leading-relaxed"
              required
            />
          </div>

          <div>
            <label className="block text-xs font-mono uppercase text-slate-400 mb-1">Evidence / Payment Details</label>
            <input
              type="text"
              value={evidenceText}
              onChange={(e) => setEvidenceText(e.target.value)}
              placeholder="e.g. Demanded ₹999 laptop registration fee via UPI ID microsoft.careers@okhdfcbank"
              className="w-full bg-cyber-bg border border-cyber-border rounded-xl p-2.5 text-xs text-white focus:outline-none focus:border-cyber-cyan"
            />
          </div>

          <div className="flex justify-end space-x-2 pt-2">
            <button
              type="button"
              onClick={() => setShowForm(false)}
              className="px-4 py-2 rounded-xl bg-cyber-card border border-cyber-border text-slate-400 hover:text-white text-xs"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-6 py-2 rounded-xl bg-cyber-cyan text-slate-950 font-bold text-xs hover:bg-cyan-400 transition-colors"
            >
              Publish Anonymous Report
            </button>
          </div>
        </form>
      )}

      {/* Category Filter Pills */}
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-[11px] font-mono uppercase text-slate-400 mr-1 flex items-center space-x-1">
          <Filter className="w-3 h-3 text-cyber-cyan" />
          <span>Category Filter:</span>
        </span>
        {[
          { id: 'all', label: `All (${reports.length})` },
          { id: 'fake_internship', label: 'Fake Internships' },
          { id: 'job_scam', label: 'Recruitment Scams' },
          { id: 'fake_scholarship', label: 'Scholarships' },
          { id: 'payment_scam', label: 'Advance Fees' },
        ].map(filter => (
          <button
            key={filter.id}
            onClick={() => setSelectedFilter(filter.id)}
            className={`px-3 py-1 rounded-full text-xs font-mono transition-all ${
              selectedFilter === filter.id
                ? 'bg-cyber-cyan text-slate-950 font-bold shadow-[0_0_10px_rgba(6,182,212,0.3)]'
                : 'bg-cyber-surface/70 border border-cyber-border text-slate-400 hover:text-white'
            }`}
          >
            {filter.label}
          </button>
        ))}
      </div>

      {/* Reports Feed */}
      <div className="space-y-4">
        {loading ? (
          <div className="p-12 text-center text-xs font-mono text-cyber-cyan animate-pulse">Loading live community telemetry...</div>
        ) : filteredReports.length === 0 ? (
          <div className="p-8 text-center text-xs text-slate-400 glass-card rounded-2xl border border-cyber-border">
            No community reports found in this category.
          </div>
        ) : (
          filteredReports.map((report) => {
            const isUpvoted = !!upvotedIds[report.id];
            return (
              <div key={report.id} className="p-5 rounded-2xl glass-card border border-cyber-border hover:border-cyber-cyan/40 transition-all space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span className="text-[10px] font-mono uppercase px-2.5 py-0.5 rounded-full bg-rose-950/80 text-rose-400 font-extrabold border border-rose-500/40">
                      {report.scam_category.replace(/_/g, ' ')}
                    </span>
                    {report.organization_name && (
                      <span className="text-xs font-bold text-white">
                        Claimed Target: {report.organization_name}
                      </span>
                    )}
                  </div>
                  <span className="text-[11px] font-mono text-slate-400">
                    {new Date(report.created_at).toLocaleDateString()}
                  </span>
                </div>

                <p className="text-xs text-slate-200 leading-relaxed">
                  {report.description}
                </p>

                {report.evidence_text && (
                  <div className="p-3 rounded-xl bg-cyber-bg/90 border border-cyber-border text-[11px] text-slate-300 font-mono">
                    <strong className="text-cyber-cyan mr-1">Observed Evidence:</strong> {report.evidence_text}
                  </div>
                )}

                <div className="flex items-center justify-between pt-2 border-t border-cyber-border/40 text-xs text-slate-400">
                  <span className="font-mono text-[11px]">Domain / Endpoint: <strong className="text-slate-300">{report.target_domain || "Direct Contact / Messaging"}</strong></span>
                  
                  <button
                    onClick={() => handleUpvote(report.id)}
                    className={`px-3 py-1 rounded-lg text-xs font-mono font-semibold transition-all flex items-center space-x-1.5 ${
                      isUpvoted
                        ? 'bg-cyber-cyan/20 border border-cyber-cyan text-cyber-cyan shadow-[0_0_10px_rgba(6,182,212,0.3)]'
                        : 'bg-cyber-surface border border-cyber-border text-slate-400 hover:text-cyber-cyan hover:border-cyber-cyan/50'
                    }`}
                  >
                    <ThumbsUp className={`w-3.5 h-3.5 ${isUpvoted ? 'text-cyber-cyan fill-cyber-cyan/30' : ''}`} />
                    <span>{report.upvotes || 1} {isUpvoted ? 'Confirmed by you' : 'Confirm'}</span>
                  </button>
                </div>
              </div>
            );
          })
        )}
      </div>

    </div>
  );
};
