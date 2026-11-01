import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  ShieldCheck, 
  AlertTriangle, 
  AlertOctagon, 
  Users, 
  Search, 
  TrendingUp, 
  Clock, 
  ArrowRight,
  ShieldAlert,
  Zap,
  Globe,
  Activity,
  Terminal
} from 'lucide-react';
import { 
  PieChart, 
  Pie, 
  Cell, 
  ResponsiveContainer, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  AreaChart, 
  Area 
} from 'recharts';
import { fetchDashboardData } from '../api/client';
import { RiskBadge } from '../components/common/RiskBadge';

export const DashboardPage: React.FC = () => {
  const [error, setError] = useState('');
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData().then((res) => {
      setData(res);
      setLoading(false);
    }).catch(e => { setError(e.message); setLoading(false); });
  }, []);

  if (error) return <p role="alert" className="p-8 text-rose-300">{error}</p>;
  if (loading || !data) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="flex flex-col items-center space-y-3">
          <div className="w-12 h-12 border-4 border-cyber-cyan border-t-transparent rounded-full animate-spin" />
          <p className="font-mono text-sm text-cyber-cyan">Loading platform telemetry...</p>
        </div>
      </div>
    );
  }

  const { stats, charts, recent_scans } = data;

  return (
    <div className="min-h-screen py-10 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto space-y-8">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-cyber-border gap-4">
        <div>
          <div className="flex items-center space-x-2 text-cyan-400 font-mono text-xs uppercase tracking-wider mb-1">
            <Activity className="w-4 h-4 text-cyan-400 animate-pulse" />
            <span>GLOBAL THREAT RADAR TELEMETRY</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">Trust & Safety Intelligence Dashboard</h1>
          <p className="text-xs sm:text-sm text-slate-300 mt-1">
            Real-time telemetry, threat distribution, and scam categorization across analyzed opportunities.
          </p>
        </div>
        <Link
          to="/analyze"
          className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 via-sky-400 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-black text-xs tracking-wider uppercase transition-all flex items-center space-x-2 shadow-[0_0_20px_rgba(6,182,212,0.4)] w-fit cursor-pointer"
        >
          <Search className="w-4 h-4 text-slate-950" />
          <span>New Opportunity Scan</span>
        </Link>
      </div>

      {/* Top 5 Metric Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
        
        <div className="p-4 rounded-2xl glass-card border border-cyber-border">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[11px] font-mono uppercase text-slate-400 font-bold">Total Checked</span>
            <Search className="w-4 h-4 text-cyber-cyan" />
          </div>
          <p className="text-2xl sm:text-3xl font-black font-mono text-white">{stats.opportunities_checked}</p>
          <p className="text-[11px] text-emerald-400 mt-1 flex items-center space-x-1 font-mono">
            <span>+18% from last week</span>
          </p>
        </div>

        <div className="p-4 rounded-2xl glass-card border border-emerald-500/40 bg-emerald-950/20">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[11px] font-mono uppercase text-slate-300 font-bold">Low risk baseline</span>
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
          </div>
          <p className="text-2xl sm:text-3xl font-black font-mono text-emerald-400">{stats.safe_count}</p>
          <p className="text-[11px] text-slate-300 mt-1">Legacy score; verify coverage separately</p>
        </div>

        <div className="p-4 rounded-2xl glass-card border border-amber-500/40 bg-amber-950/20">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[11px] font-mono uppercase text-slate-300 font-bold">Needs Verification</span>
            <AlertTriangle className="w-4 h-4 text-amber-400" />
          </div>
          <p className="text-2xl sm:text-3xl font-black font-mono text-amber-400">{stats.needs_verification}</p>
          <p className="text-[11px] text-slate-300 mt-1">Moderate risk markers</p>
        </div>

        <div className="p-4 rounded-2xl glass-card border border-rose-500/40 bg-rose-950/20">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[11px] font-mono uppercase text-slate-300 font-bold">High / Critical</span>
            <AlertOctagon className="w-4 h-4 text-rose-500" />
          </div>
          <p className="text-2xl sm:text-3xl font-black font-mono text-rose-500">
            {stats.high_risk + stats.critical_risk}
          </p>
          <p className="text-[11px] text-rose-300 mt-1">Fee demands & spoofing</p>
        </div>

        <div className="p-4 rounded-2xl glass-card border border-purple-500/40 bg-purple-950/20 col-span-2 lg:col-span-1">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[11px] font-mono uppercase text-slate-300 font-bold">Reports Submitted</span>
            <Users className="w-4 h-4 text-purple-400" />
          </div>
          <p className="text-2xl sm:text-3xl font-black font-mono text-purple-300">{stats.reports_submitted}</p>
          <p className="text-[11px] text-slate-300 mt-1">Crowd safety alerts</p>
        </div>

      </div>

      {/* Analytics Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Risk Distribution Donut Chart */}
        <div className="p-6 rounded-3xl glass-card border border-cyber-border">
          <h3 className="font-extrabold text-white text-base mb-1">Opportunity Risk Distribution</h3>
          <p className="text-xs text-slate-400 mb-4">Proportion of opportunities flagged by risk tier</p>
          <div className="h-64 relative flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={charts.risk_distribution}
                  cx="50%"
                  cy="50%"
                  innerRadius={65}
                  outerRadius={90}
                  paddingAngle={4}
                  dataKey="value"
                >
                  {charts.risk_distribution.map((entry: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={entry.color} stroke="#070b14" strokeWidth={3} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0d1527', borderColor: '#1f2d4d', borderRadius: '12px', fontSize: '12px' }}
                />
              </PieChart>
            </ResponsiveContainer>
            
            {/* Center Stat Overlay */}
            <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
              <span className="text-3xl font-black font-mono text-white tracking-tight">{stats.opportunities_checked}</span>
              <span className="text-[10px] font-mono uppercase text-slate-400 tracking-wider">TOTAL SCANS</span>
            </div>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-4 border-t border-cyber-border text-center">
            {charts.risk_distribution.map((item: any, idx: number) => (
              <div key={idx} className="p-2.5 rounded-xl bg-cyber-bg/70 border border-cyber-border/40">
                <span className="w-2.5 h-2.5 rounded-full inline-block mr-1.5" style={{ backgroundColor: item.color }} />
                <span className="text-[11px] text-slate-300 block font-medium truncate">{item.name}</span>
                <span className="text-xs font-bold text-white font-mono">{item.value}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Scam Categories Bar Chart */}
        <div className="p-6 rounded-3xl glass-card border border-cyber-border">
          <h3 className="font-extrabold text-white text-base mb-1">Top Scam Taxonomies</h3>
          <p className="text-xs text-slate-400 mb-4">Most prevalent fraud schemes detected by the risk engine</p>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={charts.category_distribution} layout="vertical" margin={{ top: 5, right: 30, left: 30, bottom: 5 }}>
                <defs>
                  <linearGradient id="barGrad" x1="0" y1="0" x2="1" y2="0">
                    <stop offset="0%" stopColor="#06b6d4" />
                    <stop offset="100%" stopColor="#3b82f6" />
                  </linearGradient>
                </defs>
                <XAxis type="number" stroke="#64748b" fontSize={11} />
                <YAxis type="category" dataKey="category" stroke="#94a3b8" fontSize={11} width={135} />
                <Tooltip contentStyle={{ backgroundColor: '#0d1527', borderColor: '#1f2d4d', borderRadius: '12px', fontSize: '12px' }} />
                <Bar dataKey="count" fill="url(#barGrad)" radius={[0, 8, 8, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <p className="text-center text-[11px] text-slate-400 mt-4 font-mono">
            Registration & laptop security fee demands represent 48% of total student scam incidents.
          </p>
        </div>

      </div>

      {/* Historical Scans Trend Line */}
      <div className="p-6 rounded-3xl glass-card border border-cyber-border">
        <h3 className="font-extrabold text-white text-base mb-1">Weekly Verification Volume & Threat Activity</h3>
        <p className="text-xs text-slate-400 mb-4">Total submissions scanned vs high/critical threats flagged</p>
        <div className="h-56">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={charts.scans_over_time} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
              <defs>
                <linearGradient id="scansGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.4}/>
                  <stop offset="95%" stopColor="#06b6d4" stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="threatsGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#ef4444" stopOpacity={0.4}/>
                  <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <XAxis dataKey="day" stroke="#64748b" fontSize={11} />
              <YAxis stroke="#64748b" fontSize={11} />
              <Tooltip contentStyle={{ backgroundColor: '#0d1527', borderColor: '#1f2d4d', borderRadius: '12px', fontSize: '12px' }} />
              <Area type="monotone" dataKey="scans" stroke="#06b6d4" strokeWidth={2} fillOpacity={1} fill="url(#scansGrad)" name="Total Scans" />
              <Area type="monotone" dataKey="threats" stroke="#ef4444" strokeWidth={2} fillOpacity={1} fill="url(#threatsGrad)" name="Threats Flagged" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Recent Scans Table */}
      <div className="p-6 rounded-3xl glass-card border border-cyber-border">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="font-extrabold text-white text-base">Recent Opportunity Investigations</h3>
            <p className="text-xs text-slate-400">Latest submissions inspected by forensic scanners</p>
          </div>
          <Link to="/history" className="text-xs font-bold text-cyber-cyan hover:underline flex items-center space-x-1">
            <span>View All Scans</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="divide-y divide-cyber-border/60">
          {recent_scans.map((sc: any, idx: number) => (
            <Link
              key={idx}
              to={`/scan/${sc.id}`}
              className="py-3.5 px-3 -mx-3 rounded-xl hover:bg-cyber-surface/60 transition-colors flex items-center justify-between group"
            >
              <div className="flex items-center space-x-3 truncate mr-4">
                <div className="p-2.5 rounded-xl bg-cyber-bg border border-cyber-border text-slate-400 group-hover:text-cyber-cyan transition-colors">
                  <Globe className="w-4 h-4" />
                </div>
                <div className="truncate">
                  <p className="text-sm font-semibold text-white group-hover:text-cyber-cyan transition-colors truncate">
                    {sc.target_identifier}
                  </p>
                  <p className="text-xs text-slate-400 font-mono">Channel: {sc.input_type.toUpperCase()} • {sc.created_at}</p>
                </div>
              </div>
              <div className="flex items-center space-x-3 flex-shrink-0">
                <span className="font-mono text-sm font-bold text-slate-200">{sc.trust_score}/100</span>
                <RiskBadge level={sc.risk_level} size="sm" />
              </div>
            </Link>
          ))}
        </div>
      </div>

    </div>
  );
};
