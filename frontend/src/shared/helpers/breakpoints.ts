/** Named CSS media queries for the adaptive layout tiers. */
export const breakpoints = {
  /** Desktop: all panes visible statically (>= 1024px). */
  desktop: "(min-width: 1024px)",
  /** Tablet: friend panel becomes a drawer (768px-1023px). */
  tablet: "(min-width: 768px) and (max-width: 1023.98px)",
  /** Mobile: both sidebars become drawers (< 768px). */
  mobile: "(max-width: 767.98px)",
} as const;
