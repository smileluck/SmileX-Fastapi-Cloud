declare namespace Api {
  namespace FileManage {
    /** 文件信息 */
    type FileInfo = {
      /** 文件ID */
      id: number;
      /** 原始文件名 */
      original_name: string;
      /** 存储文件名 */
      stored_name: string;
      /** 存储路径 */
      file_path: string;
      /** 文件大小(字节) */
      file_size: number;
      /** MIME类型 */
      mime_type: string;
      /** 扩展名 */
      extension: string;
      /** 存储平台 */
      storage_platform: string;
      /** 图片宽度(像素)，仅图片文件且请求时返回 */
      image_width?: number | null;
      /** 图片高度(像素)，仅图片文件且请求时返回 */
      image_height?: number | null;
      /** 上传时间 */
      created_at: string;
    };

    /** 文件列表项 (含上传者) */
    type FileListItem = FileInfo & {
      /** 上传者用户ID */
      created_by: number;
    };

    /** 文件搜索参数 */
    type FileSearchParams = {
      page?: number;
      page_size?: number;
      original_name?: string;
      extension?: string;
      storage_platform?: string;
    };

    /** 文件列表 (分页) */
    type FileList = Common.PaginatingQueryRecord<FileListItem>;
  }
}
