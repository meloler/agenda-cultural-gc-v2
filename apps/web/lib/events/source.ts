export type EventSourceKind = "supabase" | "mock";

export interface EventSourceResult<T> {
  kind: EventSourceKind;
  events: T[];
  warning?: string;
  isFallback?: boolean;
}

export function getPublicSupabaseConfig(env: Partial<NodeJS.ProcessEnv> = process.env):
  | { configured: true; url: string; anonKey: string }
  | { configured: false } {
  const url = env.NEXT_PUBLIC_SUPABASE_URL?.trim();
  const anonKey = env.NEXT_PUBLIC_SUPABASE_ANON_KEY?.trim();

  if (!url || !anonKey) return { configured: false };

  return { configured: true, url, anonKey };
}
