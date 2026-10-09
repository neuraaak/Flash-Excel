import { ICONS } from '../vendor/icons.js';

/**
 * Universal icon component.
 * Usage : <LucideIcon name="settings" :size="18" :stroke="1.7" />
 *
 * Props :
 *   name   - key in ICONS (e.g. "settings", "x", "moon")
 *   size   — largeur/hauteur en px (default: 16)
 *   stroke - stroke width (default: 1.7)
 */
export default {
  name: 'LucideIcon',
  props: {
    name:   { type: String, required: true },
    size:   { type: [Number, String], default: 16 },
    stroke: { type: [Number, String], default: 1.7 },
  },
  computed: {
    svgInner() {
      return ICONS[this.name] ?? '';
    },
  },
  template: `
    <svg
      :width="size"
      :height="size"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      :stroke-width="stroke"
      stroke-linecap="round"
      stroke-linejoin="round"
      v-html="svgInner"
      aria-hidden="true"
    />
  `,
};
