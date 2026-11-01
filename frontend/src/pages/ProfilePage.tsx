import React from 'react';
import { User, ShieldCheck, Key, Lock, LogOut } from 'lucide-react';

export const ProfilePage: React.FC = () => {
  return (
    <div className="min-h-screen py-10 px-4 sm:px-6 lg:px-8 max-w-3xl mx-auto space-y-6">
      
      <div className="pb-4 border-b border-cyber-border">
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white">Security Profile & Session</h1>
        <p className="text-xs sm:text-sm text-slate-400 mt-1">Manage active credentials and multi-factor session status.</p>
      </div>

      <div className="p-6 rounded-2xl glass-card border border-cyber-border space-y-6">
        <div className="flex items-center space-x-4">
          <div className="w-14 h-14 rounded-2xl bg-cyber-cyan/10 border border-cyber-cyan/30 text-cyber-cyan flex items-center justify-center font-bold text-xl">
            SA
          </div>
          <div>
            <h3 className="font-bold text-lg text-white">Security Analyst</h3>
            <p className="text-xs text-slate-400 font-mono">researcher@fakeorreal.cyber</p>
            <span className="inline-block mt-1 text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800">
              Role: ADMIN / ANALYST
            </span>
          </div>
        </div>

        <div className="pt-4 border-t border-cyber-border space-y-3 text-xs">
          <div className="flex items-center justify-between p-3 rounded-xl bg-cyber-bg border border-cyber-border">
            <div>
              <span className="font-bold text-slate-200 block">Password Authentication</span>
              <span className="text-slate-400">Argon2id / bcrypt salted hash</span>
            </div>
            <button className="text-cyber-cyan font-bold hover:underline">Change</button>
          </div>

          <div className="flex items-center justify-between p-3 rounded-xl bg-cyber-bg border border-cyber-border">
            <div>
              <span className="font-bold text-slate-200 block">Two-Factor Authentication</span>
              <span className="text-emerald-400">Enabled (TOTP Authenticator)</span>
            </div>
            <button className="text-slate-400 font-bold hover:text-white">Configure</button>
          </div>
        </div>
      </div>

    </div>
  );
};
