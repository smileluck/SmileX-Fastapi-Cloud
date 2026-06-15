/** The global namespace for the app */
declare namespace App {
  /** Theme namespace */
  namespace Theme {
    type ColorPaletteNumber = import('@sa/color').ColorPaletteNumber;

    /** NaiveUI theme overrides that can be specified in preset */
    type NaiveUIThemeOverride = import('naive-ui').GlobalThemeOverrides;

    /** Theme setting */
    interface ThemeSetting {
      /** Theme scheme */
      themeScheme: UnionKey.ThemeScheme;
      /** grayscale mode */
      grayscale: boolean;
      /** colour weakness mode */
      colourWeakness: boolean;
      /** Whether to recommend color */
      recommendColor: boolean;
      /** Theme color */
      themeColor: string;
      /** Theme radius */
      themeRadius: number;
      /** Other color */
      otherColor: OtherColor;
      /** Whether info color is followed by the primary color */
      isInfoFollowPrimary: boolean;
      /** Layout */
      layout: {
        /** Layout mode */
        mode: UnionKey.ThemeLayoutMode;
        /** Scroll mode */
        scrollMode: UnionKey.ThemeScrollMode;
      };
      /** Page */
      page: {
        /** Whether to show the page transition */
        animate: boolean;
        /** Page animate mode */
        animateMode: UnionKey.ThemePageAnimateMode;
      };
      /** Header */
      header: {
        /** Header height */
        height: number;
        /** Header breadcrumb */
        breadcrumb: {
          /** Whether to show the breadcrumb */
          visible: boolean;
          /** Whether to show the breadcrumb icon */
          showIcon: boolean;
        };
        /** Multilingual */
        multilingual: {
          /** Whether to show the multilingual */
          visible: boolean;
        };
        globalSearch: {
          /** Whether to show the GlobalSearch */
          visible: boolean;
        };
      };
      /** Tab */
      tab: {
        /** Whether to show the tab */
        visible: boolean;
        /**
         * Whether to cache the tab
         *
         * If cache, the tabs will get from the local storage when the page is refreshed
         */
        cache: boolean;
        /** Tab height */
        height: number;
        /** Tab mode */
        mode: UnionKey.ThemeTabMode;
        /** Whether to close tab by middle click */
        closeTabByMiddleClick: boolean;
      };
      /** Fixed header and tab */
      fixedHeaderAndTab: boolean;
      /** Sider */
      sider: {
        /** Inverted sider */
        inverted: boolean;
        /** Sider width */
        width: number;
        /** Collapsed sider width */
        collapsedWidth: number;
        /** Sider width when the layout is 'vertical-mix', 'top-hybrid-sidebar-first', or 'top-hybrid-header-first' */
        mixWidth: number;
        /**
         * Collapsed sider width when the layout is 'vertical-mix', 'top-hybrid-sidebar-first', or
         * 'top-hybrid-header-first'
         */
        mixCollapsedWidth: number;
        /** Child menu width when the layout is 'vertical-mix', 'top-hybrid-sidebar-first', or 'top-hybrid-header-first' */
        mixChildMenuWidth: number;
        /** Whether to auto select the first submenu */
        autoSelectFirstMenu: boolean;
      };
      /** Footer */
      footer: {
        /** Whether to show the footer */
        visible: boolean;
        /** Whether fixed the footer */
        fixed: boolean;
        /** Footer height */
        height: number;
        /**
         * Whether float the footer to the right when the layout is 'top-hybrid-sidebar-first' or
         * 'top-hybrid-header-first'
         */
        right: boolean;
      };
      /** Watermark */
      watermark: {
        /** Whether to show the watermark */
        visible: boolean;
        /** Watermark text */
        text: string;
        /** Whether to use user name as watermark text */
        enableUserName: boolean;
        /** Whether to use current time as watermark text */
        enableTime: boolean;
        /** Time format for watermark text */
        timeFormat: string;
      };
      /** define some theme settings tokens, will transform to css variables */
      tokens: {
        light: ThemeSettingToken;
        dark?: {
          [K in keyof ThemeSettingToken]?: Partial<ThemeSettingToken[K]>;
        };
      };
    }

