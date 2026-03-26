import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        ink: "#0f172a",
        mist: "#e2e8f0",
        ember: "#c2410c",
        pine: "#14532d",
        paper: "#f8fafc"
      }
    }
  },
  plugins: []
};

export default config;

