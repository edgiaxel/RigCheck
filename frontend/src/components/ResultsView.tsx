import {
  mapToDisplayVerdict,
  type AnalysisResponse,
  type CheckStatus,
  type DisplayVerdict,
  type UserProfile,
} from '../types';

interface ResultsViewProps {
  analysis: AnalysisResponse;
  profile: UserProfile | null;
  onScanAnother: () => void;
  onEditProfile: () => void;
}

export const ResultsView: React.FC<ResultsViewProps> = ({
  analysis,
  profile,
  onScanAnother,
  onEditProfile,
}) => {
  const displayVerdict: DisplayVerdict = mapToDisplayVerdict(
    analysis.compatibility_report.overall_status
  );

  const getVerdictThemeClass = (verdict: DisplayVerdict): string => {
    switch (verdict) {
      case 'Compatible':
        return 'verdict-compatible';
      case 'Incompatible':
        return 'verdict-incompatible';
      case 'Needs verification':
      default:
        return 'verdict-needs-verification';
    }
  };

  const getVerdictIcon = (verdict: DisplayVerdict): string => {
    switch (verdict) {
      case 'Compatible':
        return 'check_circle';
      case 'Incompatible':
        return 'cancel';
      case 'Needs verification':
      default:
        return 'help';
    }
  };

  const getCheckStatusBadge = (status: CheckStatus) => {
    switch (status) {
      case 'PASS':
        return <span className="badge badge-pass">PASS</span>;
      case 'FAIL':
        return <span className="badge badge-fail">FAIL</span>;
      case 'WARN':
        return <span className="badge badge-warn">WARNING</span>;
      case 'UNKNOWN':
        return <span className="badge badge-unknown">UNKNOWN</span>;
      case 'NOT_APPLICABLE':
      default:
        return <span className="badge badge-neutral">N/A</span>;
    }
  };

  const specs = analysis.extracted_specifications;
  const evidence = analysis.evidence;
  const unresolved = analysis.unresolved_fields;
  const checks = analysis.compatibility_report.checks;
  const search = analysis.search_enrichment;

  // Format IDR Currency
  const formatIdr = (amount: number | null | undefined): string => {
    if (amount === null || amount === undefined) return 'None';
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      maximumFractionDigits: 0,
    }).format(amount);
  };

  return (
    <div className="results-container">
      {/* Top Action Bar */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '1rem',
          flexWrap: 'wrap',
          gap: '0.5rem',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span className="material-symbols-outlined text-[20px] text-primary">assessment</span>
          <span style={{ fontWeight: 600, fontSize: '0.95rem' }}>Inspection Audit Report</span>
          <span className="badge badge-neutral">
            {new Date(analysis.analyzed_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </span>
        </div>

        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button onClick={onScanAnother} className="btn btn-secondary">
            <span className="material-symbols-outlined text-[16px]">add_a_photo</span>
            Scan Another
          </button>
          <button onClick={onEditProfile} className="btn btn-secondary">
            <span className="material-symbols-outlined text-[16px]">tune</span>
            Profile
          </button>
        </div>
      </div>

      {/* Primary Verdict Hero Card */}
      <div className={`verdict-hero-card ${getVerdictThemeClass(displayVerdict)}`}>
        <div className="verdict-title-row">
          <div className="verdict-status-heading">
            <span className="material-symbols-outlined text-[32px]">
              {getVerdictIcon(displayVerdict)}
            </span>
            <span>{displayVerdict}</span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
            <span className="badge badge-neutral">Status: {analysis.preliminary_status}</span>
            {specs.category && <span className="badge badge-neutral">{specs.category}</span>}
          </div>
        </div>

        {/* Component Title */}
        <div style={{ fontSize: '1.25rem', fontWeight: 700, letterSpacing: '-0.02em', color: 'var(--color-text)' }}>
          {[specs.brand, specs.model].filter(Boolean).join(' ') || 'Unidentified Hardware Component'}
          {specs.series_or_chipset && (
            <span style={{ fontSize: '0.95rem', fontWeight: 500, color: 'var(--color-text-muted)', marginLeft: '0.5rem' }}>
              ({specs.series_or_chipset})
            </span>
          )}
        </div>

        {/* High-level summary from engine */}
        <p style={{ fontSize: '0.9rem', lineHeight: 1.5, color: 'var(--color-text)' }}>
          {analysis.compatibility_report.summary}
        </p>

        {/* Target rig reference */}
        {profile && (
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.75rem',
              fontSize: '0.78rem',
              color: 'var(--color-text-muted)',
              borderTop: '1px solid rgba(0,0,0,0.06)',
              paddingTop: '0.5rem',
              flexWrap: 'wrap',
            }}
          >
            <span>Target Rig: <strong>{profile.profile_name || 'My PC Rig'}</strong></span>
            <span>•</span>
            <span>
              Configured PSU: <strong>{profile.existing_components?.psu_wattage ? `${profile.existing_components.psu_wattage}W` : 'Not Set'}</strong>
            </span>
            {profile.max_budget_idr && (
              <>
                <span>•</span>
                <span>Max Budget: <strong>{formatIdr(profile.max_budget_idr)}</strong></span>
              </>
            )}
          </div>
        )}
      </div>

      {/* Main Results Grid */}
      <div className="results-grid">
        {/* Left Column: Compatibility Checks & Recommendations */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          {/* Individual Checks Card */}
          <div className="drafting-card">
            <h2 style={{ fontSize: '1.05rem', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <span className="material-symbols-outlined text-[18px] text-primary">rule</span>
              Compatibility Rule Verifications
            </h2>

            {checks && checks.length > 0 ? (
              <div>
                {checks.map((chk, index) => (
                  <div key={index} className="check-card">
                    <div className="check-card-header">
                      <span className="check-card-name">{chk.check_name}</span>
                      {getCheckStatusBadge(chk.status)}
                    </div>
                    <p className="check-card-msg">{chk.message}</p>

                    {/* Check structured details if available */}
                    {chk.details && Object.keys(chk.details).length > 0 && (
                      <div
                        style={{
                          backgroundColor: 'var(--color-surface-container)',
                          padding: '0.4rem 0.6rem',
                          borderRadius: 'var(--radius-sm)',
                          fontSize: '0.75rem',
                          display: 'flex',
                          flexWrap: 'wrap',
                          gap: '0.6rem',
                        }}
                      >
                        {Object.entries(chk.details).map(([key, val]) => (
                          <span key={key} style={{ color: 'var(--color-text-muted)' }}>
                            <strong style={{ color: 'var(--color-text)' }}>{key.replace(/_/g, ' ')}:</strong>{' '}
                            {val === null || val === undefined ? 'Unknown' : String(val)}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p style={{ color: 'var(--color-text-muted)', fontSize: '0.85rem' }}>
                No verifiable rules could be evaluated with the current extracted parameters.
              </p>
            )}
          </div>

          {/* Actionable Recommendations */}
          {analysis.compatibility_report.recommendations &&
            analysis.compatibility_report.recommendations.length > 0 && (
              <div className="drafting-card">
                <h2 style={{ fontSize: '1.05rem', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                  <span className="material-symbols-outlined text-[18px] text-tertiary">lightbulb</span>
                  Technical Recommendations
                </h2>
                <ul style={{ paddingLeft: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.4rem', fontSize: '0.85rem' }}>
                  {analysis.compatibility_report.recommendations.map((rec, i) => (
                    <li key={i} style={{ color: 'var(--color-text)' }}>
                      {rec}
                    </li>
                  ))}
                </ul>
              </div>
            )}

          {/* Budget Breakdown Card */}
          {(analysis.user_price_idr || profile?.max_budget_idr) && (
            <div className="drafting-card">
              <h2 style={{ fontSize: '1.05rem', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <span className="material-symbols-outlined text-[18px] text-primary">payments</span>
                Budget Evaluation (IDR)
              </h2>
              <div className="spec-list">
                <div className="spec-row">
                  <span className="spec-key">Observed Component Price</span>
                  <span className="spec-val">{formatIdr(analysis.user_price_idr)}</span>
                </div>
                <div className="spec-row">
                  <span className="spec-key">Configured Maximum Budget</span>
                  <span className="spec-val">{formatIdr(profile?.max_budget_idr)}</span>
                </div>
                {analysis.compatibility_report.price_check?.difference_idr != null && (
                  <div className="spec-row">
                    <span className="spec-key">Variance</span>
                    <span
                      className="spec-val"
                      style={{
                        color:
                          analysis.compatibility_report.price_check.difference_idr >= 0
                            ? 'var(--color-pass)'
                            : 'var(--color-fail)',
                      }}
                    >
                      {analysis.compatibility_report.price_check.difference_idr >= 0 ? '+' : ''}
                      {formatIdr(analysis.compatibility_report.price_check.difference_idr)}
                    </span>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Right Column: Extracted Specs, Unresolved Fields & Evidence */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          {/* Extracted Specifications Card */}
          <div className="drafting-card">
            <h2 style={{ fontSize: '1.05rem', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <span className="material-symbols-outlined text-[18px] text-primary">memory</span>
              Extracted Specifications
            </h2>

            <div className="spec-list">
              <div className="spec-row">
                <span className="spec-key">Category</span>
                <span className="spec-val">{specs.category || 'Unknown'}</span>
              </div>
              <div className="spec-row">
                <span className="spec-key">Brand / Manufacturer</span>
                <span className="spec-val">{specs.brand || 'Unknown'}</span>
              </div>
              <div className="spec-row">
                <span className="spec-key">Model</span>
                <span className="spec-val">{specs.model || 'Unknown'}</span>
              </div>
              {specs.memory_spec && (
                <div className="spec-row">
                  <span className="spec-key">Memory / VRAM</span>
                  <span className="spec-val">{specs.memory_spec}</span>
                </div>
              )}
              <div className="spec-row">
                <span className="spec-key">Rated TDP (Watts)</span>
                <span className="spec-val">
                  {specs.power_tdp_watts !== null ? `${specs.power_tdp_watts}W` : 'Not Specified'}
                </span>
              </div>
              <div className="spec-row">
                <span className="spec-key">Recommended PSU</span>
                <span className="spec-val">
                  {specs.recommended_psu_watts !== null ? `${specs.recommended_psu_watts}W` : 'Not Specified'}
                </span>
              </div>
              {specs.socket && (
                <div className="spec-row">
                  <span className="spec-key">Socket</span>
                  <span className="spec-val">{specs.socket}</span>
                </div>
              )}
              {specs.form_factor && (
                <div className="spec-row">
                  <span className="spec-key">Form Factor</span>
                  <span className="spec-val">{specs.form_factor}</span>
                </div>
              )}
              {specs.power_connectors && (
                <div className="spec-row">
                  <span className="spec-key">Power Connectors</span>
                  <span className="spec-val">{specs.power_connectors}</span>
                </div>
              )}
              {specs.interface_or_slot && (
                <div className="spec-row">
                  <span className="spec-key">Interface / Bus</span>
                  <span className="spec-val">{specs.interface_or_slot}</span>
                </div>
              )}
              {specs.dimensions_or_clearance && (
                <div className="spec-row">
                  <span className="spec-key">Dimensions</span>
                  <span className="spec-val">{specs.dimensions_or_clearance}</span>
                </div>
              )}
            </div>
          </div>

          {/* Preserved Uncertainty: Unresolved Fields */}
          <div className="drafting-card">
            <h2 style={{ fontSize: '1.05rem', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <span className="material-symbols-outlined text-[18px] text-warn">help_outline</span>
              Unresolved & Unknown Specifications
            </h2>

            {unresolved && unresolved.length > 0 ? (
              <div>
                <p style={{ fontSize: '0.78rem', color: 'var(--color-text-muted)', marginBottom: '0.6rem' }}>
                  RigCheck strictly avoids hallucination. The following parameters were absent or illegible on the label:
                </p>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
                  {unresolved.map((field, idx) => (
                    <span key={idx} className="badge badge-warn">
                      {field.replace(/_/g, ' ')}: UNKNOWN
                    </span>
                  ))}
                </div>
              </div>
            ) : (
              <p style={{ fontSize: '0.82rem', color: 'var(--color-pass)' }}>
                All required baseline specifications were resolved with certainty.
              </p>
            )}
          </div>

          {/* Direct Label Evidence & Search Enrichment */}
          <div className="drafting-card">
            <h2 style={{ fontSize: '1.05rem', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <span className="material-symbols-outlined text-[18px] text-primary">visibility</span>
              Label Evidence & Source Attribution
            </h2>

            {evidence.part_or_model_number && (
              <div style={{ marginBottom: '0.6rem' }}>
                <div style={{ fontSize: '0.72rem', color: 'var(--color-text-subtle)', textTransform: 'uppercase' }}>
                  Part / Model / Serial Code
                </div>
                <div style={{ fontWeight: 600, fontSize: '0.85rem' }}>{evidence.part_or_model_number}</div>
              </div>
            )}

            {evidence.visible_labels && evidence.visible_labels.length > 0 && (
              <div style={{ marginBottom: '0.6rem' }}>
                <div style={{ fontSize: '0.72rem', color: 'var(--color-text-subtle)', textTransform: 'uppercase', marginBottom: '0.25rem' }}>
                  Label Markings Read Directly
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem' }}>
                  {evidence.visible_labels.map((lbl, idx) => (
                    <span key={idx} className="badge badge-neutral" style={{ fontSize: '0.7rem' }}>
                      "{lbl}"
                    </span>
                  ))}
                </div>
              </div>
            )}

            {evidence.confidence_notes && (
              <p style={{ fontSize: '0.78rem', color: 'var(--color-text-muted)', fontStyle: 'italic', marginTop: '0.4rem' }}>
                Label observation: {evidence.confidence_notes}
              </p>
            )}

            {/* Search Citations (if search was performed) */}
            {search && search.performed && (
              <div
                style={{
                  marginTop: '0.75rem',
                  paddingTop: '0.75rem',
                  borderTop: '1px dashed var(--color-border)',
                }}
              >
                <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--color-primary)' }}>
                  Web Reference Enrichment
                </div>
                <p style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginTop: '0.2rem' }}>
                  {search.search_summary}
                </p>
                {search.sources && search.sources.length > 0 && (
                  <ul style={{ paddingLeft: '1rem', marginTop: '0.3rem', fontSize: '0.72rem', color: 'var(--color-text-subtle)' }}>
                    {search.sources.map((src, i) => (
                      <li key={i}>{src}</li>
                    ))}
                  </ul>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
