declare namespace Api {
  namespace Task {
    type CommonSearchParams = Pick<Common.PaginatingCommonParams, 'page' | 'page_size'>;

    /** task type */
    type TaskType = 'patrol' | 'broadcast';

    /** task execution status */
    type TaskStatus = 'idle' | 'running' | 'paused';

    /** task execution record status */
    type TaskExecutionStatus = 'pending' | 'running' | 'paused' | 'completed' | 'failed' | 'cancelled';

    /** patrol action */
    type TaskAction = 'wave' | 'bow' | 'turn' | 'wait' | 'nod';

    /** patrol point */
    type TaskPoint = Common.CommonRecord<{
      task_id: number;
      sort_order: number;
      point_name: string | null;
      annotation_id: number | null;
      action: TaskAction;
      voice_text: string | null;
    }>;

    /** robot brief info for task */
    type TaskRobot = {
      id: number;
      name: string;
      status: string | null;
    };

    /** task */
    type Task = Omit<Common.CommonRecord<object>, 'status'> & {
      name: string;
      task_type: TaskType;
      enabled: boolean;
      status: TaskStatus;
      broadcast_text: string | null;
      broadcast_count: string | null;
      schedule_enabled: boolean;
      schedule_date: string | null;
      schedule_start_time: string | null;
      schedule_repeat_cycle: string | null;
      point_count: number;
      points: TaskPoint[] | null;
      robots: TaskRobot[] | null;
    };

    /** task search params */
    type TaskSearchParams = CommonType.RecordNullable<
      Pick<Task, 'name' | 'task_type'> & { enabled: string | null } & CommonSearchParams
    >;

    /** task list */
    type TaskList = Common.PaginatingQueryRecord<Task>;

    /** task create */
    type TaskCreate = {
      name: string;
      task_type: TaskType;
      points?: {
        sort_order: number;
        point_name?: string | null;
        annotation_id?: number | null;
        action: TaskAction;
        voice_text?: string | null;
      }[];
      broadcast_text?: string | null;
      broadcast_count?: string | null;
      robot_ids: number[];
      schedule_enabled?: boolean;
      schedule_date?: string | null;
      schedule_start_time?: string | null;
      schedule_repeat_cycle?: string | null;
    };

    /** task update */
    type TaskUpdate = Partial<TaskCreate>;

    /** task execution */
    type TaskExecution = Omit<Common.CommonRecord<object>, 'status'> & {
      task_id: number;
      task_name: string;
      task_type: TaskType;
      status: TaskExecutionStatus;
      progress: number;
      current_position: string | null;
      started_at: string | null;
      ended_at: string | null;
      error_message: string | null;
      robot_id: number | null;
      robot_name: string | null;
      triggered_by: string;
    };

    /** task execution search params */
    type TaskExecutionSearchParams = CommonType.RecordNullable<
      { task_name?: string; status?: string; start_time?: string; end_time?: string } & CommonSearchParams
    >;

    /** task execution list */
    type TaskExecutionList = Common.PaginatingQueryRecord<TaskExecution>;

    /** task execution detail (with points) */
    type TaskExecutionDetail = TaskExecution & {
      points: TaskPoint[] | null;
    };
  }
}
