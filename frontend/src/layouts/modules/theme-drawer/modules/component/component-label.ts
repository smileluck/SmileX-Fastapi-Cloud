import { i18n } from '@/locales';

/**
 * Localized component label, falling back to the raw NaiveUI component name
 * when no translation is registered.
 *
 * Reads the current locale's messages reactively (via `locale.value`), so the
 * label updates on language switch without relying on the deprecated `te` API.
 */
export function componentLabel(name: string): string {
  const locale = i18n.global.locale.value;
  const messages = i18n.global.getLocaleMessage(locale) as {
    theme?: { componentConfig?: { components?: Record<string, string> } };
  };
  const val = messages?.theme?.componentConfig?.components?.[name];
  return typeof val === 'string' ? val : name;
}
