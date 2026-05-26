import { describe, expect, it } from "vitest";
import fs from "node:fs";
import path from "node:path";

function collectSourceFiles(dir: string): string[] {
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) return collectSourceFiles(fullPath);
    return /\.(ts|tsx)$/.test(entry.name) ? [fullPath] : [];
  });
}

describe("frontend Supabase key safety", () => {
  it("does not reference the Supabase service role key in apps/web source", () => {
    const forbidden = ["SUPABASE", "SERVICE", "ROLE", "KEY"].join("_");
    const appRoot = path.join(process.cwd());
    const files = collectSourceFiles(appRoot).filter((file) => !file.includes(`${path.sep}__tests__${path.sep}`));
    const offenders = files.filter((file) => fs.readFileSync(file, "utf8").includes(forbidden));

    expect(offenders).toEqual([]);
  });
});
