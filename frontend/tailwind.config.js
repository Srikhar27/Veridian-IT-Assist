/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      colors: {
        dark: {
          950: '#070A11',
          900: '#0B0F19',
          850: '#101626',
          800: '#161F36',
          750: '#1E2945',
          700: '#263454',
          600: '#33446B',
        },
        accent: {
          blue: '#3B82F6',
          cyan: '#38BDF8',
          emerald: '#10B981',
          amber: '#F59E0B',
          red: '#EF4444',
          purple: '#8B5CF6',
        }
      }
    },
  },
  plugins: [],
}
