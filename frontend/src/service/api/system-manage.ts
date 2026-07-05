import { request } from '../request';
import { enableStatusToBoolean } from '@/utils/status';

/** get role list */
export function fetchGetRoleList(params?: Api.SystemManage.RoleSearchParams) {
  return request<Api.SystemManage.RoleList>({
    url: '/admin/sys/role/list',
    method: 'get',
    params
  });
}

/** get all roles
 *
 * these roles are all enabled
 */
export function fetchGetAllRoles() {
  return request<Api.SystemManage.AllRole[]>({
    url: '/admin/sys/role/all',
    method: 'get'
  });
}

/** get role by id */
export function fetchGetRole(roleId: number) {
  return request<Api.SystemManage.Role>({
    url: `/admin/sys/role/${roleId}`,
    method: 'get'
  });
}

/** create role */
export function fetchCreateRole(role: Api.SystemManage.RoleCreateRequest) {
  return request<Api.SystemManage.Role>({
    url: '/admin/sys/role/add',
    method: 'post',
    data: {
      name: role.name,
      desc: role.desc,
      status: enableStatusToBoolean(role.status),
      sort: 0,
      data_scope: role.data_scope || 'SELF',
      menu_ids: role.menu_ids || []
    }
  });
}

/** update role */
export function fetchUpdateRole(roleId: number, role: Api.SystemManage.RoleUpdateRequest) {
  return request<Api.SystemManage.Role>({
    url: `/admin/sys/role/${roleId}`,
    method: 'put',
    data: {
      name: role.name,
      desc: role.desc,
      status: enableStatusToBoolean(role.status),
      data_scope: role.data_scope || 'SELF',
      menu_ids: role.menu_ids || []
    }
  });
}

/** delete role */
export function fetchDeleteRole(roleId: number) {
  return request<void>({
    url: `/admin/sys/role/${roleId}`,
    method: 'delete'
  });
}

/** batch delete roles */
export function fetchBatchDeleteRole(roleIds: string[]) {
  return request<void>({
    url: '/admin/sys/role/batch',
    method: 'delete',
    data: roleIds
  });
}

/** assign menu to role */
export function fetchAssignMenuToRole(roleId: number, menuIds: number[]) {
  return request<Api.SystemManage.Role>({
    url: `/admin/sys/role/${roleId}/menus`,
    method: 'post',
    data: {
      menu_ids: menuIds
    }
  });
}

/** get menu list */
export function fetchGetMenuList() {
  return request<Api.SystemManage.MenuList>({
    url: '/admin/sys/menu/list',
    method: 'get'
  });
}

/** get all pages */
export function fetchGetAllPages() {
  return request<string[]>({
    url: '/admin/sys/menu/pages',
    method: 'get'
  });
}

/** get menu tree */
export function fetchGetMenuTree() {
  return request<Api.SystemManage.MenuTree[]>({
    url: '/admin/sys/menu/tree',
    method: 'get'
  });
}

/** get user-scoped menu tree for role permission assignment (includes buttons) */
export function fetchGetAssignMenuTree() {
  return request<Api.SystemManage.MenuTree[]>({
    url: '/admin/sys/menu/assign-tree',
    method: 'get'
  });
}

/** get menu list tree */
export function fetchGetMenuListTree() {
  return request<Api.SystemManage.Menu[]>({
    url: '/admin/sys/menu/list-tree',
    method: 'get'
  });
}

/** create menu */
export function fetchCreateMenu(menu: Partial<Api.SystemManage.Menu>) {
  return request<Api.SystemManage.Menu>({
    url: '/admin/sys/menu/add',
    method: 'post',
    data: {
      parent_id: menu.parentId || null,
      name: menu.menuName,
      path: menu.routePath,
      component: menu.component,
      redirect: null,
      permission: menu.permission || null,
      meta_icon: menu.icon,
      meta_icon_type: Number(menu.iconType) || 1,
      meta_hidden: menu.hideInMenu || false,
      meta_breadcrumb: true,
      meta_href: menu.href || null,
      meta_keep_alive: menu.keepAlive || false,
      status: true,
      type: menu.menuType === '1' ? 'catalog' : menu.menuType === '3' ? 'button' : 'menu',
      sort: menu.order || 0,
      is_system: enableStatusToBoolean(menu.is_system)
    }
  });
}

