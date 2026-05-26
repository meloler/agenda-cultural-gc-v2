export interface EventCandidate {
  id: string;
  title?: string | null;
  description?: string | null;
  starts_at?: string | null;
  ends_at?: string | null;
  venue_name?: string | null;
  municipality?: string | null;
  address?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  category?: string | null;
  tags?: string[] | null;
  price?: number | null;
  is_free?: boolean | null;
  image_url?: string | null;
  source_name?: string | null;
  source_url?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
}

export interface EventIntelligenceContext {
  now: string | Date;
  userLatitude?: number;
  userLongitude?: number;
  preferredTags?: string[];
  preferredMunicipality?: string;
}

export type CollectionId =
  | "top-today"
  | "weekend"
  | "free-or-cheap"
  | "family"
  | "live-music"
  | "stage"
  | "markets-fairs"
  | "hidden-gems";

export interface CollectionAssignment {
  id: CollectionId;
  title: string;
  reason: string;
}

export interface ScoreResult {
  score: number;
  positive: string[];
  negative: string[];
}

export interface RankingExplanation {
  score: number;
  reasons: string[];
  issues: string[];
  collections: CollectionAssignment[];
}
