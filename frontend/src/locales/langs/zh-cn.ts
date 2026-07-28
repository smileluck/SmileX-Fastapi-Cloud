const local: App.I18n.Schema = {
  system: {
    title: 'SmileX管理系统',
    updateTitle: '系统版本更新通知',
    updateContent: '检测到系统有新版本发布，是否立即刷新页面？',
    updateConfirm: '立即刷新',
    updateCancel: '稍后再说'
  },
  common: {
    selectAtLeastOne: '请至少选择一条数据',
    pleaseSelect: '请先选择要操作的数据',
    action: '操作',
    add: '新增',
    addSuccess: '添加成功',
    backToHome: '返回首页',
    back: '返回',
    batchDelete: '批量删除',
    cancel: '取消',
    close: '关闭',
    check: '勾选',
    selectAll: '全选',
    expandColumn: '展开列',
    columnSetting: '列设置',
    config: '配置',
    confirm: '确认',
    delete: '删除',
    deleteSuccess: '删除成功',
    deleteFailed: '删除失败',
    confirmDelete: '确认删除吗？',
    loadDataFailed: '加载数据失败',
    edit: '编辑',
    warning: '警告',
    error: '错误',
    index: '序号',
    keywordSearch: '请输入关键词搜索',
    logout: '退出登录',
    logoutConfirm: '确认退出登录吗？',
    lookForward: '敬请期待',
    modify: '修改',
    modifySuccess: '修改成功',
    saveSuccess: '保存成功',
    status: '状态',
    noData: '无数据',
    operate: '操作',
    pleaseCheckValue: '请检查输入的值是否合法',
    pleaseEnter: '请输入',
    refresh: '刷新',
    reset: '重置',
    search: '搜索',
    switch: '切换',
    tip: '提示',
    title: '标题',
    trigger: '触发',
    update: '更新',
    updateSuccess: '更新成功',
    updateFailed: '更新失败',
    userCenter: '个人中心',
    changePassword: '修改密码',
    yesOrNo: {
      yes: '是',
      no: '否'
    },
    actions: {
      list: '查看列表',
      add: '新增',
      edit: '编辑',
      delete: '删除',
      remove: '移除',
      publish: '发布',
      detail: '详情',
      status: '状态切换',
      trigger: '手动执行',
      view: '查看',
      kick: '踢下线',
      download: '下载',
      upload: '上传',
      assign: '分配',
      logDetail: '日志详情',
      logDelete: '删除日志'
    }
  },
  captcha: {
    success: '验证成功',
    fail: '验证失败',
    refresh: '刷新验证码',
    slideToVerify: '向右滑动完成验证',
    completeFirst: '请先完成下方滑块验证后再登录',
    selectPlaceholder: '请选择'
  },
  request: {
    logout: '请求失败后登出用户',
    logoutMsg: '用户状态失效，请重新登录',
    logoutWithModal: '请求失败后弹出模态框再登出用户',
    logoutWithModalMsg: '用户状态失效，请重新登录',
    refreshToken: '请求的token已过期，刷新token',
    tokenExpired: 'token已过期',
    error: '请求异常'
  },
  theme: {
    themeDrawerTitle: '主题配置',
    tabs: {
      appearance: '外观',
      layout: '布局',
      general: '通用',
      preset: '预设',
      component: '组件'
    },
    appearance: {
      themeSchema: {
        title: '主题模式',
        light: '亮色模式',
        dark: '暗黑模式',
        auto: '跟随系统'
      },
      grayscale: '灰色模式',
      colourWeakness: '色弱模式',
      themeColor: {
        title: '主题颜色',
        primary: '主色',
        info: '信息色',
        success: '成功色',
        warning: '警告色',
        error: '错误色',
        followPrimary: '跟随主色'
      },
      themeRadius: {
        title: '主题圆角'
      },
      recommendColor: '应用推荐算法的颜色',
      recommendColorDesc: '推荐颜色的算法参照',
      preset: {
        title: '主题预设',
        apply: '应用',
        applySuccess: '预设应用成功',
        default: {
          name: '默认预设',
          desc: 'SmileX 默认主题预设'
        },
        dark: {
          name: '暗色预设',
          desc: '适用于夜间使用的暗色主题预设'
        },
        compact: {
          name: '紧凑型',
          desc: '适用于小屏幕的紧凑布局预设'
        },
        azir: {
          name: 'Azir的预设',
          desc: '是 Azir 比较喜欢的莫兰迪色系冷淡风'
        }
      }
    },
    layout: {
      layoutMode: {
        title: '布局模式',
        vertical: '左侧菜单模式',
        'vertical-mix': '左侧菜单混合模式',
        'vertical-hybrid-header-first': '左侧混合-顶部优先',
        horizontal: '顶部菜单模式',
        'top-hybrid-sidebar-first': '顶部混合-侧边优先',
        'top-hybrid-header-first': '顶部混合-顶部优先',
        vertical_detail: '左侧菜单布局，菜单在左，内容在右。',
        'vertical-mix_detail': '左侧双菜单布局，一级菜单在左侧深色区域，二级菜单在左侧浅色区域。',
        'vertical-hybrid-header-first_detail':
          '左侧混合布局，一级菜单在顶部，二级菜单在左侧深色区域，三级菜单在左侧浅色区域。',
        horizontal_detail: '顶部菜单布局，菜单在顶部，内容在下方。',
        'top-hybrid-sidebar-first_detail': '顶部混合布局，一级菜单在左侧，二级菜单在顶部。',
        'top-hybrid-header-first_detail': '顶部混合布局，一级菜单在顶部，二级菜单在左侧。'
      },
      tab: {
        title: '标签栏设置',
        visible: '显示标签栏',
        cache: '标签栏信息缓存',
        cacheTip: '一键开启/关闭全局 keepalive',
        height: '标签栏高度',
        mode: {
          title: '标签栏风格',
          slider: '滑块风格',
          chrome: '谷歌风格',
          button: '按钮风格'
        },
        closeByMiddleClick: '鼠标中键关闭标签页',
        closeByMiddleClickTip: '启用后可以使用鼠标中键点击标签页进行关闭'
      },
      header: {
        title: '头部设置',
        height: '头部高度',
        breadcrumb: {
          visible: '显示面包屑',
          showIcon: '显示面包屑图标'
        }
      },
      sider: {
        title: '侧边栏设置',
        inverted: '深色侧边栏',
        width: '侧边栏宽度',
        collapsedWidth: '侧边栏折叠宽度',
        mixWidth: '混合布局侧边栏宽度',
        mixCollapsedWidth: '混合布局侧边栏折叠宽度',
        mixChildMenuWidth: '混合布局子菜单宽度',
        autoSelectFirstMenu: '自动选择第一个子菜单',
        autoSelectFirstMenuTip: '点击一级菜单时，自动选择并导航到第一个子菜单的最深层级'
      },
      footer: {
        title: '底部设置',
        visible: '显示底部',
        fixed: '固定底部',
        height: '底部高度',
        right: '底部居右'
      },
      content: {
        title: '内容区域设置',
        scrollMode: {
          title: '滚动模式',
          tip: '主题滚动仅 main 部分滚动，外层滚动可携带头部底部一起滚动',
          wrapper: '外层滚动',
          content: '主体滚动'
        },
        page: {
          animate: '页面切换动画',
          mode: {
            title: '页面切换动画类型',
            'fade-slide': '滑动',
            fade: '淡入淡出',
            'fade-bottom': '底部消退',
            'fade-scale': '缩放消退',
            'zoom-fade': '渐变',
            'zoom-out': '闪现',
            none: '无'
          }
        },
        fixedHeaderAndTab: '固定头部和标签栏'
      }
    },
    general: {
      title: '通用设置',
      watermark: {
        title: '水印设置',
        visible: '显示全屏水印',
        text: '自定义水印文本',
        enableUserName: '启用用户名水印',
        enableTime: '显示当前时间',
        timeFormat: '时间格式'
      },
      multilingual: {
        title: '多语言设置',
        visible: '显示多语言按钮'
      },
      globalSearch: {
        title: '全局搜索设置',
        visible: '显示全局搜索按钮'
      }
    },
    configOperation: {
      copyConfig: '复制配置',
      copySuccessMsg: '复制成功，请替换 src/theme/settings.ts 中的变量 themeSettings',
      resetConfig: '重置配置',
      resetSuccessMsg: '重置成功'
    },
    componentConfig: {
      title: '组件主题',
      searchPlaceholder: '搜索组件',
      noMatch: '无匹配组件',
      searchPropPlaceholder: '搜索属性',
      enable: '启用',
      enabled: '已启用',
      notEnabledHint: '该组件未启用，开启后可单独配置其属性',
      noProps: '该组件暂无结构化属性，请使用下方高级 JSON5 配置',
      groupColor: '颜色',
      groupSize: '尺寸',
      groupFont: '字体',
      groupOther: '其他',
      advanced: '高级配置 (JSON5)',
      advancedHint: '此处可覆盖上方常用配置，支持 JSON5',
      jsonValid: 'JSON 有效',
      jsonInvalid: 'JSON 无效',
      copy: '复制组件配置',
      copySuccess: '组件配置已复制',
      components: {
        common: '通用',
        Alert: '警告提示',
        Anchor: '锚点',
        AutoComplete: '自动补全',
        Avatar: '头像',
        AvatarGroup: '头像组',
        BackTop: '回到顶部',
        Badge: '徽标',
        Breadcrumb: '面包屑',
        Button: '按钮',
        ButtonGroup: '按钮组',
        Calendar: '日历',
        Card: '卡片',
        Carousel: '轮播图',
        Cascader: '级联选择',
        Checkbox: '复选框',
        Code: '代码',
        Collapse: '折叠面板',
        CollapseTransition: '折叠过渡',
        ColorPicker: '颜色选择器',
        DataTable: '数据表格',
        DatePicker: '日期选择器',
        Descriptions: '描述列表',
        Dialog: '对话框',
        Divider: '分割线',
        Drawer: '抽屉',
        Dropdown: '下拉菜单',
        DynamicInput: '动态输入',
        DynamicTags: '动态标签',
        Element: '元素',
        Ellipsis: '文本省略',
        Empty: '空状态',
        Equation: '公式',
        Flex: '弹性布局',
        FloatButton: '悬浮按钮',
        FloatButtonGroup: '悬浮按钮组',
        Form: '表单',
        GradientText: '渐变文字',
        Heatmap: '热力图',
        Icon: '图标',
        IconWrapper: '图标包装器',
        Image: '图片',
        Input: '输入框',
        InputNumber: '数字输入',
        InputOtp: '验证码输入',
        InternalSelection: '内部选择',
        InternalSelectMenu: '内部选择菜单',
        Layout: '布局',
        LegacyTransfer: '传统穿梭框',
        List: '列表',
        LoadingBar: '加载条',
        Log: '日志',
        Marquee: '跑马灯',
        Mention: '提及',
        Menu: '菜单',
        Message: '消息',
        Modal: '弹窗',
        Notification: '通知',
        PageHeader: '页头',
        Pagination: '分页',
        Popconfirm: '弹出确认',
        Popover: '弹出信息',
        Popselect: '弹出选择',
        Progress: '进度条',
        QrCode: '二维码',
        Radio: '单选框',
        Rate: '评分',
        Result: '结果',
        Row: '行',
        Scrollbar: '滚动条',
        Select: '选择器',
        Skeleton: '骨架屏',
        Slider: '滑块',
        Space: '间距',
        Spin: '加载',
        Split: '分割',
        Statistic: '统计数值',
        Steps: '步骤条',
        Switch: '开关',
        Table: '表格',
        Tabs: '标签页',
        Tag: '标签',
        Thing: '事物',
        Timeline: '时间线',
        TimePicker: '时间选择器',
        Tooltip: '文字提示',
        Transfer: '穿梭框',
        Tree: '树',
        TreeSelect: '树选择',
        Typography: '排版',
        Upload: '上传',
        Watermark: '水印'
      }
    }
  },
  route: {
    login: '登录',
    403: '无权限',
    404: '页面不存在',
    500: '服务器错误',
    'iframe-page': '外链页面',
    home: '首页',
    'export-record': '导出记录',
    manage: '系统管理',
    manage_dept: '部门管理',
    'merchant-open': '商户开放管理',
    'merchant-open_merchant': '商户管理',
    'merchant-open_openapi-log': '调用日志',
    manage_menu: '菜单管理',
    manage_role: '角色管理',
    manage_user: '用户管理',
    manage_dict: '字典管理',
    manage_config: '系统配置',
    manage_announcement: '通知公告',
    'manage_ip-blacklist': '黑名单管理',
    log: '日志管理',
    'log_login-log': '登录日志',
    'log_online-user': '在线用户',
    'log_operation-log': '操作日志',
    monitor: '监控仪表盘',
    about: '关于我们',
    demo: '示例',
    demo_upload: '上传演示',
    demo_dict: '字典组件演示',
    'demo_openapi-test': 'OpenAPI 测试',
    manage_file: '文件管理',
    scheduler: '定时任务',
    scheduler_task: '任务管理',
    scheduler_log: '执行日志'
  },
  page: {
    login: {
      common: {
        loginOrRegister: '登录 / 注册',
        userNamePlaceholder: '请输入用户名',
        phonePlaceholder: '请输入手机号',
        codePlaceholder: '请输入验证码',
        passwordPlaceholder: '请输入密码',
        confirmPasswordPlaceholder: '请再次输入密码',
        codeLogin: '验证码登录',
        confirm: '确定',
        back: '返回',
        validateSuccess: '验证成功',
        loginSuccess: '登录成功',
        welcomeBack: '欢迎回来，{userName} ！'
      },
      pwdLogin: {
        title: '密码登录',
        rememberMe: '记住我',
        forgetPassword: '忘记密码？',
        register: '注册账号',
        otherAccountLogin: '其他账号登录',
        otherLoginMode: '其他登录方式',
        superAdmin: '超级管理员',
        admin: '管理员',
        user: '普通用户'
      },
      codeLogin: {
        title: '验证码登录',
        getCode: '获取验证码',
        reGetCode: '{time}秒后重新获取',
        sendCodeSuccess: '验证码发送成功',
        imageCodePlaceholder: '请输入图片验证码'
      },
      register: {
        title: '注册账号',
        agreement: '我已经仔细阅读并接受',
        protocol: '《用户协议》',
        policy: '《隐私权政策》'
      },
      resetPwd: {
        title: '重置密码'
      },
      bindWeChat: {
        title: '绑定微信'
      }
    },
    home: {
      welcome: '欢迎回来，{name}',
      userCount: '用户总数',
      roleCount: '角色数量',
      onlineCount: '在线用户',
      todayLoginCount: '今日登录',
      recentLogin: '最近登录',
      latestNotice: '最新公告',
      loginSuccess: '成功',
      loginFailed: '失败',
      noData: '暂无数据'
    },
    monitor: {
      systemResources: '系统资源',
      apiStats: 'API 服务质量',
      systemInfo: '系统信息',
      cpuUsage: 'CPU 使用率',
      memoryUsage: '内存使用率',
      diskUsage: '磁盘使用率',
      avgResponseTime: '平均响应时间',
      errorRate: '错误率',
      uptime: '运行时长',
      processCount: '进程数',
      pythonVersion: 'Python 版本',
      osName: '操作系统',
      cpuCount: 'CPU 核心数',
      day: '天',
      hour: '小时',
      minute: '分钟'
    },
    about: {
      title: '关于 SmileX',
      subtitle: '基于 FastAPI 与 Vue 3 的全栈云服务管理平台',
      intro:
        'SmileX-Fastapi-Cloud 是一套开箱即用的全栈云服务管理平台。前端基于 Vue 3 + Vite + NaiveUI + UnoCSS，后端基于 FastAPI + SQLAlchemy 2.0 + PostgreSQL + Redis，内置用户认证、RBAC 权限、系统配置、定时任务、监控等完整能力，并配套分层 AI 协作文档体系。',
      techStackTitle: '技术栈',
      featuresTitle: '核心特性',
      feat1: '统一响应与分页体系，标准化 API 契约',
      feat2: '完善的 RBAC 权限控制与行级数据权限',
      feat3: '雪花 ID 主键 + 软删除 + 完整审计字段',
      feat4: '可选 MCP 工具平台，支持 AI 客户端直连调用',
      feat5: '前后端 Status / 时间字段自动桥接',
      feat6: '内置 AGENTS.MD + aiDoc 分层 AI 协作文档',
      gitHistory: 'Git 提交历史',
      gitUnavailable: '当前环境未提供 Git 提交历史',
      commitsCount: '共 {count} 条提交'
    },
    demo: {
      openapiTest: {
        title: 'OpenAPI 签名测试',
        tip: '填入商户 AppId / AppSecret，浏览器内按后端契约计算 HMAC-SHA256 签名并发送请求，用于验证开放API鉴权链路。',
        appId: 'AppId',
        appSecret: 'AppSecret',
        method: '方法',
        path: '路径',
        body: '请求体',
        url: '请求 URL',
        send: '签名并发送',
        needCredential: '请先填写 AppId 与 AppSecret',
        signatureTitle: '签名明细（学习/排查用）',
        timestamp: 'X-Timestamp',
        nonce: 'X-Nonce',
        signature: 'X-Signature',
        canonical: 'Canonical String',
        responseTitle: '响应',
        status: '状态码',
        requestId: 'Request-Id'
      },
      upload: {
        title: '文件上传演示',
        singleUpload: '单文件上传',
        multiUpload: '多文件上传',
        selectFile: '选择文件',
        selectFiles: '选择多个文件',
        uploading: '上传中...',
        uploadSuccess: '上传成功',
        uploadFailed: '上传失败',
        fileSize: '文件大小',
        fileType: '文件类型',
        fileName: '文件名称',
        uploadResult: '上传结果',
        dragOrClick: '点击或拖拽文件到此区域上传',
        startUpload: '开始上传'
      },
      dict: {
        selectDemo: 'DictSelect 下拉选择',
        selectLabel: '基础用法：通过 dict-code 加载字典选项',
        selectWithDefault: '带默认值：v-model 绑定初始值',
        tagDemo: 'DictTag 标签展示',
        tagLabel: '根据字典 value 展示对应 label 标签',
        textDemo: 'DictText 文本展示',
        textLabel: '根据字典 value 展示对应 label 纯文本',
        tableDemo: '表格中展示字典',
        tableLabel: '在 NDataTable 中使用 DictText 和 DictTag 自定义列渲染'
      }
    },
    manage: {
      common: {
        status: {
          enable: '启用',
          disable: '禁用'
        }
      },
      role: {
        title: '角色列表',
        roleName: '角色名称',
        roleCode: '角色编码',
        roleStatus: '角色状态',
        roleDesc: '角色描述',
        menuAuth: '权限配置',
        buttonAuth: '按钮权限',
        form: {
          roleName: '请输入角色名称',
          roleCode: '请输入角色编码',
          roleStatus: '请选择角色状态',
          roleDesc: '请输入角色描述',
          nameMaxLength: '角色名称长度不能超过20个字符',
          descMaxLength: '角色描述长度不能超过200个字符'
        },
        addRole: '新增角色',
        editRole: '编辑角色',
        dataScope: '数据范围',
        dataScopes: {
          ALL: '全部数据',
          DEPT_AND_SUB: '本部门及子部门',
          DEPT_ONLY: '仅本部门',
          SELF: '仅本人'
        }
      },
      user: {
        title: '用户列表',
        userName: '用户名',
        password: '密码',
        confirmPassword: '确认密码',
        userGender: '性别',
        nickName: '昵称',
        userPhone: '手机号',
        userEmail: '邮箱',
        userStatus: '用户状态',
        userRole: '用户角色',
        isSuperuser: '超级管理员',
        changePassword: '修改密码',
        form: {
          userName: '请输入用户名',
          userGender: '请选择性别',
          nickName: '请输入昵称',
          userPhone: '请输入手机号',
          userEmail: '请输入邮箱',
          userStatus: '请选择用户状态',
          userRole: '请选择用户角色',
          isSuperuser: '请选择是否为超级管理员',
          newPassword: '请输入新密码',
          confirmPassword: '请确认新密码',
          passwordMinLength: '密码长度至少为6位',
          passwordNotMatch: '两次输入的密码不一致',
          usernameLength: '用户名长度必须在4-20个字符之间',
          passwordLength: '密码长度必须在6-20个字符之间',
          emailFormat: '邮箱格式不正确',
          phoneFormat: '手机号格式不正确'
        },
        addUser: '新增用户',
        editUser: '编辑用户',
        gender: {
          male: '男',
          female: '女'
        },
        lastLoginTime: '最后登陆时间',
        lastLoginIp: '最后登录IP',
        dept: '所属部门'
      },
      menu: {
        home: '首页',
        title: '菜单列表',
        id: 'ID',
        parentId: '父级菜单ID',
        parentMenu: '父级菜单',
        menuType: '菜单类型',
        menuName: '菜单名称',
        routeName: '路由名称',
        routePath: '路由路径',
        pathParam: '路径参数',
        layout: '布局',
        layoutBase: '基础布局',
        layoutBlank: '空白布局',
        page: '页面组件',
        i18nKey: '国际化key',
        icon: '图标',
        localIcon: '本地图标',
        iconTypeTitle: '图标类型',
        order: '排序',
        constant: '常量路由',
        keepAlive: '缓存路由',
        href: '外链',
        hideInMenu: '隐藏菜单',
        activeMenu: '高亮的菜单',
        multiTab: '支持多页签',
        fixedIndexInTab: '固定在页签中的序号',
        query: '路由参数',
        button: '按钮',
        buttonCode: '按钮编码',
        buttonDesc: '按钮描述',
        permission: '权限标识',
        menuStatus: '菜单状态',
        isSystem: '系统内置',
        form: {
          home: '请选择首页',
          parentMenu: '请选择父级菜单',
          menuType: '请选择菜单类型',
          menuName: '请输入菜单名称',
          routeName: '请输入路由名称',
          routePath: '请输入路由路径',
          pathParam: '请输入路径参数',
          page: '请选择页面组件',
          layout: '请选择布局组件',
          i18nKey: '请输入国际化key',
          icon: '请输入图标',
          localIcon: '请选择本地图标',
          order: '请输入排序',
          keepAlive: '请选择是否缓存路由',
          href: '请输入外链',
          hideInMenu: '请选择是否隐藏菜单',
          activeMenu: '请选择高亮的菜单的路由名称',
          multiTab: '请选择是否支持多标签',
          fixedInTab: '请选择是否固定在页签中',
          fixedIndexInTab: '请输入固定在页签中的序号',
          queryKey: '请输入路由参数Key',
          queryValue: '请输入路由参数Value',
          button: '请选择是否按钮',
          buttonCode: '请输入按钮编码',
          buttonDesc: '请输入按钮描述',
          permission: '请输入权限标识（如 sys:menu:add）',
          menuStatus: '请选择菜单状态',
          isSystem: '请选择是否为系统内置菜单'
        },
        addMenu: '新增目录',
        editMenu: '编辑菜单',
        addChildMenu: '新增子菜单',
        addChildButton: '新增按钮',
        type: {
          directory: '目录',
          menu: '菜单',
          button: '按钮'
        },
        iconType: {
          iconify: 'iconify图标',
          local: '本地图标'
        }
      },
      dict: {
        title: '字典列表',
        dictName: '字典名称',
        dictCode: '字典编码',
        dictDesc: '字典描述',
        dictStatus: '字典状态',
        isSystem: '系统内置',
        sort: '排序',
        itemTitle: '字典项列表',
        itemValue: '字典项值',
        itemLabel: '字典项文本',
        itemDesc: '字典项描述',
        itemStatus: '字典项状态',
        form: {
          dictName: '请输入字典名称',
          dictCode: '请输入字典编码',
          dictDesc: '请输入字典描述',
          dictStatus: '请选择字典状态',
          isSystem: '请选择是否为系统内置字典',
          sort: '请输入排序号',
          itemValue: '请输入字典项值',
          itemLabel: '请输入字典项文本',
          itemDesc: '请输入字典项描述',
          extInfo: '请输入扩展信息',
          itemStatus: '请选择字典项状态'
        },
        addDict: '新增字典',
        editDict: '编辑字典',
        addDictItem: '新增字典项',
        editDictItem: '编辑字典项',
        dictManage: '字典管理',
        itemManage: '字典项管理',
        pleaseSelectDict: '请先选择一个字典'
      },
      config: {
        title: '系统配置列表',
        configKey: '配置键名',
        configValue: '配置值',
        defaultValue: '默认值',
        configDesc: '配置描述',
        configType: '配置类型',
        configGroup: '配置分组',
        editable: '可编辑',
        isSystem: '系统内置',
        required: '必填',
        validationRule: '校验规则',
        form: {
          configKey: '请输入配置键名',
          configValue: '请输入配置值',
          defaultValue: '请输入默认值',
          configDesc: '请输入配置描述',
          configType: '请选择配置类型',
          configGroup: '请选择配置分组',
          editable: '请选择是否可编辑',
          isSystem: '请选择是否为系统内置配置',
          required: '请选择是否必填',
          validationRule: '请输入校验规则',
          invalidNumber: '请输入有效的数字',
          invalidBoolean: '请输入有效的布尔值（true/false/1/0/yes/no）',
          invalidJson: '请输入有效的JSON格式',
          invalidArray: '请输入有效的数组格式',
          jsonEmpty: 'JSON字符串不能为空',
          jsonBeautifySuccess: 'JSON格式美化成功',
          jsonFormatError: 'JSON格式错误，无法美化'
        },
        addConfig: '新增配置',
        editConfig: '编辑配置',
        resetConfig: '重置配置',
        beautifyJson: '美化JSON',
        editInModal: '弹窗编辑',
        editJson: '编辑JSON',
        type: {
          string: '字符串',
          number: '数字',
          boolean: '布尔',
          json: 'JSON',
          array: '数组'
        },
        group: {
          system: '系统配置',
          security: '安全配置',
          log: '日志配置',
          network: '网络配置',
          storage: '存储配置',
          custom: '自定义配置'
        }
      },
      ipBlacklist: {
        title: 'IP 黑名单列表',
        ip: 'IP 地址',
        type: '类型',
        typePermanent: '永久',
        typeTemporary: '临时',
        reason: '原因',
        expireAt: '过期时间',
        expireAtPlaceholder: '请选择过期时间',
        expireRequired: '临时黑名单必须设置过期时间',
        createdAt: '创建时间',
        reasonPlaceholder: '请输入加入原因（选填）',
        addTitle: '新增黑名单',
        form: {
          ip: '请输入IP地址',
          type: '请选择黑名单类型'
        }
      },
      announcement: {
        title: '通知公告列表',
        noticeType: '类型',
        targetTypeLabel: '推送范围',
        priority: '优先级',
        senderName: '发送人',
        publishedAt: '发布时间',
        publish: '发布',
        publishSuccess: '发布成功',
        status: {
          published: '已发布',
          draft: '草稿'
        },
        type: {
          announcement: '公告',
          system: '系统',
          operation: '操作提醒',
          approval: '审批通知'
        },
        targetType: {
          all: '全员',
          role: '按角色',
          user: '按用户'
        },
        form: {
          title: '请输入标题',
          type: '请选择通知类型',
          targetType: '请选择推送范围',
          status: '请选择状态',
          priority: '请选择优先级',
          content: '请输入通知内容',
          roleIds: '请输入角色ID',
          userIds: '请输入用户ID',
          roleIdsPlaceholder: '请输入角色ID，多选',
          userIdsPlaceholder: '请输入用户ID，多选'
        },
        noticeContent: '通知内容',
        targetRole: '目标角色',
        targetUser: '目标用户',
        addAnnouncement: '新增通知',
        editAnnouncement: '编辑通知',
        deleteAnnouncement: '删除通知',
        priorities: {
          low: '低',
          normal: '普通',
          high: '高',
          urgent: '紧急'
        }
      },
      file: {
        title: '文件列表',
        fileName: '文件名称',
        fileSize: '文件大小',
        fileType: '文件类型',
        fileExtension: '扩展名',
        storagePlatform: '存储平台',
        uploadTime: '上传时间',
        upload: '上传文件',
        download: '下载',
        preview: '预览',
        platform: {
          local: '本地存储',
          oss: '阿里云OSS'
        },
        form: {
          fileName: '请输入文件名称',
          fileExtension: '请输入扩展名',
          storagePlatform: '请选择存储平台'
        },
        previewTitle: '预览',
        previewNotSupported: '该文件类型暂不支持在线预览',
        videoNotSupported: '您的浏览器不支持视频播放。'
      },
      dept: {
        title: '部门管理',
        deptName: '部门名称',
        deptCode: '部门编码',
        parentDept: '上级部门',
        sort: '排序',
        status: '状态',
        addDept: '新增部门',
        editDept: '编辑部门',
        addChild: '添加子部门',
        form: {
          parentDept: '请选择上级部门（可不选）',
          deptName: '请输入部门名称',
          deptCode: '请输入部门编码（可选）'
        }
      },
      merchant: {
        title: '商户管理',
        merchantName: '商户名称',
        merchantCode: '商户编码',
        appId: 'AppId',
        appSecret: 'AppSecret',
        contactName: '联系人',
        contactPhone: '联系电话',
        contactEmail: '联系邮箱',
        remark: '备注',
        sort: '排序',
        status: '状态',
        secretUpdatedAt: '密钥重置时间',
        addMerchant: '新增商户',
        editMerchant: '编辑商户',
        resetSecret: '重置密钥',
        resetSecretConfirm: '重置后旧密钥立即失效，且新密钥仅显示一次，确认继续？',
        secretResultTitle: '商户凭据（仅显示一次）',
        secretOnceWarning: '请立即复制并妥善保存 AppSecret，关闭后将无法再次查看；如需更换请使用「重置密钥」。',
        copy: '复制',
        copied: '已复制到剪贴板',
        copyFailed: '复制失败，请手动选择文本复制',
        form: {
          merchantName: '请输入商户名称',
          merchantCode: '请输入商户编码（可选）',
          appId: '请输入 AppId',
          contactName: '请输入联系人',
          contactPhone: '请输入联系电话',
          contactEmail: '请输入联系邮箱',
          remark: '请输入备注（可选）',
          status: '请选择状态',
          emailFormat: '邮箱格式不正确',
          phoneFormat: '手机号格式不正确'
        }
      },
      openapiLog: {
        title: '调用日志',
        appId: 'AppId',
        merchantName: '商户名称',
        method: '方法',
        path: '请求路径',
        status: '状态码',
        errCode: '错误码',
        clientIp: '客户端IP',
        latency: '耗时',
        createdAt: '调用时间',
        form: {
          appId: '请输入 AppId',
          path: '请输入请求路径',
          method: '请输入 HTTP 方法',
          errCode: '请输入错误码',
          clientIp: '请输入客户端 IP',
          status: '请输入状态码'
        }
      },
      scheduler: {
        title: '定时任务列表',
        taskName: '任务名称',
        taskKey: '任务标识',
        description: '任务描述',
        cronExpression: 'Cron 表达式',
        triggerType: '触发类型',
        triggerTypes: {
          cron: 'Cron 表达式',
          interval: '固定间隔',
          date: '单次执行'
        },
        status: '状态',
        statusEnabled: '已启用',
        statusDisabled: '已禁用',
        enable: '启用',
        disable: '禁用',
        lastRunAt: '上次执行',
        nextRunAt: '下次执行',
        lastStatus: '执行状态',
        lastStatuses: {
          success: '成功',
          failed: '失败',
          running: '运行中',
          timeout: '超时'
        },
        timeout: '超时(秒)',
        maxRetries: '最大重试',
        concurrentPolicy: '并发策略',
        concurrentPolicies: {
          skip: '跳过',
          replace: '替换',
          run: '允许并发'
        },
        manualTrigger: '手动执行',
        manualTriggerConfirm: '确认立即执行该任务？',
        manualTriggerSuccess: '任务已触发执行',
        cronPreview: '预览执行时间',
        nextRunTimes: '接下来 5 次执行时间',
        syncRegistry: '同步注册任务',
        syncRegistrySuccess: '同步完成',
        viewLogs: '执行日志',
        triggerParams: '触发参数',
        addTask: '新增任务',
        editTask: '编辑任务',
        isSystem: '系统任务',
        taskCategory: '任务分类',
        taskCategories: {
          generic: '通用',
          system: '系统',
          specialist: '专家'
        },
        template: '任务模板',
        templatePlaceholder: '请选择任务模板（不执行逻辑）',
        taskKeyPlaceholder: '请输入任务标识',
        taskKeyHint: '请输入任务标识，需保持唯一，例如 my-daily-ping',
        taskKeyRequired: '请输入任务标识，且保持唯一',
        advancedConfig: '高级配置',
        schemaLoading: '参数描述加载中...',
        noParams: '该任务无参数',
        paramPlaceholder: '请输入 {label}',
        form: {
          taskName: '请输入任务名称',
          taskKey: '请输入任务标识',
          cronExpression: '请输入 Cron 表达式',
          triggerType: '请选择触发类型',
          status: '请选择状态',
          concurrentPolicy: '请选择并发策略',
          description: '请输入任务描述'
        }
      },
      schedulerLog: {
        title: '任务执行日志',
        taskName: '任务名称',
        status: '执行状态',
        startTime: '开始时间',
        endTime: '结束时间',
        duration: '耗时(ms)',
        triggeredBy: '触发方式',
        triggeredByValues: {
          scheduler: '自动',
          manual: '手动'
        },
        result: '执行结果',
        errorMessage: '错误信息',
        viewDetail: '详情',
        clear: '清理日志',
        clearConfirm: '确认清理30天前的执行日志？',
        detailTitle: '执行日志详情',
        form: {
          taskName: '请输入任务名称',
          status: '请选择执行状态',
          timeRange: '时间范围'
        }
      }
    },
    log: {
      loginLog: {
        title: '登录日志列表',
        username: '用户名',
        ip: '登录IP',
        status: '登录状态',
        detail: '详细信息',
        userAgent: '登录设备',
        loginTime: '登录时间',
        success: '成功',
        failed: '失败',
        clear: '清理日志',
        clearConfirm: '确认清理30天前的登录日志？',
        form: {
          username: '请输入用户名',
          ip: '请输入IP地址',
          status: '请选择登录状态',
          timeRange: '时间范围',
          startTime: '开始时间',
          endTime: '结束时间'
        }
      },
      operationLog: {
        title: '操作日志列表',
        username: '操作人',
        module: '操作模块',
        action: '操作类型',
        description: '操作描述',
        method: '请求方法',
        path: '请求路径',
        ip: '操作IP',
        responseCode: '状态码',
        responseResult: '响应结果',
        elapsedMs: '耗时(ms)',
        requestParams: '请求参数',
        operateTime: '操作时间',
        viewDetail: '查看详情',
        detailTitle: '操作日志详情',
        clear: '清理日志',
        clearConfirm: '确认清理30天前的操作日志？',
        form: {
          username: '请输入操作人',
          module: '请输入操作模块',
          action: '请输入操作类型',
          timeRange: '时间范围',
          startTime: '开始时间',
          endTime: '结束时间'
        }
      },
      onlineUser: {
        title: '在线用户列表',
        username: '用户名',
        nickname: '昵称',
        ip: '登录IP',
        userAgent: '登录设备',
        loginTime: '登录时间',
        kick: '踢下线',
        kickAll: '全部踢下线',
        kickConfirm: '确认将该用户踢下线？',
        kickAllConfirm: '确认将所有在线用户踢下线？',
        kickSuccess: '已踢下线',
        kickAllSuccess: '已踢除所有在线会话',
        form: {
          username: '请输入用户名',
          ip: '请输入IP地址'
        }
      }
    }
  },
  form: {
    required: '不能为空',
    userName: {
      required: '请输入用户名',
      invalid: '用户名格式不正确'
    },
    phone: {
      required: '请输入手机号',
      invalid: '手机号格式不正确'
    },
    pwd: {
      required: '请输入密码',
      invalid: '密码格式不正确，需6-20位，且至少包含字母和数字'
    },
    confirmPwd: {
      required: '请输入确认密码',
      invalid: '两次输入密码不一致'
    },
    code: {
      required: '请输入验证码',
      invalid: '验证码格式不正确'
    },
    email: {
      required: '请输入邮箱',
      invalid: '邮箱格式不正确'
    }
  },
  dropdown: {
    closeCurrent: '关闭',
    closeOther: '关闭其它',
    closeLeft: '关闭左侧',
    closeRight: '关闭右侧',
    closeAll: '关闭所有',
    pin: '固定标签',
    unpin: '取消固定'
  },
  icon: {
    themeConfig: '主题配置',
    themeSchema: '主题模式',
    lang: '切换语言',
    fullscreen: '全屏',
    fullscreenExit: '退出全屏',
    reload: '刷新页面',
    collapse: '折叠菜单',
    expand: '展开菜单',
    pin: '固定',
    unpin: '取消固定'
  },
  datatable: {
    itemCount: '共 {total} 条',
    fixed: {
      left: '左固定',
      right: '右固定',
      unFixed: '取消固定'
    }
  },
  exportTask: {
    title: '导出记录',
    tooltip: '导出记录',
    taskName: '任务名称',
    moduleKey: '模块',
    status: {
      title: '状态',
      pending: '排队中',
      processing: '生成中',
      completed: '已完成',
      failed: '失败'
    },
    totalRows: '导出条数',
    fileSize: '文件大小',
    errorMessage: '失败原因',
    createdAt: '创建时间',
    finishedAt: '完成时间',
    noRecords: '暂无导出记录',
    viewAll: '查看全部',
    asyncExport: '异步导出',
    submitSuccess: '导出任务已提交',
    submitFailed: '导出任务提交失败',
    downloadFailed: '导出文件下载失败'
  },
  notification: {
    title: '通知中心',
    tooltip: '通知中心',
    markAllAsRead: '全部已读',
    noNotifications: '暂无通知',
    markAllReadSuccess: '已全部标记为已读',
    priority: {
      low: '低',
      normal: '普通',
      high: '高',
      urgent: '紧急'
    }
  }
};

export default local;
