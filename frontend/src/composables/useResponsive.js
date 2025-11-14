/**
 * Responsive utility composable for Vue 3
 *
 * Provides reactive breakpoint detection and responsive utilities
 * that can be reused across components.
 */

import { ref, computed, onMounted, onUnmounted } from 'vue'

// Breakpoint definitions
const BREAKPOINTS = {
  xs: 480,
  sm: 768,
  md: 992,
  lg: 1200,
  xl: 1600
}

// Singleton instance to share state across components
let sharedWindowWidth = null
let listeners = []

export function useResponsive() {
  // Use shared width if available
  if (!sharedWindowWidth) {
    sharedWindowWidth = ref(window.innerWidth)

    const updateWidth = () => {
      sharedWindowWidth.value = window.innerWidth
    }

    window.addEventListener('resize', updateWidth)

    // Store cleanup function
    listeners.push(() => {
      window.removeEventListener('resize', updateWidth)
    })
  }

  const windowWidth = sharedWindowWidth

  // Breakpoint checks
  const isMobile = computed(() => windowWidth.value < BREAKPOINTS.sm)
  const isTablet = computed(() =>
    windowWidth.value >= BREAKPOINTS.sm && windowWidth.value < BREAKPOINTS.md
  )
  const isDesktop = computed(() => windowWidth.value >= BREAKPOINTS.md)
  const isLargeDesktop = computed(() => windowWidth.value >= BREAKPOINTS.lg)
  const isXLarge = computed(() => windowWidth.value >= BREAKPOINTS.xl)

  // Device type
  const deviceType = computed(() => {
    if (isMobile.value) return 'mobile'
    if (isTablet.value) return 'tablet'
    return 'desktop'
  })

  // Responsive columns for grid layouts
  const gridCols = computed(() => {
    if (isMobile.value) return 1
    if (isTablet.value) return 2
    if (isDesktop.value) return 3
    return 4
  })

  // Responsive columns for stat cards
  const statCardCols = computed(() => {
    if (windowWidth.value < BREAKPOINTS.xs) return 1
    if (isMobile.value) return 2
    if (isTablet.value) return 3
    return 4
  })

  // Responsive spacing
  const spacing = computed(() => {
    if (isMobile.value) return {
      padding: '12px',
      margin: '12px',
      gap: '12px'
    }
    if (isTablet.value) return {
      padding: '16px',
      margin: '16px',
      gap: '16px'
    }
    return {
      padding: '20px',
      margin: '20px',
      gap: '20px'
    }
  })

  // Responsive font sizes
  const fontSize = computed(() => {
    if (isMobile.value) return {
      h1: '24px',
      h2: '20px',
      h3: '18px',
      body: '14px',
      small: '12px'
    }
    if (isTablet.value) return {
      h1: '28px',
      h2: '24px',
      h3: '20px',
      body: '15px',
      small: '13px'
    }
    return {
      h1: '32px',
      h2: '28px',
      h3: '24px',
      body: '16px',
      small: '14px'
    }
  })

  // Element Plus table size
  const tableSize = computed(() => {
    return isMobile.value ? 'small' : 'default'
  })

  // Element Plus button size
  const buttonSize = computed(() => {
    return isMobile.value ? 'default' : 'default'
  })

  // Element Plus form label width
  const formLabelWidth = computed(() => {
    if (isMobile.value) return '80px'
    return '120px'
  })

  // Should collapse sidebar by default
  const shouldCollapseSidebar = computed(() => {
    return windowWidth.value < BREAKPOINTS.lg
  })

  // Pagination layout
  const paginationLayout = computed(() => {
    if (isMobile.value) return 'prev, pager, next'
    return 'total, sizes, prev, pager, next, jumper'
  })

  // Dialog width
  const dialogWidth = computed(() => {
    if (isMobile.value) return '95%'
    if (isTablet.value) return '80%'
    return '50%'
  })

  // Card shadow
  const cardShadow = computed(() => {
    return isMobile.value ? 'never' : 'hover'
  })

  // Touch device detection
  const isTouchDevice = computed(() => {
    return (
      'ontouchstart' in window ||
      navigator.maxTouchPoints > 0 ||
      navigator.msMaxTouchPoints > 0
    )
  })

  // Orientation
  const orientation = ref(
    window.matchMedia('(orientation: portrait)').matches ? 'portrait' : 'landscape'
  )

  const updateOrientation = () => {
    orientation.value = window.matchMedia('(orientation: portrait)').matches
      ? 'portrait'
      : 'landscape'
  }

  onMounted(() => {
    window.addEventListener('orientationchange', updateOrientation)
  })

  onUnmounted(() => {
    window.removeEventListener('orientationchange', updateOrientation)
  })

  // Utility functions
  const isBreakpoint = (breakpoint) => {
    return windowWidth.value >= BREAKPOINTS[breakpoint]
  }

  const isAboveBreakpoint = (breakpoint) => {
    return windowWidth.value > BREAKPOINTS[breakpoint]
  }

  const isBelowBreakpoint = (breakpoint) => {
    return windowWidth.value < BREAKPOINTS[breakpoint]
  }

  const isBetweenBreakpoints = (min, max) => {
    return windowWidth.value >= BREAKPOINTS[min] && windowWidth.value < BREAKPOINTS[max]
  }

  // Get responsive value based on breakpoint
  const getResponsiveValue = (values) => {
    // values should be like: { mobile: 1, tablet: 2, desktop: 3 }
    if (isMobile.value) return values.mobile || values.default
    if (isTablet.value) return values.tablet || values.default
    return values.desktop || values.default
  }

  // Responsive class names
  const getResponsiveClasses = (config) => {
    const classes = []

    if (config.mobile && isMobile.value) {
      classes.push(config.mobile)
    }
    if (config.tablet && isTablet.value) {
      classes.push(config.tablet)
    }
    if (config.desktop && isDesktop.value) {
      classes.push(config.desktop)
    }

    return classes.join(' ')
  }

  // Debounce utility for resize handlers
  const debounce = (func, wait = 150) => {
    let timeout
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout)
        func(...args)
      }
      clearTimeout(timeout)
      timeout = setTimeout(later, wait)
    }
  }

  // Throttle utility for scroll handlers
  const throttle = (func, limit = 100) => {
    let inThrottle
    return function executedFunction(...args) {
      if (!inThrottle) {
        func(...args)
        inThrottle = true
        setTimeout(() => (inThrottle = false), limit)
      }
    }
  }

  return {
    // State
    windowWidth,
    orientation,

    // Breakpoint booleans
    isMobile,
    isTablet,
    isDesktop,
    isLargeDesktop,
    isXLarge,

    // Device info
    deviceType,
    isTouchDevice,

    // Responsive values
    gridCols,
    statCardCols,
    spacing,
    fontSize,
    tableSize,
    buttonSize,
    formLabelWidth,
    shouldCollapseSidebar,
    paginationLayout,
    dialogWidth,
    cardShadow,

    // Utility functions
    isBreakpoint,
    isAboveBreakpoint,
    isBelowBreakpoint,
    isBetweenBreakpoints,
    getResponsiveValue,
    getResponsiveClasses,
    debounce,
    throttle,

    // Constants
    BREAKPOINTS
  }
}

// Global cleanup (call this in app unmount if needed)
export function cleanupResponsive() {
  listeners.forEach(cleanup => cleanup())
  listeners = []
  sharedWindowWidth = null
}

// Export breakpoints for direct use
export { BREAKPOINTS }
