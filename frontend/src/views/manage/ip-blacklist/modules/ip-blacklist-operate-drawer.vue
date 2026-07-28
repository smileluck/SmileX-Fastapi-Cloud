<script setup lang="ts">
import { computed, reactive, watch } from 'vue';
import { useVModel } from '@vueuse/core';
import {
  NButton,
  NDatePicker,
  NDrawer,
  NDrawerContent,
  NForm,
  NFormItemGi,
  NGrid,
  NInput,
  NSelect,
  useMessage
} from 'naive-ui';
import { fetchCreateIpBlacklist } from '@/service/api';
import { useFormRules, useNaiveForm } from '@/hooks/common/form';
import { $t } from '@/locales';

export type OperateType = NaiveUI.TableOperateType;

interface Props {
  visible: boolean;
  operateType: OperateType;
  rowData?: Api.SystemManage.IpBlacklist | null;
}

const props = defineProps<Props>();
const emit = defineEmits<{
  'update:visible': [visible: boolean];
  submitted: [];
}>();

const message = useMessage();
const visible = useVModel(props, 'visible');

const { formRef, validate, restoreValidation } = useNaiveForm();
const { defaultRequiredRule } = useFormRules();

const typeOptions = [
  { label: $t('page.manage.ipBlacklist.typePermanent'), value: 'permanent' },
  { label: $t('page.manage.ipBlacklist.typeTemporary'), value: 'temporary' }
];

interface BlacklistForm {
  ip: string;
  type: string;
  reason: string;
  expire_at: number | null;
}

const defaultFormValue: BlacklistForm = {
  ip: '',
  type: 'permanent',
  reason: '',
  expire_at: null
};

const form = reactive<BlacklistForm>({ ...defaultFormValue });

const formRules = computed(() => ({
  ip: [defaultRequiredRule],
  type: [defaultRequiredRule],
  expire_at: [
    {
      validator: (_rule: App.Global.FormRule, value: number | null) => {
        if (form.type === 'temporary' && !value) {
          return new Error($t('page.manage.ipBlacklist.expireRequired'));
        }
        return true;
      },
      trigger: ['change']
    }
  ]
}));

const drawerTitle = computed(() => {
  return $t('page.manage.ipBlacklist.addTitle');
});

watch(
  () => props.visible,
  val => {
    if (val) {
      restoreValidation();
      Object.assign(form, defaultFormValue);
    }
  }
);

async function handleSubmit() {
  try {
    await validate();
    const data: Api.SystemManage.IpBlacklistCreate = {
      ip: form.ip,
      type: form.type,
      reason: form.reason || undefined,
      expire_at: form.type === 'temporary' && form.expire_at ? new Date(form.expire_at).toISOString() : null
    };
    const { error } = await fetchCreateIpBlacklist(data);
    if (error) return;
    message.success($t('common.addSuccess'));
    emit('submitted');
    visible.value = false;
  } catch {
    // 表单校验失败：交给 NForm 自动提示
  }
}
</script>

<template>
  <NDrawer v-model:show="visible" :width="480" preset="card">
    <NDrawerContent :title="drawerTitle" :native-scrollbar="false">
      <NForm ref="formRef" :model="form" :rules="formRules" label-placement="left" label-width="auto" size="small">
        <NGrid :x-gap="16" :cols="24">
          <NFormItemGi :span="24" :label="$t('page.manage.ipBlacklist.ip')" path="ip">
            <NInput v-model:value="form.ip" placeholder="e.g. 1.2.3.4" />
          </NFormItemGi>
          <NFormItemGi :span="24" :label="$t('page.manage.ipBlacklist.type')" path="type">
            <NSelect v-model:value="form.type" :options="typeOptions" />
          </NFormItemGi>
          <NFormItemGi
            v-if="form.type === 'temporary'"
            :span="24"
            :label="$t('page.manage.ipBlacklist.expireAt')"
            path="expire_at"
          >
            <NDatePicker
              v-model:value="form.expire_at"
              type="datetime"
              clearable
              class="w-full"
              :placeholder="$t('page.manage.ipBlacklist.expireAtPlaceholder')"
            />
          </NFormItemGi>
          <NFormItemGi :span="24" :label="$t('page.manage.ipBlacklist.reason')">
            <NInput
              v-model:value="form.reason"
              type="textarea"
              :autosize="{ minRows: 2, maxRows: 4 }"
              :placeholder="$t('page.manage.ipBlacklist.reasonPlaceholder')"
            />
          </NFormItemGi>
        </NGrid>
      </NForm>
      <template #footer>
        <div class="gap-12px flex-justify-end">
          <NButton size="small" @click="visible = false">
            {{ $t('common.cancel') }}
          </NButton>
          <NButton type="primary" size="small" @click="handleSubmit">
            {{ $t('common.confirm') }}
          </NButton>
        </div>
      </template>
    </NDrawerContent>
  </NDrawer>
</template>

<style scoped></style>
