declare namespace Api {
  namespace Scene {
    type CommonSearchParams = Pick<Common.PaginatingCommonParams, 'page' | 'page_size'>;

    /** scene group */
    type SceneGroup = Common.CommonRecord<{
      /** group name */
      name: string;
      /** parent group id */
      parent_id: number | null;
      /** sort order */
      sort: number;
    }>;

    /** scene group search params */
    type SceneGroupSearchParams = CommonType.RecordNullable<
      Pick<SceneGroup, 'name' | 'status'> & CommonSearchParams
    >;

    /** scene group list */
    type SceneGroupList = Common.PaginatingQueryRecord<SceneGroup>;

    /** scene group create */
    type SceneGroupCreate = Pick<SceneGroup, 'name'> & {
      parent_id?: number | null;
      sort?: number;
      status?: Common.EnableStatus;
    };

    /** scene group update */
    type SceneGroupUpdate = Partial<SceneGroupCreate>;

    /** scene group tree node */
    type SceneGroupTreeNode = {
      id: number;
      name: string;
      parent_id: number | null;
      sort: number;
      status: Common.EnableStatus;
      children?: SceneGroupTreeNode[];
    };

    /** scene map */
    type SceneMap = Common.CommonRecord<{
      /** map name */
      name: string;
      /** group id */
      group_id: number | null;
      /** group name (joined) */
      group_name?: string;
      /** image file id */
      image_id: number | null;
      /** map width */
      width: number | null;
      /** map height */
      height: number | null;
      /** resolution (meters/pixel) */
      resolution: number;
      /** start point x */
      start_point_x: number;
      /** start point y */
      start_point_y: number;
    }>;

    /** scene map search params */
    type SceneMapSearchParams = CommonType.RecordNullable<
      Pick<SceneMap, 'name' | 'status'> & { group_id?: number } & CommonSearchParams
    >;

    /** scene map list */
    type SceneMapList = Common.PaginatingQueryRecord<SceneMap>;

    /** scene map create */
    type SceneMapCreate = Pick<SceneMap, 'name'> & {
      group_id?: number | null;
      group_name?: string | null;
      image_id?: number | null;
      width?: number | null;
      height?: number | null;
      resolution?: number;
      start_point_x?: number;
      start_point_y?: number;
      status?: Common.EnableStatus;
    };

    /** scene map update */
    type SceneMapUpdate = Partial<SceneMapCreate>;

    /** scene map annotation */
    type SceneMapAnnotation = Common.CommonRecord<{
      /** map id */
      map_id: number;
      /** x coordinate */
      x: number;
      /** y coordinate */
      y: number;
      /** annotation name */
      name: string;
      /** angle */
      angle: number;
      /** type (dict value) */
      type: string;
    }>;

    /** scene map annotation list */
    type SceneMapAnnotationList = Common.PaginatingQueryRecord<SceneMapAnnotation>;

    /** scene map annotation create */
    type SceneMapAnnotationCreate = {
      map_id: number;
      x: number;
      y: number;
      name: string;
      angle?: number;
      type: string;
    };

    /** scene map annotation update */
    type SceneMapAnnotationUpdate = Partial<Omit<SceneMapAnnotationCreate, 'map_id'>>;

    /** scene map object */
    type SceneMapObject = Common.CommonRecord<{
      /** map id */
      map_id: number;
      /** object type (dict value) */
      type: string;
      /** x coordinate */
      x: number;
      /** y coordinate */
      y: number;
      /** width */
      width: number;
      /** height */
      height: number;
      /** polygon points (JSON) */
      points: string | null;
    }>;

    /** scene map object list */
    type SceneMapObjectList = Common.PaginatingQueryRecord<SceneMapObject>;

    /** scene map object create */
    type SceneMapObjectCreate = {
      map_id: number;
      type: string;
      x: number;
      y: number;
      width?: number;
      height?: number;
      points?: string | null;
    };

    /** scene map object update */
    type SceneMapObjectUpdate = Partial<Omit<SceneMapObjectCreate, 'map_id'>>;

    /** scene map path */
    type SceneMapPath = Common.CommonRecord<{
      /** map id */
      map_id: number;
      /** start annotation id */
      start_annotation_id: number;
      /** end annotation id */
      end_annotation_id: number;
      /** path name */
      name: string | null;
      /** intermediate points (JSON) */
      points: string | null;
    }>;

    /** scene map path list */
    type SceneMapPathList = Common.PaginatingQueryRecord<SceneMapPath>;

    /** scene map path create */
    type SceneMapPathCreate = {
      map_id: number;
      start_annotation_id: number;
      end_annotation_id: number;
      name?: string | null;
      points?: string | null;
    };

    /** scene map path update */
    type SceneMapPathUpdate = Partial<Omit<SceneMapPathCreate, 'map_id'>>;

    /** editor annotation item */
    type EditorAnnotationItem = {
      id?: number | null;
      x: number;
      y: number;
      name: string;
      angle: number;
      type: string;
    };

    /** editor path item */
    type EditorPathItem = {
      id?: number | null;
      start_annotation_id: number;
      end_annotation_id: number;
      name?: string | null;
      points?: string | null;
    };

    /** editor object item */
    type EditorObjectItem = {
      id?: number | null;
      type: string;
      x: number;
      y: number;
      width: number;
      height: number;
      points?: string | null;
    };

    /** editor save request */
    type EditorSaveRequest = {
      annotations: EditorAnnotationItem[];
      paths: EditorPathItem[];
      objects: EditorObjectItem[];
      deleted_annotation_ids: number[];
      deleted_path_ids: number[];
      deleted_object_ids: number[];
    };

    /** editor map data */
    type EditorMapData = {
      map: SceneMap;
      annotations: SceneMapAnnotation[];
      paths: SceneMapPath[];
      objects: SceneMapObject[];
    };
  }
}
