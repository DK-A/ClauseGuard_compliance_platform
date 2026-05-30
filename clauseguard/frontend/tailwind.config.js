/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        "primary": "#2563eb", /* Primary Cobalt */
        "primary-accent": "#b4c5ff",
        "on-primary": "#ffffff",
        "primary-container": "#2563eb",
        "on-primary-container": "#eeefff",
        "surface": "#121317",
        "surface-dim": "#121317",
        "surface-bright": "#38393e",
        "surface-container-lowest": "#0d0e12",
        "surface-container-low": "#1a1b20",
        "surface-container": "#1f1f24",
        "surface-container-high": "#292a2e",
        "surface-container-highest": "#343439",
        "on-surface": "#e3e2e8",
        "on-surface-variant": "#c3c6d7",
        "outline": "#8d90a0",
        "outline-variant": "#434655",
        "background": "#0b0c10",
        "on-background": "#e3e2e8",
        "tertiary": "#ffb596",
        "tertiary-container": "#bc4800",
        "error": "#ffb4ab",
        "error-container": "#93000a"
      },
      fontFamily: {
        headline: ["IBM Plex Mono", "monospace"],
        body: ["Inter", "sans-serif"],
      },
      borderRadius: {
        sm: "0.25rem",
        DEFAULT: "0.5rem",
        md: "0.75rem",
        lg: "1rem",
        xl: "1.5rem",
        full: "9999px"
      }
    },
  },
  plugins: [],
}
