declare namespace Api {
  /**
   * namespace SystemManage
   *
   * backend api module: "systemManage"
   */
  namespace SystemManage {
    type CommonSearchParams = Pick<Common.PaginatingCommonParams, 'page' | 'page_size'>;

    /** role */
    type Role = Common.CommonRecord<{
      /** role name */
      name: string;
      /** role description */
      desc: string;
      /** menu ids */
      menu_ids?: number[];
    }>;

    /** role search params */
    type RoleSearchParams = CommonType.RecordNullable<
      Pick<Api.SystemManage.Role, 'name' | 'status'> & CommonSearchParams
    >;

    /** role list */
    type RoleList = Common.PaginatingQueryRecord<Role>;

    /** all role */
    type AllRole = Pick<Role, 'id' | 'name'>;

    /**
     * user gender
     *
     * - "1": "male"
     * - "2": "female"
     */
    type UserGender = '1' | '2';

    /** user */
    type User = Common.CommonRecord<{
      /** user name */
      username: string;
      /** user nick name */
      nickname: string;
      /** user phone */
      phone: string;
      /** user email */
      email: string;
      /** is super user */
      is_superuser: boolean;
      /** user role name collection */
      userRoles: string[];
      /** last login time */
      last_login_at?: string;
      /** last login ip */
      last_login_ip?: string;
    }>;

    /** raw user response from backend (before transform) */
    type RawUser = Omit<User, 'userRoles'> & {
      roles?: { id: number; name: string }[];
    };

    /** user search params */
    type UserSearchParams = CommonType.RecordNullable<
      Pick<Api.SystemManage.User, 'username' | 'nickname' | 'phone' | 'email' | 'is_superuser' | 'status'> &
        CommonSearchParams
    >;

    /** user list */
    type UserList = Common.PaginatingQueryRecord<User>;

    /** change password request */
    type ChangePasswordRequest = {
      /** new password */
      new_password: string;
    };

    /** user create */
    type UserCreate = Pick<User, 'username' | 'nickname' | 'phone' | 'email' | 'status'> & {
      /** user password */
      password: string;
      /** user role name collection */
      userRoles: string[];
    };

    /** user update */
    type UserUpdate = Pick<User, 'username' | 'nickname' | 'phone' | 'email' | 'status'> & {
      /** user role name collection */
      userRoles: string[];
    };

    /**
     * menu type
     *
     * - "1": directory
     * - "2": menu
     * - "3": button
     */
    type MenuType = '1' | '2' | '3';

    type MenuButton = {
      /**
       * button code
       *
       * it can be used to control the button permission
       */
      code: string;
      /** button description */
      desc: string;
    };

    /**
     * icon type
     *
     * - "1": iconify icon
     * - "2": local icon
     */
    type IconType = '1' | '2';

    type MenuPropsOfRoute = Pick<
      import('vue-router').RouteMeta,
      | 'i18nKey'
      | 'keepAlive'
      | 'constant'
      | 'order'
      | 'href'
      | 'hideInMenu'
      | 'activeMenu'
      | 'multiTab'
      | 'fixedIndexInTab'
      | 'query'
    >;

    type Menu = Common.CommonRecord<{
      /** parent menu id */
      parentId: number;
      /** menu type */
      menuType: MenuType;
      /** menu name */
      menuName: string;
      /** route name */
      routeName: string;
      /** route path */
      routePath: string;
      /** component */
      component?: string;
      /** iconify icon name or local icon name */
      icon: string;
      /** icon type */
      iconType: IconType;
      /** buttons */
      buttons?: MenuButton[] | null;
      /** permission code (for button-type menu) */
      permission?: string | null;
      /** children menu */
      children?: Menu[] | null;
      /** is system built-in menu */
      is_system: Common.EnableStatus;
    }> &
      MenuPropsOfRoute;

    /** menu list */
    type MenuList = Common.PaginatingQueryRecord<Menu>;

    type MenuTree = {
      id: number;
      label: string;
      pId: number;
      menuType: MenuType;
      children?: MenuTree[];
    };

    /** 字典 */
    type Dict = Common.CommonRecord<{
      /** 字典名称 */
      name: string;
      /** 字典编码 */
      code: string;
      /** 字典描述 */
      description?: string;
      /** 是否启用 */
      status: Common.EnableStatus;
      /** 是否为系统内置字典 */
      is_system: Common.EnableStatus;
      /** 排序号 */
      sort: number;
    }>;

    /** 字典项 */
    type DictItem = Common.CommonRecord<{
      /** 关联字典ID */
      dict_id: number;
      /** 字典项值 */
      value: string;
      /** 字典项文本 */
      label: string;
      /** 字典项描述 */
      description?: string;
      /** 扩展信息(JSON格式) */
      ext_info?: string;
      /** 排序号 */
      sort: number;
    }>;

    /** 字典搜索参数 */
    type DictSearchParams = CommonType.RecordNullable<
      Pick<Dict, 'name' | 'code' | 'is_system' | 'status'> & CommonSearchParams
    >;

    /** 字典列表 */
    type DictList = Common.PaginatingQueryRecord<Dict>;

    /** 字典项搜索参数 */
    type DictItemSearchParams = CommonType.RecordNullable<
      Pick<DictItem, 'dict_id' | 'label' | 'value' | 'status'> & CommonSearchParams
    >;

    /** 字典项列表 */
    type DictItemList = Common.PaginatingQueryRecord<DictItem>;

    /** 带字典项的字典 */
    type DictWithItems = Dict & {
      items: DictItem[];
    };

