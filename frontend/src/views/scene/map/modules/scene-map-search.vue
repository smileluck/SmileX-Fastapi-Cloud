<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { jsonClone } from '@sa/utils';
import { fetchGetSceneGroupList } from '@/service/api';

defineOptions({
  name: 'SceneMapSearch'
});

interface Emits {
  (e: 'search'): void;
  (e: 'reset'): void;
}

const emit = defineEmits<Emits>();

const model = defineModel<Api.Scene.SceneMapSearchParams>('model', { required: true });

const defaultModel = jsonClone(model.value);

/** 分组选项 */
const groupOptions = ref<{ label: string; value: number }[]>([]);

async function loadGroupOptions() {
  const { data } = await fetchGetSceneGroupList({ page: 1, page_size: 1000 });
  if (data?.records) {
    groupOptions.value = data.records.map((item: any) => ({
      label: item.name,
      value: item.id
    }));
  }
}

function resetModel() {
  Object.assign(model.value, defaultModel);
  emit('reset');
}

function search() {
  emit('search');
}

onMounted(() => {
  loadGroupOptions();
});
</script>

<template>
  <NCard :bordered="false" size="small" class="card-wrapper">
    <NCollapse :default-expanded-names="['scene-map-search']">
      <NCollapseItem title="搜索" name="scene-map-search">
        <NForm :model="model" label-placement="left" :label-width="80">
          <NGrid responsive="screen" item-responsive>
            <NFormItemGi span="24 s:12 m:6" label="地图名称" path="name" class="pr-24px">
              <NInput v-model:value="model.name" placeholder="请输入地图名称" clearable />
            </NFormItemGi>
            <NFormItemGi span="24 s:12 m:6" label="所属分组" path="group_id" class="pr-24px">
              <NSelect
                v-model:value="model.group_id"
                :options="groupOptions"
                placeholder="请选择所属分组"
                clearable
              />
            </NFormItemGi>
            <NFormItemGi span="24 m:12" class="pr-24px">
              <NSpace class="w-full" justify="end">
                <NButton @click="resetModel">
                  <template #icon>
                    <icon-ic-round-refresh class="text-icon" />
                  </template>
                  重置
                </NButton>
                <NButton type="primary" ghost @click="search">
                  <template #icon>
                    <icon-ic-round-search class="text-icon" />
                  </template>
                  搜索
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
