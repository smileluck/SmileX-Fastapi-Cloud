declare namespace Api {
  /**
   * namespace Dashboard
   *
   * backend api module: "dashboard" (首页仪表盘)
   */
  namespace Dashboard {
    /** 统计数据（4 个核心指标） */
    interface Stats {
      /** 用户总数 */
      user_count: number;
      /** 角色总数 */
      role_count: number;
      /** 在线用户数 */
      online_count: number;
      /** 今日登录次数 */
      today_login_count: number;
    }

    /** 最近登录记录 */
    interface RecentLogin {
      /** 登录用户名 */
      username: string;
      /** 客户端IP */
      ip: string;
      /** 登录状态：true-成功，false-失败 */
      status: boolean;
      /** 登录时间 */
      login_time: string;
    }

    /** 最新公告 */
    interface LatestNotice {
      /** 公告ID */
      id: string;
      /** 公告标题 */
      title: string;
      /** 公告类型：announcement/system/operation/approval */
      type: string;
      /** 创建时间 */
      created_at: string;
    }

    /** 仪表盘汇总数据 */
    interface Summary {
      /** 统计数据 */
      stats: Stats;
      /** 最近登录列表 */
      recent_logins: RecentLogin[];
      /** 最新公告列表 */
      latest_notices: LatestNotice[];
    }
  }
}
