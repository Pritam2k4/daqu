/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            fontFamily: {
                sans: ['Space Grotesk', 'system-ui', 'sans-serif'],
                display: ['Clash Display', 'Space Grotesk', 'system-ui', 'sans-serif'],
            },
            colors: {
                primary: {
                    50: '#FDF9E9',
                    100: '#FCF3D3',
                    200: '#F9E7A7',
                    300: '#F5D76B',
                    400: '#E5C234',
                    500: '#C5A439',  // Main gold
                    600: '#A88A2D',
                    700: '#8B6914',
                    800: '#6B4F0D',
                    900: '#4A3608',
                },
                mocha: {
                    300: '#C9A090',
                    400: '#B88B78',
                    500: '#A47764',  // Pantone 2025
                    600: '#8A6354',
                },
                surface: {
                    dark: '#0A0A0B',
                    card: '#111113',
                    elevated: '#1A1A1D',
                },
                cream: '#F5F0E8',
            },
            animation: {
                'float': 'float 6s ease-in-out infinite',
                'float-slow': 'float 8s ease-in-out infinite',
                'float-slower': 'float 12s ease-in-out infinite',
                'pulse-slow': 'pulse 4s ease-in-out infinite',
                'glow': 'glow 2s ease-in-out infinite alternate',
                'gradient-x': 'gradient-x 15s ease infinite',
                'gradient-y': 'gradient-y 15s ease infinite',
                'spin-slow': 'spin 20s linear infinite',
                'bounce-slow': 'bounce 3s ease-in-out infinite',
                'fade-in': 'fadeIn 0.6s ease-out forwards',
                'slide-up': 'slideUp 0.6s ease-out forwards',
                'slide-down': 'slideDown 0.6s ease-out forwards',
                'slide-left': 'slideLeft 0.6s ease-out forwards',
                'slide-right': 'slideRight 0.6s ease-out forwards',
                'scale-in': 'scaleIn 0.5s ease-out forwards',
                'blur-in': 'blurIn 0.8s ease-out forwards',
                'counter': 'counter 2s ease-out forwards',
                'morph': 'morph 8s ease-in-out infinite',
                'shimmer': 'shimmer 2s linear infinite',
            },
            keyframes: {
                float: {
                    '0%, 100%': { transform: 'translateY(0) rotate(0deg)' },
                    '50%': { transform: 'translateY(-20px) rotate(2deg)' },
                },
                glow: {
                    '0%': { boxShadow: '0 0 20px rgba(197, 164, 57, 0.3)' },
                    '100%': { boxShadow: '0 0 40px rgba(197, 164, 57, 0.6), 0 0 80px rgba(197, 164, 57, 0.3)' },
                },
                'gradient-x': {
                    '0%, 100%': { backgroundPosition: '0% 50%' },
                    '50%': { backgroundPosition: '100% 50%' },
                },
                'gradient-y': {
                    '0%, 100%': { backgroundPosition: '50% 0%' },
                    '50%': { backgroundPosition: '50% 100%' },
                },
                fadeIn: {
                    '0%': { opacity: '0', transform: 'translateY(10px)' },
                    '100%': { opacity: '1', transform: 'translateY(0)' },
                },
                slideUp: {
                    '0%': { opacity: '0', transform: 'translateY(40px)' },
                    '100%': { opacity: '1', transform: 'translateY(0)' },
                },
                slideDown: {
                    '0%': { opacity: '0', transform: 'translateY(-40px)' },
                    '100%': { opacity: '1', transform: 'translateY(0)' },
                },
                slideLeft: {
                    '0%': { opacity: '0', transform: 'translateX(40px)' },
                    '100%': { opacity: '1', transform: 'translateX(0)' },
                },
                slideRight: {
                    '0%': { opacity: '0', transform: 'translateX(-40px)' },
                    '100%': { opacity: '1', transform: 'translateX(0)' },
                },
                scaleIn: {
                    '0%': { opacity: '0', transform: 'scale(0.9)' },
                    '100%': { opacity: '1', transform: 'scale(1)' },
                },
                blurIn: {
                    '0%': { opacity: '0', filter: 'blur(10px)' },
                    '100%': { opacity: '1', filter: 'blur(0)' },
                },
                morph: {
                    '0%, 100%': { borderRadius: '60% 40% 30% 70%/60% 30% 70% 40%' },
                    '50%': { borderRadius: '30% 60% 70% 40%/50% 60% 30% 60%' },
                },
                shimmer: {
                    '0%': { backgroundPosition: '-200% 0' },
                    '100%': { backgroundPosition: '200% 0' },
                },
            },
            backgroundImage: {
                'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
                'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
                'shimmer': 'linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent)',
            },
        },
    },
    plugins: [],
}
