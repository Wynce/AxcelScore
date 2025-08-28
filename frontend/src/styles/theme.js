// ==============================
// 🎨 styles/theme.js - Enhanced UI Theme System with Gen Alpha Design
// ==============================

/**
 * Enhanced color palette with Gen Alpha theme support
 * Designed for Gen Alpha students (modern, vibrant, engaging)
 */
export const colors = {
  // Primary Colors
  primary: {
    blue: '#0453f1',      // Main buttons, primary actions
    blueHover: '#0341c7', // Hover states for primary blue
    blueDark: '#032c99',  // Active/pressed states
  },
  
  // Secondary Colors
  secondary: {
    blue: '#e5e6ea',      // Light backgrounds, secondary elements
    blueHover: '#d1d2d6', // Hover states for secondary elements
    blueDark: '#b8bac0',  // Active states for secondary
  },
  
  // Accent Colors
  accent: {
    orange: '#FF6701',     // Highlights, call-to-action buttons
    orangeHover: '#e55a01', // Orange hover state
    orangeLight: '#fff5f0', // Light orange background for hover
  },
  
  // Gen Alpha Gradient Colors
  genalpha: {
    primary: '#667eea',
    secondary: '#764ba2',
    accent1: '#f093fb',
    accent2: '#f5576c',
    accent3: '#4facfe',
    glow: '#ff6b6b',
    glowSecondary: '#4ecdc4',
    glowTertiary: '#45b7d1',
  },
  
  // Success & Feedback
  success: {
    orange: '#f2e08a',    // Success states, positive feedback
    green: '#4CAF50',     // Correct answers, checkmarks
    greenLight: '#e8f5e8', // Light green backgrounds
    genalphaGreen: '#56ab2f', // Gen Alpha success color
    genalphaGreenLight: '#a8e6cf', // Gen Alpha success light
  },
  
  // Error States
  error: {
    red: '#F44336',       // Incorrect answers, error states
    redLight: '#fdeaea',  // Light red backgrounds
    genalphaRed: '#ff6b6b', // Gen Alpha error color
    genalphaRedLight: '#ffa07a', // Gen Alpha error light
  },
  
  // Backgrounds
  background: {
    white: '#FFFFFF',     // Main background
    gray: '#e9f0f6',      // Card backgrounds, subtle sections
    lightGray: '#f8f9fa', // Very light sections
    dark: '#0f172a',      // Dark theme background
    darkSecondary: '#1e293b', // Dark theme secondary
    genalphaGlass: 'rgba(255, 255, 255, 0.15)', // Gen Alpha glassmorphism
    genalphaGlassDark: 'rgba(255, 255, 255, 0.1)', // Gen Alpha darker glass
  },
  
  // Borders & Dividers
  border: {
    gray: '#e5e6ea',      // Default borders
    light: '#f0f1f5',     // Subtle borders
    medium: '#d1d2d6',    // More prominent borders
    dark: '#374151',      // Dark theme borders
    genalphaWhite: 'rgba(255, 255, 255, 0.2)', // Gen Alpha borders
    genalphaWhiteBright: 'rgba(255, 255, 255, 0.3)', // Gen Alpha bright borders
  },
  
  // Text Colors
  text: {
    primary: '#000000',   // Main text
    secondary: '#58585A', // Supporting text, labels
    muted: '#8a8a8c',     // Disabled text, placeholders
    white: '#FFFFFF',     // Text on dark backgrounds
    darkPrimary: '#f8fafc', // Dark theme primary text
    darkSecondary: '#cbd5e1', // Dark theme secondary text
    genalphaWhite: '#ffffff', // Gen Alpha white text
    genalphaWhiteSecondary: 'rgba(255, 255, 255, 0.9)', // Gen Alpha secondary white
  }
};

/**
 * Enhanced typography system with Gen Alpha considerations
 */