/** update menu */
export function fetchUpdateMenu(menuId: number, menu: Partial<Api.SystemManage.Menu>) {
  return request<Api.SystemManage.Menu>({
    url: `/admin/sys/menu/${menuId}`,
    method: 'put',
    data: {
      parent_id: menu.parentId || null,
      name: menu.menuName,
      path: menu.routePath,
      component: menu.component,
      meta_icon: menu.icon,
      meta_icon_type: Number(menu.iconType) || 1,
      meta_hidden: menu.hideInMenu || false,
      meta_href: menu.href || null,
      meta_keep_alive: menu.keepAlive || false,
      status: enableStatusToBoolean(menu.status),
      sort: menu.order,
      is_system: enableStatusToBoolean(menu.is_system)
    }
  });
}

/** delete menu */
export function fetchDeleteMenu(menuId: number) {
  return request<void>({
    url: `/admin/sys/menu/${menuId}`,
    method: 'delete'
  });
}

/** batch delete menus */
export function fetchBatchDeleteMenu(menuIds: number[]) {
  return request<void>({
    url: '/admin/sys/menu/batch/delete',
    method: 'delete',
    data: menuIds
  });
}

/** change user password */
export function fetchChangeUserPassword(userId: number, newPassword: string) {
  return request<void>({
    url: `/admin/sys/user/${userId}/password`,
    method: 'put',
    data: {
      new_password: newPassword
    }
  });
}

/** create user */
export function fetchCreateUser(user: Api.SystemManage.UserCreateRequest) {
  return request<Api.SystemManage.User>({
    url: '/admin/sys/user/add',
    method: 'post',
    data: {
      username: user.username,
      nickname: user.nickname,
      phone: user.phone,
      email: user.email,
      password: user.password,
      status: enableStatusToBoolean(user.status),
      role_ids: user.role_ids || [],
      dept_id: user.dept_id ?? null
    }
  });
}

/** update user */
export function fetchUpdateUser(userId: number, user: Api.SystemManage.UserUpdateRequest) {
  return request<Api.SystemManage.User>({
    url: `/admin/sys/user/${userId}`,
    method: 'put',
    data: {
      username: user.username,
      nickname: user.nickname,
      phone: user.phone,
      email: user.email,
      status: enableStatusToBoolean(user.status),
      ...(user.role_ids !== undefined ? { role_ids: user.role_ids } : {}),
      ...(user.dept_id !== undefined ? { dept_id: user.dept_id } : {})
    }
  });
}

/** delete user */
export function fetchDeleteUser(userId: number) {
  return request<void>({
    url: `/admin/sys/user/${userId}`,
    method: 'delete'
  });
}

/** get user list with transform */
export function fetchGetUserList(params?: Api.SystemManage.UserSearchParams) {
  return request<Api.SystemManage.UserList>({
    url: '/admin/sys/user/list',
    method: 'get',
    params
  });
}

/** ==================== 字典管理 API ==================== */

/** get dict list */
export function fetchGetDictList(params?: Api.SystemManage.DictSearchParams) {
  return request<Api.SystemManage.DictList>({
    url: '/admin/sys/dict/list',
    method: 'get',
    params
  });
}

/** get all dicts */
export function fetchGetAllDicts(status?: boolean) {
  return request<Api.SystemManage.Dict[]>({
    url: '/admin/sys/dict/all',
    method: 'get',
    params: { status }
  });
}

/** get dict by code */
export function fetchGetDictByCode(code: string) {
  return request<Api.SystemManage.DictWithItems>({
    url: `/admin/sys/dict/code/${code}`,
    method: 'get'
  });
}

