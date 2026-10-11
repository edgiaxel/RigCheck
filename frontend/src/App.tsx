import React, { useState, useEffect, useCallback } from 'react';
import './App.css';
import type { AnalysisResponse, BackendHealth, UserProfile } from './types';
import { fetchHealth, fetchProfile, getApiBaseUrl, setApiBaseUrl } from './services/api';
import { Header } from './components/Header';
import { ScannerView } from './components/ScannerView';
import { ResultsView } from './components/ResultsView';
import { ProfileView } from './components/ProfileView';
import { HistoryView } from './components/HistoryView';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('scanner');
  const [health, setHealth] = useState<BackendHealth | null>(null);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [latestAnalysis, setLatestAnalysis] = useState<AnalysisResponse | null>(null);
  const [sessionAnalyses, setSessionAnalyses] = useState<AnalysisResponse[]>([]);
  const [initError, setInitError] = useState<string | null>(null);

  const isRemoteStaticHost = typeof window !== 'undefined' &&
    !['localhost', '127.0.0.1'].includes(window.location.hostname) &&
    !window.location.hostname.endsWith('.trycloudflare.com');

  const [apiUrlInput, setApiUrlInput] = useState<string>(getApiBaseUrl());
  const [showConnectionBar, setShowConnectionBar] = useState<boolean>(
    Boolean(isRemoteStaticHost && !getApiBaseUrl())
  );
  const [isConnecting, setIsConnecting] = useState<boolean>(false);

  const loadData = useCallback(async () => {
    try {
      const [healthData, profileData] = await Promise.all([
        fetchHealth().catch(() => null),
        fetchProfile().catch(() => null),
      ]);
      if (healthData) {
        setHealth(healthData);
        setInitError(null);
      } else {
        setHealth(null);
        if (isRemoteStaticHost && !getApiBaseUrl()) {
          setInitError('Backend not connected. Paste your PC Cloudflare Tunnel URL above.');
        } else {
          setInitError('Could not reach PC backend. Check if your Cloudflare tunnel and backend are running.');
        }
      }
      if (profileData) {
        setProfile(profileData);
      }
    } catch (err: any) {
      setInitError(err.message || 'Could not load station profile data.');
    }
  }, [isRemoteStaticHost]);

  useEffect(() => {
    let ignore = false;
    Promise.all([
      fetchHealth().catch(() => null),
      fetchProfile().catch(() => null),
    ]).then(([healthData, profileData]) => {
      if (ignore) return;
      if (healthData) {
        setHealth(healthData);
        setInitError(null);
      } else {
        setHealth(null);
        if (isRemoteStaticHost && !getApiBaseUrl()) {
          setInitError('Backend not connected. Paste your PC Cloudflare Tunnel URL above.');
        } else {
          setInitError('Could not reach PC backend. Check if your Cloudflare tunnel and backend are running.');
        }
      }
      if (profileData) {
        setProfile(profileData);
      }
    }).catch((err: any) => {
      if (!ignore) {
        setInitError(err.message || 'Could not load station profile data.');
      }
    });

    return () => {
      ignore = true;
    };
  }, [isRemoteStaticHost]);

  const handleConnect = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setIsConnecting(true);
    setInitError(null);
    let target = apiUrlInput.trim();
    if (target && !target.startsWith('http://') && !target.startsWith('https://')) {
      target = `https://${target}`;
      setApiUrlInput(target);
    }
    setApiBaseUrl(target || null);
    await loadData();
    setIsConnecting(false);
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
        onToggleConnection={() => setShowConnectionBar(!showConnectionBar)}
      />

      {/* Connection Bar (Render cross-origin bridge to local PC) */}
      {(showConnectionBar || (isRemoteStaticHost && !health)) && (
        <form onSubmit={handleConnect} className="connection-panel">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <span className="material-symbols-outlined text-[18px] text-primary">cloud_sync</span>
            <span style={{ fontWeight: 600, fontSize: '0.78rem' }}>
              PC Backend Tunnel URL:
            </span>
          </div>
          <input
            type="url"
            className="form-input"
            style={{ maxWidth: '340px', fontSize: '0.78rem', padding: '0.4rem 0.6rem' }}
            placeholder="https://xxxx.trycloudflare.com (empty for local)"
            value={apiUrlInput}
            onChange={(e) => setApiUrlInput(e.target.value)}
          />
          <button
            type="submit"
            className="btn btn-primary"
            style={{ padding: '0.4rem 0.85rem', fontSize: '0.78rem' }}
            disabled={isConnecting}
          >
            {isConnecting ? 'Connecting...' : (health ? 'Update URL' : 'Connect to PC')}
          </button>
          {getApiBaseUrl() && (
            <button
              type="button"
              className="btn btn-secondary"
              style={{ padding: '0.4rem 0.6rem', fontSize: '0.75rem' }}
              onClick={() => {
                setApiUrlInput('');
                setApiBaseUrl(null);
                loadData();
              }}
            >
              Reset to Local
            </button>
          )}
        </form>
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