export const typography = {
  // Font families
  fonts: {
    primary: '"Gill Sans MT", "Gill Sans", "Trebuchet MS", sans-serif',
    fallback: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    genalpha: '"Inter", system-ui, sans-serif', // Gen Alpha preferred font
  },
  
  // Font sizes (mobile-first, Gen Alpha optimized)
  sizes: {
    xs: '0.75rem',    // 12px - Small labels
    sm: '0.875rem',   // 14px - Secondary text
    base: '1rem',     // 16px - Base text (minimum for mobile)
    lg: '1.125rem',   // 18px - Larger body text
    xl: '1.25rem',    // 20px - Small headings
    '2xl': '1.5rem',  // 24px - Medium headings
    '3xl': '1.875rem', // 30px - Large headings
    '4xl': '2.25rem', // 36px - Extra large headings
    '5xl': '3rem',    // 48px - Hero text
    '6xl': '3.75rem', // 60px - Display text
  },
  
  // Font weights
  weights: {
    normal: '400',
    medium: '500',
    semibold: '600',
    bold: '700',
    extrabold: '800', // Added for Gen Alpha emphasis
  },
  
  // Line heights
  leading: {
    tight: '1.25',
    normal: '1.5',
    relaxed: '1.75',
  }
};

/**
 * Enhanced spacing system
 */
export const spacing = {
  0: '0',
  1: '0.25rem',   // 4px
  2: '0.5rem',    // 8px
  3: '0.75rem',   // 12px
  4: '1rem',      // 16px
  5: '1.25rem',   // 20px
  6: '1.5rem',    // 24px
  8: '2rem',      // 32px
  10: '2.5rem',   // 40px
  12: '3rem',     // 48px
  16: '4rem',     // 64px
  20: '5rem',     // 80px
  24: '6rem',     // 96px
};

/**
 * Enhanced border radius with Gen Alpha values
 */
export const borderRadius = {
  none: '0',
  sm: '0.25rem',    // 4px
  base: '0.5rem',   // 8px - Default
  md: '0.75rem',    // 12px
  lg: '1rem',       // 16px - Cards, major elements
  xl: '1.5rem',     // 24px - Large cards
  '2xl': '2rem',    // 32px - Gen Alpha preferred
  '3xl': '3rem',    // 48px - Extra large Gen Alpha
  full: '9999px',   // Perfect circles
};

/**
 * Enhanced shadow system with Gen Alpha variants
 */
export const shadows = {
  none: 'none',
  sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
  base: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
  md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
  lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
  xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
  
  // Gen Alpha specific shadows
  genalpha: {
    glow: '0 0 20px rgba(255, 107, 107, 0.3)',
    glowHover: '0 0 30px rgba(255, 107, 107, 0.6), 0 0 40px rgba(76, 201, 196, 0.4)',
    card: '0 8px 32px rgba(0, 0, 0, 0.1)',
    timer: '0 0 30px rgba(239, 68, 68, 0.6)',
  }
};

/**
 * Theme-aware component styles with Gen Alpha support
 */