/** get dict by id */
export function fetchGetDict(dictId: number) {
  return request<Api.SystemManage.Dict>({
    url: `/admin/sys/dict/${dictId}`,
    method: 'get'
  });
}

/** get dict with items */
export function fetchGetDictWithItems(dictId: number) {
  return request<Api.SystemManage.DictWithItems>({
    url: `/admin/sys/dict/${dictId}/with-items`,
    method: 'get'
  });
}

/** create dict */
export function fetchCreateDict(dict: Api.SystemManage.DictCreate) {
  const transformedDict = {
    ...dict,
    status: enableStatusToBoolean(dict.status),
    is_system: enableStatusToBoolean(dict.is_system)
  };

  return request<Api.SystemManage.Dict>({
    url: '/admin/sys/dict/add',
    method: 'post',
    data: transformedDict
  });
}

/** update dict */
export function fetchUpdateDict(dictId: number, dict: Api.SystemManage.DictUpdate) {
  const transformedDict = {
    ...dict,
    ...(dict.status !== undefined ? { status: enableStatusToBoolean(dict.status) } : {}),
    ...(dict.is_system !== undefined ? { is_system: enableStatusToBoolean(dict.is_system) } : {})
  };

  return request<Api.SystemManage.Dict>({
    url: `/admin/sys/dict/${dictId}`,
    method: 'put',
    data: transformedDict
  });
}

/** batch update dict status */
export function fetchBatchUpdateDictStatus(data: Api.SystemManage.DictBatchUpdateStatus) {
  return request<void>({
    url: '/admin/sys/dict/batch/status',
    method: 'put',
    data
  });
}

/** delete dict */
export function fetchDeleteDict(dictId: number) {
  return request<void>({
    url: `/admin/sys/dict/${dictId}`,
    method: 'delete'
  });
}

/** ==================== 字典项管理 API ==================== */

/** get dict item list */
export function fetchGetDictItemList(params?: Api.SystemManage.DictItemSearchParams) {
  return request<Api.SystemManage.DictItemList>({
    url: '/admin/sys/dict/item/list',
    method: 'get',
    params
  });
}

/** get dict items by dict code */
export function fetchGetDictItemsByDictCode(dictCode: string) {
  return request<Api.SystemManage.DictItem[]>({
    url: `/admin/sys/dict/item/all/${dictCode}`,
    method: 'get'
  });
}

/** get dict item by id */
export function fetchGetDictItem(itemId: number) {
  return request<Api.SystemManage.DictItem>({
    url: `/admin/sys/dict/item/${itemId}`,
    method: 'get'
  });
}

/** create dict item */
export function fetchCreateDictItem(item: Api.SystemManage.DictItemCreate) {
  return request<Api.SystemManage.DictItem>({
    url: '/admin/sys/dict/item/add',
    method: 'post',
    data: {
      ...item,
      status: enableStatusToBoolean(item.status)
    }
  });
}

/** update dict item */
export function fetchUpdateDictItem(itemId: number, item: Api.SystemManage.DictItemUpdate) {
  const transformedItem = {
    ...item,
    ...(item.status !== undefined ? { status: enableStatusToBoolean(item.status) } : {})
  };

  return request<Api.SystemManage.DictItem>({
    url: `/admin/sys/dict/item/${itemId}`,
    method: 'put',
    data: transformedItem
  });
}

/** batch update dict item status */
export function fetchBatchUpdateDictItemStatus(data: Api.SystemManage.DictItemBatchUpdateStatus) {
  return request<void>({
    url: '/admin/sys/dict/item/batch/status',
    method: 'put',
    data
  });
}

/** delete dict item */
export function fetchDeleteDictItem(itemId: number) {
  return request<void>({
    url: `/admin/sys/dict/item/${itemId}`,
    method: 'delete'
  });
}

/** ==================== 系统配置管理 API ==================== */

/** get config list */
export function fetchGetConfigList(params?: Api.SystemManage.ConfigSearchParams) {
  return request<Api.SystemManage.ConfigList>({
    url: '/admin/sys/config/list',
    method: 'get',
    params
  });
}

