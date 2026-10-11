import React from 'react';
import { mapToDisplayVerdict, type AnalysisResponse } from '../types';

interface HistoryViewProps {
  sessionAnalyses: AnalysisResponse[];
  onSelectAnalysis: (analysis: AnalysisResponse) => void;
  onNavigateToScanner: () => void;
}

export const HistoryView: React.FC<HistoryViewProps> = ({
  sessionAnalyses,
  onSelectAnalysis,
  onNavigateToScanner,
}) => {
  return (
    <div className="history-container">
      {/* Banner */}
      <div className="welcome-banner">
        <div className="welcome-info">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span className="badge badge-neutral">Session Records</span>
            <span style={{ fontSize: '0.78rem', color: 'var(--color-text-muted)' }}>
              Ephemeral Browser Storage
            </span>
          </div>
          <h1 className="banner-tagline">Inspection History</h1>
          <p className="banner-desc">
            To guarantee complete privacy, RigCheck does not persist scans to an external server database. Scans performed in your current browser session are listed below.
          </p>
        </div>

        <button onClick={onNavigateToScanner} className="btn btn-primary">
          <span className="material-symbols-outlined text-[18px]">add_a_photo</span>
          Scan Component
        </button>
      </div>

      {sessionAnalyses.length === 0 ? (
        /* Empty State */
        <div className="drafting-card" style={{ textAlign: 'center', padding: '3.5rem 1.5rem' }}>
          <div
            style={{
              width: '60px',
              height: '60px',
              borderRadius: '50%',
              backgroundColor: 'var(--color-surface-container)',
              color: 'var(--color-text-subtle)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 1rem auto',
            }}
          >
            <span className="material-symbols-outlined text-[30px]">history_toggle_off</span>
          </div>
          <h2 style={{ fontSize: '1.2rem', marginBottom: '0.4rem' }}>No Scans in Current Session</h2>
          <p
            style={{
              color: 'var(--color-text-muted)',
              fontSize: '0.85rem',
              maxWidth: '440px',
              margin: '0 auto 1.5rem auto',
            }}
          >
            No hardware labels have been scanned yet in this session. Once you scan a component label, its verified report will appear here.
          </p>
          <button onClick={onNavigateToScanner} className="btn btn-secondary">
            <span className="material-symbols-outlined text-[18px]">qr_code_scanner</span>
            Open Scanner Now
          </button>
        </div>
      ) : (
        /* Real Session Scans */
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {sessionAnalyses.map((scan, idx) => {
            const verdict = mapToDisplayVerdict(scan.compatibility_report.overall_status);
            const specs = scan.extracted_specifications;
            return (
              <div
                key={idx}
                className="drafting-card"
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  flexWrap: 'wrap',
                  gap: '1rem',
                }}
              >
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.35rem' }}>
                    <span
                      className={`badge ${
                        verdict === 'Compatible'
                          ? 'badge-pass'
                          : verdict === 'Incompatible'
                          ? 'badge-fail'
                          : 'badge-warn'
                      }`}
                    >
                      {verdict}
                    </span>
                    <span style={{ fontSize: '0.75rem', color: 'var(--color-text-subtle)' }}>
                      {new Date(scan.analyzed_at).toLocaleString()}
                    </span>
                  </div>

                  <h3 style={{ fontSize: '1.1rem' }}>
                    {[specs.brand, specs.model].filter(Boolean).join(' ') || 'Hardware Component'}
                  </h3>

                  <p style={{ color: 'var(--color-text-muted)', fontSize: '0.82rem', marginTop: '0.2rem' }}>
                    {scan.compatibility_report.summary}
                  </p>
                </div>

                <button
                  onClick={() => onSelectAnalysis(scan)}
                  className="btn btn-secondary"
                  style={{ alignSelf: 'center' }}
                >
                  <span className="material-symbols-outlined text-[16px]">visibility</span>
                  View Report
                </button>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