export const components = {
  // Enhanced Button variants with theme support
  buttons: {
    // Light theme buttons
    primary: `
      bg-[${colors.primary.blue}] 
      text-[${colors.text.white}] 
      hover:bg-[${colors.primary.blueHover}] 
      active:bg-[${colors.primary.blueDark}]
      font-semibold 
      px-6 py-3 
      rounded-lg 
      transition-colors 
      duration-200
      min-h-[44px]
    `,
    
    secondary: `
      bg-[${colors.secondary.blue}] 
      text-[${colors.text.primary}] 
      hover:bg-[${colors.secondary.blueHover}] 
      active:bg-[${colors.secondary.blueDark}]
      font-medium 
      px-6 py-3 
      rounded-lg 
      transition-colors 
      duration-200
      min-h-[44px]
    `,
    
    accent: `
      bg-[${colors.accent.orange}] 
      text-[${colors.text.white}] 
      hover:bg-[${colors.accent.orangeHover}] 
      font-semibold 
      px-6 py-3 
      rounded-lg 
      transition-colors 
      duration-200
      min-h-[44px]
    `,
    
    // Dark theme buttons
    darkPrimary: `
      bg-blue-600 
      text-white 
      hover:bg-blue-700 
      active:bg-blue-800
      font-semibold 
      px-6 py-3 
      rounded-lg 
      transition-colors 
      duration-200
      min-h-[44px]
    `,
    
    darkSecondary: `
      bg-gray-700 
      text-gray-100 
      hover:bg-gray-600 
      active:bg-gray-800
      font-medium 
      px-6 py-3 
      rounded-lg 
      transition-colors 
      duration-200
      min-h-[44px]
    `,
    
    // Gen Alpha buttons
    genalpha: `
      genalpha-button
      font-semibold 
      px-6 py-3 
      rounded-lg 
      transition-all 
      duration-300
      min-h-[44px]
      text-white
      relative
      overflow-hidden
    `,
    
    genalphaSecondary: `
      genalpha-card
      font-medium 
      px-6 py-3 
      rounded-lg 
      transition-all 
      duration-300
      min-h-[44px]
      text-white
      border
      border-white/20
    `,
    
    disabled: `
      bg-[${colors.secondary.blue}] 
      text-[${colors.text.muted}] 
      cursor-not-allowed 
      font-medium 
      px-6 py-3 
      rounded-lg
      min-h-[44px]
    `,
  },
  
  // Enhanced Card styles with theme support
  cards: {
    // Light theme cards
    primary: `
      bg-[${colors.background.white}] 
      border 
      border-[${colors.border.gray}] 
      rounded-xl 
      p-6 
      shadow-sm
    `,
    
    secondary: `
      bg-[${colors.background.gray}] 
      border 
      border-[${colors.border.gray}] 
      rounded-xl 
      p-6
    `,
    
    interactive: `
      bg-[${colors.background.gray}] 
      border 
      border-[${colors.border.gray}] 
      rounded-xl 
      p-6 
      cursor-pointer 
      hover:bg-[${colors.secondary.blueHover}] 
      transition-colors 
      duration-200
    `,
    
    // Dark theme cards
    darkPrimary: `
      bg-gray-800 
      border 
      border-gray-700 
      rounded-xl 
      p-6 
      shadow-sm
    `,
    
    darkSecondary: `
      bg-gray-900 
      border 
      border-gray-800 
      rounded-xl 
      p-6
    `,
    
    // Gen Alpha cards
    genalpha: `
      genalpha-card
      rounded-xl 
      p-6 
      backdrop-blur-xl
      border
      border-white/20
    `,
    
    genalphaInteractive: `
      genalpha-card
      interactive-element
      rounded-xl 
      p-6 
      cursor-pointer 
      backdrop-blur-xl
      border
      border-white/20
      hover:border-white/30
    `,
  },
  
  // Enhanced Input styles with theme support
  inputs: {
    // Light theme inputs
    base: `
      w-full 
      px-4 py-3 
      border 
      border-[${colors.border.gray}] 
      rounded-lg 
      bg-[${colors.background.white}] 
      text-[${colors.text.primary}] 
      placeholder-[${colors.text.muted}] 
      focus:outline-none 
      focus:border-[${colors.primary.blue}] 
      focus:ring-2 
      focus:ring-[${colors.primary.blue}] 
      focus:ring-opacity-20
      min-h-[44px]
    `,
    
    // Dark theme inputs
    dark: `
      w-full 
      px-4 py-3 
      border 
      border-gray-600 
      rounded-lg 
      bg-gray-800 
      text-white 
      placeholder-gray-400 
      focus:outline-none 
      focus:border-blue-500 
      focus:ring-2 
      focus:ring-blue-500 
      focus:ring-opacity-20
      min-h-[44px]
    `,
    
    // Gen Alpha inputs (handled by CSS classes)
    genalpha: `
      w-full 
      px-4 py-3 
      border-2 
      border-white/30 
      rounded-lg 
      backdrop-blur-xl
      text-white 
      placeholder-white/70 
      focus:outline-none 
      focus:border-white/60 
      min-h-[44px]
    `,
  },
  
  // Enhanced Answer option styles with theme support
  answers: {
    // Light theme answers
    default: `
      w-full 
      p-4 
      rounded-lg 
      border-2 
      border-[${colors.border.gray}] 
      bg-[${colors.background.white}] 
      text-[${colors.text.primary}] 
      text-left 
      hover:border-[${colors.accent.orange}] 
      hover:bg-[${colors.accent.orangeLight}] 
      transition-all 
      duration-200
      min-h-[44px]
    `,
    
    selected: `
      w-full 
      p-4 
      rounded-lg 
      border-2 
      border-[${colors.accent.orange}] 
      bg-[${colors.accent.orange}] 
      text-[${colors.text.white}] 
      text-left
      min-h-[44px]
    `,
    
    correct: `
      w-full 
      p-4 
      rounded-lg 
      border-2 
      border-[${colors.success.green}] 
      bg-[${colors.success.greenLight}] 
      text-[${colors.text.primary}] 
      text-left
      min-h-[44px]
    `,
    
    incorrect: `
      w-full 
      p-4 
      rounded-lg 
      border-2 
      border-[${colors.error.red}] 
      bg-[${colors.error.redLight}] 
      text-[${colors.text.primary}] 
      text-left
      min-h-[44px]
    `,
    
    // Dark theme answers
    darkDefault: `
      w-full 
      p-4 
      rounded-lg 
      border-2 
      border-gray-600 
      bg-gray-800 
      text-white 
      text-left 
      hover:border-orange-500 
      hover:bg-orange-900/20 
      transition-all 
      duration-200
      min-h-[44px]
    `,
    
    darkSelected: `
      w-full 
      p-4 
      rounded-lg 
      border-2 
      border-orange-500 
      bg-orange-600 
      text-white 
      text-left
      min-h-[44px]
    `,
    
    // Gen Alpha answers
    genalphaDefault: `
      w-full 
      p-4 
      rounded-lg 
      border-2 
      border-white/20 
      backdrop-blur-xl 
      bg-white/10 
      text-white 
      text-left 
      hover:border-white/40 
      hover:bg-white/20 
      transition-all 
      duration-300
      min-h-[44px]
    `,
    
    genalphaSelected: `
      w-full 
      p-4 
      rounded-lg 
      border-2 
      border-white/60 
      genalpha-button 
      text-white 
      text-left
      min-h-[44px]
    `,
    
    genalphaCorrect: `
      w-full 
      p-4 
      rounded-lg 
      border-2 
      border-green-400 
      status-success 
      text-white 
      text-left
      min-h-[44px]
    `,
    
    genalphaIncorrect: `
      w-full 
      p-4 
      rounded-lg 
      border-2 
      border-red-400 
      status-error 
      text-white 
      text-left
      min-h-[44px]
    `,
  },
};

