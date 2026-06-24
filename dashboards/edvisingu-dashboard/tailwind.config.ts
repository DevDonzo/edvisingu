import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        surface: { DEFAULT: "#18181b", elevated: "#111113" },
        accent: { DEFAULT: "#f59e0b", dim: "rgba(245,158,11,0.08)" },
      },
      fontFamily: {
        sans: ["Geist", "SF Pro Display", "-apple-system", "system-ui", "sans-serif"],
        mono: ["Geist Mono", "SF Mono", "monospace"],
      },
    },
  },
  plugins: [],
};

export default config;
