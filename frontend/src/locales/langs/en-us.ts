const local: App.I18n.Schema = {
  system: {
    title: 'SmileX System',
    updateTitle: 'System Version Update Notification',
    updateContent: 'A new version of the system has been detected. Do you want to refresh the page immediately?',
    updateConfirm: 'Refresh immediately',
    updateCancel: 'Later'
  },
  common: {
    selectAtLeastOne: 'Please select at least one item',
    pleaseSelect: 'Please select data to operate first',
    action: 'Action',
    add: 'Add',
    addSuccess: 'Add Success',
    backToHome: 'Back to home',
    back: 'Back',
    batchDelete: 'Batch Delete',
    cancel: 'Cancel',
    close: 'Close',
    check: 'Check',
    selectAll: 'Select All',
    expandColumn: 'Expand Column',
    columnSetting: 'Column Setting',
    config: 'Config',
    confirm: 'Confirm',
    delete: 'Delete',
    deleteSuccess: 'Delete Success',
    deleteFailed: 'Delete Failed',
    confirmDelete: 'Are you sure you want to delete?',
    loadDataFailed: 'Failed to load data',
    edit: 'Edit',
    warning: 'Warning',
    error: 'Error',
    index: 'Index',
    keywordSearch: 'Please enter keyword',
    logout: 'Logout',
    logoutConfirm: 'Are you sure you want to log out?',
    lookForward: 'Coming soon',
    modify: 'Modify',
    modifySuccess: 'Modify Success',
    saveSuccess: 'Save Success',
    status: 'Status',
    noData: 'No Data',
    operate: 'Operate',
    pleaseCheckValue: 'Please check whether the value is valid',
    pleaseEnter: 'Please enter',
    refresh: 'Refresh',
    reset: 'Reset',
    search: 'Search',
    switch: 'Switch',
    tip: 'Tip',
    title: 'Title',
    trigger: 'Trigger',
    update: 'Update',
    updateSuccess: 'Update Success',
    updateFailed: 'Update Failed',
    userCenter: 'User Center',
    changePassword: 'Change Password',
    yesOrNo: {
      yes: 'Yes',
      no: 'No'
    },
    actions: {
      list: 'List',
      add: 'Add',
      edit: 'Edit',
      delete: 'Delete',
      remove: 'Remove',
      publish: 'Publish',
      detail: 'Detail',
      status: 'Toggle Status',
      trigger: 'Run Now',
      view: 'View',
      kick: 'Kick',
      download: 'Download',
      upload: 'Upload',
      assign: 'Assign',
      logDetail: 'Log Detail',
      logDelete: 'Delete Log'
    }
  },
  request: {
    logout: 'Logout user after request failed',
    logoutMsg: 'User status is invalid, please log in again',
    logoutWithModal: 'Pop up modal after request failed and then log out user',
    logoutWithModalMsg: 'User status is invalid, please log in again',
    refreshToken: 'The requested token has expired, refresh the token',
    tokenExpired: 'The requested token has expired',
    error: 'Request Exception'
  },
  captcha: {
    success: 'Verification succeeded',
    fail: 'Verification failed',
    refresh: 'Refresh captcha',
    slideToVerify: 'Slide right to verify',
    completeFirst: 'Please complete the slider verification below before logging in',
    selectPlaceholder: 'Please select'
  },
  theme: {
    themeDrawerTitle: 'Theme Configuration',
    tabs: {
      appearance: 'Appearance',
      layout: 'Layout',
      general: 'General',
      preset: 'Preset',
      component: 'Component'
    },
    appearance: {
      themeSchema: {
        title: 'Theme Schema',
        light: 'Light',
        dark: 'Dark',
        auto: 'Follow System'
      },
      grayscale: 'Grayscale',
      colourWeakness: 'Colour Weakness',
      themeColor: {
        title: 'Theme Color',
        primary: 'Primary',
        info: 'Info',
        success: 'Success',
        warning: 'Warning',
        error: 'Error',
        followPrimary: 'Follow Primary'
      },
      themeRadius: {
        title: 'Theme Radius'
      },
      recommendColor: 'Apply Recommended Color Algorithm',
      recommendColorDesc: 'The recommended color algorithm refers to',
      preset: {
        title: 'Theme Presets',
        apply: 'Apply',
        applySuccess: 'Preset applied successfully',
        default: {
          name: 'Default Preset',
          desc: 'Default theme preset with balanced settings'
        },
        dark: {
          name: 'Dark Preset',
          desc: 'Dark theme preset for night time usage'
        },
        compact: {
          name: 'Compact Preset',
          desc: 'Compact layout preset for small screens'
        },
        azir: {
          name: "Azir's Preset",
          desc: 'It is a cold and elegant preset that Azir likes'
        }
      }
    },
    layout: {
      layoutMode: {
        title: 'Layout Mode',
        vertical: 'Vertical Mode',
        horizontal: 'Horizontal Mode',
        'vertical-mix': 'Vertical Mix Mode',
        'vertical-hybrid-header-first': 'Left Hybrid Header-First',
        'top-hybrid-sidebar-first': 'Top-Hybrid Sidebar-First',
        'top-hybrid-header-first': 'Top-Hybrid Header-First',
        vertical_detail: 'Vertical menu layout, with the menu on the left and content on the right.',
        'vertical-mix_detail':
          'Vertical mix-menu layout, with the primary menu on the dark left side and the secondary menu on the lighter left side.',
        'vertical-hybrid-header-first_detail':
          'Left hybrid layout, with the primary menu at the top, the secondary menu on the dark left side, and the tertiary menu on the lighter left side.',
        horizontal_detail: 'Horizontal menu layout, with the menu at the top and content below.',
        'top-hybrid-sidebar-first_detail':
          'Top hybrid layout, with the primary menu on the left and the secondary menu at the top.',
        'top-hybrid-header-first_detail':
          'Top hybrid layout, with the primary menu at the top and the secondary menu on the left.'
      },
      tab: {
        title: 'Tab Settings',
        visible: 'Tab Visible',
        cache: 'Tag Bar Info Cache',
        cacheTip: 'One-click to open/close global keepalive',
        height: 'Tab Height',
        mode: {
          title: 'Tab Mode',
          slider: 'Slider',
          chrome: 'Chrome',
          button: 'Button'
        },
        closeByMiddleClick: 'Close Tab by Middle Click',
        closeByMiddleClickTip: 'Enable closing tabs by clicking with the middle mouse button'
      },
      header: {
        title: 'Header Settings',
        height: 'Header Height',
        breadcrumb: {
          visible: 'Breadcrumb Visible',
          showIcon: 'Breadcrumb Icon Visible'
        }
      },
      sider: {
        title: 'Sider Settings',
        inverted: 'Dark Sider',
        width: 'Sider Width',
        collapsedWidth: 'Sider Collapsed Width',
        mixWidth: 'Mix Sider Width',
        mixCollapsedWidth: 'Mix Sider Collapse Width',
        mixChildMenuWidth: 'Mix Child Menu Width',
        autoSelectFirstMenu: 'Auto Select First Submenu',
        autoSelectFirstMenuTip:
          'When a first-level menu is clicked, the first submenu is automatically selected and navigated to the deepest level'
      },
      footer: {
        title: 'Footer Settings',
        visible: 'Footer Visible',
        fixed: 'Fixed Footer',
        height: 'Footer Height',
        right: 'Right Footer'
      },
      content: {
        title: 'Content Area Settings',
        scrollMode: {
          title: 'Scroll Mode',
          tip: 'The theme scroll only scrolls the main part, the outer scroll can carry the header and footer together',
          wrapper: 'Wrapper',
          content: 'Content'
        },
        page: {
          animate: 'Page Animate',
          mode: {
            title: 'Page Animate Mode',
            fade: 'Fade',
            'fade-slide': 'Slide',
            'fade-bottom': 'Fade Zoom',
            'fade-scale': 'Fade Scale',
            'zoom-fade': 'Zoom Fade',
            'zoom-out': 'Zoom Out',
            none: 'None'
          }
        },
        fixedHeaderAndTab: 'Fixed Header And Tab'
      }
    },
    general: {
      title: 'General Settings',
      watermark: {
        title: 'Watermark Settings',
        visible: 'Watermark Full Screen Visible',
        text: 'Custom Watermark Text',
        enableUserName: 'Enable User Name Watermark',
        enableTime: 'Show Current Time',
        timeFormat: 'Time Format'
      },
      multilingual: {
        title: 'Multilingual Settings',
        visible: 'Display multilingual button'
      },
      globalSearch: {
        title: 'Global Search Settings',
        visible: 'Display GlobalSearch button'
      }
    },
    configOperation: {
      copyConfig: 'Copy Config',
      copySuccessMsg: 'Copy Success, Please replace the variable "themeSettings" in "src/theme/settings.ts"',
      resetConfig: 'Reset Config',
      resetSuccessMsg: 'Reset Success'
    },
    componentConfig: {
      title: 'Component Theme',
      searchPlaceholder: 'Search components',
      noMatch: 'No matching components',
      searchPropPlaceholder: 'Search properties',
      enable: 'Enable',
      enabled: 'Enabled',
      notEnabledHint: 'This component is not enabled. Turn it on to configure its properties individually.',
      noProps: 'No structured properties for this component. Use the advanced JSON5 below.',
      groupColor: 'Color',
      groupSize: 'Size',
      groupFont: 'Font',
      groupOther: 'Other',
      advanced: 'Advanced (JSON5)',
      advancedHint: 'Overrides the fields above. JSON5 is supported.',
      jsonValid: 'Valid JSON',
      jsonInvalid: 'Invalid JSON',
      copy: 'Copy Component Config',
      copySuccess: 'Component config copied',
      preview: 'Preview',
      components: {
        common: 'Common',
        Alert: 'Alert',
        Anchor: 'Anchor',
        AutoComplete: 'Auto Complete',
        Avatar: 'Avatar',
        AvatarGroup: 'Avatar Group',
        BackTop: 'Back Top',
        Badge: 'Badge',
        Breadcrumb: 'Breadcrumb',
        Button: 'Button',
        ButtonGroup: 'Button Group',
        Calendar: 'Calendar',
        Card: 'Card',
        Carousel: 'Carousel',
        Cascader: 'Cascader',
        Checkbox: 'Checkbox',
        Code: 'Code',
        Collapse: 'Collapse',
        CollapseTransition: 'Collapse Transition',
        ColorPicker: 'Color Picker',
        DataTable: 'Data Table',
        DatePicker: 'Date Picker',
        Descriptions: 'Descriptions',
        Dialog: 'Dialog',
        Divider: 'Divider',
        Drawer: 'Drawer',
        Dropdown: 'Dropdown',
        DynamicInput: 'Dynamic Input',
        DynamicTags: 'Dynamic Tags',
        Element: 'Element',
        Ellipsis: 'Ellipsis',
        Empty: 'Empty',
        Equation: 'Equation',
        Flex: 'Flex',
        FloatButton: 'Float Button',
        FloatButtonGroup: 'Float Button Group',
        Form: 'Form',
        GradientText: 'Gradient Text',
        Heatmap: 'Heatmap',
        Icon: 'Icon',
        IconWrapper: 'Icon Wrapper',
        Image: 'Image',
        Input: 'Input',
        InputNumber: 'Input Number',
        InputOtp: 'OTP Input',
        InternalSelection: 'Internal Selection',
        InternalSelectMenu: 'Internal Select Menu',
        Layout: 'Layout',
        LegacyTransfer: 'Legacy Transfer',
        List: 'List',
        LoadingBar: 'Loading Bar',
        Log: 'Log',
        Marquee: 'Marquee',
        Mention: 'Mention',
        Menu: 'Menu',
        Message: 'Message',
        Modal: 'Modal',
        Notification: 'Notification',
        PageHeader: 'Page Header',
        Pagination: 'Pagination',
        Popconfirm: 'Popconfirm',
        Popover: 'Popover',
        Popselect: 'Popselect',
        Progress: 'Progress',
        QrCode: 'QR Code',
        Radio: 'Radio',
        Rate: 'Rate',
        Result: 'Result',
        Row: 'Row',
        Scrollbar: 'Scrollbar',
        Select: 'Select',
        Skeleton: 'Skeleton',
        Slider: 'Slider',
        Space: 'Space',
        Spin: 'Spin',
        Split: 'Split',
        Statistic: 'Statistic',
        Steps: 'Steps',
        Switch: 'Switch',
        Table: 'Table',
        Tabs: 'Tabs',
        Tag: 'Tag',
        Thing: 'Thing',
        Timeline: 'Timeline',
        TimePicker: 'Time Picker',
        Tooltip: 'Tooltip',
        Transfer: 'Transfer',
        Tree: 'Tree',
        TreeSelect: 'Tree Select',
        Typography: 'Typography',
        Upload: 'Upload',
        Watermark: 'Watermark'
      }
    }
  },
  route: {
    login: 'Login',
    403: 'No Permission',
    404: 'Page Not Found',
    500: 'Server Error',
    'iframe-page': 'Iframe',
    home: 'Home',
    'export-record': 'Export Records',
    manage: 'Manage',
    manage_menu: 'Menu Management',
    manage_dept: 'Department Management',
    'merchant-open': 'Merchant Open',
    'merchant-open_merchant': 'Merchant Management',
    'merchant-open_openapi-log': 'Call Log',
    manage_role: 'Role Management',
    manage_user: 'User Management',
    'manage_app-user': 'App User',
    manage_dict: 'Dict Management',
    manage_config: 'System Config',
    manage_announcement: 'Announcement',
    'manage_ip-blacklist': 'IP Blacklist',
    log: 'Log Management',
    'log_login-log': 'Login Log',
    'log_online-user': 'Online Users',
    'log_operation-log': 'Operation Log',
    monitor: 'Monitor Dashboard',
    about: 'About',
    demo: 'Example',
    demo_upload: 'Upload Demo',
    demo_dict: 'Dict Component Demo',
    'demo_openapi-test': 'OpenAPI Test',
    manage_file: 'File Management',
    scheduler: 'Scheduler',
    scheduler_task: 'Task Management',
    scheduler_log: 'Execution Log'
  },
  page: {
    login: {
      common: {
        loginOrRegister: 'Login / Register',
        userNamePlaceholder: 'Please enter user name',
        phonePlaceholder: 'Please enter phone number',
        codePlaceholder: 'Please enter verification code',
        passwordPlaceholder: 'Please enter password',
        confirmPasswordPlaceholder: 'Please enter password again',
        codeLogin: 'Verification code login',
        confirm: 'Confirm',
        back: 'Back',
        validateSuccess: 'Verification passed',
        loginSuccess: 'Login successfully',
        welcomeBack: 'Welcome back, {userName} !'
      },
      pwdLogin: {
        title: 'Password Login',
        rememberMe: 'Remember me',
        forgetPassword: 'Forget password?',
        register: 'Register',
        otherAccountLogin: 'Other Account Login',
        otherLoginMode: 'Other Login Mode',
        superAdmin: 'Super Admin',
        admin: 'Admin',
        user: 'User'
      },
      codeLogin: {
        title: 'Verification Code Login',
        getCode: 'Get verification code',
        reGetCode: 'Reacquire after {time}s',
        sendCodeSuccess: 'Verification code sent successfully',
        imageCodePlaceholder: 'Please enter image verification code'
      },
      register: {
        title: 'Register',
        agreement: 'I have read and agree to',
        protocol: '《User Agreement》',
        policy: '《Privacy Policy》'
      },
      resetPwd: {
        title: 'Reset Password'
      },
      bindWeChat: {
        title: 'Bind WeChat'
      }
    },
    home: {
      welcome: 'Welcome back, {name}',
      userCount: 'Total Users',
      roleCount: 'Total Roles',
      onlineCount: 'Online Users',
      todayLoginCount: "Today's Logins",
      recentLogin: 'Recent Logins',
      latestNotice: 'Latest Notices',
      loginSuccess: 'Success',
      loginFailed: 'Failed',
      noData: 'No data'
    },
    monitor: {
      systemResources: 'System Resources',
      apiStats: 'API Service Quality',
      systemInfo: 'System Info',
      cpuUsage: 'CPU Usage',
      memoryUsage: 'Memory Usage',
      diskUsage: 'Disk Usage',
      avgResponseTime: 'Avg Response Time',
      errorRate: 'Error Rate',
      uptime: 'Uptime',
      processCount: 'Process Count',
      pythonVersion: 'Python Version',
      osName: 'OS',
      cpuCount: 'CPU Cores',
      day: 'd',
      hour: 'h',
      minute: 'm'
    },
    about: {
      title: 'About SmileX',
      subtitle: 'A full-stack cloud service platform built on FastAPI and Vue 3',
      intro:
        'SmileX-Fastapi-Cloud is an out-of-the-box full-stack cloud service platform. The frontend is built with Vue 3 + Vite + NaiveUI + UnoCSS, and the backend with FastAPI + SQLAlchemy 2.0 + PostgreSQL + Redis. It ships with authentication, RBAC, system config, scheduled tasks, monitoring, and a layered AI collaboration doc system.',
      techStackTitle: 'Tech Stack',
      featuresTitle: 'Key Features',
      feat1: 'Unified response & pagination system with standardized API contracts',
      feat2: 'Comprehensive RBAC with row-level data permissions',
      feat3: 'Snowflake ID primary keys + soft delete + full audit fields',
      feat4: 'Optional MCP tool platform for direct AI client invocation',
      feat5: 'Automatic Status / datetime bridging between frontend and backend',
      feat6: 'Built-in AGENTS.MD + aiDoc layered AI collaboration docs',
      gitHistory: 'Git Commit History',
      gitUnavailable: 'No Git history available in the current environment',
      commitsCount: '{count} commits'
    },
    demo: {
      openapiTest: {
        title: 'OpenAPI Signature Test',
        tip: 'Fill in merchant AppId / AppSecret. The browser computes the HMAC-SHA256 signature per the backend contract and sends the request, to verify the open API auth chain.',
        appId: 'AppId',
        appSecret: 'AppSecret',
        method: 'Method',
        path: 'Path',
        body: 'Body',
        url: 'Request URL',
        send: 'Sign & Send',
        needCredential: 'Please fill AppId and AppSecret first',
        signatureTitle: 'Signature Details (for learning/debug)',
        timestamp: 'X-Timestamp',
        nonce: 'X-Nonce',
        signature: 'X-Signature',
        canonical: 'Canonical String',
        responseTitle: 'Response',
        status: 'Status',
        requestId: 'Request-Id'
      },
      upload: {
        title: 'File Upload Demo',
        singleUpload: 'Single File Upload',
        multiUpload: 'Multi-File Upload',
        selectFile: 'Select File',
        selectFiles: 'Select Multiple Files',
        uploading: 'Uploading...',
        uploadSuccess: 'Upload Success',
        uploadFailed: 'Upload Failed',
        fileSize: 'File Size',
        fileType: 'File Type',
        fileName: 'File Name',
        uploadResult: 'Upload Result',
        dragOrClick: 'Click or drag files to this area to upload',
        startUpload: 'Start Upload'
      },
      dict: {
        selectDemo: 'DictSelect Dropdown',
        selectLabel: 'Basic usage: load dict options via dict-code',
        selectWithDefault: 'With default value: v-model binds initial value',
        tagDemo: 'DictTag Display',
        tagLabel: 'Show label tag based on dict value',
        textDemo: 'DictText Display',
        textLabel: 'Show label text based on dict value',
        tableDemo: 'Dict in Table',
        tableLabel: 'Use DictText and DictTag for custom column rendering in NDataTable'
      }
    },

    manage: {
      common: {
        status: {
          enable: 'Enable',
          disable: 'Disable'
        }
      },
      role: {
        title: 'Role List',
        roleName: 'Role Name',
        roleCode: 'Role Code',
        roleStatus: 'Role Status',
        roleDesc: 'Role Description',
        dataScope: 'Data Scope',
        dataScopes: {
          ALL: 'All Data',
          DEPT_AND_SUB: 'Dept & Sub',
          DEPT_ONLY: 'Dept Only',
          SELF: 'Self Only'
        },
        menuAuth: 'Permission Config',
        buttonAuth: 'Button Auth',
        form: {
          roleName: 'Please enter role name',
          roleCode: 'Please enter role code',
          roleStatus: 'Please select role status',
          roleDesc: 'Please enter role description',
          nameMaxLength: 'Role name cannot exceed 20 characters',
          descMaxLength: 'Role description cannot exceed 200 characters'
        },
        addRole: 'Add Role',
        editRole: 'Edit Role'
      },
      user: {
        title: 'User List',
        userName: 'User Name',
        password: 'Password',
        confirmPassword: 'Confirm Password',
        userGender: 'Gender',
        nickName: 'Nick Name',
        userPhone: 'Phone Number',
        userEmail: 'Email',
        userStatus: 'User Status',
        userRole: 'User Role',
        isSuperuser: 'Super Admin',
        changePassword: 'Change Password',
        lastLoginTime: 'Last Login Time',
        lastLoginIp: 'Last Login IP',
        form: {
          userName: 'Please enter user name',
          userGender: 'Please select gender',
          nickName: 'Please enter nick name',
          userPhone: 'Please enter phone number',
          userEmail: 'Please enter email',
          userStatus: 'Please select user status',
          userRole: 'Please select user role',
          isSuperuser: 'Please select whether to be a super admin',
          newPassword: 'Please enter new password',
          confirmPassword: 'Please confirm new password',
          passwordMinLength: 'Password length must be at least 6 characters',
          passwordNotMatch: 'The two passwords do not match',
          usernameLength: 'user name length must be between 4 and 20 characters',
          passwordLength: 'password length must be between 6 and 20 characters',
          emailFormat: 'Email format is incorrect',
          phoneFormat: 'Phone number format is incorrect'
        },
        addUser: 'Add User',
        editUser: 'Edit User',
        dept: 'Department',
        gender: {
          male: 'Male',
          female: 'Female'
        }
      },
      appUser: {
        title: 'App User List',
        userName: 'User Name',
        phoneCode: 'Phone Code',
        userPhone: 'Phone Number',
        userEmail: 'Email',
        userStatus: 'User Status',
        password: 'Password',
        confirmPassword: 'Confirm Password',
        changePassword: 'Change Password',
        bindWechat: 'WeChat',
        bound: 'Bound',
        unbound: 'Unbound',
        lastLoginTime: 'Last Login Time',
        lastLoginIp: 'Last Login IP',
        addUser: 'Add App User',
        editUser: 'Edit App User',
        form: {
          userName: 'Please enter user name',
          phoneCode: 'Please enter phone code, e.g. 86',
          userPhone: 'Please enter phone number',
          userEmail: 'Please enter email',
          userStatus: 'Please select user status',
          newPassword: 'Please enter new password',
          confirmPassword: 'Please confirm new password',
          passwordPlaceholder: 'Leave blank for SMS login only; 6-20 chars with letters and digits',
          passwordNotMatch: 'The two passwords do not match',
          emailFormat: 'Email format is incorrect',
          phoneFormat: 'Phone number format is incorrect'
        }
      },
      menu: {
        home: 'Home',
        title: 'Menu List',
        id: 'ID',
        parentId: 'Parent ID',
        parentMenu: 'Parent Menu',
        menuType: 'Menu Type',
        menuName: 'Menu Name',
        routeName: 'Route Name',
        routePath: 'Route Path',
        pathParam: 'Path Param',
        layout: 'Layout Component',
        layoutBase: 'Base Layout',
        layoutBlank: 'Blank Layout',
        page: 'Page Component',
        i18nKey: 'I18n Key',
        icon: 'Icon',
        localIcon: 'Local Icon',
        iconTypeTitle: 'Icon Type',
        order: 'Order',
        constant: 'Constant',
        keepAlive: 'Keep Alive',
        href: 'Href',
        hideInMenu: 'Hide In Menu',
        activeMenu: 'Active Menu',
        multiTab: 'Multi Tab',
        fixedIndexInTab: 'Fixed Index In Tab',
        query: 'Query Params',
        button: 'Button',
        buttonCode: 'Button Code',
        buttonDesc: 'Button Desc',
        permission: 'Permission Code',
        menuStatus: 'Menu Status',
        isSystem: 'System Built-in',
        form: {
          home: 'Please select home',
          parentMenu: 'Please select parent menu',
          menuType: 'Please select menu type',
          menuName: 'Please enter menu name',
          routeName: 'Please enter route name',
          routePath: 'Please enter route path',
          pathParam: 'Please enter path param',
          page: 'Please select page component',
          layout: 'Please select layout component',
          i18nKey: 'Please enter i18n key',
          icon: 'Please enter iconify name',
          localIcon: 'Please enter local icon name',
          order: 'Please enter order',
          keepAlive: 'Please select whether to cache route',
          href: 'Please enter href',
          hideInMenu: 'Please select whether to hide menu',
          activeMenu: 'Please select route name of the highlighted menu',
          multiTab: 'Please select whether to support multiple tabs',
          fixedInTab: 'Please select whether to fix in the tab',
          fixedIndexInTab: 'Please enter the index fixed in the tab',
          queryKey: 'Please enter route parameter Key',
          queryValue: 'Please enter route parameter Value',
          button: 'Please select whether it is a button',
          buttonCode: 'Please enter button code',
          buttonDesc: 'Please enter button description',
          permission: 'Please enter permission code (e.g. sys:menu:add)',
          menuStatus: 'Please select menu status',
          isSystem: 'Please select whether it is a system built-in menu'
        },
        addMenu: 'Add Catalog',
        editMenu: 'Edit Menu',
        addChildMenu: 'Add Child Menu',
        addChildButton: 'Add Button',
        type: {
          directory: 'Directory',
          menu: 'Menu',
          button: 'Button'
        },
        iconType: {
          iconify: 'Iconify Icon',
          local: 'Local Icon'
        }
      },
      dict: {
        title: 'Dict List',
        dictName: 'Dict Name',
        dictCode: 'Dict Code',
        dictDesc: 'Dict Description',
        dictStatus: 'Dict Status',
        isSystem: 'System Built-in',
        sort: 'Sort',
        itemTitle: 'Dict Item List',
        itemValue: 'Item Value',
        itemLabel: 'Item Label',
        itemDesc: 'Item Description',
        itemStatus: 'Item Status',
        form: {
          dictName: 'Please enter dict name',
          dictCode: 'Please enter dict code',
          dictDesc: 'Please enter dict description',
          dictStatus: 'Please select dict status',
          isSystem: 'Please select whether it is a system built-in dict',
          sort: 'Please enter sort number',
          itemValue: 'Please enter item value',
          itemLabel: 'Please enter item label',
          itemDesc: 'Please enter item description',
          extInfo: 'Please enter extension info',
          itemStatus: 'Please select item status'
        },
        addDict: 'Add Dict',
        editDict: 'Edit Dict',
        addDictItem: 'Add Dict Item',
        editDictItem: 'Edit Dict Item',
        dictManage: 'Dict Manage',
        itemManage: 'Item Manage',
        pleaseSelectDict: 'Please select a dict first'
      },
      config: {
        title: 'System Config List',
        configKey: 'Config Key',
        configValue: 'Config Value',
        defaultValue: 'Default Value',
        configDesc: 'Config Description',
        configType: 'Config Type',
        configGroup: 'Config Group',
        editable: 'Editable',
        isSystem: 'System Built-in',
        required: 'Required',
        validationRule: 'Validation Rule',
        form: {
          configKey: 'Please enter config key',
          configValue: 'Please enter config value',
          defaultValue: 'Please enter default value',
          configDesc: 'Please enter config description',
          configType: 'Please select config type',
          configGroup: 'Please select config group',
          editable: 'Please select whether it is editable',
          isSystem: 'Please select whether it is a system built-in config',
          required: 'Please select whether it is required',
          validationRule: 'Please enter validation rule',
          invalidNumber: 'Please enter valid number',
          invalidBoolean: 'Please enter valid boolean value (true/false/1/0/yes/no)',
          invalidJson: 'Please enter valid JSON format',
          invalidArray: 'Please enter valid array format',
          jsonEmpty: 'JSON string cannot be empty',
          jsonBeautifySuccess: 'JSON format beautified successfully',
          jsonFormatError: 'JSON format error, cannot beautify'
        },
        addConfig: 'Add Config',
        editConfig: 'Edit Config',
        resetConfig: 'Reset Config',
        beautifyJson: 'Beautify JSON',
        editInModal: 'Edit in Modal',
        editJson: 'Edit JSON',
        type: {
          string: 'String',
          number: 'Number',
          boolean: 'Boolean',
          json: 'JSON',
          array: 'Array'
        },
        group: {
          system: 'System',
          security: 'Security',
          log: 'Log',
          network: 'Network',
          storage: 'Storage',
          custom: 'Custom'
        }
      },
      ipBlacklist: {
        title: 'IP Blacklist',
        ip: 'IP Address',
        type: 'Type',
        typePermanent: 'Permanent',
        typeTemporary: 'Temporary',
        reason: 'Reason',
        expireAt: 'Expire At',
        expireAtPlaceholder: 'Select expire time',
        expireRequired: 'Temporary blacklist must have an expire time',
        createdAt: 'Created At',
        reasonPlaceholder: 'Enter reason (optional)',
        addTitle: 'Add IP Blacklist',
        form: {
          ip: 'Please enter IP address',
          type: 'Please select blacklist type'
        }
      },
      announcement: {
        title: 'Announcement List',
        noticeType: 'Type',
        noticeContent: 'Content',
        targetTypeLabel: 'Target',
        targetRole: 'Target Roles',
        targetUser: 'Target Users',
        priority: 'Priority',
        senderName: 'Sender',
        publishedAt: 'Published At',
        publish: 'Publish',
        publishSuccess: 'Published successfully',
        addAnnouncement: 'Add Announcement',
        editAnnouncement: 'Edit Announcement',
        deleteAnnouncement: 'Delete Announcement',
        status: {
          published: 'Published',
          draft: 'Draft'
        },
        type: {
          announcement: 'Announcement',
          system: 'System',
          operation: 'Operation',
          approval: 'Approval'
        },
        targetType: {
          all: 'Broadcast',
          role: 'By Role',
          user: 'Specific User'
        },
        priorities: {
          low: 'Low',
          normal: 'Normal',
          high: 'High',
          urgent: 'Urgent'
        },
        form: {
          title: 'Please enter notice title',
          content: 'Please enter notice content',
          type: 'Please select notice type',
          targetType: 'Please select target',
          status: 'Please select status',
          priority: 'Please select priority',
          roleIds: 'Please enter role IDs',
          userIds: 'Please enter user IDs',
          roleIdsPlaceholder: 'Enter role IDs, multi-select',
          userIdsPlaceholder: 'Enter user IDs, multi-select'
        }
      },
      file: {
        title: 'File List',
        fileName: 'File Name',
        fileSize: 'File Size',
        fileType: 'File Type',
        fileExtension: 'Extension',
        storagePlatform: 'Storage',
        uploadTime: 'Upload Time',
        upload: 'Upload Files',
        download: 'Download',
        preview: 'Preview',
        previewTitle: 'Preview',
        previewNotSupported: 'This file type does not support online preview',
        videoNotSupported: 'Your browser does not support video playback.',
        platform: {
          local: 'Local Storage',
          oss: 'Aliyun OSS'
        },
        form: {
          fileName: 'Enter file name',
          fileExtension: 'Enter extension',
          storagePlatform: 'Select storage platform'
        }
      },
      dept: {
        title: 'Department',
        deptName: 'Department Name',
        deptCode: 'Department Code',
        parentDept: 'Parent Dept',
        sort: 'Sort',
        status: 'Status',
        addDept: 'Add Department',
        editDept: 'Edit Department',
        addChild: 'Add SubDept',
        form: {
          parentDept: 'Select parent department (optional)',
          deptName: 'Enter department name',
          deptCode: 'Enter department code (optional)'
        }
      },
      merchant: {
        title: 'Merchant Management',
        merchantName: 'Merchant Name',
        merchantCode: 'Merchant Code',
        appId: 'AppId',
        appSecret: 'AppSecret',
        contactName: 'Contact',
        contactPhone: 'Phone',
        contactEmail: 'Email',
        remark: 'Remark',
        sort: 'Sort',
        status: 'Status',
        secretUpdatedAt: 'Secret Reset At',
        addMerchant: 'Add Merchant',
        editMerchant: 'Edit Merchant',
        resetSecret: 'Reset Secret',
        resetSecretConfirm:
          'The old secret will be invalidated immediately and the new one is shown only once. Continue?',
        secretResultTitle: 'Merchant Credentials (shown only once)',
        secretOnceWarning:
          'Copy and save the AppSecret now. It cannot be viewed again after closing. Use "Reset Secret" to rotate.',
        copy: 'Copy',
        copied: 'Copied to clipboard',
        copyFailed: 'Copy failed, please select text manually',
        form: {
          merchantName: 'Enter merchant name',
          merchantCode: 'Enter merchant code (optional)',
          appId: 'Enter AppId',
          contactName: 'Enter contact name',
          contactPhone: 'Enter phone',
          contactEmail: 'Enter email',
          remark: 'Enter remark (optional)',
          status: 'Select status',
          emailFormat: 'Invalid email format',
          phoneFormat: 'Invalid phone format'
        }
      },
      openapiLog: {
        title: 'Call Log',
        appId: 'AppId',
        merchantName: 'Merchant',
        method: 'Method',
        path: 'Path',
        status: 'Status',
        errCode: 'Err Code',
        clientIp: 'Client IP',
        latency: 'Latency',
        createdAt: 'Called At',
        form: {
          appId: 'Enter AppId',
          path: 'Enter path',
          method: 'Enter HTTP method',
          errCode: 'Enter err code',
          clientIp: 'Enter client IP',
          status: 'Enter status code'
        }
      },
      scheduler: {
        title: 'Scheduled Task List',
        taskName: 'Task Name',
        taskKey: 'Task Key',
        description: 'Description',
        cronExpression: 'Cron Expression',
        triggerType: 'Trigger Type',
        triggerTypes: {
          cron: 'Cron',
          interval: 'Interval',
          date: 'One-shot'
        },
        status: 'Status',
        statusEnabled: 'Enabled',
        statusDisabled: 'Disabled',
        enable: 'Enable',
        disable: 'Disable',
        lastRunAt: 'Last Run',
        nextRunAt: 'Next Run',
        lastStatus: 'Last Status',
        lastStatuses: {
          success: 'Success',
          failed: 'Failed',
          running: 'Running',
          timeout: 'Timeout'
        },
        timeout: 'Timeout(s)',
        maxRetries: 'Max Retries',
        concurrentPolicy: 'Concurrent Policy',
        concurrentPolicies: {
          skip: 'Skip',
          replace: 'Replace',
          run: 'Allow Concurrent'
        },
        manualTrigger: 'Run Now',
        manualTriggerConfirm: 'Execute this task immediately?',
        manualTriggerSuccess: 'Task triggered',
        cronPreview: 'Preview Schedule',
        nextRunTimes: 'Next 5 Run Times',
        syncRegistry: 'Sync Registry',
        syncRegistrySuccess: 'Sync completed',
        viewLogs: 'Logs',
        triggerParams: 'Trigger Params',
        addTask: 'Add Task',
        editTask: 'Edit Task',
        isSystem: 'System Task',
        taskCategory: 'Category',
        taskCategories: {
          generic: 'Generic',
          system: 'System',
          specialist: 'Specialist'
        },
        template: 'Task Template',
        templatePlaceholder: 'Select task template (no logic)',
        taskKeyPlaceholder: 'Enter task key',
        taskKeyHint: 'Enter a unique task key, e.g. my-daily-ping',
        taskKeyRequired: 'Please enter task key, must be unique',
        advancedConfig: 'Advanced',
        schemaLoading: 'Loading parameters...',
        noParams: 'No parameters',
        paramPlaceholder: 'Enter {label}',
        form: {
          taskName: 'Enter task name',
          taskKey: 'Enter task key',
          cronExpression: 'Enter cron expression',
          triggerType: 'Select trigger type',
          status: 'Select status',
          concurrentPolicy: 'Select concurrent policy',
          description: 'Enter description'
        }
      },
      schedulerLog: {
        title: 'Task Execution Log',
        taskName: 'Task Name',
        status: 'Status',
        startTime: 'Start Time',
        endTime: 'End Time',
        duration: 'Duration(ms)',
        triggeredBy: 'Triggered By',
        triggeredByValues: {
          scheduler: 'Auto',
          manual: 'Manual'
        },
        result: 'Result',
        errorMessage: 'Error',
        viewDetail: 'Detail',
        clear: 'Clear Logs',
        clearConfirm: 'Clear execution logs older than 30 days?',
        detailTitle: 'Execution Log Detail',
        form: {
          taskName: 'Enter task name',
          status: 'Select status',
          timeRange: 'Time Range'
        }
      }
    },
    log: {
      loginLog: {
        title: 'Login Log List',
        username: 'Username',
        ip: 'Login IP',
        status: 'Status',
        detail: 'Detail',
        userAgent: 'Device',
        loginTime: 'Login Time',
        success: 'Success',
        failed: 'Failed',
        clear: 'Clear Logs',
        clearConfirm: 'Confirm to clear login logs older than 30 days?',
        form: {
          username: 'Enter username',
          ip: 'Enter IP address',
          status: 'Select status',
          timeRange: 'Time Range',
          startTime: 'Start time',
          endTime: 'End time'
        }
      },
      operationLog: {
        title: 'Operation Log List',
        username: 'Operator',
        module: 'Module',
        action: 'Action',
        description: 'Description',
        method: 'Method',
        path: 'Path',
        ip: 'IP',
        responseCode: 'Status Code',
        responseResult: 'Response Result',
        elapsedMs: 'Elapsed(ms)',
        requestParams: 'Request Params',
        operateTime: 'Operate Time',
        viewDetail: 'Detail',
        detailTitle: 'Operation Log Detail',
        clear: 'Clear Logs',
        clearConfirm: 'Confirm to clear operation logs older than 30 days?',
        form: {
          username: 'Enter operator',
          module: 'Enter module',
          action: 'Enter action',
          timeRange: 'Time Range',
          startTime: 'Start time',
          endTime: 'End time'
        }
      },
      onlineUser: {
        title: 'Online Users',
        username: 'Username',
        nickname: 'Nickname',
        ip: 'Login IP',
        userAgent: 'Device',
        loginTime: 'Login Time',
        kick: 'Kick',
        kickAll: 'Kick All',
        kickConfirm: 'Confirm to kick this user offline?',
        kickAllConfirm: 'Confirm to kick all online users offline?',
        kickSuccess: 'User kicked offline',
        kickAllSuccess: 'All sessions kicked offline',
        form: {
          username: 'Enter username',
          ip: 'Enter IP address'
        }
      }
    }
  },
  form: {
    required: 'Cannot be empty',
    userName: {
      required: 'Please enter user name',
      invalid: 'User name format is incorrect'
    },
    phone: {
      required: 'Please enter phone number',
      invalid: 'Phone number format is incorrect'
    },
    pwd: {
      required: 'Please enter password',
      invalid: '6-20 characters, must include both letters and numbers'
    },
    confirmPwd: {
      required: 'Please enter password again',
      invalid: 'The two passwords are inconsistent'
    },
    code: {
      required: 'Please enter verification code',
      invalid: 'Verification code format is incorrect'
    },
    email: {
      required: 'Please enter email',
      invalid: 'Email format is incorrect'
    }
  },
  dropdown: {
    closeCurrent: 'Close Current',
    closeOther: 'Close Other',
    closeLeft: 'Close Left',
    closeRight: 'Close Right',
    closeAll: 'Close All',
    pin: 'Pin Tab',
    unpin: 'Unpin Tab'
  },
  icon: {
    themeConfig: 'Theme Configuration',
    themeSchema: 'Theme Schema',
    lang: 'Switch Language',
    fullscreen: 'Fullscreen',
    fullscreenExit: 'Exit Fullscreen',
    reload: 'Reload Page',
    collapse: 'Collapse Menu',
    expand: 'Expand Menu',
    pin: 'Pin',
    unpin: 'Unpin'
  },
  datatable: {
    itemCount: 'Total {total} items',
    fixed: {
      left: 'Left Fixed',
      right: 'Right Fixed',
      unFixed: 'Unfixed'
    }
  },
  exportTask: {
    title: 'Export Records',
    tooltip: 'Export Records',
    taskName: 'Task Name',
    moduleKey: 'Module',
    status: {
      title: 'Status',
      pending: 'Pending',
      processing: 'Processing',
      completed: 'Completed',
      failed: 'Failed'
    },
    totalRows: 'Total Rows',
    fileSize: 'File Size',
    errorMessage: 'Error Message',
    createdAt: 'Created At',
    finishedAt: 'Finished At',
    noRecords: 'No export records',
    viewAll: 'View All',
    asyncExport: 'Async Export',
    submitSuccess: 'Export task submitted',
    submitFailed: 'Failed to submit export task',
    downloadFailed: 'Failed to download export file'
  },
  notification: {
    title: 'Notification Center',
    tooltip: 'Notification Center',
    markAllAsRead: 'Mark all as read',
    noNotifications: 'No notifications',
    markAllReadSuccess: 'Marked all as read',
    priority: {
      low: 'Low',
      normal: 'Normal',
      high: 'High',
      urgent: 'Urgent'
    }
  }
};

export default local;
