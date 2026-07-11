declare namespace Api {
  /**
   * namespace ExportTask
   *
   * backend api module: "export task"
   */
  namespace ExportTask {
    /** export task status */
    type ExportTaskStatus = 'pending' | 'processing' | 'completed' | 'failed';

    /** export task record */
    type ExportTask = {
      /** task id */
      id: number;
      /** task name */
      task_name: string;
      /** module key */
      module_key: string;
      /** template id */
      template_id?: number | null;
      /** task status */
      status: ExportTaskStatus;
      /** total rows exported */
      total_rows?: number | null;
      /** file size in bytes */
      file_size?: number | null;
      /** error message when failed */
      error_message?: string | null;
      /** created at */
      created_at?: string | null;
      /** started at */
      started_at?: string | null;
      /** finished at */
      finished_at?: string | null;
    };

    /** export task list */
    type ExportTaskList = Common.PaginatingQueryRecord<ExportTask>;

    /** export task submit params */
    type ExportTaskSubmit = {
      module_key?: string | null;
      template_id?: number | null;
      query_params?: Record<string, any>;
    };

    /** export task search params */
    type ExportTaskSearchParams = CommonType.RecordNullable<{
      status?: ExportTaskStatus;
    } & CommonSearchParams>;
  }
}
