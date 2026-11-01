import { authenticate } from '../api/client';
import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ShieldCheck, Lock, Mail, ArrowRight } from 'lucide-react';

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const [error, setError] = useState('');
  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true); setError('');
    try { await authenticate('login', email, password); navigate('/dashboard'); }
    catch (e) { setError(e instanceof Error ? e.message : 'Authentication failed'); }
    finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen py-16 px-4 flex items-center justify-center">
      <div className="w-full max-w-md p-8 rounded-3xl glass-card border border-cyber-border shadow-2xl space-y-6">
        
        <div className="text-center space-y-2">
          <div className="inline-flex p-3 rounded-2xl bg-cyber-cyan/10 border border-cyber-cyan/30 text-cyber-cyan mb-1">
            <ShieldCheck className="w-8 h-8" />
          </div>
          <h1 className="text-2xl font-extrabold text-white">Sign In to UNMASK</h1>
          <p className="text-xs text-slate-400">Enter your credentials to access saved audit reports and dashboard</p>
        </div>

        {error && <p role="alert" className="text-rose-300 text-sm">{error}</p>}
        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="block text-xs font-mono uppercase text-slate-400 mb-1">Email Address</label>
            <div className="relative">
              <Mail className="w-4 h-4 text-slate-500 absolute left-3.5 top-3.5" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="analyst@fakeorreal.cyber"
                className="w-full bg-cyber-bg border border-cyber-border rounded-xl pl-10 pr-3.5 py-2.5 text-xs text-white focus:outline-none focus:border-cyber-cyan"
                required
              />
            </div>
          </div>

          <div>
            <div className="flex justify-between items-center mb-1">
              <label className="block text-xs font-mono uppercase text-slate-400">Password</label>
              <Link to="/forgot-password" className="text-[11px] text-cyber-cyan hover:underline">Forgot?</Link>
            </div>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-500 absolute left-3.5 top-3.5" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                className="w-full bg-cyber-bg border border-cyber-border rounded-xl pl-10 pr-3.5 py-2.5 text-xs text-white focus:outline-none focus:border-cyber-cyan"
                required
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-bold text-xs tracking-wide transition-all shadow-[0_0_15px_rgba(6,182,212,0.3)] flex items-center justify-center space-x-1.5"
          >
            <span>{loading ? "Authenticating..." : "Sign In"}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        <div className="pt-4 border-t border-cyber-border text-center text-xs text-slate-400">
          Don't have an account?{" "}
          <Link to="/register" className="text-cyber-cyan font-bold hover:underline">Register</Link>
        </div>

      </div>
    </div>
  );
};
