import { request } from '../request';

/** ==================== 机器人参数配置 API ==================== */

/** 获取语音合成配置 */
export function fetchGetVoiceConfig(robotId: number) {
  return request<Api.RobotConfig.VoiceConfig>({
    url: '/robot/config/voice',
    method: 'get',
    params: { robot_id: robotId }
  });
}

/** 保存语音合成配置 */
export function fetchSaveVoiceConfig(data: Api.RobotConfig.VoiceConfig) {
  return request<Api.RobotConfig.VoiceConfig>({
    url: '/robot/config/voice',
    method: 'post',
    data
  });
}

/** 测试唤醒词 */
export function fetchTestWakeWord(text: string) {
  return request<void>({
    url: '/robot/config/voice/test-wake-word',
    method: 'post',
    data: { text }
  });
}

/** 测试TTS语音合成 */
export function fetchTestTTS(data: Api.RobotConfig.TestTTSRequest) {
  return request<void>({
    url: '/robot/config/voice/test-tts',
    method: 'post',
    data
  });
}

/** 上传人脸识别人像 */
export function fetchUploadFacePhoto(file: File) {
  const formData = new FormData();
  formData.append('file', file);
  return request<Api.FileManage.FileInfo>({
    url: '/robot/config/face/upload',
    method: 'post',
    data: formData,
    headers: { 'Content-Type': 'multipart/form-data' }
  });
}

/** 获取人脸识别TTS配置列表 */
export function fetchGetFaceRecognitionList(params?: Api.RobotConfig.CommonSearchParams) {
  return request<Api.RobotConfig.FaceRecognitionList>({
    url: '/robot/config/face',
    method: 'get',
    params
  });
}

/** 创建人脸识别TTS配置 */
export function fetchCreateFaceRecognition(data: Api.RobotConfig.FaceRecognitionCreate) {
  return request<Api.RobotConfig.FaceRecognition>({
    url: '/robot/config/face',
    method: 'post',
    data
  });
}

/** 更新人脸识别TTS配置 */
export function fetchUpdateFaceRecognition(id: number, data: Api.RobotConfig.FaceRecognitionCreate) {
  return request<Api.RobotConfig.FaceRecognition>({
    url: `/robot/config/face/${id}`,
    method: 'put',
    data
  });
}

/** 删除人脸识别TTS配置 */
export function fetchDeleteFaceRecognition(id: number) {
  return request<void>({
    url: `/robot/config/face/${id}`,
    method: 'delete'
  });
}