/**
 * Enhanced animations with Gen Alpha effects
 */
export const animations = {
  transitions: {
    fast: 'transition-all duration-150 ease-in-out',
    normal: 'transition-all duration-200 ease-in-out',
    slow: 'transition-all duration-300 ease-in-out',
    genalpha: 'transition-all duration-300 cubic-bezier(0.175, 0.885, 0.32, 1.275)',
  },
  
  transforms: {
    scaleHover: 'hover:scale-105',
    scaleTap: 'active:scale-95',
    slideIn: 'transform translate-x-0 opacity-100',
    slideOut: 'transform translate-x-full opacity-0',
    genalphaHover: 'hover:scale-110 hover:-translate-y-1',
    genalphaActive: 'active:scale-95',
  },
  
  // Progress animations
  progress: {
    bar: 'transition-all duration-300 ease-out',
    pulse: 'animate-pulse',
    genalphaPulse: 'genAlphaPulse 2s ease-in-out infinite',
  },
  
  // Gen Alpha specific animations
  genalpha: {
    gradient: 'gradientShift 8s ease infinite',
    shine: 'shine 3s infinite',
    glow: 'genAlphaGlow 3s ease-in-out infinite',
    pulse: 'genAlphaPulse 2s ease-in-out infinite',
  },
};

/**
 * Enhanced responsive breakpoints
 */
export const breakpoints = {
  sm: '640px',   // Small devices
  md: '768px',   // Tablets
  lg: '1024px',  // Laptops
  xl: '1280px',  // Desktops
  '2xl': '1536px', // Large desktops
};

/**
 * Theme-aware utility functions
 */
