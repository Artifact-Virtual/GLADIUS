/**
 * Global Theme Configuration
 * Centralized theme system for consistent styling across all components
 */

export const GlobalTheme = {
  // Color palette
  colors: {
    primary: {
      main: '#2563eb',      // Blue
      light: '#3b82f6',
      dark: '#1d4ed8',
      contrast: '#ffffff'
    },
    secondary: {
      main: '#64748b',      // Slate
      light: '#94a3b8',
      dark: '#475569',
      contrast: '#ffffff'
    },
    success: {
      main: '#10b981',      // Emerald
      light: '#34d399',
      dark: '#059669',
      contrast: '#ffffff'
    },
    warning: {
      main: '#f59e0b',      // Amber
      light: '#fbbf24',
      dark: '#d97706',
      contrast: '#ffffff'
    },
    error: {
      main: '#ef4444',      // Red
      light: '#f87171',
      dark: '#dc2626',
      contrast: '#ffffff'
    },
    info: {
      main: '#06b6d4',      // Cyan
      light: '#22d3ee',
      dark: '#0891b2',
      contrast: '#ffffff'
    },
    background: {
      default: '#f8fafc',   // Very light gray
      paper: '#ffffff',
      dark: '#1e293b',
      darker: '#0f172a'
    },
    text: {
      primary: '#1e293b',
      secondary: '#64748b',
      disabled: '#94a3b8',
      light: '#ffffff'
    },
    border: {
      light: '#e2e8f0',
      medium: '#cbd5e1',
      dark: '#64748b'
    }
  },

  // Typography
  typography: {
    fontFamily: '"Inter", "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    fontSize: {
      xs: '0.75rem',     // 12px
      sm: '0.875rem',    // 14px
      base: '1rem',      // 16px
      lg: '1.125rem',    // 18px
      xl: '1.25rem',     // 20px
      '2xl': '1.5rem',   // 24px
      '3xl': '1.875rem', // 30px
      '4xl': '2.25rem',  // 36px
      '5xl': '3rem'      // 48px
    },
    fontWeight: {
      normal: '400',
      medium: '500',
      semibold: '600',
      bold: '700'
    },
    lineHeight: {
      tight: '1.25',
      normal: '1.5',
      relaxed: '1.75'
    }
  },

  // Spacing
  spacing: {
    xs: '0.25rem',    // 4px
    sm: '0.5rem',     // 8px
    md: '1rem',       // 16px
    lg: '1.5rem',     // 24px
    xl: '2rem',       // 32px
    '2xl': '3rem',    // 48px
    '3xl': '4rem',    // 64px
    '4xl': '6rem'     // 96px
  },

  // Border radius
  borderRadius: {
    none: '0',
    sm: '0.125rem',   // 2px
    md: '0.25rem',    // 4px
    lg: '0.5rem',     // 8px
    xl: '0.75rem',    // 12px
    '2xl': '1rem',    // 16px
    full: '9999px'
  },

  // Shadows
  shadows: {
    none: 'none',
    sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
    md: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
    lg: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
    xl: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
    '2xl': '0 25px 50px -12px rgb(0 0 0 / 0.25)'
  },

  // Animation
  animation: {
    duration: {
      fast: '150ms',
      normal: '300ms',
      slow: '500ms'
    },
    easing: {
      easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
      easeOut: 'cubic-bezier(0, 0, 0.2, 1)',
      easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)'
    }
  },

  // Layout
  layout: {
    sidebar: {
      width: '280px',
      collapsedWidth: '64px'
    },
    header: {
      height: '64px'
    },
    maxWidth: {
      sm: '640px',
      md: '768px',
      lg: '1024px',
      xl: '1280px',
      '2xl': '1536px'
    }
  }
};

