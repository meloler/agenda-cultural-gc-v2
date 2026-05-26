import { describe, expect, it, vi } from "vitest";

describe("Supabase fallback messaging", () => {
  it("does not silently hide missing Supabase config in production", async () => {
    vi.resetModules();
    const originalEnv = process.env.NODE_ENV;
    vi.stubEnv("NODE_ENV", "production");

    const { fetchSupabaseEvents } = await import("../supabase");
    const result = await fetchSupabaseEvents(new Date("2026-06-12T10:00:00.000Z"));

    expect(result.kind).toBe("mock");
    expect(result.isFallback).toBe(true);
    expect(result.warning).toContain("no se cargan eventos reales");

    vi.stubEnv("NODE_ENV", originalEnv);
    vi.unstubAllEnvs();
  });
});