/** get all configs */
export function fetchGetAllConfigs(group?: Api.SystemManage.ConfigGroup, editableOnly?: boolean) {
  return request<Api.SystemManage.Config[]>({
    url: '/admin/sys/config/all',
    method: 'get',
    params: { group, editable_only: editableOnly }
  });
}

/** get configs by group */
export function fetchGetConfigsByGroup(group: Api.SystemManage.ConfigGroup, editableOnly?: boolean) {
  return request<Api.SystemManage.Config[]>({
    url: `/admin/sys/config/group/${group}`,
    method: 'get',
    params: { editable_only: editableOnly }
  });
}

/** get config by id */
export function fetchGetConfigById(configId: number) {
  return request<Api.SystemManage.Config>({
    url: `/admin/sys/config/id/${configId}`,
    method: 'get'
  });
}

/** get config by key */
export function fetchGetConfigByKey(configKey: string) {
  return request<Api.SystemManage.Config>({
    url: `/admin/sys/config/key/${configKey}`,
    method: 'get'
  });
}

/** get config value */
export function fetchGetConfigValue(configKey: string, defaultValue?: string) {
  return request({
    url: `/admin/sys/config/value/${configKey}`,
    method: 'get',
    params: { default: defaultValue }
  });
}

/** create config */
export function fetchCreateConfig(config: Api.SystemManage.ConfigCreate) {
  const transformedConfig = {
    ...config,
    is_system: config.is_system === '1'
  };

  return request<Api.SystemManage.Config>({
    url: '/admin/sys/config/add',
    method: 'post',
    data: transformedConfig
  });
}

/** update config */
export function fetchUpdateConfig(configId: number, config: Api.SystemManage.ConfigUpdate) {
  const transformedConfig = {
    ...config,
    is_system: config.is_system === '1'
  };

  return request<Api.SystemManage.Config>({
    url: `/admin/sys/config/${configId}`,
    method: 'put',
    data: transformedConfig
  });
}

/** batch update configs */
export function fetchBatchUpdateConfigs(data: Api.SystemManage.ConfigBatchUpdate) {
  return request<void>({
    url: '/admin/sys/config/batch/update',
    method: 'put',
    data
  });
}

/** reset configs */
export function fetchResetConfigs(data: Api.SystemManage.ConfigReset) {
  return request<void>({
    url: '/admin/sys/config/batch/reset',
    method: 'put',
    data
  });
}

/** delete config */
export function fetchDeleteConfig(configId: number) {
  return request<void>({
    url: `/admin/sys/config/${configId}`,
    method: 'delete'
  });
}

/** batch delete configs */
export function fetchBatchDeleteConfig(configIds: number[]) {
  return request<void>({
    url: '/admin/sys/config/batch',
    method: 'delete',
    data: configIds
  });
}

/** ==================== IP 黑名单管理 API ==================== */

/** get ip blacklist list */
export function fetchGetIpBlacklistList(params?: Api.SystemManage.IpBlacklistSearchParams) {
  return request<Api.SystemManage.IpBlacklistList>({
    url: '/admin/sys/ip-blacklist/list',
    method: 'get',
    params
  });
}

/** create ip blacklist */
export function fetchCreateIpBlacklist(data: Api.SystemManage.IpBlacklistCreate) {
  return request<Api.SystemManage.IpBlacklist>({
    url: '/admin/sys/ip-blacklist/add',
    method: 'post',
    data
  });
}

/** delete ip blacklist */
export function fetchDeleteIpBlacklist(id: number) {
  return request<void>({
    url: `/admin/sys/ip-blacklist/${id}`,
    method: 'delete'
  });
}

/** batch delete ip blacklist */
export function fetchBatchDeleteIpBlacklist(ids: number[]) {
  return request<void>({
    url: '/admin/sys/ip-blacklist/batch/delete',
    method: 'delete',
    data: { ids }
  });
}

/** ==================== 部门管理 API ==================== */

