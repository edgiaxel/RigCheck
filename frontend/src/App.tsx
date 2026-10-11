import React, { useState, useEffect } from 'react';
import './App.css';
import type { AnalysisResponse, BackendHealth, UserProfile } from './types';
import { checkAuthStatus, fetchHealth, fetchProfile, logout } from './services/api';
import { Header } from './components/Header';
import { ScannerView } from './components/ScannerView';
import { ResultsView } from './components/ResultsView';
import { ProfileView } from './components/ProfileView';
import { HistoryView } from './components/HistoryView';
import { AuthModal } from './components/AuthModal';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('scanner');
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);
  const [health, setHealth] = useState<BackendHealth | null>(null);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [latestAnalysis, setLatestAnalysis] = useState<AnalysisResponse | null>(null);
  const [sessionAnalyses, setSessionAnalyses] = useState<AnalysisResponse[]>([]);
  const [initError, setInitError] = useState<string | null>(null);

  const loadData = async () => {
    try {
      const [healthData, profileData] = await Promise.all([
        fetchHealth().catch(() => null),
        fetchProfile().catch(() => null),
      ]);
      if (healthData) setHealth(healthData);
      if (profileData) setProfile(profileData);
      setInitError(null);
    } catch {
      setInitError('Could not load station profile data.');
    }
  };

  useEffect(() => {
    // Check initial auth status
    const initAuth = async () => {
      const authed = await checkAuthStatus();
      setIsAuthenticated(authed);
      if (authed) {
        await loadData();
      }
    };

    initAuth();
  }, []);

  const handleAuthSuccess = async () => {
    setIsAuthenticated(true);
    await loadData();
  };

  const handleLogout = async () => {
    await logout();
    setIsAuthenticated(false);
    setProfile(null);
  };

  const handleAnalysisSuccess = (result: AnalysisResponse) => {
    setLatestAnalysis(result);
    setSessionAnalyses((prev) => [result, ...prev]);
    setActiveTab('results');
  };

  const handleProfileUpdated = (updated: UserProfile) => {
    setProfile(updated);
  };

  return (
    <div className="app-container">
      {/* Top Header */}
      <Header
        currentTab={activeTab}
        onSelectTab={setActiveTab}
        health={health}
        profile={profile}
        hasAnalysis={latestAnalysis !== null}
        isAuthenticated={Boolean(isAuthenticated)}
        onLogout={handleLogout}
      />

      {/* Access Verification Modal when station is locked */}
      {isAuthenticated === false && (
        <AuthModal onSuccess={handleAuthSuccess} />
      )}

      {/* Main Content Area */}
      <main className="app-main">
        {initError && (
          <div
            style={{
              backgroundColor: 'var(--color-fail-bg)',
              color: 'var(--color-fail)',
              border: '1px solid var(--color-fail-border)',
              padding: '0.85rem 1.25rem',
              borderRadius: 'var(--radius-md)',
              marginBottom: '1.25rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.6rem',
            }}
          >
            <span className="material-symbols-outlined text-[20px]">cloud_off</span>
            <span style={{ fontSize: '0.85rem' }}>{initError}</span>
          </div>
        )}

        {activeTab === 'scanner' && (
          <ScannerView
            profile={profile}
            onAnalysisSuccess={handleAnalysisSuccess}
            onNavigateToProfile={() => setActiveTab('profile')}
          />
        )}

        {activeTab === 'results' && latestAnalysis && (
          <ResultsView
            analysis={latestAnalysis}
            profile={profile}
            onScanAnother={() => setActiveTab('scanner')}
            onEditProfile={() => setActiveTab('profile')}
          />
        )}

        {activeTab === 'profile' && (
          <ProfileView
            key={profile?.updated_at || 'profile-view'}
            initialProfile={profile}
            onProfileUpdated={handleProfileUpdated}
            onNavigateToScanner={() => setActiveTab('scanner')}
          />
        )}

        {activeTab === 'history' && (
          <HistoryView
            sessionAnalyses={sessionAnalyses}
            onSelectAnalysis={(selected) => {
              setLatestAnalysis(selected);
              setActiveTab('results');
            }}
            onNavigateToScanner={() => setActiveTab('scanner')}
          />
        )}
      </main>

      {/* Bottom Navigation for Mobile Screens */}
      <nav className="mobile-nav-bar">
        <button
          className={`mobile-nav-btn ${activeTab === 'scanner' ? 'active' : ''}`}
          onClick={() => setActiveTab('scanner')}
        >
          <span className="material-symbols-outlined">qr_code_scanner</span>
          <span>Scanner</span>
        </button>

        {latestAnalysis && (
          <button
            className={`mobile-nav-btn ${activeTab === 'results' ? 'active' : ''}`}
            onClick={() => setActiveTab('results')}
          >
            <span className="material-symbols-outlined">analytics</span>
            <span>Report</span>
          </button>
        )}

        <button
          className={`mobile-nav-btn ${activeTab === 'profile' ? 'active' : ''}`}
          onClick={() => setActiveTab('profile')}
        >
          <span className="material-symbols-outlined">tune</span>
          <span>Profile</span>
        </button>

        <button
          className={`mobile-nav-btn ${activeTab === 'history' ? 'active' : ''}`}
          onClick={() => setActiveTab('history')}
        >
          <span className="material-symbols-outlined">history</span>
          <span>History</span>
        </button>
      </nav>
    </div>
  );
};

export default App;
