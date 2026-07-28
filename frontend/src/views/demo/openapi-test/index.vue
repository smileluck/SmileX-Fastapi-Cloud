<script setup lang="ts">
import { computed, reactive, ref } from 'vue';
import { useMessage } from 'naive-ui';
import { getServiceBaseURL } from '@/utils/service';
import { hmacSha256Hex, sha256Hex } from '@/utils/hmac-sha256';
import { $t } from '@/locales';

defineOptions({ name: 'OpenapiTest' });

const message = useMessage();

const isHttpProxy = import.meta.env.DEV && import.meta.env.VITE_HTTP_PROXY === 'Y';
const { baseURL } = getServiceBaseURL(import.meta.env, isHttpProxy);

const form = reactive({
  app_id: '',
  app_secret: '',
  method: 'GET' as 'GET' | 'POST' | 'PUT' | 'DELETE',
  path: '/open/demo/ping',
  body: ''
});

const methodOptions = [
  { label: 'GET', value: 'GET' },
  { label: 'POST', value: 'POST' },
  { label: 'PUT', value: 'PUT' },
  { label: 'DELETE', value: 'DELETE' }
];

const sending = ref(false);

/** 签名中间态（生成签名后填充，供学习/排查） */
const signature = reactive({
  timestamp: '',
  nonce: '',
  canonical: '',
  sig: ''
});

/** 响应结果 */
const response = reactive({
  status: '' as string | number,
  body: '',
  request_id: ''
});

const fullUrl = computed(() => `${baseURL}${form.path}`);

function genNonce(): string {
  const bytes = new Uint8Array(16);
  crypto.getRandomValues(bytes);
  return Array.from(bytes)
    .map(b => b.toString(16).padStart(2, '0'))
    .join('');
}

/** 按后端契约构建 canonical string 并计算签名，返回请求头 */
async function buildSignedHeaders(): Promise<Record<string, string>> {
  const timestamp = String(Math.floor(Date.now() / 1000));
  const nonce = genNonce();
  const bodyBytes = form.body ? form.body : '';
  const bodyHash = bodyBytes ? await sha256Hex(bodyBytes) : '';
  // 6 段，以 \n 连接；body 为空时第 6 段为空串（canonical 末尾保留 \n）
  const canonical = [form.method.toUpperCase(), form.path, timestamp, nonce, form.app_id, bodyHash].join('\n');
  const sig = await hmacSha256Hex(form.app_secret, canonical);

  signature.timestamp = timestamp;
  signature.nonce = nonce;
  signature.canonical = canonical;
  signature.sig = sig;

  return {
    'X-App-Id': form.app_id,
    'X-Timestamp': timestamp,
    'X-Nonce': nonce,
    'X-Signature': sig
  };
}

async function send() {
  if (!form.app_id || !form.app_secret) {
    message.warning($t('page.demo.openapiTest.needCredential'));
    return;
  }
  sending.value = true;
  response.status = '';
  response.body = '';
  response.request_id = '';

  try {
    const headers = await buildSignedHeaders();
    const fetchOpts: RequestInit = { method: form.method, headers };
    if (form.method !== 'GET' && form.body) {
      fetchOpts.body = form.body;
    }

    const res = await fetch(fullUrl.value, fetchOpts);
    response.status = res.status;
    const text = await res.text();
    let pretty = text;
    try {
      pretty = JSON.stringify(JSON.parse(text), null, 2);
      const parsed = JSON.parse(text);
      response.request_id = parsed?.request_id ?? '';
    } catch {
      // 非 JSON 响应
    }
    response.body = pretty;
  } catch (err) {
    response.status = 'ERROR';
    response.body = String(err);
  } finally {
    sending.value = false;
  }
}
</script>