    interface OtherColor {
      info: string;
      success: string;
      warning: string;
      error: string;
    }

    interface ThemeColor extends OtherColor {
      primary: string;
    }

    type ThemeColorKey = keyof ThemeColor;

    type ThemePaletteColor = {
      [key in ThemeColorKey | `${ThemeColorKey}-${ColorPaletteNumber}`]: string;
    };

    type BaseToken = Record<string, Record<string, string>>;

    interface ThemeSettingTokenColor {
      /** the progress bar color, if not set, will use the primary color */
      nprogress?: string;
      container: string;
      layout: string;
      inverted: string;
      'base-text': string;
    }

    interface ThemeSettingTokenBoxShadow {
      header: string;
      sider: string;
      tab: string;
    }

    interface ThemeSettingToken {
      colors: ThemeSettingTokenColor;
      boxShadow: ThemeSettingTokenBoxShadow;
    }

    type ThemeTokenColor = ThemePaletteColor & ThemeSettingTokenColor;

    /** Theme token CSS variables */
    type ThemeTokenCSSVars = {
      colors: ThemeTokenColor & { [key: string]: string };
      boxShadow: ThemeSettingTokenBoxShadow & { [key: string]: string };
    };
  }

  /** Global namespace */
  namespace Global {
    type VNode = import('vue').VNode;
    type RouteLocationNormalizedLoaded = import('vue-router').RouteLocationNormalizedLoaded;
    type RouteKey = import('@elegant-router/types').RouteKey;
    type RouteMap = import('@elegant-router/types').RouteMap;
    type RoutePath = import('@elegant-router/types').RoutePath;
    type LastLevelRouteKey = import('@elegant-router/types').LastLevelRouteKey;

    /** The router push options */
    type RouterPushOptions = {
      query?: Record<string, string>;
      params?: Record<string, string>;
    };

    /** The global header props */
    interface HeaderProps {
      /** Whether to show the logo */
      showLogo?: boolean;
      /** Whether to show the menu toggler */
      showMenuToggler?: boolean;
      /** Whether to show the menu */
      showMenu?: boolean;
    }

    /** The global menu */
    type Menu = {
      /**
       * The menu key
       *
       * Equal to the route key
       */
      key: string;
      /** The menu label */
      label: string;
      /** The menu i18n key */
      i18nKey?: I18n.I18nKey | null;
      /** The route key */
      routeKey: RouteKey;
      /** The route path */
      routePath: RoutePath;
      /** The menu icon */
      icon?: () => VNode;
      /** The menu children */
      children?: Menu[];
    };

    type Breadcrumb = Omit<Menu, 'children'> & {
      options?: Breadcrumb[];
    };

    /** Tab route */
    type TabRoute = Pick<RouteLocationNormalizedLoaded, 'name' | 'path' | 'meta'> &
      Partial<Pick<RouteLocationNormalizedLoaded, 'fullPath' | 'query' | 'matched'>>;

    /** The global tab */
    type Tab = {
      /** The tab id */
      id: string;
      /** The tab label */
      label: string;
      /**
       * The new tab label
       *
       * If set, the tab label will be replaced by this value
       */
      newLabel?: string;
      /**
       * The old tab label
       *
       * when reset the tab label, the tab label will be replaced by this value
       */
      oldLabel?: string;
      /** The tab route key */
      routeKey: LastLevelRouteKey;
      /** The tab route path */
      routePath: RouteMap[LastLevelRouteKey];
      /** The tab route full path */
      fullPath: string;
      /** The tab fixed index */
      fixedIndex?: number | null;
      /**
       * Tab icon
       *
       * Iconify icon
       */
      icon?: string;
      /**
       * Tab local icon
       *
       * Local icon
       */
      localIcon?: string;
      /** I18n key */
      i18nKey?: I18n.I18nKey | null;
    };

