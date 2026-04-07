import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        "secondary-fixed": "#ffdeac",
        "on-secondary": "#432c00",
        "secondary": "#ffd799",
        "surface-dim": "#131313",
        "tertiary-fixed-dim": "#ffb4a2",
        "on-tertiary-container": "#b82a00",
        "on-error-container": "#ffdad6",
        "outline": "#84967e",
        "secondary-container": "#feb300",
        "on-tertiary-fixed": "#3c0700",
        "on-error": "#690005",
        "on-primary": "#003907",
        "error-container": "#93000a",
        "surface": "#131313",
        "outline-variant": "#3b4b37",
        "on-secondary-fixed-variant": "#604100",
        "on-surface": "#e5e2e1",
        "surface-bright": "#3a3939",
        "on-secondary-fixed": "#281900",
        "surface-container-low": "#1c1b1b",
        "primary": "#ebffe2",
        "inverse-on-surface": "#313030",
        "primary-container": "#00ff41",
        "on-surface-variant": "#b9ccb2",
        "surface-container-lowest": "#0e0e0e",
        "secondary-fixed-dim": "#ffba38",
        "on-primary-fixed": "#002203",
        "on-primary-container": "#007117",
        "surface-container-high": "#2a2a2a",
        "on-primary-fixed-variant": "#00530e",
        "background": "#131313",
        "tertiary-fixed": "#ffdad2",
        "inverse-primary": "#006e16",
        "tertiary-container": "#ffd3c8",
        "inverse-surface": "#e5e2e1",
        "tertiary": "#fff8f6",
        "on-secondary-container": "#6a4800",
        "surface-container-highest": "#353534",
        "primary-fixed": "#72ff70",
        "surface-variant": "#353534",
        "on-tertiary-fixed-variant": "#8a1d00",
        "on-tertiary": "#621100",
        "error": "#ffb4ab",
        "primary-fixed-dim": "#00e639",
        "on-background": "#e5e2e1",
        "surface-tint": "#00e639",
        "surface-container": "#201f1f"
      },
      borderRadius: {
        "DEFAULT": "0.25rem",
        "lg": "0.5rem",
        "xl": "0.75rem",
        "full": "9999px"
      },
      fontFamily: {
        "headline": ["Space Grotesk"],
        "body": ["Space Grotesk"],
        "label": ["Space Grotesk"]
      }
    },
  },
  plugins: [],
};
export default config;
