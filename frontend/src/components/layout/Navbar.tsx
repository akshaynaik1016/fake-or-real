import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  ShieldCheck, 
  Search, 
  LayoutDashboard,
  FolderOpen, 
  History, 
  GitCompare, 
  Users, 
  AlertTriangle, 
  Sparkles,
  Menu,
  X,
  Lock,
  ExternalLink
} from 'lucide-react';

export const Navbar: React.FC = () => {
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);

  const navLinks = [
    { name: 'Cases', path: '/cases', icon: FolderOpen },
    { name: 'Analyze', path: '/analyze', icon: Search },
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'History', path: '/history', icon: History },
    { name: 'Compare', path: '/compare', icon: GitCompare },
    { name: 'Community', path: '/community', icon: Users },
    { name: 'Demo Hub', path: '/demo', icon: Sparkles, badge: 'Judge 1-Click' },
  ];

  return (
    <header className="sticky top-0 z-50 glass-panel border-b border-cyber-border/80 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Brand Logo */}
        <Link to="/" className="flex items-center space-x-3 group flex-shrink-0">
          <div className="relative flex items-center justify-center w-10 h-10 rounded-xl bg-cyber-surface border border-cyber-cyan/40 group-hover:border-cyber-cyan transition-all duration-300 shadow-[0_0_15px_rgba(6,182,212,0.25)] flex-shrink-0">
            <ShieldCheck className="w-6 h-6 text-cyber-cyan group-hover:scale-110 transition-transform duration-300" />
            <span className="absolute -bottom-1 -right-1 w-3 h-3 bg-cyber-emerald rounded-full border-2 border-cyber-bg animate-pulse"></span>
          </div>
          <div className="flex flex-col justify-center">
            <div className="flex items-center space-x-2">
              <span className="font-black tracking-wider text-base sm:text-lg bg-gradient-to-r from-white via-slate-100 to-cyber-cyan bg-clip-text text-transparent whitespace-nowrap leading-tight">
                FAKE OR REAL
              </span>
              <span className="text-[10px] font-mono uppercase px-1.5 py-0.5 rounded bg-cyber-cyan/15 text-cyber-cyan border border-cyber-cyan/30 whitespace-nowrap leading-none font-semibold">
                v1.0
              </span>
            </div>
            <p className="text-[10px] sm:text-[11px] text-slate-400 font-mono tracking-tight whitespace-nowrap mt-0.5 leading-none">Don't trust. Verify.</p>
          </div>
        </Link>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center space-x-1">
          {navLinks.map((link) => {
            const Icon = link.icon;
            const isActive = location.pathname === link.path || (link.path === '/cases' && location.pathname.startsWith('/cases/'));
            return (
              <Link
                key={link.name}
                to={link.path}
                className={`relative flex items-center space-x-1.5 px-2 py-1.5 rounded-lg text-xs font-medium transition-all duration-200 ${
                  isActive
                    ? 'text-white bg-cyber-card border border-cyber-cyan/40 shadow-[0_0_12px_rgba(6,182,212,0.15)]'
                    : 'text-slate-300 hover:text-white hover:bg-cyber-surface/60'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-cyber-cyan' : 'text-slate-400'}`} />
                <span>{link.name}</span>
                {link.badge && (
                  <span className="ml-1 text-[9px] font-semibold tracking-wide uppercase px-1.5 py-0.2 rounded-full bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-sm">
                    {link.badge}
                  </span>
                )}
              </Link>
            );
          })}
        </nav>

        {/* Right Action Buttons */}
        <div className="hidden md:flex items-center space-x-3">
          {/* Emergency "I Already Clicked" Button */}
          <Link
            to="/emergency"
            className="flex items-center space-x-1.5 px-3.5 py-1.5 rounded-lg text-xs font-bold uppercase tracking-wider text-rose-200 bg-rose-950/40 border border-rose-500/50 hover:bg-rose-900/60 hover:border-rose-400 transition-all duration-200 shadow-[0_0_15px_rgba(244,63,94,0.2)] animate-pulse-slow"
          >
            <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />
            <span>I Already Clicked</span>
          </Link>

          {/* Admin link */}
          <Link
            to="/admin"
            className="p-2 rounded-lg text-slate-400 hover:text-cyber-cyan hover:bg-cyber-surface transition-colors"
            title="Admin Console"
          >
            <Lock className="w-4 h-4" />
          </Link>
        </div>

        {/* Mobile menu button */}
        <div className="flex md:hidden items-center space-x-2">
          <Link
            to="/emergency"
            className="px-2.5 py-1 rounded text-[11px] font-bold text-rose-300 bg-rose-950/60 border border-rose-500/40"
          >
            Emergency
          </Link>
          <button
            onClick={() => setMobileOpen(!mobileOpen)}
            className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-cyber-surface"
            aria-label="Toggle Navigation Menu"
          >
            {mobileOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileOpen && (
        <div className="md:hidden border-t border-cyber-border/80 bg-cyber-bg/95 px-4 pt-3 pb-6 space-y-2">
          {navLinks.map((link) => {
            const Icon = link.icon;
            const isActive = location.pathname === link.path || (link.path === '/cases' && location.pathname.startsWith('/cases/'));
            return (
              <Link
                key={link.name}
                to={link.path}
                onClick={() => setMobileOpen(false)}
                className={`flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium ${
                  isActive ? 'bg-cyber-card text-cyber-cyan border border-cyber-cyan/30' : 'text-slate-300'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{link.name}</span>
                {link.badge && (
                  <span className="text-[9px] px-1.5 py-0.5 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                    {link.badge}
                  </span>
                )}
              </Link>
            );
          })}
          <div className="pt-2 border-t border-cyber-border/60">
            <Link
              to="/emergency"
              onClick={() => setMobileOpen(false)}
              className="flex items-center space-x-2 px-3 py-2 rounded-lg text-xs font-bold text-rose-300 bg-rose-950/50 border border-rose-500/50"
            >
              <AlertTriangle className="w-4 h-4" />
              <span>I Already Clicked — Emergency Triage</span>
            </Link>
          </div>
        </div>
      )}
    </header>
  );
};