// Component-specific themes
export const ComponentThemes = {
  dashboard: {
    card: {
      backgroundColor: GlobalTheme.colors.background.paper,
      borderRadius: GlobalTheme.borderRadius.lg,
      boxShadow: GlobalTheme.shadows.md,
      border: `1px solid ${GlobalTheme.colors.border.light}`,
      padding: GlobalTheme.spacing.lg
    },
    header: {
      backgroundColor: GlobalTheme.colors.background.paper,
      borderBottom: `1px solid ${GlobalTheme.colors.border.light}`,
      height: GlobalTheme.layout.header.height,
      padding: `0 ${GlobalTheme.spacing.lg}`
    },
    metric: {
      backgroundColor: GlobalTheme.colors.background.paper,
      borderRadius: GlobalTheme.borderRadius.md,
      padding: GlobalTheme.spacing.md,
      border: `1px solid ${GlobalTheme.colors.border.light}`
    }
  },
  
  button: {
    primary: {
      backgroundColor: GlobalTheme.colors.primary.main,
      color: GlobalTheme.colors.primary.contrast,
      padding: `${GlobalTheme.spacing.sm} ${GlobalTheme.spacing.lg}`,
      borderRadius: GlobalTheme.borderRadius.md,
      fontWeight: GlobalTheme.typography.fontWeight.medium,
      border: 'none',
      cursor: 'pointer',
      transition: `all ${GlobalTheme.animation.duration.normal} ${GlobalTheme.animation.easing.easeInOut}`
    },
    secondary: {
      backgroundColor: 'transparent',
      color: GlobalTheme.colors.primary.main,
      padding: `${GlobalTheme.spacing.sm} ${GlobalTheme.spacing.lg}`,
      borderRadius: GlobalTheme.borderRadius.md,
      fontWeight: GlobalTheme.typography.fontWeight.medium,
      border: `1px solid ${GlobalTheme.colors.primary.main}`,
      cursor: 'pointer',
      transition: `all ${GlobalTheme.animation.duration.normal} ${GlobalTheme.animation.easing.easeInOut}`
    }
  },

  table: {
    backgroundColor: GlobalTheme.colors.background.paper,
    borderRadius: GlobalTheme.borderRadius.lg,
    overflow: 'hidden',
    boxShadow: GlobalTheme.shadows.md,
    header: {
      backgroundColor: GlobalTheme.colors.background.default,
      fontWeight: GlobalTheme.typography.fontWeight.semibold,
      color: GlobalTheme.colors.text.primary,
      padding: GlobalTheme.spacing.md
    },
    cell: {
      padding: GlobalTheme.spacing.md,
      borderBottom: `1px solid ${GlobalTheme.colors.border.light}`
    }
  },

  alert: {
    success: {
      backgroundColor: '#f0fdf4',
      color: GlobalTheme.colors.success.dark,
      border: `1px solid ${GlobalTheme.colors.success.light}`,
      borderRadius: GlobalTheme.borderRadius.md,
      padding: GlobalTheme.spacing.md
    },
    warning: {
      backgroundColor: '#fffbeb',
      color: GlobalTheme.colors.warning.dark,
      border: `1px solid ${GlobalTheme.colors.warning.light}`,
      borderRadius: GlobalTheme.borderRadius.md,
      padding: GlobalTheme.spacing.md
    },
    error: {
      backgroundColor: '#fef2f2',
      color: GlobalTheme.colors.error.dark,
      border: `1px solid ${GlobalTheme.colors.error.light}`,
      borderRadius: GlobalTheme.borderRadius.md,
      padding: GlobalTheme.spacing.md
    },
    info: {
      backgroundColor: '#f0f9ff',
      color: GlobalTheme.colors.info.dark,
      border: `1px solid ${GlobalTheme.colors.info.light}`,
      borderRadius: GlobalTheme.borderRadius.md,
      padding: GlobalTheme.spacing.md
    }
  }
};

// CSS Custom Properties Generator
export const generateCSSVariables = () => {
  const cssVars = {};
  
  // Colors
  Object.entries(GlobalTheme.colors).forEach(([category, colors]) => {
    if (typeof colors === 'object') {
      Object.entries(colors).forEach(([shade, value]) => {
        cssVars[`--color-${category}-${shade}`] = value;
      });
    } else {
      cssVars[`--color-${category}`] = colors;
    }
  });
  
  // Typography
  Object.entries(GlobalTheme.typography.fontSize).forEach(([size, value]) => {
    cssVars[`--font-size-${size}`] = value;
  });
  
  // Spacing
  Object.entries(GlobalTheme.spacing).forEach(([size, value]) => {
    cssVars[`--spacing-${size}`] = value;
  });
  
  // Border radius
  Object.entries(GlobalTheme.borderRadius).forEach(([size, value]) => {
    cssVars[`--border-radius-${size}`] = value;
  });
  
  return cssVars;
};

// Style helpers
export const createStyles = (styles) => {
  return Object.entries(styles).reduce((acc, [key, value]) => {
    if (typeof value === 'object') {
      acc[key] = createStyles(value);
    } else {
      acc[key] = value;
    }
    return acc;
  }, {});
};

export default GlobalTheme;
