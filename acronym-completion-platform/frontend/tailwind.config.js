/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      backgroundColor: {
        'glass': 'rgba(255, 255, 255, 0.25)',
        'glass-dark': 'rgba(17, 25, 40, 0.75)',
        'glass-light': 'rgba(255, 255, 255, 0.4)',
        'glass-light-dark': 'rgba(17, 25, 40, 0.4)',
      },
      borderColor: {
        'glass-border': 'rgba(255, 255, 255, 0.18)',
        'glass-border-dark': 'rgba(255, 255, 255, 0.125)',
      },
      backdropBlur: {
        'xs': '2px',
      },
      boxShadow: {
        'glass': '0 8px 32px 0 rgba(31, 38, 135, 0.37)',
      },
      borderWidth: {
        'glass': '1px',
      },
      opacity: {
        '15': '0.15',
        '35': '0.35',
        '65': '0.65',
        '85': '0.85',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
  safelist: [
    {
      pattern: /^bg-.*\/\d+$/,
      variants: ['hover', 'focus', 'active'],
    },
  ],
  future: {
    hoverOnlyWhenSupported: true,
  },
  corePlugins: {
    backgroundOpacity: true,
    textOpacity: true,
    borderOpacity: true,
  },
} 