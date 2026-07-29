import { $t } from '@/locales';

/**
 * Transform record to option
 *
 * @example
 *   ```ts
 *   const record = {
 *     key1: 'label1',
 *     key2: 'label2'
 *   };
 *   const options = transformRecordToOption(record);
 *   // [
 *   //   { value: 'key1', label: 'label1' },
 *   //   { value: 'key2', label: 'label2' }
 *   // ]
 *   ```;
 *
 * @param record
 */
export function transformRecordToOption<T extends Record<string, string>>(record: T) {
  return Object.entries(record).map(([value, label]) => ({
    value,
    label
  })) as CommonType.Option<keyof T, T[keyof T]>[];
}

/**
 * Translate options
 *
 * @param options
 */
export function translateOptions(options: CommonType.Option<string, App.I18n.I18nKey>[]) {
  return options.map(option => ({
    ...option,
    label: $t(option.label)
  }));
}

/**
 * 计算搜索栏「搜索/重置」按钮所在 NGrid 网格项的响应式 span，
 * 使按钮填满最后一行的剩余宽度，配合 `NSpace justify="end"` 让按钮固定在搜索区右下角。
 *
 * 约定字段网格为 24 栏，字段默认每行数量：移动端(base) 1 个 / s 断点 2 个 / m 断点 4 个
 * （即字段使用 `span="24 s:12 m:6"`）。
 *
 * @param fieldCount 搜索字段数量（不含按钮所在网格项）
 * @param perRow 各断点下每行字段数量，默认 `{ base: 1, s: 2, m: 4 }`
 * @returns 与字段同格式的 span 字符串
 *
 * @example
 *   ```ts
 *   getGridActionSpan(5); // '24 s:12 m:18'  最后一行 1 字段，按钮填满剩余 18 栏
 *   getGridActionSpan(4); // '24 s:24 m:24'  字段刚好排满，按钮独占末行
 *   ```
 */
export function getGridActionSpan(
  fieldCount: number,
  perRow: { base: number; s: number; m: number } = { base: 1, s: 2, m: 4 }
): string {
  const TOTAL = 24;

  function spanOf(cols: number) {
    const remainder = fieldCount % cols;
    return remainder === 0 ? TOTAL : TOTAL - remainder * (TOTAL / cols);
  }

  return `${spanOf(perRow.base)} s:${spanOf(perRow.s)} m:${spanOf(perRow.m)}`;
}

/**
 * Toggle html class
 *
 * @param className
 */
export function toggleHtmlClass(className: string) {
  function add() {
    document.documentElement.classList.add(className);
  }

  function remove() {
    document.documentElement.classList.remove(className);
  }

  return {
    add,
    remove
  };
}
