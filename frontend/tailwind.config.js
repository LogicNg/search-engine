/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        'sf': ['SF Pro', 'sans-serif'], // Add SF Pro as the default sans-serif font
      },
    },
  },
  plugins: [],
}
