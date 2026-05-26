import { describe, expect, it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { SafeExternalLink, isSafeExternalUrl } from "../SafeExternalLink";

describe("SafeExternalLink", () => {
  it("rejects unsafe javascript URLs", () => {
    expect(isSafeExternalUrl("javascript:alert(1)")).toBe(false);
    expect(renderToStaticMarkup(<SafeExternalLink href="javascript:alert(1)">Ir</SafeExternalLink>)).toBe("");
  });

  it("uses target blank and noopener noreferrer for safe URLs", () => {
    const html = renderToStaticMarkup(<SafeExternalLink href="https://example.com/evento">Ver información oficial</SafeExternalLink>);

    expect(html).toContain('target="_blank"');
    expect(html).toContain('rel="noopener noreferrer"');
    expect(html).toContain('href="https://example.com/evento"');
  });
});