<template>
  <NSpace vertical :size="16">
    <NCard :bordered="false" :title="$t('page.demo.openapiTest.title')" class="card-wrapper">
      <NAlert type="info" :bordered="false" class="mb-12px">
        {{ $t('page.demo.openapiTest.tip') }}
      </NAlert>
      <NForm label-placement="left" :label-width="100">
        <NGrid responsive="screen" item-responsive>
          <NFormItemGi span="24 m:12" :label="$t('page.demo.openapiTest.appId')" path="app_id">
            <NInput v-model:value="form.app_id" placeholder="SMX..." />
          </NFormItemGi>
          <NFormItemGi span="24 m:12" :label="$t('page.demo.openapiTest.appSecret')" path="app_secret">
            <NInput v-model:value="form.app_secret" type="password" show-password-on="click" placeholder="AppSecret" />
          </NFormItemGi>
          <NFormItemGi span="24 m:6" :label="$t('page.demo.openapiTest.method')" path="method">
            <NSelect v-model:value="form.method" :options="methodOptions" />
          </NFormItemGi>
          <NFormItemGi span="24 m:18" :label="$t('page.demo.openapiTest.path')" path="path">
            <NInput v-model:value="form.path" placeholder="/open/demo/ping" />
          </NFormItemGi>
          <NFormItemGi v-if="form.method !== 'GET'" span="24" :label="$t('page.demo.openapiTest.body')" path="body">
            <NInput
              v-model:value="form.body"
              type="textarea"
              :autosize="{ minRows: 2, maxRows: 6 }"
              placeholder='{"key":"value"}'
            />
          </NFormItemGi>
          <NFormItemGi span="24" :label="$t('page.demo.openapiTest.url')" path="url">
            <NText code class="break-all">{{ fullUrl }}</NText>
          </NFormItemGi>
        </NGrid>
        <NSpace justify="end">
          <NButton type="primary" :loading="sending" @click="send">
            {{ $t('page.demo.openapiTest.send') }}
          </NButton>
        </NSpace>
      </NForm>
    </NCard>

    <NCard
      v-if="signature.sig"
      :bordered="false"
      :title="$t('page.demo.openapiTest.signatureTitle')"
      class="card-wrapper"
    >
      <NDescriptions label-placement="left" :column="1" bordered size="small">
        <NDescriptionsItem :label="$t('page.demo.openapiTest.timestamp')">{{ signature.timestamp }}</NDescriptionsItem>
        <NDescriptionsItem :label="$t('page.demo.openapiTest.nonce')">{{ signature.nonce }}</NDescriptionsItem>
        <NDescriptionsItem :label="$t('page.demo.openapiTest.signature')">
          <NText code class="break-all">{{ signature.sig }}</NText>
        </NDescriptionsItem>
        <NDescriptionsItem :label="$t('page.demo.openapiTest.canonical')">
          <pre class="whitespace-pre-wrap break-all text-13px font-mono">{{ signature.canonical }}</pre>
        </NDescriptionsItem>
      </NDescriptions>
    </NCard>

    <NCard
      v-if="response.status !== ''"
      :bordered="false"
      :title="$t('page.demo.openapiTest.responseTitle')"
      class="card-wrapper"
    >
      <NDescriptions label-placement="left" :column="2" bordered size="small" class="mb-12px">
        <NDescriptionsItem :label="$t('page.demo.openapiTest.status')">
          <NTag
            :type="
              typeof response.status === 'number' && response.status >= 200 && response.status < 300
                ? 'success'
                : 'error'
            "
          >
            {{ response.status }}
          </NTag>
        </NDescriptionsItem>
        <NDescriptionsItem :label="$t('page.demo.openapiTest.requestId')">
          {{ response.request_id || '-' }}
        </NDescriptionsItem>
      </NDescriptions>
      <pre class="whitespace-pre-wrap break-all rounded-4px bg-#f5f5f5 p-12px text-13px font-mono dark:bg-#1e1e1e">{{
        response.body
      }}</pre>
    </NCard>
  </NSpace>
</template>

<style scoped></style>
