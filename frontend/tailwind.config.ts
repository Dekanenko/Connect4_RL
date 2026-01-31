import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        background: 'var(--background)',
        foreground: 'var(--foreground)',
        card: 'var(--card)',
        'card-foreground': 'var(--card-foreground)',
        primary: 'var(--primary)',
        'primary-foreground': 'var(--primary-foreground)',
        secondary: 'var(--secondary)',
        'secondary-foreground': 'var(--secondary-foreground)',
        muted: 'var(--muted)',
        'muted-foreground': 'var(--muted-foreground)',
        accent: 'var(--accent)',
        'accent-foreground': 'var(--accent-foreground)',
        destructive: 'var(--destructive)',
        border: 'var(--border)',
        input: 'var(--input)',
        ring: 'var(--ring)',
      },
      fontFamily: {
        sans: ['var(--font-sans)', 'system-ui', 'sans-serif'],
        mono: ['var(--font-mono)', 'ui-monospace', 'monospace'],
      },
      animation: {
        'drop-in': 'drop-in 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) forwards',
        'float-particle': 'float-particle 6s ease-in-out infinite',
        'fade-down': 'fade-down 0.5s ease-out forwards',
        'fade-up': 'fade-up 0.5s ease-out 0.2s both',
        'fade-in': 'fade-in 0.3s ease-out forwards',
        'cursor-float': 'cursor-float 3s ease-in-out infinite',
        'glitch-cyan': 'glitch-cyan 0.15s ease infinite',
        'glitch-rose': 'glitch-rose 0.15s ease infinite 0.05s',
        'scan': 'scan-line 1.5s linear infinite',
        'slide-progress': 'slideProgress 1.5s linear infinite',
        'pulse-glow': 'pulse-glow 2s ease-in-out infinite',
        'glitch-appear': 'glitch-appear 0.4s cubic-bezier(0.23, 1, 0.32, 1) forwards',
      },
      keyframes: {
        'drop-in': {
          '0%': { transform: 'translateY(-300px)', opacity: '0' },
          '60%': { transform: 'translateY(10px)' },
          '80%': { transform: 'translateY(-5px)' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        'float-particle': {
          '0%, 100%': { transform: 'translateY(0)', opacity: '0' },
          '50%': { transform: 'translateY(-100px)', opacity: '0.6' },
        },
        'fade-down': {
          from: { opacity: '0', transform: 'translateY(-20px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
        'fade-up': {
          from: { opacity: '0', transform: 'translateY(20px) scale(0.95)' },
          to: { opacity: '1', transform: 'translateY(0) scale(1)' },
        },
        'fade-in': {
          from: { opacity: '0' },
          to: { opacity: '1' },
        },
        'glitch-cyan': {
          '0%, 100%': { transform: 'translateX(0)', opacity: '0' },
          '10%, 30%': { transform: 'translateX(-2px)', opacity: '0.8' },
          '20%, 40%': { transform: 'translateX(2px)', opacity: '0.8' },
        },
        'glitch-rose': {
          '0%, 100%': { transform: 'translateX(0)', opacity: '0' },
          '10%, 30%': { transform: 'translateX(2px)', opacity: '0.8' },
          '20%, 40%': { transform: 'translateX(-2px)', opacity: '0.8' },
        },
        'scan-line': {
          '0%': { transform: 'translateY(-100%)', opacity: '1' },
          '100%': { transform: 'translateY(100%)', opacity: '1' },
        },
        'cursor-float': {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-5px)' },
        },
        slideProgress: {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(400%)' },
        },
        'pulse-glow': {
          '0%, 100%': { opacity: '0.5', transform: 'scale(1)' },
          '50%': { opacity: '1', transform: 'scale(1.05)' },
        },
        'glitch-appear': {
          '0%': { opacity: '0', transform: 'scale(0.8)', filter: 'blur(8px) hue-rotate(90deg)' },
          '10%': { opacity: '0.5', transform: 'scale(1.1) translateX(-3px)', filter: 'blur(4px) hue-rotate(-45deg)' },
          '20%': { opacity: '0.3', transform: 'scale(0.95) translateX(3px)', filter: 'blur(6px) hue-rotate(45deg)' },
          '30%': { opacity: '0.8', transform: 'scale(1.05) translateY(-2px)', filter: 'blur(2px) hue-rotate(-20deg)' },
          '40%': { opacity: '0.6', transform: 'scale(0.98) translateY(2px) translateX(-2px)', filter: 'blur(3px) hue-rotate(30deg)' },
          '50%': { opacity: '0.9', transform: 'scale(1.02)', filter: 'blur(1px) hue-rotate(-10deg)' },
          '60%': { opacity: '1', transform: 'scale(0.99) translateX(1px)', filter: 'blur(0.5px) hue-rotate(5deg)' },
          '70%': { opacity: '1', transform: 'scale(1.01) translateX(-1px)', filter: 'blur(0)' },
          '80%, 100%': { opacity: '1', transform: 'scale(1)', filter: 'none' },
        },
      },
      backgroundImage: {
        'grid-pattern': 'linear-gradient(rgba(0,200,255,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(0,200,255,0.03) 1px, transparent 1px)',
        'scanlines': 'repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,200,255,0.05) 2px, rgba(0,200,255,0.05) 4px)',
      },
    },
  },
  plugins: [],
}

export default config
