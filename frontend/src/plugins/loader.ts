// 前端插件动态加载器
// 使用 Vite import.meta.glob 扫描 plugins/*/index.ts
// 插件安装时复制文件到此目录, 卸载时删除.
// 目录为空时此模块不加载任何插件.

const pluginModules = import.meta.glob<{ default?: unknown }>('./*/index.ts', { eager: true });

export async function initPlugins() {
  const names = Object.keys(pluginModules);
  if (names.length === 0) return;

  for (const path of names) {
    try {
      // eager 已加载, 此处触发副作用(自注册 Header 组件等)
      pluginModules[path];
    } catch (e) {
      console.warn(`[PluginLoader] Failed to load plugin: ${path}`, e);
    }
  }
}
