import type { PluginOption } from 'vite';
import { spawnSync } from 'node:child_process';

/** virtual module 标识 */
const VIRTUAL_ID = 'virtual:smilex-git-log';
const RESOLVED_ID = `\0${VIRTUAL_ID}`;

/** 最多采集的提交条数 */
const COMMIT_LIMIT = 50;

/**
 * 构建期采集 git 提交历史。
 *
 * - 通过 `spawnSync` 调用 `git log`,git 会自动向上查找仓库根,无需写死工作目录;
 * - 字段以 `|` 分隔(hash / short hash / date 均不含 `|`;提交信息可能含 `|`,故用剩余部分 join 还原);
 * - 无 git / 非 git 目录 / 命令失败时返回 `available:false`,不阻断构建。
 */
function collectGitLog() {
  try {
    const result = spawnSync(
      'git',
      ['log', `--max-count=${COMMIT_LIMIT}`, '--pretty=format:%H|%h|%an|%ad|%s', '--date=iso'],
      { encoding: 'utf-8' }
    );

    if (result.status !== 0 || !result.stdout) {
      return { available: false, generatedAt: '', commits: [] };
    }

    const commits = result.stdout
      .trim()
      .split('\n')
      .filter(Boolean)
      .map(line => {
        const [hash, shortHash, author, date, ...messageParts] = line.split('|');
        return {
          hash,
          shortHash,
          author,
          date,
          message: messageParts.join('|')
        };
      });

    return {
      available: true,
      generatedAt: new Date().toISOString(),
      commits
    };
  } catch {
    return { available: false, generatedAt: '', commits: [] };
  }
}

/**
 * 将 git 提交历史以 virtual module `virtual:smilex-git-log` 暴露给前端。
 *
 * dev 启动与 build 时各执行一次采集,适合「关于」这类展示性场景(非实时)。
 */
export function setupGitLogPlugin(): PluginOption {
  let data: ReturnType<typeof collectGitLog> | null = null;

  return {
    name: 'vite-plugin-smilex-git-log',
    buildStart() {
      data = collectGitLog();
    },
    resolveId(id) {
      if (id === VIRTUAL_ID) {
        return RESOLVED_ID;
      }
      return null;
    },
    load(id) {
      if (id === RESOLVED_ID) {
        const payload = data ?? { available: false, generatedAt: '', commits: [] };
        return `export default ${JSON.stringify(payload)}`;
      }
      return null;
    }
  };
}
