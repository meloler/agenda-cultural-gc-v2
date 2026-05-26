import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  transpilePackages: ["@agenda-cultural-gc/event-intelligence"],
};

export default nextConfig;