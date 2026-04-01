/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        display: ['"Zen Old Mincho"', 'serif'],
      },
      colors: {
        border: "hsl(var(--border))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        gold: "hsl(var(--gold))",
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        deepCrimson: {
          DEFAULT: "hsl(var(--deep-crimson))",
          foreground: "hsl(var(--deep-crimson-foreground))",
        },
        primary: {
          DEFAULT: "hsl(346 87% 43%)", 
          foreground: "hsl(60 9% 98%)",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
      }
    },
  },
  plugins: [],
}