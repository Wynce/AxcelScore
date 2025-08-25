// ==============================
// 🎨 styles/theme.js - UI Theme System for Gen Alpha Design
// ==============================

/**
 * Color palette based on PRD specifications
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
  
  // Success & Feedback
  success: {
    orange: '#f2e08a',    // Success states, positive feedback
    green: '#4CAF50',     // Correct answers, checkmarks
    greenLight: '#e8f5e8', // Light green backgrounds
  },
  
  // Error States
  error: {
    red: '#F44336',       // Incorrect answers, error states
    redLight: '#fdeaea',  // Light red backgrounds
  },
  
  // Backgrounds
  background: {
    white: '#FFFFFF',     // Main background
    gray: '#e9f0f6',      // Card backgrounds, subtle sections
    lightGray: '#f8f9fa', // Very light sections
  },
  
  // Borders & Dividers
  border: {
    gray: '#e5e6ea',      // Default borders
    light: '#f0f1f5',     // Subtle borders
    medium: '#d1d2d6',    // More prominent borders
  },
  
  // Text Colors
  text: {
    primary: '#000000',   // Main text
    secondary: '#58585A', // Supporting text, labels
    muted: '#8a8a8c',     // Disabled text, placeholders
    white: '#FFFFFF',     // Text on dark backgrounds
  }
};

/**
 * Typography system for consistent text styling
 */
export const typography = {
  // Font families
  fonts: {
    primary: '"Gill Sans MT", "Gill Sans", "Trebuchet MS", sans-serif',
    fallback: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
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
  },
  
  // Line heights
  leading: {
    tight: '1.25',
    normal: '1.5',
    relaxed: '1.75',
  }
};

/**
 * Spacing system for consistent layout
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
 * Border radius values for consistent rounded corners
 */
export const borderRadius = {
  none: '0',
  sm: '0.25rem',    // 4px
  base: '0.5rem',   // 8px - Default
  md: '0.75rem',    // 12px
  lg: '1rem',       // 16px - Cards, major elements
  xl: '1.5rem',     // 24px - Large cards
  '2xl': '2rem',    // 32px
  full: '9999px',   // Perfect circles
};

/**
 * Shadow system for depth and elevation
 */
export const shadows = {
  none: 'none',
  sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
  base: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
  md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
  lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
  xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
};

/**
 * Pre-built component styles for common UI elements
 */
export const components = {
  // Button variants
  buttons: {
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
  
  // Card styles
  cards: {
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
  },
  
  // Input styles
  inputs: {
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
  },
  
  // Answer option styles
  answers: {
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
  },
};

/**
 * Animation presets for micro-interactions
 */
export const animations = {
  transitions: {
    fast: 'transition-all duration-150 ease-in-out',
    normal: 'transition-all duration-200 ease-in-out',
    slow: 'transition-all duration-300 ease-in-out',
  },
  
  transforms: {
    scaleHover: 'hover:scale-105',
    scaleTap: 'active:scale-95',
    slideIn: 'transform translate-x-0 opacity-100',
    slideOut: 'transform translate-x-full opacity-0',
  },
  
  // Progress animations
  progress: {
    bar: 'transition-all duration-300 ease-out',
    pulse: 'animate-pulse',
  },
};

/**
 * Responsive breakpoints for mobile-first design
 */
export const breakpoints = {
  sm: '640px',   // Small devices
  md: '768px',   // Tablets
  lg: '1024px',  // Laptops
  xl: '1280px',  // Desktops
  '2xl': '1536px', // Large desktops
};

/**
 * Utility function to generate Tailwind classes from theme
 */
export const getThemeClasses = (componentType, variant = 'default') => {
  return components[componentType]?.[variant] || '';
};

/**
 * Custom CSS variables for dynamic theming
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
  cssVariables,
};