    /** Form rule */
    type FormRule = import('naive-ui').FormItemRule;

    /** The global dropdown key */
    type DropdownKey = 'closeCurrent' | 'closeOther' | 'closeLeft' | 'closeRight' | 'closeAll' | 'pin' | 'unpin';
  }

  /**
   * I18n namespace
   *
   * Locales type
   */
  namespace I18n {
    type RouteKey = import('@elegant-router/types').RouteKey;

    type LangType = 'en-US' | 'zh-CN';

    type LangOption = {
      label: string;
      key: LangType;
    };

    type I18nRouteKey = Exclude<RouteKey, 'root' | 'not-found'>;

    type FormMsg = {
      required: string;
      invalid: string;
    };

    type Schema = {
      system: {
        title: string;
        updateTitle: string;
        updateContent: string;
        updateConfirm: string;
        updateCancel: string;
      };
      common: {
        selectAtLeastOne: string;
        pleaseSelect: string;
        action: string;
        add: string;
        addSuccess: string;
        backToHome: string;
        back: string;
        batchDelete: string;
        cancel: string;
        close: string;
        check: string;
        selectAll: string;
        expandColumn: string;
        columnSetting: string;
        config: string;
        confirm: string;
        delete: string;
        deleteSuccess: string;
        deleteFailed: string;
        confirmDelete: string;
        edit: string;
        warning: string;
        error: string;
        index: string;
        keywordSearch: string;
        logout: string;
        logoutConfirm: string;
        lookForward: string;
        modify: string;
        modifySuccess: string;
        saveSuccess: string;
        noData: string;
        operate: string;
        pleaseCheckValue: string;
        pleaseEnter: string;
        status: string;
        title: string;
        refresh: string;
        reset: string;
        search: string;
        switch: string;
        tip: string;
        trigger: string;
        update: string;
        updateSuccess: string;
        updateFailed: string;
        userCenter: string;
        changePassword: string;
        loadDataFailed: string;
        yesOrNo: {
          yes: string;
          no: string;
        };
      };
      request: {
        logout: string;
        logoutMsg: string;
        logoutWithModal: string;
        logoutWithModalMsg: string;
        refreshToken: string;
        tokenExpired: string;
        error: string;
      };
      theme: {
        themeDrawerTitle: string;
        tabs: {
          appearance: string;
          layout: string;
          general: string;
          preset: string;
        };
        appearance: {
          themeSchema: { title: string } & Record<UnionKey.ThemeScheme, string>;
          grayscale: string;
          colourWeakness: string;
          themeColor: {
            title: string;
            followPrimary: string;
          } & Record<Theme.ThemeColorKey, string>;
          recommendColor: string;
          recommendColorDesc: string;
          themeRadius: {
            title: string;
          };
          preset: {
            title: string;
            apply: string;
            applySuccess: string;
            [key: string]:
              | {
                  name: string;
                  desc: string;
                }
              | string;
          };
        };
        layout: {
          layoutMode: { title: string } & Record<UnionKey.ThemeLayoutMode, string> & {
              [K in `${UnionKey.ThemeLayoutMode}_detail`]: string;
            };
          tab: {
            title: string;
            visible: string;
            cache: string;
            cacheTip: string;
            height: string;
            mode: { title: string } & Record<UnionKey.ThemeTabMode, string>;
            closeByMiddleClick: string;
            closeByMiddleClickTip: string;
          };
          header: {
            title: string;
            height: string;
            breadcrumb: {
              visible: string;
              showIcon: string;
            };
          };
          sider: {
            title: string;
            inverted: string;
            width: string;
            collapsedWidth: string;
            mixWidth: string;
            mixCollapsedWidth: string;
            mixChildMenuWidth: string;
            autoSelectFirstMenu: string;
            autoSelectFirstMenuTip: string;
          };
          footer: {
            title: string;
            visible: string;
            fixed: string;
            height: string;
            right: string;
          };
          content: {
            title: string;
            scrollMode: { title: string; tip: string } & Record<UnionKey.ThemeScrollMode, string>;
            page: {
              animate: string;
              mode: { title: string } & Record<UnionKey.ThemePageAnimateMode, string>;
            };
            fixedHeaderAndTab: string;
          };
        };
        general: {
          title: string;
          watermark: {
            title: string;
            visible: string;
            text: string;
            enableUserName: string;
            enableTime: string;
            timeFormat: string;
          };
          multilingual: {
            title: string;
            visible: string;
          };
          globalSearch: {
            title: string;
            visible: string;
          };
        };
        configOperation: {
          copyConfig: string;
          copySuccessMsg: string;
          resetConfig: string;
          resetSuccessMsg: string;
        };
      };
      route: Record<I18nRouteKey, string>;
      page: {
        login: {
          common: {
            loginOrRegister: string;
            userNamePlaceholder: string;
            phonePlaceholder: string;
            codePlaceholder: string;
            passwordPlaceholder: string;
            confirmPasswordPlaceholder: string;
            codeLogin: string;
            confirm: string;
            back: string;
            validateSuccess: string;
            loginSuccess: string;
            welcomeBack: string;
          };
          pwdLogin: {
            title: string;
            rememberMe: string;
            forgetPassword: string;
            register: string;
            otherAccountLogin: string;
            otherLoginMode: string;
            superAdmin: string;
            admin: string;
            user: string;
          };
          codeLogin: {
            title: string;
            getCode: string;
            reGetCode: string;
            sendCodeSuccess: string;
            imageCodePlaceholder: string;
          };
          register: {
            title: string;
            agreement: string;
            protocol: string;
            policy: string;
          };
          resetPwd: {
            title: string;
          };
          bindWeChat: {
            title: string;
          };
        };
        home: {
          branchDesc: string;
          greeting: string;
          weatherDesc: string;
          projectCount: string;
          todo: string;
          message: string;
          downloadCount: string;
          registerCount: string;
          schedule: string;
          study: string;
          work: string;
          rest: string;
          entertainment: string;
          visitCount: string;
          turnover: string;
          dealCount: string;
          projectNews: {
            title: string;
            moreNews: string;
            desc1: string;
            desc2: string;
            desc3: string;
            desc4: string;
            desc5: string;
          };
          creativity: string;
        };
        monitor: {
          systemResources: string;
          apiStats: string;
          systemInfo: string;
          osName: string;
          cpuCount: string;
          cpuUsage: string;
          memoryUsage: string;
          diskUsage: string;
          avgResponseTime: string;
          errorRate: string;
          uptime: string;
          processCount: string;
          pythonVersion: string;
          day: string;
          hour: string;
          minute: string;
        };

        demo: {
          upload: {
            title: string;
            singleUpload: string;
            multiUpload: string;
            selectFile: string;
            selectFiles: string;
            uploading: string;
            uploadSuccess: string;
            uploadFailed: string;
            fileSize: string;
            fileType: string;
            fileName: string;
            uploadResult: string;
            dragOrClick: string;
            startUpload: string;
          };
          dict: {
            selectDemo: string;
            selectLabel: string;
            selectWithDefault: string;
            tagDemo: string;
            tagLabel: string;
            textDemo: string;
            textLabel: string;
            tableDemo: string;
            tableLabel: string;
          };
        };

        manage: {
          common: {
            status: {
              enable: string;
              disable: string;
            };
          };
          role: {
            title: string;
            roleName: string;
            roleCode: string;
            roleStatus: string;
            roleDesc: string;
            form: {
              roleName: string;
              roleCode: string;
              roleStatus: string;
              roleDesc: string;
            };
            addRole: string;
            editRole: string;
            menuAuth: string;
            buttonAuth: string;
          };
          user: {
            title: string;
            userName: string;
            userGender: string;
            password: string;
            confirmPassword: string;
            nickName: string;
            userPhone: string;
            userEmail: string;
            userStatus: string;
            userRole: string;
            isSuperuser: string;
            changePassword: string;
            lastLoginTime: string;
            lastLoginIp: string;
            form: {
              userName: string;
              userGender: string;
              nickName: string;
              userPhone: string;
              userEmail: string;
              userStatus: string;
              userRole: string;
              isSuperuser: string;
              newPassword: string;
              confirmPassword: string;
              passwordMinLength: string;
              passwordNotMatch: string;
              usernameLength: string;
              passwordLength: string;
              emailFormat: string;
              phoneFormat: string;
            };
            addUser: string;
            editUser: string;
            gender: {
              male: string;
              female: string;
            };
          };
          menu: {
            home: string;
            title: string;
            id: string;
            parentId: string;
            parentMenu: string;
            menuType: string;
            menuName: string;
            routeName: string;
            routePath: string;
            pathParam: string;
            layout: string;
            layoutBase: string;
            layoutBlank: string;
            page: string;
            i18nKey: string;
            icon: string;
            localIcon: string;
            iconTypeTitle: string;
            order: string;
            constant: string;
            keepAlive: string;
            href: string;
            hideInMenu: string;
            activeMenu: string;
            multiTab: string;
            fixedIndexInTab: string;
            query: string;
            button: string;
            buttonCode: string;
            buttonDesc: string;
            permission: string;
            isSystem: string;
            menuStatus: string;
            form: {
              home: string;
              parentMenu: string;
              menuType: string;
              menuName: string;
              routeName: string;
              routePath: string;
              pathParam: string;
              layout: string;
              page: string;
              i18nKey: string;
              icon: string;
              localIcon: string;
              order: string;
              keepAlive: string;
              href: string;
              hideInMenu: string;
              activeMenu: string;
              multiTab: string;
              fixedInTab: string;
              fixedIndexInTab: string;
              queryKey: string;
              queryValue: string;
              button: string;
              buttonCode: string;
              buttonDesc: string;
              permission: string;
              isSystem: string;
              menuStatus: string;
            };
            addMenu: string;
            editMenu: string;
            addChildMenu: string;
            addChildButton: string;
            type: {
              directory: string;
              menu: string;
              button: string;
            };
            iconType: {
              iconify: string;
              local: string;
            };
          };
          dict: {
            title: string;
            dictManage: string;
            itemManage: string;
            itemTitle: string;
            dictName: string;
            dictCode: string;
            dictDesc: string;
            dictStatus: string;
            isSystem: string;
            sort: string;
            itemValue: string;
            itemLabel: string;
            itemDesc: string;
            itemStatus: string;
            form: {
              dictName: string;
              dictCode: string;
              dictDesc: string;
              dictStatus: string;
              isSystem: string;
              sort: string;
              itemValue: string;
              itemLabel: string;
              itemDesc: string;
              extInfo: string;
              itemStatus: string;
            };
            addDict: string;
            editDict: string;
            addDictItem: string;
            editDictItem: string;
            pleaseSelectDict: string;
          };
          config: {
            title: string;
            configKey: string;
            configValue: string;
            defaultValue: string;
            configDesc: string;
            configType: string;
            configGroup: string;
            editable: string;
            isSystem: string;
            required: string;
            resetConfig: string;
            validationRule: string;
            beautifyJson: string;
            editInModal: string;
            editJson: string;
            form: {
              configKey: string;
              configValue: string;
              defaultValue: string;
              validationRule: string;
              configDesc: string;
              configType: string;
              configGroup: string;
              editable: string;
              isSystem: string;
              required: string;
              invalidNumber: string;
              invalidBoolean: string;
              invalidJson: string;
              invalidArray: string;
              jsonEmpty: string;
              jsonBeautifySuccess: string;
              jsonFormatError: string;
            };
            addConfig: string;
            editConfig: string;
            type: {
              string: string;
              number: string;
              boolean: string;
              json: string;
              array: string;
            };
            group: {
              system: string;
              security: string;
              log: string;
              network: string;
              storage: string;
              custom: string;
            };
          };
          ipBlacklist: {
            title: string;
            ip: string;
            type: string;
            typePermanent: string;
            typeTemporary: string;
            reason: string;
            expireAt: string;
            expireAtPlaceholder: string;
            expireRequired: string;
            createdAt: string;
            reasonPlaceholder: string;
            addTitle: string;
            form: {
              ip: string;
              type: string;
            };
          };
          announcement: {
            title: string;
            noticeType: string;
            targetTypeLabel: string;
            priority: string;
            senderName: string;
            publishedAt: string;
            publish: string;
            publishSuccess: string;
            status: {
              published: string;
              draft: string;
            };
            type: {
              announcement: string;
              system: string;
              operation: string;
              approval: string;
            };
            targetType: {
              all: string;
              role: string;
              user: string;
            };
            form: {
              title: string;
              type: string;
              targetType: string;
              status: string;
              priority: string;
            };
          };
          file: {
            title: string;
            fileName: string;
            fileSize: string;
            fileType: string;
            fileExtension: string;
            storagePlatform: string;
            uploadTime: string;
            upload: string;
            download: string;
            preview: string;
            platform: {
              local: string;
              oss: string;
            };
            form: {
              fileName: string;
              fileExtension: string;
              storagePlatform: string;
            };
          };
        };
      log: {
        loginLog: {
          title: string;
          username: string;
          ip: string;
          status: string;
          detail: string;
          userAgent: string;
          loginTime: string;
          success: string;
          failed: string;
          clear: string;
          clearConfirm: string;
          form: {
            username: string;
            ip: string;
            status: string;
            timeRange: string;
            startTime: string;
            endTime: string;
          };
        };
        operationLog: {
          title: string;
          username: string;
          module: string;
          action: string;
          description: string;
          method: string;
          path: string;
          ip: string;
          responseCode: string;
          responseResult: string;
          elapsedMs: string;
          requestParams: string;
          operateTime: string;
          viewDetail: string;
          detailTitle: string;
          clear: string;
          clearConfirm: string;
          form: {
            username: string;
            module: string;
            action: string;
            timeRange: string;
            startTime: string;
            endTime: string;
          };
        };
        onlineUser: {
          title: string;
          username: string;
          nickname: string;
          ip: string;
          userAgent: string;
          loginTime: string;
          kick: string;
          kickAll: string;
          kickConfirm: string;
          kickAllConfirm: string;
          kickSuccess: string;
          kickAllSuccess: string;
          form: {
            username: string;
            ip: string;
          };
        };
        robotEventLog: {
          title: string;
          robotName: string;
          eventType: string;
          eventStatus: string;
          eventContent: string;
          typeTask: string;
          typeAlarm: string;
          statusNormal: string;
          statusAbnormal: string;
          clear: string;
          clearConfirm: string;
          form: {
            robotName: string;
            eventType: string;
            eventStatus: string;
            timeRange: string;
          };
        };
      };
      };
      form: {
        required: string;
        userName: FormMsg;
        phone: FormMsg;
        pwd: FormMsg;
        confirmPwd: FormMsg;
        code: FormMsg;
        email: FormMsg;
      };
      dropdown: Record<Global.DropdownKey, string>;
      icon: {
        themeConfig: string;
        themeSchema: string;
        lang: string;
        fullscreen: string;
        fullscreenExit: string;
        reload: string;
        collapse: string;
        expand: string;
        pin: string;
        unpin: string;
      };
      datatable: {
        itemCount: string;
        fixed: {
          left: string;
          right: string;
          unFixed: string;
        };
      };
      notification: {
        title: string;
        markAllAsRead: string;
        noNotifications: string;
        markAllReadSuccess: string;
        priority: {
          low: string;
          normal: string;
          high: string;
          urgent: string;
        };
      };
    };

