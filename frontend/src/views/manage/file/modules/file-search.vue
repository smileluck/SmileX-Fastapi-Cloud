<script setup lang="ts">
import { toRaw } from 'vue';
import { NButton, NCollapse, NCollapseItem, NForm, NFormItemGi, NGrid, NInput, NSelect, NSpace } from 'naive-ui';
import { jsonClone } from '@sa/utils';
import { $t } from '@/locales';

defineOptions({
  name: 'FileSearch'
});

interface Emits {
  (e: 'search'): void;
  (e: 'reset'): void;
}

const emit = defineEmits<Emits>();

const model = defineModel<Api.FileManage.FileSearchParams>('model', { required: true });

const defaultModel = jsonClone(toRaw(model.value));

const storagePlatformOptions = [
  { label: $t('page.manage.file.platform.local'), value: 'local' },
  { label: $t('page.manage.file.platform.oss'), value: 'oss' }
];

function resetModel() {
  Object.assign(model.value, defaultModel);
  emit('reset');
}

function search() {
  emit('search');
}
</script>

<template>
  <NCard :bordered="false" size="small" class="card-wrapper">
    <NCollapse :default-expanded-names="['file-search']">
      <NCollapseItem :title="$t('common.search')" name="file-search">
        <NForm :model="model" label-placement="left" :label-width="80">
          <NGrid responsive="screen" item-responsive>
            <NFormItemGi
              span="24 s:12 m:6"
              :label="$t('page.manage.file.fileName')"
              path="original_name"
              class="pr-24px"
            >
              <NInput
                v-model:value="model.original_name"
                :placeholder="$t('page.manage.file.form.fileName')"
                clearable
              />
            </NFormItemGi>
            <NFormItemGi
              span="24 s:12 m:6"
              :label="$t('page.manage.file.fileExtension')"
              path="extension"
              class="pr-24px"
            >
              <NInput
                v-model:value="model.extension"
                :placeholder="$t('page.manage.file.form.fileExtension')"
                clearable
              />
            </NFormItemGi>
            <NFormItemGi
              span="24 s:12 m:6"
              :label="$t('page.manage.file.storagePlatform')"
              path="storage_platform"
              class="pr-24px"
            >
              <NSelect
                v-model:value="model.storage_platform"
                :options="storagePlatformOptions"
                :placeholder="$t('page.manage.file.form.storagePlatform')"
                clearable
              />
            </NFormItemGi>
            <NFormItemGi span="24 m:6" class="pr-24px">
              <NSpace class="w-full" justify="end">
                <NButton @click="resetModel">
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
