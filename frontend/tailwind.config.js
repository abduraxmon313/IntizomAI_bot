/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './main.jsx',
    './App.jsx',
    './components/**/*.{js,jsx}',
    './services/**/*.{js,jsx}',
    './store/**/*.{js,jsx}',
  ],
  theme: {
    extend: {},
  },
  darkMode: 'class',
  plugins: [],
};
