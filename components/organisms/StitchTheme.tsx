import React from 'react';

/**
 * StitchTheme injections as requested by the user.
 * Injects Design System Tokens and specific styles 
 * required for High-Fidelity Stitch-generated content.
 */
export function StitchTheme() {
    return (
        <>
            <style dangerouslySetInnerHTML={{
                __html: `
        /* ── Design System Tokens ── */
        :root {
            --color-primary: #7000bb;
            --color-primary-light: #00d22c;
            --color-primary-dark: #c815fb;
            --color-success: #c52222;
            --color-warning: #f59e0b;
            --color-danger: #ef4444;
            --color-info: #a53bf6;
            --color-text-primary: #ffffff;
            --color-text-secondary: #a1a1aa;
            --color-text-muted: #52525b;
            --color-bg-app: #020202;
            --color-bg-card: #111118;
            --color-bg-sidebar: #0d0d12;
            --color-bg-input: #1a1a24;
            --font-size-h1: 48px;
            --font-size-h2: 36px;
            --font-size-h3: 24px;
            --font-size-body: 16px;
            --font-size-sm: 14px;
            --font-size-xs: 12px;
            --color-border: #27272a;
            --color-chart-equities: #db0000;
            --color-chart-real-estate: #3b82f6;
            --color-chart-fixed-income: #81ea28;
            --color-chart-crypto: #34d399;
            --color-chart-portfolio-purple: #13db00;
            --color-chart-portfolio-gold: #eab308;
            --color-text-on-dark: #ffffff;
            --color-bg-page: #181818;
            --font-size-h4: 22px;
            --font-size-h5: 18px;
            --font-size-h6: 16px;
            --font-size-caption: 13px;
            --font-size-small: 12px;
            --font-weight-light: 300;
            --font-weight-regular: 400;
            --font-weight-medium: 500;
            --font-weight-semibold: 600;
            --font-weight-bold: 700;
            --font-weight-black: 900;
            --line-height-tight: 120;
            --line-height-snug: 135;
            --line-height-normal: 150;
            --line-height-relaxed: 165;
            --line-height-loose: 200;
            --spacing-1: 4px;
            --spacing-2: 8px;
            --spacing-3: 12px;
            --spacing-4: 16px;
            --spacing-5: 20px;
            --spacing-6: 24px;
            --spacing-8: 32px;
            --spacing-10: 40px;
            --spacing-12: 48px;
            --spacing-16: 64px;
            --spacing-20: 80px;
            --spacing-24: 96px;
            --radius-none: 0px;
            --radius-sm: 3px;
            --radius-md: 6px;
            --radius-lg: 9px;
            --radius-xl: 17px;
            --radius-2xl: 30px;
            --radius-3xl: 46px;
            --blur-sm: 4px;
            --blur-md: 8px;
            --blur-lg: 16px;
            --blur-xl: 32px;
            --blur-2xl: 64px;
            --blur-3xl: 120px;
            --background: 240 10% 3.9%;
            --foreground: 0 0% 98%;
            --card: 240 10% 3.9%;
            --card-foreground: 0 0% 98%;
            --popover: 240 10% 3.9%;
            --popover-foreground: 0 0% 98%;
            --primary: 271 100% 43%;
            --primary-foreground: 0 0% 98%;
            --secondary: 240 3.7% 15.9%;
            --secondary-foreground: 0 0% 98%;
            --muted: 240 3.7% 15.9%;
            --muted-foreground: 240 5% 64.9%;
            --accent: 240 3.7% 15.9%;
            --accent-foreground: 0 0% 98%;
            --destructive: 0 62.8% 30.6%;
            --destructive-foreground: 0 0% 98%;
            --border: 240 3.7% 15.9%;
            --input: 240 3.7% 15.9%;
            --ring: 271 100% 43%;
            --radius: 1rem;
        }

        .glass-panel {
            background: rgba(26, 17, 34, 0.6);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(127, 25, 230, 0.2);
        }
        .text-gradient {
            background: linear-gradient(to right, #7f19e6, #c084fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .glow-effect {
            box-shadow: 0 0 20px rgba(127, 25, 230, 0.3);
        }
      ` }} />

            {/* External CSS / Fonts requested */}
            <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap" rel="stylesheet" />
            <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet" />

            {/* Tailwind Runtime Config for Stitch Designs */}
            <script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
            <script dangerouslySetInnerHTML={{
                __html: `
        tailwind.config = {
            darkMode: "class",
            theme: {
                extend: {
                    colors: {
                        "primary": "#7f19e6",
                        "primary-light": "#a35ceb",
                        "primary-dark": "#5911a1",
                        "background-light": "#f7f6f8",
                        "background-dark": "#0f0a14",
                        "surface-dark": "#1a1122",
                        "glass": "rgba(255, 255, 255, 0.05)",
                        "glass-border": "rgba(255, 255, 255, 0.1)",
                    },
                    fontFamily: {
                        "display": ["Space Grotesk", "sans-serif"],
                        "sans": ["Space Grotesk", "sans-serif"],
                    },
                    backgroundImage: {
                        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
                    }
                },
            },
        }
      ` }} />
        </>
    );
}
