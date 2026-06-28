<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { jsonClone } from '@sa/utils';
import { useNaiveForm } from '@/hooks/common/form';
import { $t } from '@/locales';
import { fetchCreateNotice, fetchUpdateNotice } from '@/service/api';

defineOptions({
  name: 'NoticeOperateDrawer'
});

interface Props {
  operateType: NaiveUI.TableOperateType;
  rowData?: Api.Notification.Notice | null;
}

const props = defineProps<Props>();

interface Emits {
  (e: 'submitted'): void;
}

const emit = defineEmits<Emits>();

const visible = defineModel<boolean>('visible', {
  default: false
});

const { formRef, validate, restoreValidation } = useNaiveForm();

const title = computed(() => {
  const titles: Record<NaiveUI.TableOperateType, string> = {
    add: $t('page.manage.announcement.addAnnouncement'),
    edit: $t('page.manage.announcement.editAnnouncement')
  };
  return titles[props.operateType];
});

const model = ref(createDefaultModel());

function createDefaultModel(): Api.Notification.NoticeCreate {
  return {
    title: '',
    content: '',
    type: 'system',
    target_type: 'all',
    target_role_ids: undefined,
    target_user_ids: undefined,
    priority: 'normal'
  };
}

const rules = {
  title: { required: true, message: $t('page.manage.announcement.form.title'), trigger: 'blur' },
  content: { required: true, message: $t('page.manage.announcement.form.content'), trigger: 'blur' },
  type: { required: true, message: $t('page.manage.announcement.form.type'), trigger: 'change' },
  target_type: { required: true, message: $t('page.manage.announcement.form.targetType'), trigger: 'change' },
  priority: { required: true, message: $t('page.manage.announcement.form.priority'), trigger: 'change' }
};

const noticeId = computed(() => props.rowData?.id || -1);
const isEdit = computed(() => props.operateType === 'edit');

function handleInitModel() {
  model.value = createDefaultModel();

  if (props.operateType === 'edit' && props.rowData) {
    const clonedData = jsonClone(props.rowData);
    model.value.title = clonedData.title || '';
    model.value.content = clonedData.content || '';
    model.value.type = clonedData.type || 'system';
    model.value.target_type = clonedData.target_type || 'all';
    model.value.target_role_ids = clonedData.target_role_ids || undefined;
    model.value.target_user_ids = clonedData.target_user_ids || undefined;
    model.value.priority = clonedData.priority || 'normal';
  }
}

function closeDrawer() {
  visible.value = false;
}

async function handleSubmit() {
  await validate();

  let error: unknown = null;

  if (isEdit.value) {
    const result = await fetchUpdateNotice(noticeId.value, model.value);
    error = result.error;
  } else {
    const result = await fetchCreateNotice(model.value);
    error = result.error;
  }

  if (!error) {
    window.$message?.success(isEdit.value ? $t('common.updateSuccess') : $t('common.addSuccess'));
    closeDrawer();
    emit('submitted');
  }
}

watch(visible, () => {
  if (visible.value) {
    handleInitModel();
    restoreValidation();
  }
});
</script>

<template>
  <NDrawer v-model:show="visible" display-directive="show" :width="560">
    <NDrawerContent :title="title" :native-scrollbar="false" closable>
      <NForm ref="formRef" :model="model" :rules="rules">
        <NFormItem :label="$t('page.manage.announcement.noticeType')" path="title">
          <NInput v-model:value="model.title" :placeholder="$t('page.manage.announcement.form.title')" maxlength="200" show-count />
        </NFormItem>
        <NFormItem :label="$t('page.manage.announcement.noticeContent')" path="content">
          <NInput
            v-model:value="model.content"
            type="textarea"
            :placeholder="$t('page.manage.announcement.form.content')"
            :rows="6"
          />
        </NFormItem>
        <NFormItem :label="$t('page.manage.announcement.noticeType')" path="type">
          <NRadioGroup v-model:value="model.type">
            <NRadio value="announcement">{{ $t('page.manage.announcement.type.announcement') }}</NRadio>
            <NRadio value="system">{{ $t('page.manage.announcement.type.system') }}</NRadio>
            <NRadio value="operation">{{ $t('page.manage.announcement.type.operation') }}</NRadio>
            <NRadio value="approval">{{ $t('page.manage.announcement.type.approval') }}</NRadio>
          </NRadioGroup>
        </NFormItem>
        <NFormItem :label="$t('page.manage.announcement.targetTypeLabel')" path="target_type">
          <NRadioGroup v-model:value="model.target_type">
            <NRadio value="all">{{ $t('page.manage.announcement.targetType.all') }}</NRadio>
            <NRadio value="role">{{ $t('page.manage.announcement.targetType.role') }}</NRadio>
            <NRadio value="user">{{ $t('page.manage.announcement.targetType.user') }}</NRadio>
          </NRadioGroup>
        </NFormItem>
        <NFormItem
          v-if="model.target_type === 'role'"
          :label="$t('page.manage.announcement.targetRole')"
          path="target_role_ids"
          :rule="{ required: true, message: $t('page.manage.announcement.form.roleIds'), type: 'array', trigger: 'change' }"
        >
          <NSelect
            v-model:value="model.target_role_ids"
            multiple
            :placeholder="$t('page.manage.announcement.form.roleIdsPlaceholder')"
            :options="[]"
            tag
            filterable
          />
        </NFormItem>
        <NFormItem
          v-if="model.target_type === 'user'"
          :label="$t('page.manage.announcement.targetUser')"
          path="target_user_ids"
          :rule="{ required: true, message: $t('page.manage.announcement.form.userIds'), type: 'array', trigger: 'change' }"
        >
          <NSelect
            v-model:value="model.target_user_ids"
            multiple
            :placeholder="$t('page.manage.announcement.form.userIdsPlaceholder')"
            :options="[]"
            tag
            filterable
          />
        </NFormItem>
        <NFormItem :label="$t('page.manage.announcement.priority')" path="priority">
          <NRadioGroup v-model:value="model.priority">
            <NRadio value="low">{{ $t('page.manage.announcement.priorities.low') }}</NRadio>
            <NRadio value="normal">{{ $t('page.manage.announcement.priorities.normal') }}</NRadio>
            <NRadio value="high">{{ $t('page.manage.announcement.priorities.high') }}</NRadio>
            <NRadio value="urgent">{{ $t('page.manage.announcement.priorities.urgent') }}</NRadio>
          </NRadioGroup>
        </NFormItem>
      </NForm>
      <template #footer>
        <NSpace :size="16">
          <NButton @click="closeDrawer">{{ $t('common.cancel') }}</NButton>
          <NButton type="primary" @click="handleSubmit">{{ $t('common.confirm') }}</NButton>
        </NSpace>
      </template>
    </NDrawerContent>
  </NDrawer>
</template>
