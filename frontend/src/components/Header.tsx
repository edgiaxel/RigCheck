import React from 'react';
import type { BackendHealth, UserProfile } from '../types';
import { getApiBaseUrl } from '../services/api';

interface HeaderProps {
  currentTab: string;
  onSelectTab: (tab: string) => void;
  health: BackendHealth | null;
  profile: UserProfile | null;
  hasAnalysis: boolean;
  onToggleConnection: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  currentTab,
  onSelectTab,
  health,
  profile,
  hasAnalysis,
  onToggleConnection,
}) => {
  const isOllamaOnline = health?.ollama?.available ?? false;

  return (
    <header className="app-header">
      <div className="brand-section">
        <div className="brand-logo-icon">
          <span className="material-symbols-outlined text-[20px]">memory</span>
        </div>
        <div>
          <div className="brand-title">RigCheck</div>
          <div className="brand-subtitle">Archival Compatibility Canvas</div>
        </div>
      </div>

      <nav className="nav-links">
        <button
          className={`nav-btn ${currentTab === 'scanner' ? 'active' : ''}`}
          onClick={() => onSelectTab('scanner')}
        >
          <span className="material-symbols-outlined text-[18px]">qr_code_scanner</span>
          Scanner
        </button>

        {hasAnalysis && (
          <button
            className={`nav-btn ${currentTab === 'results' ? 'active' : ''}`}
            onClick={() => onSelectTab('results')}
          >
            <span className="material-symbols-outlined text-[18px]">analytics</span>
            Latest Report
          </button>
        )}

        <button
          className={`nav-btn ${currentTab === 'profile' ? 'active' : ''}`}
          onClick={() => onSelectTab('profile')}
        >
          <span className="material-symbols-outlined text-[18px]">tune</span>
          My PC Profile
        </button>

        <button
          className={`nav-btn ${currentTab === 'history' ? 'active' : ''}`}
          onClick={() => onSelectTab('history')}
        >
          <span className="material-symbols-outlined text-[18px]">history</span>
          Scan History
        </button>
      </nav>

      <div className="header-meta">
        {profile && (
          <div className="telemetry-chip hidden-mobile" title="Current Configured Rig">
            <span className="material-symbols-outlined text-[15px] text-primary">developer_board</span>
            <span>{profile.profile_name || 'My PC Rig'}</span>
            {profile.existing_components?.psu_wattage && (
              <span className="badge badge-neutral">{profile.existing_components.psu_wattage}W</span>
            )}
          </div>
        )}

        <div className="telemetry-chip" title="Local Inference Engine Status">
          <span className={`pulse-dot ${isOllamaOnline ? 'pulse-dot-green' : 'pulse-dot-amber'}`} />
          <span style={{ fontSize: '0.7rem' }}>
            {isOllamaOnline ? 'Ollama: Ready' : (health ? 'Connecting...' : 'PC Offline')}
          </span>
        </div>

        <button
          onClick={onToggleConnection}
          className="telemetry-chip"
          title="Configure PC Connection (Cloudflare Tunnel URL)"
          style={{ cursor: 'pointer', transition: 'all 0.15s ease' }}
        >
          <span className="material-symbols-outlined text-[16px] text-primary">settings_ethernet</span>
          <span style={{ fontSize: '0.7rem' }}>
            {getApiBaseUrl() ? 'Tunnel URL' : 'Connect PC'}
          </span>
        </button>
      </div>
    </header>
  );
};
