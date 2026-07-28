/**
 * Property metadata + inference helpers for the NaiveUI component theme config.
 *
 * The catalog data lives in `theme-catalog.generated.ts` (codegen output); the
 * *contract* (types) and the inference logic live here, hand-written and stable.
 */

/** Input control kind for a GlobalThemeOverrides property */
export type PropKind = 'color' | 'number' | 'text';

/** Display group for a GlobalThemeOverrides property */
export type PropGroup = 'color' | 'size' | 'font' | 'other';

/** Order of groups in the editor UI */
export const PROP_GROUP_ORDER: PropGroup[] = ['color', 'size', 'font', 'other'];

/** One property definition, extracted from naive-ui's GlobalThemeOverrides type */
export interface ThemePropDef {
  /** GlobalThemeOverrides property name, e.g. "borderRadius", "colorPrimary" */
  key: string;
  /** Raw type text from the declaration; used as a hint for kind inference */
  typeText: string;
}

/** One component's property definitions */
export interface ThemeComponentDef {
  /** Component name = GlobalThemeOverrides top-level key, e.g. "common", "Button" */
  name: string;
  props: ThemePropDef[];
}

/**
 * Infer the input control kind from a property key + its type text.
 *
 * - keys containing `Color` (string-valued) → color picker
 * - purely numeric types → number input
 * - everything else (CSS strings like "10px", "600", "small") → text input
 */
export function inferPropKind(key: string, typeText: string): PropKind {
  if (/Color/i.test(key)) return 'color';
  if (
    typeText === 'number' ||
    /^number\s*(\|\s*undefined)?$/.test(typeText) ||
    /^undefined\s*(\|\s*number)?$/.test(typeText)
  )
    return 'number';
  return 'text';
}

/**
 * Infer the display group from a property key.
 * Color takes precedence; then font; then size; the rest → other.
 */
export function inferPropGroup(key: string): PropGroup {
  if (/Color/i.test(key)) return 'color';
  if (/font|lineHeight|letterSpacing/i.test(key)) return 'font';
  if (/radius|padding|margin|width|height|gap|size|offset|border/i.test(key)) return 'size';
  return 'other';
}

/** Dimensional keys accept CSS length values like "8px" / "0.5rem" — show a unit hint */
const UNIT_HINT_RE = /(size|radius|padding|margin|width|height|gap|offset|border|lineHeight|letterSpacing)/i;

/** Whether a text-input property should show a CSS unit hint (px / rem) */
export function needsUnitHint(key: string): boolean {
  return UNIT_HINT_RE.test(key);
}
