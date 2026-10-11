import React, { useState } from 'react';
import { loginWithSecret, ApiError, getApiBaseUrl, setApiBaseUrl } from '../services/api';

interface AuthModalProps {
  onSuccess: () => void;
}

export const AuthModal: React.FC<AuthModalProps> = ({ onSuccess }) => {
  const [secret, setSecret] = useState<string>('');
  const [showSecret, setShowSecret] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [apiUrl, setApiUrl] = useState<string>(getApiBaseUrl());
  const [showConnectionConfig, setShowConnectionConfig] = useState<boolean>(Boolean(getApiBaseUrl()));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!secret.trim()) {
      setErrorMessage('Please enter the access secret.');
      return;
    }

    setIsLoading(true);
    setErrorMessage(null);

    try {
      // Save custom API base URL if adjusted
      setApiBaseUrl(apiUrl.trim() || null);
      await loginWithSecret(secret.trim());
      onSuccess();
    } catch (err: any) {
      if (err instanceof ApiError) {
        setErrorMessage(err.detail);
      } else {
        setErrorMessage(err.message || 'Authentication failed. Please verify your secret.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(28, 27, 26, 0.7)',
        backdropFilter: 'blur(8px)',
        WebkitBackdropFilter: 'blur(8px)',
        zIndex: 100,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '1rem',
      }}
    >
      <div
        className="drafting-card"
        style={{
          width: '100%',
          maxWidth: '440px',
          padding: '2rem 1.75rem',
          backgroundColor: 'var(--color-surface)',
          boxShadow: 'var(--shadow-lg)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.5rem' }}>
          <div
            style={{
              width: '38px',
              height: '38px',
              borderRadius: 'var(--radius-sm)',
              backgroundColor: 'var(--color-primary-subtle)',
              color: 'var(--color-primary)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <span className="material-symbols-outlined text-[22px]">lock</span>
          </div>
          <div>
            <h2 style={{ fontSize: '1.25rem', lineHeight: 1.2 }}>Hardware Station Locked</h2>
            <span className="badge badge-neutral" style={{ marginTop: '0.2rem' }}>
              Access Verification Required
            </span>
          </div>
        </div>

        <p style={{ color: 'var(--color-text-muted)', fontSize: '0.82rem', margin: '1rem 0 1.25rem 0' }}>
          This RigCheck instance is running locally on your PC. Enter the configured access secret to unlock remote phone inspection and profile management.
        </p>

        {errorMessage && (
          <div
            style={{
              backgroundColor: 'var(--color-fail-bg)',
              border: '1px solid var(--color-fail-border)',
              color: 'var(--color-fail)',
              padding: '0.75rem',
              borderRadius: 'var(--radius-sm)',
              marginBottom: '1rem',
              fontSize: '0.82rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
            }}
          >
            <span className="material-symbols-outlined text-[18px]">error</span>
            <span>{errorMessage}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div className="form-group">
            <label className="form-label" htmlFor="access-secret-input">
              <span>Access Secret</span>
              <button
                type="button"
                onClick={() => setShowSecret(!showSecret)}
                style={{ fontSize: '0.7rem', color: 'var(--color-primary)', background: 'none' }}
              >
                {showSecret ? 'Hide' : 'Show'}
              </button>
            </label>
            <input
              id="access-secret-input"
              type={showSecret ? 'text' : 'password'}
              className="form-input"
              placeholder="Enter your ACCESS_SECRET"
              value={secret}
              onChange={(e) => setSecret(e.target.value)}
              disabled={isLoading}
              autoComplete="current-password"
              autoFocus
            />
          </div>

          {/* Optional Cross-Origin API Endpoint (Render to Cloudflare Tunnel) */}
          <div style={{ marginTop: '-0.25rem' }}>
            <button
              type="button"
              onClick={() => setShowConnectionConfig(!showConnectionConfig)}
              style={{
                background: 'none',
                border: 'none',
                color: 'var(--color-primary)',
                fontSize: '0.74rem',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '0.35rem',
                padding: '0.15rem 0',
              }}
            >
              <span className="material-symbols-outlined text-[15px]">settings_ethernet</span>
              <span>{showConnectionConfig ? 'Hide Backend Tunnel Settings' : 'Configure Backend Tunnel URL'}</span>
            </button>

            {showConnectionConfig && (
              <div
                style={{
                  marginTop: '0.5rem',
                  padding: '0.65rem 0.75rem',
                  backgroundColor: 'var(--color-bg)',
                  borderRadius: 'var(--radius-sm)',
                  border: '1px solid var(--color-border)',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '0.35rem',
                }}
              >
                <label
                  htmlFor="backend-api-url"
                  style={{
                    fontSize: '0.72rem',
                    color: 'var(--color-text-muted)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                  }}
                >
                  <span>Backend Tunnel URL</span>
                  <span style={{ fontSize: '0.68rem', color: 'var(--color-text-subtle)' }}>
                    {apiUrl ? 'Cross-Origin' : 'Default (/api)'}
                  </span>
                </label>
                <input
                  id="backend-api-url"
                  type="url"
                  className="form-input"
                  style={{ fontSize: '0.78rem', padding: '0.4rem 0.6rem' }}
                  placeholder="https://xxxx.trycloudflare.com (empty for local /api)"
                  value={apiUrl}
                  onChange={(e) => setApiUrl(e.target.value)}
                  disabled={isLoading}
                />
                <div style={{ fontSize: '0.68rem', color: 'var(--color-text-subtle)', lineHeight: 1.3 }}>
                  Use this when RigCheck frontend is deployed on Render to route requests to your PC's Cloudflare Tunnel.
                </div>
              </div>
            )}
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            disabled={isLoading || !secret.trim()}
            style={{ width: '100%', padding: '0.75rem' }}
          >
            {isLoading ? (
              <>
                <span className="pulse-dot pulse-dot-amber" />
                Verifying Credentials...
              </>
            ) : (
              <>
                <span className="material-symbols-outlined text-[18px]">key</span>
                Unlock Station
              </>
            )}
          </button>
        </form>

        <div
          style={{
            marginTop: '1.25rem',
            paddingTop: '1rem',
            borderTop: '1px dashed var(--color-border)',
            fontSize: '0.72rem',
            color: 'var(--color-text-subtle)',
            lineHeight: 1.4,
          }}
        >
          <strong>Security Note:</strong> The secret is stored locally in your host PC's <code>.env</code> file (or terminal startup log). It is never transmitted to external cloud providers.
        </div>
      </div>
    </div>
  );
};
