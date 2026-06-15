const local: App.I18n.Schema = {
  system: {
    title: "SmileX管理系统",
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
    }
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
      preset: '预设'
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
    }
  },
  route: {
    login: '登录',
    403: '无权限',
    404: '页面不存在',
    500: '服务器错误',
    'iframe-page': '外链页面',
    home: '首页',
    manage: '管理',
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
    'log_robot-log': '机器人事件日志',
    monitor: '监控仪表盘',
    demo: '示例',
    demo_upload: '上传演示',
    demo_dict: '字典组件演示',
    manage_file: '文件管理',
    manage_scheduler: '任务管理',
    'manage_scheduler-log': '执行日志',
    robot: '机器人',
    robot_model: '型号管理',
    robot_manage: '机器人管理',
    scene: '场景管理',
    settings: '参数配置',
    scene_group: '场景分组',
    scene_map: '场景地图',
    'scene_map-editor': '地图编辑器',
    task: '任务管理',
    'operation-monitor': '运行监控'
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
      branchDesc:
        '为了方便大家开发和更新合并，我们对main分支的代码进行了精简，只保留了首页菜单，其余内容已移至example分支进行维护。预览地址显示的内容即为example分支的内容。',
      greeting: '早安，{userName}, 今天又是充满活力的一天!',
      weatherDesc: '今日多云转晴，20℃ - 25℃!',
      projectCount: '项目数',
      todo: '待办',
      message: '消息',
      downloadCount: '下载量',
      registerCount: '注册量',
      schedule: '作息安排',
      study: '学习',
      work: '工作',
      rest: '休息',
      entertainment: '娱乐',
      visitCount: '访问量',
      turnover: '成交额',
      dealCount: '成交量',
      projectNews: {
        title: '项目动态',
        moreNews: '更多动态',
        desc1: 'SmileX 在2021年5月28日创建了开源项目 soybean-admin!',
        desc2: 'Yanbowe 向 soybean-admin 提交了一个bug，多标签栏不会自适应。',
        desc3: 'SmileX 准备为 soybean-admin 的发布做充分的准备工作!',
        desc4: 'SmileX 正在忙于为soybean-admin写项目说明文档！',
        desc5: 'SmileX 刚才把工作台页面随便写了一些，凑合能看了！'
      },
      creativity: '创意'
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
    demo: {
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
          roleDesc: '请输入角色描述'
        },
        addRole: '新增角色',
        editRole: '编辑角色'
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
        lastLoginIp: '最后登录IP'
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
          priority: '请选择优先级'
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
      },
      robotEventLog: {
        title: '机器人事件日志列表',
        robotName: '机器人名称',
        eventType: '事件类型',
        eventStatus: '事件状态',
        eventContent: '事件内容',
        typeTask: '任务',
        typeAlarm: '告警',
        statusNormal: '正常',
        statusAbnormal: '异常',
        clear: '清理日志',
        clearConfirm: '确认清理30天前的机器人事件日志？',
        form: {
          robotName: '请选择机器人',
          eventType: '请选择事件类型',
          eventStatus: '请选择事件状态',
          timeRange: '时间范围'
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
      invalid: '密码格式不正确，6-18位字符，包含字母、数字、下划线'
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
  notification: {
    title: '通知中心',
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
