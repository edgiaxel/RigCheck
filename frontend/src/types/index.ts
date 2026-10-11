export interface ExistingComponents {
  cpu?: string | null;
  gpu?: string | null;
  motherboard?: string | null;
  ram?: string | null;
  psu_wattage?: number | null;
  psu_model?: string | null;
  case_model?: string | null;
  form_factor?: string | null;
  additional_notes?: string | null;
}

export interface IntendedUpgrade {
  target_category?: string | null;
  target_model?: string | null;
  notes?: string | null;
}

export interface CompatibilityRequirements {
  min_psu_wattage?: number | null;
  preferred_form_factor?: string | null;
  socket?: string | null;
  pcie_slot?: string | null;
  max_gpu_length_mm?: number | null;
}

export interface UserProfile {
  profile_name: string;
  existing_components: ExistingComponents;
  intended_upgrade?: IntendedUpgrade | null;
  compatibility_requirements?: CompatibilityRequirements | null;
  max_budget_idr?: number | null;
  updated_at?: string | null;
}

export interface ExtractedSpecifications {
  category?: string | null;
  brand?: string | null;
  model?: string | null;
  series_or_chipset?: string | null;
  power_tdp_watts?: number | null;
  recommended_psu_watts?: number | null;
  socket?: string | null;
  form_factor?: string | null;
  memory_spec?: string | null;
  interface_or_slot?: string | null;
  dimensions_or_clearance?: string | null;
  power_connectors?: string | null;
  other_visible_specs?: Record<string, string>;
}

export interface VisionExtractionEvidence {
  visible_labels: string[];
  part_or_model_number?: string | null;
  confidence_notes?: string | null;
}

export interface SearchEnrichment {
  performed: boolean;
  query?: string | null;
  sources: string[];
  resolved_fields: string[];
  search_summary?: string | null;
}

export type CheckStatus = 'PASS' | 'FAIL' | 'WARN' | 'UNKNOWN' | 'NOT_APPLICABLE';

export interface CompatibilityCheckItem {
  check_name: string;
  status: CheckStatus;
  message: string;
  details: Record<string, any>;
}

export type OverallCompatibilityStatus = 'COMPATIBLE' | 'INCOMPATIBLE' | 'WARNING' | 'NEEDS_INFO';

export interface CompatibilityReport {
  overall_status: OverallCompatibilityStatus;
  summary: string;
  checks: CompatibilityCheckItem[];
  price_check?: {
    entered_price_idr?: number | null;
    max_budget_idr?: number | null;
    difference_idr?: number | null;
    within_budget?: boolean;
  } | null;
  recommendations: string[];
}

export type PreliminaryAnalysisStatus = 'EXTRACTED' | 'PARTIALLY_IDENTIFIED' | 'UNCERTAIN' | 'INSUFFICIENT_DATA';

export interface AnalysisResponse {
  preliminary_status: PreliminaryAnalysisStatus;
  extracted_specifications: ExtractedSpecifications;
  evidence: VisionExtractionEvidence;
  unresolved_fields: string[];
  search_enrichment?: SearchEnrichment | null;
  compatibility_report: CompatibilityReport;
  user_price_idr?: number | null;
  analyzed_at: string;
}

export interface BackendHealth {
  status: string;
  service: string;
  version: string;
  ollama: {
    available: boolean;
    model_present: boolean;
    configured_model: string;
    installed_models: string[];
  };
  search_service: {
    enabled: boolean;
    configured: boolean;
  };
  storage: {
    path: string;
    profile_loaded: boolean;
  };
}

// Visual mapped verdict status for RigCheck UI
export type DisplayVerdict = 'Compatible' | 'Incompatible' | 'Needs verification';

export function mapToDisplayVerdict(status: OverallCompatibilityStatus): DisplayVerdict {
  if (status === 'COMPATIBLE') return 'Compatible';
  if (status === 'INCOMPATIBLE') return 'Incompatible';
  return 'Needs verification'; // WARNING and NEEDS_INFO map cleanly to 'Needs verification'
}