    type PluginI18nSchema = {
      route: {
        scheduler: string;
      };
      page: {
        manage: {
          scheduler: {
            title: string;
            taskName: string;
            taskKey: string;
            description: string;
            cronExpression: string;
            triggerType: string;
            triggerTypes: {
              cron: string;
              interval: string;
              date: string;
            };
            status: string;
            statusEnabled: string;
            statusDisabled: string;
            enable: string;
            disable: string;
            lastRunAt: string;
            nextRunAt: string;
            lastStatus: string;
            lastStatuses: {
              success: string;
              failed: string;
              running: string;
              timeout: string;
            };
            timeout: string;
            maxRetries: string;
            concurrentPolicy: string;
            concurrentPolicies: {
              skip: string;
              replace: string;
              run: string;
            };
            manualTrigger: string;
            manualTriggerConfirm: string;
            manualTriggerSuccess: string;
            cronPreview: string;
            nextRunTimes: string;
            syncRegistry: string;
            syncRegistrySuccess: string;
            viewLogs: string;
            triggerParams: string;
            addTask: string;
            editTask: string;
            isSystem: string;
            form: {
              taskName: string;
              taskKey: string;
              cronExpression: string;
              triggerType: string;
              status: string;
              concurrentPolicy: string;
              description: string;
            };
          };
          schedulerLog: {
            title: string;
            taskName: string;
            status: string;
            startTime: string;
            endTime: string;
            duration: string;
            triggeredBy: string;
            triggeredByValues: {
              scheduler: string;
              manual: string;
            };
            result: string;
            errorMessage: string;
            viewDetail: string;
            clear: string;
            clearConfirm: string;
            detailTitle: string;
            form: {
              taskName: string;
              status: string;
              timeRange: string;
            };
          };
        };
      };
    }

