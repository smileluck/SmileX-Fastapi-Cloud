declare namespace Api {
  namespace Scheduler {
    type CommonSearchParams = Pick<Common.PaginatingCommonParams, 'page' | 'page_size'>;

    type TaskCategory = 'specialist' | 'generic';

    /** 定时任务 */
    type ScheduledTask = {
      id: number;
      name: string;
      task_key: string;
      description: string | null;
      cron_expression: string;
      trigger_type: string;
      trigger_params: string | null;
      status: Common.EnableStatus;
      module: string | null;
      function_path: string | null;
      is_system: Common.EnableStatus;
      last_run_at: string | null;
      next_run_at: string | null;
      last_status: string | null;
      timeout: number;
      max_retries: number;
      concurrent_policy: string;
      params: Record<string, any> | null;
      created_at: string | null;
      updated_at: string | null;
    };

    type ScheduledTaskSearchParams = CommonType.RecordNullable<
      Pick<ScheduledTask, 'name' | 'task_key' | 'status' | 'trigger_type'> & CommonSearchParams
    >;

    type ScheduledTaskList = Common.PaginatingQueryRecord<ScheduledTask>;

    type ScheduledTaskCreate = {
      name: string;
      task_key: string;
      description?: string;
      cron_expression: string;
      trigger_type: string;
      trigger_params?: string;
      timeout: number;
      max_retries: number;
      concurrent_policy: string;
      params?: Record<string, any> | null;
      function_path?: string;
    };

    type ScheduledTaskUpdate = Partial<ScheduledTaskCreate>;

    /** Cron 预览 */
    type CronPreviewRequest = {
      cron_expression: string;
    };

    type CronPreviewResponse = {
      next_run_times: string[];
    };

    /** 装饰器注册的任务 */
    type RegistryTask = {
      task_key: string;
      name: string;
      description: string;
      cron_expression: string;
      trigger_type: string;
      trigger_params: Record<string, any> | null;
      module: string | null;
      function_path: string | null;
      is_system: boolean;
      timeout: number;
      max_retries: number;
      concurrent_policy: string;
      has_params: boolean;
      task_category: TaskCategory;
    };

    /** JSON Schema 字段定义（简化版） */
    type JsonSchemaProperty = {
      type?: 'string' | 'integer' | 'number' | 'boolean' | 'object' | 'array' | 'null';
      title?: string;
      description?: string;
      default?: any;
      enum?: any[];
      minimum?: number;
      maximum?: number;
      minLength?: number;
      maxLength?: number;
      items?: JsonSchemaProperty;
      properties?: Record<string, JsonSchemaProperty>;
      required?: string[];
      anyOf?: JsonSchemaProperty[];
      allOf?: JsonSchemaProperty[];
      $ref?: string;
    };

    type TaskParamsSchema = {
      type?: string;
      title?: string;
      description?: string;
      properties?: Record<string, JsonSchemaProperty>;
      required?: string[];
      $defs?: Record<string, JsonSchemaProperty>;
    };

    /** 任务执行日志 */
    type TaskLog = {
      id: number;
      task_id: number;
      task_name: string;
      task_key: string;
      status: string;
      start_time: string | null;
      end_time: string | null;
      duration_ms: number | null;
      result: string | null;
      error_message: string | null;
      retry_count: number;
      triggered_by: string;
      created_at: string | null;
    };

    type TaskLogSearchParams = CommonType.RecordNullable<
      {
        task_id?: number;
        task_name?: string;
        task_key?: string;
        status?: string;
        start_time?: string;
        end_time?: string;
      } & CommonSearchParams
    >;

    type TaskLogList = Common.PaginatingQueryRecord<TaskLog>;

    type TaskLogDetail = TaskLog;
  }
}