    /** 字典创建 */
    type DictCreate = {
      /** 字典名称 */
      name: string;
      /** 字典编码 */
      code: string;
      /** 字典描述 */
      description?: string;
      /** 是否启用 */
      status: Common.EnableStatus;
      /** 是否为系统内置字典 */
      is_system: Common.EnableStatus;
      /** 排序号 */
      sort: number;
    };

    /** 字典更新 */
    type DictUpdate = Partial<DictCreate>;

    /** 字典项创建 */
    type DictItemCreate = {
      /** 关联字典ID */
      dict_id: number;
      /** 字典项值 */
      value: string;
      /** 字典项文本 */
      label: string;
      /** 字典项描述 */
      description?: string;
      /** 扩展信息(JSON格式) */
      ext_info?: string;
      /** 是否启用 */
      status: Common.EnableStatus;
      /** 排序号 */
      sort: number;
    };

    /** 字典项更新 */
    type DictItemUpdate = Partial<DictItemCreate>;

    /** 批量更新字典状态 */
    type DictBatchUpdateStatus = {
      ids: number[];
      status: boolean;
    };

    /** 批量更新字典项状态 */
    type DictItemBatchUpdateStatus = {
      ids: number[];
      status: boolean;
    };

    /** 配置类型 */
    type ConfigType = 'string' | 'number' | 'boolean' | 'json' | 'array';

    /** 配置分组 */
    type ConfigGroup = 'system' | 'security' | 'log' | 'network' | 'storage' | 'custom';

    /** 系统配置 */
    type Config = Common.CommonRecord<{
      /** 配置键名 */
      key: string;
      /** 配置值 */
      value: string;
      /** 默认值 */
      default_value?: string;
      /** 校验规则 */
      validation_rule?: string;
      /** 配置描述 */
      description?: string;
      /** 配置类型 */
      type: ConfigType;
      /** 配置分组 */
      group: ConfigGroup;

      /** 是否为系统内置配置 */
      is_system: Common.EnableStatus;
    }>;

    /** 配置搜索参数 */
    type ConfigSearchParams = CommonType.RecordNullable<
      Pick<Config, 'key' | 'description' | 'type' | 'group' | 'is_system'> & CommonSearchParams
    >;

    /** 配置列表 */
    type ConfigList = Common.PaginatingQueryRecord<Config>;

    /** 配置创建 */
    type ConfigCreate = Pick<
      Config,
      'key' | 'value' | 'default_value' | 'validation_rule' | 'description' | 'type' | 'group' | 'is_system'
    >;

    /** 配置更新 */
    type ConfigUpdate = Partial<ConfigCreate>;

    /** 批量更新配置 */
    type ConfigBatchUpdate = {
      configs: Array<{ id: number; value: string }>;
    };

    /** 重置配置 */
    type ConfigReset = {
      ids: string[];
    };

    /** 登录日志搜索参数 */
    type LoginLogSearchParams = CommonType.RecordNullable<{
      username?: string;
      ip?: string;
      status?: boolean | null;
      start_time?: string;
      end_time?: string;
    } & CommonSearchParams>;

    /** 登录日志 */
    type LoginLog = {
      id: number;
      username: string;
      ip: string | null;
      status: boolean;
      detail: string | null;
      user_agent: string | null;
      login_time: string | null;
      created_at: string | null;
    };

    /** 登录日志列表 */
    type LoginLogList = Common.PaginatingQueryRecord<LoginLog>;

    /** 操作日志搜索参数 */
    type OperationLogSearchParams = CommonType.RecordNullable<{
      username?: string;
      module?: string;
      action?: string;
      start_time?: string;
      end_time?: string;
    } & CommonSearchParams>;

    /** 操作日志 */
    type OperationLog = {
      id: number;
      user_id: number;
      username: string;
      module: string;
      action: string;
      description: string | null;
      method: string | null;
      path: string | null;
      ip: string | null;
      response_code: number | null;
      response_result: string | null;
      elapsed_ms: number | null;
      created_at: string | null;
    };

    /** 操作日志详情 */
    type OperationLogDetail = OperationLog & {
      request_params: string | null;
    };

    /** 操作日志列表 */
    type OperationLogList = Common.PaginatingQueryRecord<OperationLog>;

    /** 在线用户搜索参数 */
    type OnlineUserSearchParams = CommonType.RecordNullable<{
      username?: string;
      ip?: string;
    } & CommonSearchParams>;

    /** 在线用户 */
    type OnlineUser = {
      user_id: number;
      username: string | null;
      nickname: string | null;
      avatar: string | null;
      session_id: string;
      ip: string | null;
      user_agent: string | null;
      login_time: string | null;
    };

    /** 在线用户列表 */
    type OnlineUserList = Common.PaginatingQueryRecord<OnlineUser>;

    /** IP 黑名单 */
    type IpBlacklist = {
      id: number;
      ip: string;
      type: string;
      reason: string | null;
      expire_at: string | null;
      creator_id: number | null;
      created_at: string;
      updated_at: string;
    };

    /** IP 黑名单搜索参数 */
    type IpBlacklistSearchParams = CommonType.RecordNullable<{
      ip?: string;
      type?: string;
      start_date?: string;
      end_date?: string;
    } & CommonSearchParams>;

    /** IP 黑名单列表 */
    type IpBlacklistList = Common.PaginatingQueryRecord<IpBlacklist>;

    /** IP 黑名单新增 */
    type IpBlacklistCreate = {
      ip: string;
      type: string;
      reason?: string;
      expire_at?: string | null;
    };

    /** IP 黑名单批量删除 */
    type IpBlacklistBatchDelete = {
      ids: number[];
    };
  }
}
