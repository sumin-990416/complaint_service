/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ['class'],
  content: [
    './index.html',
    './src/**/*.{vue,js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        background: '#F2F4F8',
        surface:    '#FFFFFF',
        foreground: '#0F172A',
        primary: {
          DEFAULT: '#3B6EF8',
          foreground: '#FFFFFF',
          light: '#EEF2FF',
        },
        border:  '#E2E8F0',
        input:   '#F8FAFC',
        muted: {
          DEFAULT:    '#F1F5F9',
          foreground: '#64748B',
        },
        night:   '#EDE9FE',
        weekend: '#DCFCE7',
      },
      borderRadius: {
        xl2: '20px',
        lg:  '14px',
        md:  '10px',
        sm:  '6px',
      },
      boxShadow: {
        card:   '0 2px 12px 0 rgba(15,23,42,0.07)',
        'card-hover': '0 6px 24px 0 rgba(15,23,42,0.13)',
      },
    },
  },
  plugins: [],
}


