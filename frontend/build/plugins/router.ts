import type { RouteMeta } from 'vue-router';
import ElegantVueRouter from '@elegant-router/vue/vite';
import type { RouteKey } from '@elegant-router/types';

export function setupElegantRouter() {
  return ElegantVueRouter({
    layouts: {
      base: 'src/layouts/base-layout/index.vue',
      blank: 'src/layouts/blank-layout/index.vue'
    },
    routePathTransformer(routeName, routePath) {
      const key = routeName as RouteKey;

      if (key === 'login') {
        const modules: UnionKey.LoginModule[] = ['pwd-login', 'code-login', 'register', 'reset-pwd', 'bind-wechat'];

        const moduleReg = modules.join('|');

        return `/login/:module(${moduleReg})?`;
      }

      return routePath;
    },
    onRouteMetaGen(routeName) {
      const key = routeName as RouteKey;

      // export-record 作为常量路由：动态路由模式下后端菜单不返回 hideInMenu 路由，
      // 头部「查看全部」需直接跳转，故纳入 constant 列表保证始终注册
      const constantRoutes: RouteKey[] = ['login', '403', '404', '500', 'export-record', 'about'];

      const meta: Partial<RouteMeta> = {
        title: key,
        i18nKey: `route.${key}` as App.I18n.I18nKey
      };

      if (constantRoutes.includes(key)) {
        meta.constant = true;
      }

      // 「关于」为常驻路由,补充菜单图标与排序,使其排到侧边栏底部
      if (key === 'about') {
        meta.icon = 'mdi:information-outline';
        meta.order = 9999;
      }

      return meta;
    }
  });
}
