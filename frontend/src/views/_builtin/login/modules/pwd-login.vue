<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue';
import { loginModuleRecord } from '@/constants/app';
import { useAuthStore } from '@/store/modules/auth';
import { useRouterPush } from '@/hooks/common/router';
import { useFormRules, useNaiveForm } from '@/hooks/common/form';
import { useSliderCaptcha } from '@/hooks/business/slider-captcha';
import { localStg } from '@/utils/storage';
import { $t } from '@/locales';
import SliderCaptcha from '@/components/custom/slider-captcha.vue';

defineOptions({
  name: 'PwdLogin'
});

const authStore = useAuthStore();
const { toggleLoginModule } = useRouterPush();
const { formRef, validate } = useNaiveForm();
const sliderCaptchaRef = ref<InstanceType<typeof SliderCaptcha>>();

const {
  captchaRequired,
  captchaToken,
  captchaId,
  backgroundImage,
  puzzleImage,
  puzzleY,
  sliderWidth,
  loading: captchaLoading,
  showCaptcha,
  resetCaptcha,
  fetchCaptcha
} = useSliderCaptcha();

const loginDisabled = computed(() => {
  return captchaRequired.value && !captchaToken.value;
});

const REMEMBER_KEY = 'rememberLogin';
const savedLogin = localStg.get(REMEMBER_KEY);
const rememberMe = ref(Boolean(savedLogin?.userName));

interface FormModel {
  userName: string;
  password: string;
}

const model: FormModel = reactive({
  userName: savedLogin?.userName ?? '',
  password: savedLogin?.password ?? ''
});

watch(rememberMe, val => {
  if (!val) {
    localStg.remove(REMEMBER_KEY);
  }
});

const rules = computed<Record<keyof FormModel, App.Global.FormRule[]>>(() => {
  // inside computed to make locale reactive, if not apply i18n, you can define it without computed
  const { formRules } = useFormRules();

  return {
    userName: formRules.userName,
    password: formRules.pwd
  };
});

async function handleSubmit() {
  await validate();

  if (captchaRequired.value && !captchaToken.value) {
    showCaptcha();
    return;
  }

  const errCode = await authStore.login(model.userName, model.password, captchaToken.value ?? undefined);

  if (errCode === 10911) {
    showCaptcha();
  } else if (errCode) {
    captchaToken.value = null;
    showCaptcha();
  } else {
    if (rememberMe.value) {
      localStg.set(REMEMBER_KEY, { userName: model.userName, password: model.password });
    } else {
      localStg.remove(REMEMBER_KEY);
    }
    resetCaptcha();
  }
}

function onCaptchaSuccess(token: string) {
  captchaToken.value = token;
  handleSubmit();
}

function onCaptchaFail() {
  captchaToken.value = null;
}

function onCaptchaRefresh() {
  fetchCaptcha();
}

type AccountKey = 'super' | 'admin' | 'user';

interface Account {
  key: AccountKey;
  label: string;
  userName: string;
  password: string;
}

const accounts = computed<Account[]>(() => [
  {
    key: 'super',
    label: $t('page.login.pwdLogin.superAdmin'),
    userName: 'Super',
    password: '123456'
  },
  {
    key: 'admin',
    label: $t('page.login.pwdLogin.admin'),
    userName: 'Admin',
    password: '123456'
  },
  {
    key: 'user',
    label: $t('page.login.pwdLogin.user'),
    userName: 'User',
    password: '123456'
  }
]);

async function handleAccountLogin(account: Account) {
  await authStore.login(account.userName, account.password);
}
</script>

<template>
  <NForm ref="formRef" :model="model" :rules="rules" size="large" :show-label="false" @keyup.enter="handleSubmit">
    <NFormItem path="userName">
      <NInput v-model:value="model.userName" :placeholder="$t('page.login.common.userNamePlaceholder')" />
    </NFormItem>
    <NFormItem path="password">
      <NInput v-model:value="model.password" type="password" show-password-on="click"
        :placeholder="$t('page.login.common.passwordPlaceholder')" />
    </NFormItem>
    <NSpace vertical :size="24">
      <div class="flex-y-center justify-between">
        <NCheckbox v-model:checked="rememberMe">{{ $t('page.login.pwdLogin.rememberMe') }}</NCheckbox>
        <!-- <NButton quaternary @click="toggleLoginModule('reset-pwd')">
          {{ $t('page.login.pwdLogin.forgetPassword') }}
        </NButton> -->
      </div>
      <!-- Slider Captcha -->
      <div v-if="captchaRequired" class="captcha-wrapper">
        <NText v-if="loginDisabled" depth="3" class="captcha-hint">
          {{ $t('captcha.completeFirst') }}
        </NText>
        <NSpin :show="captchaLoading">
          <SliderCaptcha
            ref="sliderCaptchaRef"
            :captcha-id="captchaId"
            :background-image="backgroundImage"
            :puzzle-image="puzzleImage"
            :puzzle-y="puzzleY"
            :slider-width="sliderWidth"
            @success="onCaptchaSuccess"
            @fail="onCaptchaFail"
            @refresh="onCaptchaRefresh"
          />
        </NSpin>
      </div>
      <NButton
        type="primary"
        size="large"
        round
        block
        :loading="authStore.loginLoading"
        :disabled="loginDisabled"
        @click="handleSubmit"
      >
        {{ $t('route.login') }}
      </NButton>
      <!-- <div class="flex-y-center justify-between gap-12px">
        <NButton class="flex-1" block @click="toggleLoginModule('code-login')">
          {{ $t(loginModuleRecord['code-login']) }}
        </NButton>
        <NButton class="flex-1" block @click="toggleLoginModule('register')">
          {{ $t(loginModuleRecord.register) }}
        </NButton>
      </div>
      <NDivider class="text-14px text-#666 !m-0">{{ $t('page.login.pwdLogin.otherAccountLogin') }}</NDivider>
      <div class="flex-center gap-12px">
        <NButton v-for="item in accounts" :key="item.key" type="primary" @click="handleAccountLogin(item)">
          {{ item.label }}
        </NButton>
      </div> -->
    </NSpace>
  </NForm>
</template>

<style scoped>
.captcha-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.captcha-hint {
  font-size: 13px;
  text-align: center;
}
</style>
