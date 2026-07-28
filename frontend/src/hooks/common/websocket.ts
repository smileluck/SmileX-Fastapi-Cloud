import { ref } from 'vue';

const WS_BASE_URL = `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}`;

let ws: WebSocket | null = null;
let reconnectTimer: ReturnType<typeof setTimeout> | null = null;
let heartbeatTimer: ReturnType<typeof setInterval> | null = null;
let currentToken: string | null = null;
let shouldReconnect = false;
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 5;
const BASE_RECONNECT_INTERVAL = 3000;
const HEARTBEAT_INTERVAL = 30000;

const connected = ref(false);
const lastMessage = ref<any>(null);

export function useWebSocketNotification() {
  function doConnect(token: string) {
    const wsUrl = `${WS_BASE_URL}/admin/ws/notifications?token=${token}`;
    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      connected.value = true;
      reconnectAttempts = 0;
      console.log('[WebSocket] 连接已建立');
      startHeartbeat();
    };

    ws.onmessage = event => {
      try {
        const data = JSON.parse(event.data);
        lastMessage.value = data;

        // 触发全局事件，供通知中心监听
        if (data.type === 'notification') {
          window.dispatchEvent(new CustomEvent('ws:notification', { detail: data.data }));
        } else if (data.type === 'export_task') {
          window.dispatchEvent(new CustomEvent('ws:export_task', { detail: data.data }));
        }
      } catch (e) {
        console.warn('[WebSocket] 消息解析失败:', event.data);
      }
    };

    ws.onclose = () => {
      connected.value = false;
      ws = null;
      stopHeartbeat();
      console.log('[WebSocket] 连接已关闭');

      if (shouldReconnect && reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
        reconnectAttempts += 1;
        const delay = BASE_RECONNECT_INTERVAL * 2 ** (reconnectAttempts - 1);
        console.log(`[WebSocket] ${delay}ms 后尝试第 ${reconnectAttempts} 次重连...`);
        reconnectTimer = setTimeout(() => {
          if (currentToken) {
            doConnect(currentToken);
          }
        }, delay);
      } else if (reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
        console.warn('[WebSocket] 已达到最大重连次数，停止重连');
      }
    };

    ws.onerror = error => {
      console.error('[WebSocket] 连接错误:', error);
    };
  }

  function connect(token: string) {
    // 清理旧状态
    shouldReconnect = true;
    currentToken = token;
    reconnectAttempts = 0;
    clearTimers();

    if (ws) {
      ws.close();
      ws = null;
    }

    doConnect(token);
  }

  function disconnect() {
    shouldReconnect = false;
    currentToken = null;
    reconnectAttempts = 0;
    clearTimers();

    if (ws) {
      ws.close();
      ws = null;
    }
    connected.value = false;
  }

  function clearTimers() {
    if (reconnectTimer) {
      clearTimeout(reconnectTimer);
      reconnectTimer = null;
    }
    stopHeartbeat();
  }

  function startHeartbeat() {
    stopHeartbeat();
    heartbeatTimer = setInterval(() => {
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'ping' }));
      }
    }, HEARTBEAT_INTERVAL);
  }

  function stopHeartbeat() {
    if (heartbeatTimer) {
      clearInterval(heartbeatTimer);
      heartbeatTimer = null;
    }
  }

  function sendPing() {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: 'ping' }));
    }
  }

  return {
    connected,
    lastMessage,
    connect,
    disconnect,
    sendPing
  };
}