/** get dept list */
export function fetchGetDeptList(params?: Api.SystemManage.DeptSearchParams) {
  return request<Api.SystemManage.DeptList>({
    url: '/admin/sys/dept/list',
    method: 'get',
    params
  });
}

/** get dept tree (full fields) */
export function fetchGetDeptTree(onlyActive = false) {
  return request<Api.SystemManage.Dept[]>({
    url: '/admin/sys/dept/tree',
    method: 'get',
    params: { only_active: onlyActive }
  });
}

/** get dept tree (simplified, for dropdowns) */
export function fetchGetDeptTreeSelect(onlyActive = true) {
  return request<Api.SystemManage.DeptTree[]>({
    url: '/admin/sys/dept/tree-select',
    method: 'get',
    params: { only_active: onlyActive }
  });
}

/** get dept by id */
export function fetchGetDept(deptId: number) {
  return request<Api.SystemManage.Dept>({
    url: `/admin/sys/dept/${deptId}`,
    method: 'get'
  });
}

/** create dept */
export function fetchCreateDept(dept: Api.SystemManage.DeptCreate) {
  return request<Api.SystemManage.Dept>({
    url: '/admin/sys/dept/add',
    method: 'post',
    data: {
      ...dept,
      status: enableStatusToBoolean(dept.status)
    }
  });
}

/** update dept */
export function fetchUpdateDept(deptId: number, dept: Api.SystemManage.DeptUpdate) {
  return request<Api.SystemManage.Dept>({
    url: `/admin/sys/dept/${deptId}`,
    method: 'put',
    data: {
      ...dept,
      ...(dept.status !== undefined ? { status: enableStatusToBoolean(dept.status) } : {})
    }
  });
}

/** delete dept */
export function fetchDeleteDept(deptId: number) {
  return request<void>({
    url: `/admin/sys/dept/${deptId}`,
    method: 'delete'
  });
}

/** batch delete depts */
export function fetchBatchDeleteDept(deptIds: number[]) {
  return request<void>({
    url: '/admin/sys/dept/batch',
    method: 'delete',
    data: deptIds
  });
}

/** batch update dept status */
export function fetchBatchUpdateDeptStatus(data: Api.SystemManage.DeptBatchUpdateStatus) {
  return request<void>({
    url: '/admin/sys/dept/batch/status',
    method: 'put',
    data
  });
}

/** get merchant list */
export function fetchGetMerchantList(params?: Api.SystemManage.MerchantSearchParams) {
  return request<Api.SystemManage.MerchantList>({
    url: '/admin/sys/merchant/list',
    method: 'get',
    params
  });
}

/** get merchant by id */
export function fetchGetMerchant(merchantId: number) {
  return request<Api.SystemManage.Merchant>({
    url: `/admin/sys/merchant/${merchantId}`,
    method: 'get'
  });
}

/** create merchant (返回一次性明文 app_secret) */
export function fetchCreateMerchant(merchant: Api.SystemManage.MerchantCreate) {
  return request<Api.SystemManage.MerchantCreateResult>({
    url: '/admin/sys/merchant/add',
    method: 'post',
    data: {
      ...merchant,
      status: enableStatusToBoolean(merchant.status)
    }
  });
}

/** update merchant */
export function fetchUpdateMerchant(merchantId: number, merchant: Api.SystemManage.MerchantUpdate) {
  return request<Api.SystemManage.Merchant>({
    url: `/admin/sys/merchant/${merchantId}`,
    method: 'put',
    data: {
      ...merchant,
      ...(merchant.status !== undefined ? { status: enableStatusToBoolean(merchant.status) } : {})
    }
  });
}

/** delete merchant */
export function fetchDeleteMerchant(merchantId: number) {
  return request<void>({
    url: `/admin/sys/merchant/${merchantId}`,
    method: 'delete'
  });
}

/** reset merchant secret (返回一次性明文 app_secret) */
export function fetchResetMerchantSecret(merchantId: number) {
  return request<Api.SystemManage.MerchantSecretResetResult>({
    url: `/admin/sys/merchant/${merchantId}/reset-secret`,
    method: 'put'
  });
}
