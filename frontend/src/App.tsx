import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Navbar } from './components/layout/Navbar';
import { Footer } from './components/layout/Footer';

import {EvidenceChallengePage} from './pages/EvidenceChallengePage';
import { CasesPage } from './pages/CasesPage';
import { CaseWorkspacePage } from './pages/CaseWorkspacePage';
// Pages
import { LandingPage } from './pages/LandingPage';
import { AnalyzePage } from './pages/AnalyzePage';
import { ScanResultPage } from './pages/ScanResultPage';
import { DashboardPage } from './pages/DashboardPage';
import { HistoryPage } from './pages/HistoryPage';
import { ComparePage } from './pages/ComparePage';
import { CommunityPage } from './pages/CommunityPage';
import { EmergencyPage } from './pages/EmergencyPage';
import { TrustPassportPage } from './pages/TrustPassportPage';
import { ExtensionPage } from './pages/ExtensionPage';
import { DemoPage } from './pages/DemoPage';
import { AdminPage } from './pages/AdminPage';
import { SettingsPage } from './pages/SettingsPage';
import { ProfilePage } from './pages/ProfilePage';
import { SecurityPage } from './pages/SecurityPage';
import { PrivacyPage } from './pages/PrivacyPage';
import { AboutPage } from './pages/AboutPage';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { ForgotPasswordPage } from './pages/ForgotPasswordPage';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <div className="flex flex-col min-h-screen bg-cyber-bg text-slate-100 selection:bg-cyber-cyan selection:text-slate-950 font-sans">
        <Navbar />
        <main className="flex-1">
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/challenge" element={<EvidenceChallengePage />} />
            <Route path="/cases" element={<CasesPage />} />
            <Route path="/cases/:id" element={<CaseWorkspacePage />} />
            <Route path="/analyze" element={<AnalyzePage />} />
            <Route path="/scan/:id" element={<ScanResultPage />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/history" element={<HistoryPage />} />
            <Route path="/compare" element={<ComparePage />} />
            <Route path="/community" element={<CommunityPage />} />
            <Route path="/reports" element={<CommunityPage />} />
            <Route path="/report/:id" element={<ScanResultPage />} />
            <Route path="/trust-passport/:id" element={<TrustPassportPage />} />
            <Route path="/emergency" element={<EmergencyPage />} />
            <Route path="/extension" element={<ExtensionPage />} />
            <Route path="/demo" element={<DemoPage />} />
            <Route path="/admin" element={<AdminPage />} />
            <Route path="/settings" element={<SettingsPage />} />
            <Route path="/profile" element={<ProfilePage />} />
            <Route path="/security" element={<SecurityPage />} />
            <Route path="/privacy" element={<PrivacyPage />} />
            <Route path="/about" element={<AboutPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/forgot-password" element={<ForgotPasswordPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </BrowserRouter>
  );
};

export default App;
