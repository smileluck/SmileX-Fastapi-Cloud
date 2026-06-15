declare namespace Api.RobotConfig {
  type CommonSearchParams = Pick<Common.PaginatingCommonParams, 'page' | 'page_size'>;

  interface VoiceConfig {
    id?: number;
    robot_id: number;
    wake_word: string;
    tts_voice: string;
    tts_speed: number;
    tts_volume: number;
    created_at?: string;
    updated_at?: string | null;
  }

  interface FaceRecognition {
    id: number;
    person_name: string;
    photo_url: string;
    broadcast_text: string;
    created_at: string;
    updated_at: string | null;
  }

  interface FaceRecognitionCreate {
    person_name: string;
    photo_url: string;
    broadcast_text: string;
  }

  interface FaceRecognitionList {
    records: FaceRecognition[];
    page: number;
    page_size: number;
    total: number;
    total_pages: number;
  }

  interface TestWakeWordRequest {
    text: string;
  }

  interface TestTTSRequest {
    voice: string;
    speed: number;
    volume: number;
    text: string;
  }
}
