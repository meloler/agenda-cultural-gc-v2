import type { ReactNode } from "react";

export function isSafeExternalUrl(url: string | null | undefined): boolean {
  if (!url) return false;
  try {
    const parsed = new URL(url);
    return parsed.protocol === "https:" || parsed.protocol === "http:";
  } catch {
    return false;
  }
}

export function SafeExternalLink({ href, children, className }: { href?: string | null; children: ReactNode; className?: string }) {
  if (!isSafeExternalUrl(href)) return null;

  return (
    <a className={className} href={href ?? undefined} target="_blank" rel="noopener noreferrer">
      {children}
    </a>
  );
}
