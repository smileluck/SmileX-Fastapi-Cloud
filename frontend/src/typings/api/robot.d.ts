declare namespace Api {
  namespace Robot {
    type CommonSearchParams = Pick<Common.PaginatingCommonParams, 'page' | 'page_size'>;

    /** robot model */
    type RobotModel = Common.CommonRecord<{
      /** model name */
      name: string;
      /** brand */
      brand: string;
      /** model identifier */
      model: string;
      /** sort order */
      sort: number;
    }>;

    /** robot model search params */
    type RobotModelSearchParams = CommonType.RecordNullable<
      Pick<RobotModel, 'name' | 'brand' | 'status'> & CommonSearchParams
    >;

    /** robot model list */
    type RobotModelList = Common.PaginatingQueryRecord<RobotModel>;

    /** robot model create */
    type RobotModelCreate = Pick<RobotModel, 'name' | 'brand' | 'model' | 'status' | 'sort'>;

    /** robot model update */
    type RobotModelUpdate = Partial<RobotModelCreate>;

    /** all robot model (for dropdown) */
    type AllRobotModel = Pick<RobotModel, 'id' | 'name' | 'brand' | 'model'>;

    /** robot status enum */
    type RobotStatusEnum = 'online' | 'offline' | 'inactive';

    /** robot */
    type Robot = Omit<Common.CommonRecord<object>, 'status'> & {
      /** robot name */
      name: string;
      /** model id */
      model_id: number;
      /** model name (joined) */
      model_name?: string;
      /** serial number */
      serial_number: string;
      /** bound scene map id */
      map_id?: number | null;
      /** bound scene map name */
      map_name?: string | null;
      /** status */
      status: RobotStatusEnum;
      /** speed level */
      speed_level?: string | null;
      /** battery threshold */
      battery_threshold?: number | null;
    };

    /** location info */
    type LocationInfo = {
      /** x coordinate */
      x?: number;
      /** y coordinate */
      y?: number;
      /** angle */
      angle?: number;
      /** update time */
      update_at?: string | null;
    };

    /** robot search params */
    type RobotSearchParams = CommonType.RecordNullable<
      Pick<Robot, 'name' | 'serial_number' | 'status'> & { model_id?: number; map_id?: number } & CommonSearchParams
    >;

    /** robot list */
    type RobotList = Common.PaginatingQueryRecord<Robot>;

    /** robot create */
    type RobotCreate = {
      name: string;
      model_id: number;
      serial_number: string;
      map_id?: number | null;
      status?: RobotStatusEnum;
    };

    /** robot update */
    type RobotUpdate = Partial<RobotCreate> & {
      speed_level?: string | null;
      battery_threshold?: number | null;
    };

    /** robot status record */
    type RobotStatusRecord = Common.CommonRecord<{
      /** robot id */
      robot_id: number;
      /** battery percentage */
      battery: number;
      /** signal strength */
      signal: number;
      /** speed */
      speed: number;
      /** location info (JSON) */
      location: string | null;
      /** location info */
      location_info: LocationInfo | null;
    }>;

    /** robot status record list */
    type RobotStatusRecordList = Common.PaginatingQueryRecord<RobotStatusRecord>;
  }
}
