import { fetchJson } from '../api/client';
import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { History, Search, Filter, Globe, ArrowRight, ShieldCheck, AlertOctagon } from 'lucide-react';
import { RiskBadge } from '../components/common/RiskBadge';

export const HistoryPage: React.FC = () => {
  const [error, setError] = useState('');
  const [scans, setScans] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterRisk, setFilterRisk] = useState('ALL');

  useEffect(() => {
    fetchJson('/scans')
      .then(data => {
        setScans(data);
        setLoading(false);
      })
      .catch(e => { setError(e.message); setLoading(false); });
  }, []);

  if (error) return <p role="alert" className="p-8 text-rose-300">{error}</p>;
  const filtered = scans.filter((s) => {
    const matchesQuery = s.target_identifier?.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         s.input_type?.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesRisk = filterRisk === 'ALL' || s.risk_level.includes(filterRisk);
    return matchesQuery && matchesRisk;
  });

  return (
    <div className="min-h-screen py-10 px-4 sm:px-6 lg:px-8 max-w-6xl mx-auto space-y-6">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-cyber-border gap-4">
        <div>
          <div className="flex items-center space-x-2 text-cyber-cyan mb-1">
            <History className="w-5 h-5" />
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white">Scan History Directory</h1>
          </div>
          <p className="text-xs sm:text-sm text-slate-400">
            Browse, search, and audit past opportunity investigations and verification scores.
          </p>
        </div>
        <Link
          to="/analyze"
          className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 via-sky-400 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-black text-xs tracking-wider uppercase transition-all flex items-center space-x-1.5 shadow-[0_0_20px_rgba(6,182,212,0.4)] w-fit cursor-pointer"
        >
          <Search className="w-4 h-4 text-slate-950" />
          <span>New Scan</span>
        </Link>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row items-center gap-3">
        <div className="relative flex-1 w-full">
          <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-3.5" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search scans by opportunity title, domain, or channel..."
            className="w-full bg-cyber-bg border border-cyber-border rounded-xl pl-10 pr-4 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyber-cyan"
          />
        </div>

        <div className="flex items-center space-x-2 w-full sm:w-auto">
          <Filter className="w-4 h-4 text-slate-400" />
          <select
            value={filterRisk}
            onChange={(e) => setFilterRisk(e.target.value)}
            className="bg-cyber-surface border border-cyber-border text-slate-300 rounded-xl px-3 py-2.5 text-xs focus:outline-none focus:border-cyber-cyan"
          >
            <option value="ALL">All Risk Tiers</option>
            <option value="LOW">Low Risk</option>
            <option value="MODERATE">Moderate Risk</option>
            <option value="HIGH">High Risk</option>
            <option value="CRITICAL">Critical Risk</option>
          </select>
        </div>
      </div>

      {/* Scans List */}
      <div className="space-y-3">
        {loading ? (
          <div className="p-12 text-center text-xs font-mono text-cyber-cyan">Loading history records...</div>
        ) : filtered.length === 0 ? (
          <div className="p-12 rounded-2xl glass-card text-center text-slate-400 text-xs">
            No matching scan records found.
          </div>
        ) : (
          filtered.map((sc) => (
            <Link
              key={sc.id}
              to={`/scan/${sc.id}`}
              className="p-4 rounded-xl glass-card border border-cyber-border hover:border-cyber-cyan/50 transition-all flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 group"
            >
              <div className="flex items-start sm:items-center space-x-3.5 truncate">
                <div className="p-2.5 rounded-xl bg-cyber-bg border border-cyber-border text-slate-400 group-hover:text-cyber-cyan transition-colors">
                  <Globe className="w-5 h-5" />
                </div>
                <div className="truncate">
                  <h3 className="font-bold text-sm text-white group-hover:text-cyber-cyan transition-colors truncate">
                    {sc.target_identifier || "General Opportunity"}
                  </h3>
                  <div className="flex flex-wrap items-center gap-2 mt-0.5 text-xs text-slate-400 font-mono">
                    <span>Input: {sc.input_type.toUpperCase()}</span>
                    <span>•</span>
                    <span>Confidence: {sc.analysis_confidence}%</span>
                    <span>•</span>
                    <span>{new Date(sc.created_at).toLocaleDateString()}</span>
                  </div>
                </div>
              </div>

              <div className="flex items-center space-x-4 self-end sm:self-center flex-shrink-0">
                <div className="text-right">
                  <span className="text-[10px] font-mono text-slate-400 block uppercase">Trust Score</span>
                  <span className="font-mono text-base font-extrabold text-white">{sc.trust_score}/100</span>
                </div>
                <RiskBadge level={sc.risk_level} size="sm" />
                <ArrowRight className="w-4 h-4 text-slate-500 group-hover:text-cyber-cyan transition-colors" />
              </div>
            </Link>
          ))
        )}
      </div>

    </div>
  );
};
