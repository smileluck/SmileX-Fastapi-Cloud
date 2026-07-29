<script setup lang="ts">
import { computed, toRaw } from 'vue';
import { jsonClone } from '@sa/utils';
import { enableStatusOptions } from '@/constants/business';
import { useFormRules, useNaiveForm } from '@/hooks/common/form';
import { $t } from '@/locales';

defineOptions({
  name: 'AppUserSearch'
});

interface Emits {
  (e: 'search'): void;
}

const emit = defineEmits<Emits>();

const { formRef, validate, restoreValidation } = useNaiveForm();

const model = defineModel<Api.SystemManage.AppUserSearchParams>('model', { required: true });

type RuleKey = Extract<keyof Api.SystemManage.AppUserSearchParams, 'email' | 'phone'>;

const rules = computed<Record<RuleKey, App.Global.FormRule>>(() => {
  const { patternRules } = useFormRules(); // inside computed to make locale reactive

  return {
    email: patternRules.email,
    phone: patternRules.phone
  };
});

const defaultModel = jsonClone(toRaw(model.value));

function resetModel() {
  Object.assign(model.value, defaultModel);
}

async function reset() {
  await restoreValidation();
  resetModel();
}

async function search() {
  await validate();
  emit('search');
}
</script>

<template>
  <NCard :bordered="false" size="small" class="card-wrapper">
    <NCollapse :default-expanded-names="['app-user-search']">
      <NCollapseItem :title="$t('common.search')" name="app-user-search">
        <NForm ref="formRef" :model="model" :rules="rules" label-placement="left" :label-width="80">
          <NGrid responsive="screen" item-responsive>
            <NFormItemGi span="24 s:12 m:6" :label="$t('page.manage.appUser.userName')" path="name" class="pr-24px">
              <NInput v-model:value="model.name" :placeholder="$t('page.manage.appUser.form.userName')" />
            </NFormItemGi>
            <NFormItemGi span="24 s:12 m:6" :label="$t('page.manage.appUser.userPhone')" path="phone" class="pr-24px">
              <NInput v-model:value="model.phone" :placeholder="$t('page.manage.appUser.form.userPhone')" />
            </NFormItemGi>
            <NFormItemGi span="24 s:12 m:6" :label="$t('page.manage.appUser.userEmail')" path="email" class="pr-24px">
              <NInput v-model:value="model.email" :placeholder="$t('page.manage.appUser.form.userEmail')" />
            </NFormItemGi>
            <NFormItemGi span="24 s:12 m:6" :label="$t('page.manage.appUser.userStatus')" path="status" class="pr-24px">
              <NSelect
                v-model:value="model.status"
                :placeholder="$t('page.manage.appUser.form.userStatus')"
                :options="enableStatusOptions"
                clearable
              />
            </NFormItemGi>
            <NFormItemGi span="24 m:12" class="pr-24px">
              <NSpace class="w-full" justify="end">
                <NButton @click="reset">
                  <template #icon>
                    <icon-ic-round-refresh class="text-icon" />
                  </template>
                  {{ $t('common.reset') }}
                </NButton>
                <NButton type="primary" ghost @click="search">
                  <template #icon>
                    <icon-ic-round-search class="text-icon" />
                  </template>
                  {{ $t('common.search') }}
                </NButton>
              </NSpace>
            </NFormItemGi>
          </NGrid>
        </NForm>
      </NCollapseItem>
    </NCollapse>
  </NCard>
</template>

<style scoped></style>
