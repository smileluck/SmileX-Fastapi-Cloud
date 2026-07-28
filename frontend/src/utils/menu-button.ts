import { $t } from '@/locales';

type ActionKey = keyof App.I18n.Schema['common']['actions'];

/**
 * action 词根 → i18n action key 映射。
 * 词根来自按钮 name（如 manage_dept_add）的末段，或 permission（如 sys:dept:add）的末段。
 */
const ACTION_MAP: Record<string, ActionKey> = {
  list: 'list',
  add: 'add',
  edit: 'edit',
  delete: 'delete',
  remove: 'remove',
  publish: 'publish',
  detail: 'detail',
  status: 'status',
  trigger: 'trigger',
  view: 'view',
  kick: 'kick',
  download: 'download',
  upload: 'upload',
  assign: 'assign'
};

/**
 * 把按钮的 permission（如 `sys:dept:add`）解析为 action 词根。
 * 优先匹配两段（log:detail / log:delete），再匹配单段。
 */
function resolveFromPermission(permission: string): ActionKey | null {
  const parts = permission.split(':');
  if (parts.length < 2) return null;
  if (parts.length >= 3) {
    const lastTwo = parts.slice(-2).join(':');
    if (lastTwo === 'log:detail') return 'logDetail';
    if (lastTwo === 'log:delete') return 'logDelete';
  }
  return ACTION_MAP[parts[parts.length - 1]] ?? null;
}

/**
 * 把按钮的 name（如 `manage_dept_add`）解析为 action 词根。
 * 特殊：name 末段是 logdetail/logdelete 时映射到 logDetail/logDelete。
 */
function resolveFromName(name: string): ActionKey | null {
  const parts = name.split('_');
  if (parts.length < 2) return null;
  const last = parts[parts.length - 1].toLowerCase();
  return ACTION_MAP[last] ?? null;
}

/**
 * 渲染按钮的显示标签：`{父菜单名} - {动作}` 或 fallback 到原 name。
 *
 * @param buttonName  按钮的 name（如 manage_dept_add）
 * @param permission  按钮的 permission（如 sys:dept:add），可选
 * @param parentName  父菜单的 name（如 manage_dept），可选
 */
export function formatButtonLabel(buttonName: string, permission?: string | null, parentName?: string | null): string {
  const actionKey = (permission && resolveFromPermission(permission)) || resolveFromName(buttonName);
  const actionLabel = actionKey ? $t(`common.actions.${actionKey}`) : '';
  const parentLabel = parentName ? $t(`route.${parentName}` as App.I18n.I18nKey) : '';

  // 父菜单 i18n 没翻译（fallback 到 key 本身）→ 不拼父级
  const cleanParent = parentLabel && parentLabel !== `route.${parentName}` ? parentLabel : '';

  if (cleanParent && actionLabel) return `${cleanParent} - ${actionLabel}`;
  if (actionLabel) return actionLabel;
  return buttonName;
}
