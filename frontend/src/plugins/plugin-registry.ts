import type { Component } from 'vue';
import { i18n } from '@/locales';

type HeaderPlugin = Component;

const _headerPlugins: HeaderPlugin[] = [];

export function registerHeaderPlugin(component: HeaderPlugin) {
  _headerPlugins.push(component);
}

export function getHeaderPlugins(): HeaderPlugin[] {
  return _headerPlugins;
}

export function registerPluginI18n(pluginName: string, messages: Record<string, Record<string, unknown>>) {
  for (const [locale, msg] of Object.entries(messages)) {
    i18n.global.mergeLocaleMessage(locale, msg);
  }
}
