import React, { useState } from 'react';
import type { UserProfile } from '../types';
import { saveProfile, ApiError } from '../services/api';

interface ProfileViewProps {
  initialProfile: UserProfile | null;
  onProfileUpdated: (updated: UserProfile) => void;
  onNavigateToScanner: () => void;
}

export const ProfileView: React.FC<ProfileViewProps> = ({
  initialProfile,
  onProfileUpdated,
  onNavigateToScanner,
}) => {
  const [profile, setProfile] = useState<UserProfile>(() => (
    initialProfile || {
      profile_name: 'My PC Rig',
      existing_components: {},
      intended_upgrade: {},
      compatibility_requirements: {},
      max_budget_idr: null,
    }
  ));

  const [budgetDisplay, setBudgetDisplay] = useState<string>(() => (
    initialProfile?.max_budget_idr ? initialProfile.max_budget_idr.toString() : ''
  ));
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [statusMessage, setStatusMessage] = useState<{ text: string; isError: boolean } | null>(null);

  const handleExistingChange = (field: string, value: any) => {
    setProfile((prev) => ({
      ...prev,
      existing_components: {
        ...prev.existing_components,
        [field]: value,
      },
    }));
  };

  const handleUpgradeChange = (field: string, value: any) => {
    setProfile((prev) => ({
      ...prev,
      intended_upgrade: {
        ...(prev.intended_upgrade || {}),
        [field]: value,
      },
    }));
  };

  const handleRequirementsChange = (field: string, value: any) => {
    setProfile((prev) => ({
      ...prev,
      compatibility_requirements: {
        ...(prev.compatibility_requirements || {}),
        [field]: value,
      },
    }));
  };

  const handleBudgetChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const raw = e.target.value.replace(/\D/g, '');
    setBudgetDisplay(raw);
    const num = raw ? parseInt(raw, 10) : null;
    setProfile((prev) => ({ ...prev, max_budget_idr: num }));
  };

  const formatIdrDisplay = (value: string): string => {
    if (!value) return '';
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      maximumFractionDigits: 0,
    }).format(Number(value));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    setStatusMessage(null);

    try {
      const saved = await saveProfile(profile);
      onProfileUpdated(saved);
      setStatusMessage({ text: 'PC configuration profile saved successfully!', isError: false });
    } catch (err: any) {
      if (err instanceof ApiError) {
        setStatusMessage({ text: `Failed to save (${err.statusCode}): ${err.detail}`, isError: true });
      } else {
        setStatusMessage({ text: err.message || 'Error saving profile', isError: true });
      }
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="profile-container">
      {/* Header Banner */}
      <div className="welcome-banner">
        <div className="welcome-info">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span className="badge badge-neutral">Profile Builder</span>
            <span style={{ fontSize: '0.78rem', color: 'var(--color-text-muted)' }}>
              Source of Truth for Compatibility Checks
            </span>
          </div>
          <h1 className="banner-tagline">Configure Your Existing PC Rig</h1>
          <p className="banner-desc">
            RigCheck compares scanned hardware labels against your components here. Keep your PSU wattage, motherboard socket, and budget up to date.
          </p>
        </div>

        <button onClick={onNavigateToScanner} className="btn btn-primary">
          <span className="material-symbols-outlined text-[18px]">qr_code_scanner</span>
          Open Scanner
        </button>
      </div>

      {/* Status Feedback Notification */}
      {statusMessage && (
        <div
          style={{
            backgroundColor: statusMessage.isError ? 'var(--color-fail-bg)' : 'var(--color-pass-bg)',
            border: `1px solid ${statusMessage.isError ? 'var(--color-fail-border)' : 'var(--color-pass-border)'}`,
            color: statusMessage.isError ? 'var(--color-fail)' : 'var(--color-pass)',
            padding: '0.85rem 1rem',
            borderRadius: 'var(--radius-md)',
            marginBottom: '1.25rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.6rem',
            fontSize: '0.88rem',
            fontWeight: 500,
          }}
        >
          <span className="material-symbols-outlined text-[20px]">
            {statusMessage.isError ? 'error' : 'check_circle'}
          </span>
          <span>{statusMessage.text}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        {/* Profile Name & Budget */}
        <div className="drafting-card">
          <h2 style={{ fontSize: '1.1rem', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <span className="material-symbols-outlined text-[18px] text-primary">badge</span>
            Rig Identity & Budget
          </h2>

          <div className="profile-form-grid">
            <div className="form-group">
              <label className="form-label" htmlFor="profile-name">
                Profile Name
              </label>
              <input
                id="profile-name"
                type="text"
                className="form-input"
                placeholder="e.g. My Battle Station"
                value={profile.profile_name}
                onChange={(e) => setProfile({ ...profile, profile_name: e.target.value })}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="max-budget">
                <span>Maximum Upgrade Budget</span>
                <span style={{ fontSize: '0.7rem', color: 'var(--color-text-subtle)' }}>IDR</span>
              </label>
              <input
                id="max-budget"
                type="text"
                className="form-input"
                placeholder="e.g. 10000000"
                value={budgetDisplay}
                onChange={handleBudgetChange}
              />
              {budgetDisplay && (
                <div style={{ fontSize: '0.75rem', color: 'var(--color-primary)', fontWeight: 600 }}>
                  {formatIdrDisplay(budgetDisplay)}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Existing Components */}
        <div className="drafting-card">
          <h2 style={{ fontSize: '1.1rem', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <span className="material-symbols-outlined text-[18px] text-primary">memory</span>
            Existing Components
          </h2>

          <div className="profile-form-grid">
            <div className="form-group">
              <label className="form-label" htmlFor="cpu">CPU Model</label>
              <input
                id="cpu"
                type="text"
                className="form-input"
                placeholder="e.g. AMD Ryzen 5 5600X"
                value={profile.existing_components.cpu || ''}
                onChange={(e) => handleExistingChange('cpu', e.target.value || null)}
              />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="gpu">Current GPU</label>
              <input
                id="gpu"
                type="text"
                className="form-input"
                placeholder="e.g. NVIDIA GTX 1660 Super"
                value={profile.existing_components.gpu || ''}
                onChange={(e) => handleExistingChange('gpu', e.target.value || null)}
              />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="motherboard">Motherboard</label>
              <input
                id="motherboard"
                type="text"
                className="form-input"
                placeholder="e.g. Gigabyte B550M DS3H"
                value={profile.existing_components.motherboard || ''}
                onChange={(e) => handleExistingChange('motherboard', e.target.value || null)}
              />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="psu-wattage">
                <span>PSU Wattage</span>
                <span style={{ fontSize: '0.7rem', color: 'var(--color-text-subtle)' }}>Watts (W)</span>
              </label>
              <input
                id="psu-wattage"
                type="number"
                className="form-input"
                placeholder="e.g. 550"
                min="0"
                max="2500"
                value={profile.existing_components.psu_wattage ?? ''}
                onChange={(e) =>
                  handleExistingChange(
                    'psu_wattage',
                    e.target.value ? parseInt(e.target.value, 10) : null
                  )
                }
              />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="psu-model">PSU Model & Rating</label>
              <input
                id="psu-model"
                type="text"
                className="form-input"
                placeholder="e.g. Corsair CV550 80+ Bronze"
                value={profile.existing_components.psu_model || ''}
                onChange={(e) => handleExistingChange('psu_model', e.target.value || null)}
              />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="form-factor">Case Form Factor</label>
              <select
                id="form-factor"
                className="form-select"
                value={profile.existing_components.form_factor || ''}
                onChange={(e) => handleExistingChange('form_factor', e.target.value || null)}
              >
                <option value="">Select or Unspecified</option>
                <option value="ATX">Standard ATX</option>
                <option value="Micro-ATX">Micro-ATX (mATX)</option>
                <option value="Mini-ITX">Mini-ITX (SFF)</option>
                <option value="E-ATX">Extended ATX (E-ATX)</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="ram">RAM Details</label>
              <input
                id="ram"
                type="text"
                className="form-input"
                placeholder="e.g. 16GB DDR4 3200MHz"
                value={profile.existing_components.ram || ''}
                onChange={(e) => handleExistingChange('ram', e.target.value || null)}
              />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="case-model">PC Case Enclosure</label>
              <input
                id="case-model"
                type="text"
                className="form-input"
                placeholder="e.g. Deepcool CC560"
                value={profile.existing_components.case_model || ''}
                onChange={(e) => handleExistingChange('case_model', e.target.value || null)}
              />
            </div>
          </div>
        </div>

        {/* Intended Upgrade & Constraints */}
        <div className="drafting-card">
          <h2 style={{ fontSize: '1.1rem', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <span className="material-symbols-outlined text-[18px] text-primary">upgrade</span>
            Intended Upgrade & Specific Requirements
          </h2>

          <div className="profile-form-grid">
            <div className="form-group">
              <label className="form-label" htmlFor="target-category">Target Component Category</label>
              <select
                id="target-category"
                className="form-select"
                value={profile.intended_upgrade?.target_category || ''}
                onChange={(e) => handleUpgradeChange('target_category', e.target.value || null)}
              >
                <option value="">Select Category</option>
                <option value="GPU">Graphics Card (GPU)</option>
                <option value="CPU">Processor (CPU)</option>
                <option value="Motherboard">Motherboard</option>
                <option value="RAM">Memory (RAM)</option>
                <option value="PSU">Power Supply (PSU)</option>
                <option value="Storage">Storage (SSD/NVMe)</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="target-model">Desired Component Model</label>
              <input
                id="target-model"
                type="text"
                className="form-input"
                placeholder="e.g. RTX 4070 or RX 7800 XT"
                value={profile.intended_upgrade?.target_model || ''}
                onChange={(e) => handleUpgradeChange('target_model', e.target.value || null)}
              />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="socket-req">Motherboard Socket Requirement</label>
              <input
                id="socket-req"
                type="text"
                className="form-input"
                placeholder="e.g. AM4, AM5, LGA1700"
                value={profile.compatibility_requirements?.socket || ''}
                onChange={(e) => handleRequirementsChange('socket', e.target.value || null)}
              />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="min-psu">Minimum Desired PSU (Watts)</label>
              <input
                id="min-psu"
                type="number"
                className="form-input"
                placeholder="e.g. 650"
                value={profile.compatibility_requirements?.min_psu_wattage ?? ''}
                onChange={(e) =>
                  handleRequirementsChange(
                    'min_psu_wattage',
                    e.target.value ? parseInt(e.target.value, 10) : null
                  )
                }
              />
            </div>
          </div>
        </div>

        {/* Action Controls */}
        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '0.5rem' }}>
          <button
            type="submit"
            className="btn btn-primary"
            disabled={isSaving}
            style={{ padding: '0.75rem 1.75rem' }}
          >
            {isSaving ? (
              <>
                <span className="pulse-dot pulse-dot-amber" />
                Saving Profile...
              </>
            ) : (
              <>
                <span className="material-symbols-outlined text-[18px]">save</span>
                Save PC Profile
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};