    type GetI18nKey<T extends Record<string, unknown>, K extends keyof T = keyof T> = K extends string
      ? T[K] extends Record<string, unknown>
        ? `${K}.${GetI18nKey<T[K]>}`
        : K
      : never;

    type I18nKey = GetI18nKey<Schema> | GetI18nKey<PluginI18nSchema>;

    type TranslateOptions<Locales extends string> = import('vue-i18n').TranslateOptions<Locales>;

    interface $T {
      (key: I18nKey): string;
      (key: I18nKey, plural: number, options?: TranslateOptions<LangType>): string;
      (key: I18nKey, defaultMsg: string, options?: TranslateOptions<I18nKey>): string;
      (key: I18nKey, list: unknown[], options?: TranslateOptions<I18nKey>): string;
      (key: I18nKey, list: unknown[], plural: number): string;
      (key: I18nKey, list: unknown[], defaultMsg: string): string;
      (key: I18nKey, named: Record<string, unknown>, options?: TranslateOptions<LangType>): string;
      (key: I18nKey, named: Record<string, unknown>, plural: number): string;
      (key: I18nKey, named: Record<string, unknown>, defaultMsg: string): string;
    }
  }

  /** Service namespace */
  namespace Service {
    /** Other baseURL key */
    type OtherBaseURLKey = 'demo';

    interface ServiceConfigItem {
      /** The backend service base url */
      baseURL: string;
      /** The proxy pattern of the backend service base url */
      proxyPattern: string;
    }

    interface OtherServiceConfigItem extends ServiceConfigItem {
      key: OtherBaseURLKey;
    }

    /** The backend service config */
    interface ServiceConfig extends ServiceConfigItem {
      /** Other backend service config */
      other: OtherServiceConfigItem[];
    }

    interface SimpleServiceConfig extends Pick<ServiceConfigItem, 'baseURL'> {
      other: Record<OtherBaseURLKey, string>;
    }

    /** The backend service response data */
    type Response<T = unknown> = {
      /** The backend service response code */
      code: string;
      /** The backend service response message */
      msg: string;
      /** The backend service response data */
      data: T;
      /** The backend service request id */
      requestId?: string;
      /** The backend service error code */
      error_code?: string;
    };

    /** The demo backend service response data */
    type DemoResponse<T = unknown> = {
      /** The backend service response code */
      status: string;
      /** The backend service response message */
      message: string;
      /** The backend service response data */
      result: T;
    };
  }
}
