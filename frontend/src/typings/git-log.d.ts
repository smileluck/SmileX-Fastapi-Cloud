/**
 * vite 插件 build/plugins/git-log.ts 通过 virtual module 暴露的 git 提交历史类型。
 *
 * 数据由构建期采集(dev 启动 / build 各一次),非实时。
 */
declare module 'virtual:smilex-git-log' {
  export interface GitCommit {
    /** 完整 commit hash */
    hash: string;
    /** 短 hash */
    shortHash: string;
    /** 提交者 */
    author: string;
    /** 提交时间(iso 字符串) */
    date: string;
    /** 提交信息(subject) */
    message: string;
  }

  export interface GitLogData {
    /** 当前环境是否成功采集到 git 历史 */
    available: boolean;
    /** 采集时间(iso 字符串) */
    generatedAt: string;
    /** 提交列表(最新在前) */
    commits: GitCommit[];
  }

  const data: GitLogData;

  export default data;
}
