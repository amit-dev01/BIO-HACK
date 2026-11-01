import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./context/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        // Custom CanopyAI Color Palette
        forest: {
          DEFAULT: "#1B5E20",
          50: "#E8F5E9",
          100: "#C8E6C9",
          500: "#2E7D32",
          600: "#1B5E20",
          700: "#144717",
          800: "#0D300F",
        },
        leaf: {
          DEFAULT: "#4CAF50",
          50: "#F1F8E9",
          100: "#DCEDC8",
          400: "#66BB6A",
          500: "#4CAF50",
          600: "#43A047",
        },
        amber: {
          DEFAULT: "#FF8F00",
          50: "#FFF8E1",
          100: "#FFECB3",
          500: "#FF8F00",
          600: "#FF6F00",
        },
        offwhite: "#F5F5F0",
        surface: "#FFFFFF",
        charcoal: "#1A1A1A",
        slate: {
          DEFAULT: "#64748B",
          50: "#F8FAFC",
          100: "#F1F5F9",
          200: "#E2E8F0",
          300: "#CBD5E1",
          400: "#94A3B8",
          500: "#64748B",
          600: "#475569",
          700: "#334155",
          800: "#1E293B",
          900: "#0F172A",
        },
        // Semantic mappings
        primary: {
          DEFAULT: "#1B5E20",
          foreground: "#FFFFFF",
        },
        secondary: {
          DEFAULT: "#4CAF50",
          foreground: "#FFFFFF",
        },
        accent: {
          DEFAULT: "#FF8F00",
          foreground: "#FFFFFF",
        },
        background: "#F5F5F0",
        card: {
          DEFAULT: "#FFFFFF",
          foreground: "#1A1A1A",
        },
        popover: {
          DEFAULT: "#FFFFFF",
          foreground: "#1A1A1A",
        },
        muted: {
          DEFAULT: "#E5E7EB",
          foreground: "#64748B",
        },
        destructive: {
          DEFAULT: "#EF4444",
          foreground: "#FFFFFF",
        },
        border: "#E2E8F0",
        input: "#E2E8F0",
        ring: "#1B5E20",
        text: {
          primary: "#1A1A1A",
          secondary: "#64748B",
        },
      },
      fontFamily: {
        sans: ["var(--font-inter)", "Inter", "sans-serif"],
        inter: ["var(--font-inter)", "Inter", "sans-serif"],
        mono: ["var(--font-jetbrains-mono)", "JetBrains Mono", "monospace"],
      },
      borderRadius: {
        card: "12px", // rounded-xl for cards
        button: "8px", // rounded-lg for buttons
        lg: "8px",
        md: "6px",
        sm: "4px",
        xl: "12px",
        "2xl": "16px",
      },
      spacing: {
        "grid-1": "8px",
        "grid-2": "16px",
        "grid-3": "24px",
        "grid-4": "32px",
        "grid-5": "40px",
        "grid-6": "48px",
        "grid-8": "64px",
        "grid-10": "80px",
        "grid-12": "96px",
        "grid-16": "128px",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};

export default config;

