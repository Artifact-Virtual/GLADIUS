/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#0A0E27',
        secondary: '#1A1F3A',
        accent: '#00D9FF',
        'accent-purple': '#9D4EDD',
        success: '#00FF87',
        warning: '#FFB800',
        error: '#FF3366',
        text: '#E8E9ED',
        'text-dim': '#9CA3AF',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['Fira Code', 'Courier New', 'monospace'],
      },
    },
  },
  plugins: [],
}
