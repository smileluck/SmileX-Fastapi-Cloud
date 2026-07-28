declare namespace Api {
  /**
   * namespace Notification
   *
   * backend api module: "notification"
   */
  namespace Notification {
    /** notice type */
    type NoticeType = 'announcement' | 'system' | 'operation' | 'approval';

    /** notice target type */
    type NoticeTargetType = 'all' | 'role' | 'user';

    /** notice priority */
    type NoticePriority = 'low' | 'normal' | 'high' | 'urgent';

    /** notice (after transform: status is EnableStatus, not boolean) */
    type Notice = Common.CommonRecord<{
      /** notice title */
      title: string;
      /** notice content */
      content: string;
      /** notice type */
      type: NoticeType;
      /** target type */
      target_type: NoticeTargetType;
      /** target role ids */
      target_role_ids?: number[] | null;
      /** target user ids */
      target_user_ids?: number[] | null;
      /** sender id */
      sender_id: number;
      /** sender name */
      sender_name: string;
      /** priority */
      priority: NoticePriority;
      /** published at */
      published_at?: string | null;
    }>;

    /** notice search params */
    type NoticeSearchParams = CommonType.RecordNullable<
      Pick<Notice, 'title' | 'type' | 'target_type' | 'status' | 'priority' | 'sender_id'> & CommonSearchParams
    >;

    /** notice list */
    type NoticeList = Common.PaginatingQueryRecord<Notice>;

    /** notice create */
    type NoticeCreate = Pick<Notice, 'title' | 'content' | 'type' | 'target_type' | 'priority'> & {
      target_role_ids?: number[];
      target_user_ids?: number[];
    };

    /** notice update */
    type NoticeUpdate = Partial<NoticeCreate>;

    /** my notice */
    type MyNotice = Pick<Notice, 'id' | 'title' | 'content' | 'type' | 'sender_name' | 'priority' | 'published_at'> & {
      /** is read */
      is_read: boolean;
      /** read at */
      read_at?: string | null;
    };

    /** my notice search params */
    type MyNoticeSearchParams = CommonType.RecordNullable<
      {
        is_read?: boolean;
        type?: NoticeType;
      } & CommonSearchParams
    >;

    /** my notice list */
    type MyNoticeList = Common.PaginatingQueryRecord<MyNotice>;

    /** batch read request */
    type BatchReadRequest = {
      notice_ids: number[];
    };
  }
}
