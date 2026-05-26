/**
 * Conceptual types for V1 registered-user preferences.
 *
 * NOT connected to production, Supabase or any auth provider.
 * NOT used by any V0 component or page.
 * Defines the future data contract only — see docs/plans/active/user-personalization-v1.md.
 *
 * Do not activate, import from UI pages or connect to auth until:
 * - docs/checklists/auth-readiness.md is complete.
 * - docs/checklists/personalization-readiness.md is complete.
 * - RLS, migrations and privacy review are done.
 */

// --- Explicit preference types (V1) ---

export type BudgetPreference = "free" | "low" | "any";

export type InterestSource = "explicit"; // V1 only. V2 adds "inferred" with consent.

export type EventFeedbackValue = "like" | "not_interested"; // V1. V2 adds "dislike".

// --- Conceptual entity shapes (V1) ---

/** Stored explicit preferences collected during onboarding. */
export interface UserProfile {
  user_id: string;
  display_name?: string;
  preferred_municipality?: string;
  budget_preference?: BudgetPreference;
  has_children_plan_interest?: boolean;
  created_at: string;
  updated_at: string;
}

/** Explicit cultural interest tag with user-assigned weight. */
export interface UserInterest {
  user_id: string;
  tag: string;
  weight: number; // 1–5
  source: InterestSource;
  created_at: string;
}

/** Event saved by the user for later. */
export interface SavedEvent {
  user_id: string;
  event_id: string;
  created_at: string;
}

/** User's explicit feedback on a single event. */
export interface EventFeedback {
  user_id: string;
  event_id: string;
  feedback: EventFeedbackValue;
  created_at: string;
}

/**
 * Consent record per user.
 * behavioral_personalization_enabled defaults to false and requires V2 activation.
 */
export interface PersonalizationConsent {
  user_id: string;
  explicit_preferences_enabled: boolean;
  behavioral_personalization_enabled: false; // Always false in V1.
  analytics_enabled: boolean;
  consent_version: string;
  updated_at: string;
}
