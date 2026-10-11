import React, { useState, useRef } from 'react';
import type { AnalysisResponse, UserProfile } from '../types';
import { analyzeComponent, ApiError } from '../services/api';

interface ScannerViewProps {
  profile: UserProfile | null;
  onAnalysisSuccess: (response: AnalysisResponse) => void;
  onNavigateToProfile: () => void;
}

export const ScannerView: React.FC<ScannerViewProps> = ({
  profile,
  onAnalysisSuccess,
  onNavigateToProfile,
}) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [priceInput, setPriceInput] = useState<string>('');
  const [enableSearch, setEnableSearch] = useState<boolean>(true);
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [loadingStep, setLoadingStep] = useState<string>('Initializing vision pipeline...');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const cameraInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelection = (file: File) => {
    setErrorMessage(null);

    // Client-side quick validation
    const allowedTypes = ['image/jpeg', 'image/png', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
      setErrorMessage(`Invalid image format (${file.type || 'unknown'}). Please provide a JPG, PNG, or WebP image.`);
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      setErrorMessage(`File size (${(file.size / (1024 * 1024)).toFixed(1)} MB) exceeds maximum allowed limit of 10 MB.`);
      return;
    }

    if (file.size === 0) {
      setErrorMessage('Selected file is empty.');
      return;
    }

    setSelectedFile(file);
    const objectUrl = URL.createObjectURL(file);
    setPreviewUrl(objectUrl);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileSelection(e.dataTransfer.files[0]);
    }
  };

  const clearSelection = () => {
    setSelectedFile(null);
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
      setPreviewUrl(null);
    }
    setErrorMessage(null);
  };

  const formatIdrDisplay = (value: string): string => {
    const numeric = value.replace(/\D/g, '');
    if (!numeric) return '';
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      maximumFractionDigits: 0,
    }).format(Number(numeric));
  };

  const handlePriceChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const raw = e.target.value.replace(/\D/g, '');
    setPriceInput(raw);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) {
      setErrorMessage('Please select or capture a component label image first.');
      return;
    }

    setIsLoading(true);
    setErrorMessage(null);
    setLoadingStep('Uploading component label to local backend...');

    const parsedPrice = priceInput.trim() ? parseInt(priceInput, 10) : null;

    try {
      // Step simulator for realistic technical telemetry
      const timer1 = setTimeout(() => {
        setLoadingStep('Running local Gemma 3 4B vision inference via Ollama...');
      }, 1200);

      const timer2 = setTimeout(() => {
        setLoadingStep('Evaluating physical clearance & PSU constraints against your profile...');
      }, 3500);

      const result = await analyzeComponent(selectedFile, parsedPrice, enableSearch);

      clearTimeout(timer1);
      clearTimeout(timer2);
      onAnalysisSuccess(result);
    } catch (err: any) {
      if (err instanceof ApiError) {
        setErrorMessage(`Backend error (${err.statusCode}): ${err.detail}`);
      } else {
        setErrorMessage(err.message || 'An unexpected error occurred during analysis.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="scanner-container">
      {/* Welcome Banner */}
      <div className="welcome-banner">
        <div className="welcome-info">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
            <span className="badge badge-neutral">Archival Hardware Intake</span>
            <span style={{ color: 'var(--color-text-subtle)' }}>•</span>
            <span style={{ fontSize: '0.78rem', color: 'var(--color-text-muted)' }}>
              100% On-Device Privacy Guaranteed
            </span>
          </div>
          <h1 className="banner-tagline">Know before you buy.</h1>
          <p className="banner-desc">
            Capture or upload a component retail label, serial plate, or box packaging. RigCheck extracts visible specs via local Gemma 3 4B vision and validates physical & power tolerances against your configured rig.
          </p>
        </div>

        {profile && (
          <div className="active-rig-pill">
            <span className="material-symbols-outlined text-[18px] text-primary">computer</span>
            <div>
              <div style={{ fontWeight: 600, fontSize: '0.82rem' }}>
                {profile.profile_name || 'Configured PC'}
              </div>
              <div style={{ fontSize: '0.7rem', color: 'var(--color-text-muted)' }}>
                {profile.existing_components?.psu_wattage
                  ? `PSU: ${profile.existing_components.psu_wattage}W`
                  : 'PSU: Unspecified'}{' '}
                • Socket:{' '}
                {profile.compatibility_requirements?.socket ||
                  profile.existing_components?.motherboard ||
                  'N/A'}
              </div>
            </div>
            <button
              onClick={onNavigateToProfile}
              className="btn btn-secondary"
              style={{ padding: '0.25rem 0.5rem', fontSize: '0.72rem', marginLeft: '0.5rem' }}
              title="Edit Profile"
            >
              Edit
            </button>
          </div>
        )}
      </div>

      {/* Error Banner */}
      {errorMessage && (
        <div
          style={{
            backgroundColor: 'var(--color-fail-bg)',
            border: '1px solid var(--color-fail-border)',
            color: 'var(--color-fail)',
            padding: '1rem',
            borderRadius: 'var(--radius-md)',
            marginBottom: '1.5rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem',
          }}
        >
          <span className="material-symbols-outlined text-[22px]">error</span>
          <div style={{ flex: 1, fontSize: '0.85rem' }}>{errorMessage}</div>
          <button
            onClick={() => setErrorMessage(null)}
            style={{ color: 'inherit', fontWeight: 600, fontSize: '0.8rem' }}
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Main Scanner Grid */}
      <div className="scanner-grid">
        {/* Left: Input / Dropzone or Preview / Progress */}
        <div>
          {isLoading ? (
            /* Stitch-inspired Scan In Progress Card */
            <div className="scanning-card">
              <div className="scanner-frame-box">
                <span className="corner-tl" />
                <span className="corner-tr" />
                <span className="corner-bl" />
                <span className="corner-br" />
                <div className="scanning-laser" />
                <span className="material-symbols-outlined text-[36px] text-primary">
                  photo_camera
                </span>
              </div>
              <div>
                <h3 style={{ fontSize: '1.2rem', marginBottom: '0.35rem' }}>
                  Analyzing Hardware Component
                </h3>
                <p style={{ color: 'var(--color-text-muted)', fontSize: '0.85rem' }}>
                  {loadingStep}
                </p>
              </div>
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  fontSize: '0.75rem',
                  color: 'var(--color-text-subtle)',
                }}
              >
                <span className="pulse-dot pulse-dot-amber" />
                <span>Ollama gemma3:4b active • Images streamed in-memory</span>
              </div>
            </div>
          ) : previewUrl ? (
            /* Image Preview Card */
            <div className="drafting-card" style={{ padding: '1rem' }}>
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  marginBottom: '0.75rem',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                  <span className="material-symbols-outlined text-[18px] text-primary">image</span>
                  <span style={{ fontWeight: 600, fontSize: '0.88rem' }}>Intake Preview</span>
                  <span className="badge badge-neutral">
                    {selectedFile ? `${(selectedFile.size / 1024).toFixed(0)} KB` : ''}
                  </span>
                </div>
                <button onClick={clearSelection} className="retake-btn" type="button">
                  Clear & Retake
                </button>
              </div>

              <div className="preview-container">
                <img src={previewUrl} alt="Selected component" className="preview-image" />
                <div className="preview-overlay-info">
                  <span>{selectedFile?.name || 'component_label.jpg'}</span>
                  <span>Ready for Inspection</span>
                </div>
              </div>
            </div>
          ) : (
            /* Upload / Capture Dropzone */
            <div
              className={`dropzone-container ${isDragging ? 'drag-over' : ''}`}
              onDragOver={(e) => {
                e.preventDefault();
                setIsDragging(true);
              }}
              onDragLeave={() => setIsDragging(false)}
              onDrop={handleDrop}
            >
              <div
                style={{
                  width: '64px',
                  height: '64px',
                  borderRadius: '50%',
                  backgroundColor: 'var(--color-surface-container)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'var(--color-primary)',
                }}
              >
                <span className="material-symbols-outlined text-[32px]">add_a_photo</span>
              </div>

              <div>
                <h3 style={{ fontSize: '1.15rem', marginBottom: '0.25rem' }}>
                  Capture or Upload Component Label
                </h3>
                <p style={{ color: 'var(--color-text-muted)', fontSize: '0.82rem', maxWidth: '380px' }}>
                  Drag & drop an image here, snap with your phone camera, or choose a file from your gallery.
                </p>
              </div>

              {/* Action Buttons for Mobile Camera & Desktop Browse */}
              <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap', justifyContent: 'center' }}>
                {/* Camera capture (mobile friendly) */}
                <button
                  type="button"
                  className="btn btn-primary"
                  onClick={() => cameraInputRef.current?.click()}
                >
                  <span className="material-symbols-outlined text-[18px]">photo_camera</span>
                  Camera
                </button>

                {/* File picker */}
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => fileInputRef.current?.click()}
                >
                  <span className="material-symbols-outlined text-[18px]">folder_open</span>
                  Browse Files
                </button>
              </div>

              <div style={{ fontSize: '0.72rem', color: 'var(--color-text-subtle)' }}>
                Supports JPG, PNG, WebP up to 10 MB • Zero server persistence
              </div>

              {/* Hidden file inputs */}
              <input
                ref={fileInputRef}
                type="file"
                accept="image/jpeg,image/png,image/webp"
                style={{ display: 'none' }}
                onChange={(e) => {
                  if (e.target.files && e.target.files[0]) {
                    handleFileSelection(e.target.files[0]);
                  }
                }}
              />
              <input
                ref={cameraInputRef}
                type="file"
                accept="image/*"
                capture="environment"
                style={{ display: 'none' }}
                onChange={(e) => {
                  if (e.target.files && e.target.files[0]) {
                    handleFileSelection(e.target.files[0]);
                  }
                }}
              />
            </div>
          )}
        </div>

        {/* Right: Inspection Parameters & Submission */}
        <div className="drafting-card">
          <h2 style={{ fontSize: '1.05rem', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <span className="material-symbols-outlined text-[18px] text-primary">tune</span>
            Inspection Parameters
          </h2>

          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.1rem' }}>
            {/* Observed Price Input */}
            <div className="form-group">
              <label className="form-label" htmlFor="price-input">
                <span>Observed Price (Optional)</span>
                <span style={{ fontSize: '0.7rem', color: 'var(--color-text-subtle)' }}>IDR</span>
              </label>
              <input
                id="price-input"
                type="text"
                className="form-input"
                placeholder="e.g. 7500000"
                value={priceInput}
                onChange={handlePriceChange}
                disabled={isLoading}
              />
              {priceInput && (
                <div style={{ fontSize: '0.75rem', color: 'var(--color-primary)', fontWeight: 600 }}>
                  {formatIdrDisplay(priceInput)}
                </div>
              )}
              {profile?.max_budget_idr && (
                <div style={{ fontSize: '0.72rem', color: 'var(--color-text-muted)' }}>
                  Max budget configured:{' '}
                  {new Intl.NumberFormat('id-ID', {
                    style: 'currency',
                    currency: 'IDR',
                    maximumFractionDigits: 0,
                  }).format(profile.max_budget_idr)}
                </div>
              )}
            </div>

            {/* Technical Search Enrichment Toggle */}
            <div
              style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: '0.6rem',
                padding: '0.65rem',
                borderRadius: 'var(--radius-sm)',
                backgroundColor: 'var(--color-surface-container)',
              }}
            >
              <input
                id="search-toggle"
                type="checkbox"
                checked={enableSearch}
                onChange={(e) => setEnableSearch(e.target.checked)}
                disabled={isLoading}
                style={{ marginTop: '0.2rem', cursor: 'pointer' }}
              />
              <label htmlFor="search-toggle" style={{ cursor: 'pointer', fontSize: '0.78rem' }}>
                <div style={{ fontWeight: 600, color: 'var(--color-text)' }}>
                  Web Specification Lookup
                </div>
                <div style={{ color: 'var(--color-text-muted)', fontSize: '0.72rem', marginTop: '0.15rem' }}>
                  If critical wattage or socket specs are omitted from the label, query technical references via SerpAPI.
                </div>
              </label>
            </div>

            {/* Privacy Shield Notice */}
            <div
              style={{
                fontSize: '0.72rem',
                color: 'var(--color-text-muted)',
                display: 'flex',
                alignItems: 'center',
                gap: '0.4rem',
                borderTop: '1px dashed var(--color-border)',
                paddingTop: '0.75rem',
              }}
            >
              <span className="material-symbols-outlined text-[16px] text-pass">shield</span>
              <span>Image stays in RAM • Model runs 100% locally on Ollama</span>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              className="btn btn-primary"
              disabled={!selectedFile || isLoading}
              style={{ width: '100%', padding: '0.75rem' }}
            >
              {isLoading ? (
                <>
                  <span className="pulse-dot pulse-dot-amber" />
                  Analyzing Component...
                </>
              ) : (
                <>
                  <span className="material-symbols-outlined text-[18px]">verified</span>
                  Run RigCheck Analysis
                </>
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};