export const getThemeClasses = (componentType, variant = 'default', theme = 'light') => {
  const themePrefix = theme === 'light' ? '' : theme === 'dark' ? 'dark' : 'genalpha';
  const key = themePrefix ? `${themePrefix}${variant.charAt(0).toUpperCase()}${variant.slice(1)}` : variant;
  
  return components[componentType]?.[key] || components[componentType]?.[variant] || '';
};

/**
 * Theme detection utility
 */
export const getActiveTheme = () => {
  const root = document.documentElement;
  if (root.classList.contains('genalpha')) return 'genalpha';
  if (root.classList.contains('dark')) return 'dark';
  return 'light';
};

/**
 * Theme-specific CSS class generators
 */
export const getThemeSpecificClasses = (theme) => {
  switch(theme) {
    case 'dark':
      return {
        background: 'bg-gray-900',
        backgroundSecondary: 'bg-gray-800',
        text: 'text-white',
        textSecondary: 'text-gray-300',
        border: 'border-gray-700',
        card: 'bg-gray-800 border-gray-700',
        button: 'bg-blue-600 hover:bg-blue-700 text-white',
      };
    
    case 'genalpha':
      return {
        background: 'genalpha genalpha-animated',
        backgroundSecondary: 'genalpha-card',
        text: 'text-white',
        textSecondary: 'text-white/90',
        border: 'border-white/20',
        card: 'genalpha-card backdrop-blur-xl border-white/20',
        button: 'genalpha-button text-white',
      };
    
    default: // light
      return {
        background: 'bg-white',
        backgroundSecondary: 'bg-gray-50',
        text: 'text-gray-900',
        textSecondary: 'text-gray-600',
        border: 'border-gray-200',
        card: 'bg-white border-gray-200',
        button: 'bg-blue-600 hover:bg-blue-700 text-white',
      };
  }
};

/**
 * Enhanced CSS variables with Gen Alpha support
 */
export const cssVariables = `
  :root {
    --primary-blue: ${colors.primary.blue};
    --secondary-blue: ${colors.secondary.blue};
    --accent-orange: ${colors.accent.orange};
    --light-orange: ${colors.success.orange};
    --background-white: ${colors.background.white};
    --background-gray: ${colors.background.gray};
    --border-gray: ${colors.border.gray};
    --text-primary: ${colors.text.primary};
    --text-secondary: ${colors.text.secondary};
    --success-green: ${colors.success.green};
    --error-red: ${colors.error.red};
    
    /* Gen Alpha Variables */
    --genalpha-primary: ${colors.genalpha.primary};
    --genalpha-secondary: ${colors.genalpha.secondary};
    --genalpha-glow: ${colors.genalpha.glow};
    --genalpha-glass: ${colors.background.genalphaGlass};
    
    /* Animation Variables */
    --gradient-animation: gradientShift 8s ease infinite;
    --shine-animation: shine 3s infinite;
    --pulse-animation: genAlphaPulse 2s ease-in-out infinite;
  }
  
  * {
    font-family: ${typography.fonts.primary}, ${typography.fonts.fallback};
  }
  
  body {
    font-size: ${typography.sizes.base};
    line-height: ${typography.leading.normal};
    color: ${colors.text.primary};
    background-color: ${colors.background.white};
  }
  
  /* Touch targets for mobile accessibility */
  button, [role="button"], input, select, textarea {
    min-height: 44px;
    min-width: 44px;
  }
  
  /* Smooth animations for better UX */
  * {
    transition: color 0.2s ease, background-color 0.2s ease, border-color 0.2s ease;
  }
`;

/**
 * Theme toggle utility function
 */
export const toggleTheme = (currentTheme) => {
  switch(currentTheme) {
    case 'light': return 'dark';
    case 'dark': return 'genalpha';
    case 'genalpha': return 'light';
    default: return 'light';
  }
};

export default {
  colors,
  typography,
  spacing,
  borderRadius,
  shadows,
  components,
  animations,
  breakpoints,
  getThemeClasses,
  getActiveTheme,
  getThemeSpecificClasses,
  toggleTheme,
  cssVariables,
};