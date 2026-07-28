<script setup lang="tsx">
import { ref } from 'vue';

defineOptions({ name: 'DictDemoPage' });

const selectedGender = ref<string | null>(null);
const selectedGender2 = ref<string | null>('0');

const tableData = [
  { name: 'Alice', gender: '1' },
  { name: 'Bob', gender: '2' },
  { name: 'Unknown', gender: '0' }
];

const tableColumns = [
  { key: 'name', title: 'Name', align: 'center' as const, width: 120 },
  {
    key: 'gender_text',
    title: 'Gender (DictText)',
    align: 'center' as const,
    width: 160,
    render: (row: any) => <DictText dictCode="gender" value={row.gender} />
  },
  {
    key: 'gender_tag',
    title: 'Gender (DictTag)',
    align: 'center' as const,
    width: 160,
    render: (row: any) => <DictTag dictCode="gender" value={row.gender} type="primary" />
  }
];
</script>

<template>
  <NSpace vertical :size="16">
    <NCard :bordered="false" :title="$t('page.demo.dict.selectDemo')" class="card-wrapper">
      <NSpace vertical :size="12">
        <NText>{{ $t('page.demo.dict.selectLabel') }}</NText>
        <DictSelect v-model:value="selectedGender" dict-code="gender" />
        <NText depth="3">v-model value: {{ selectedGender ?? 'null' }}</NText>

        <NDivider />

        <NText>{{ $t('page.demo.dict.selectWithDefault') }}</NText>
        <DictSelect v-model:value="selectedGender2" dict-code="gender" />
        <NText depth="3">v-model value: {{ selectedGender2 ?? 'null' }}</NText>
      </NSpace>
    </NCard>

    <NCard :bordered="false" :title="$t('page.demo.dict.tagDemo')" class="card-wrapper">
      <NSpace vertical :size="12">
        <NText>{{ $t('page.demo.dict.tagLabel') }}</NText>
        <NSpace :size="8">
          <DictTag dict-code="gender" value="1" type="primary" />
          <DictTag dict-code="gender" value="2" type="error" />
          <DictTag dict-code="gender" value="0" type="warning" />
        </NSpace>
      </NSpace>
    </NCard>

    <NCard :bordered="false" :title="$t('page.demo.dict.textDemo')" class="card-wrapper">
      <NSpace vertical :size="12">
        <NText>{{ $t('page.demo.dict.textLabel') }}</NText>
        <NDescriptions bordered :column="3" label-placement="left">
          <NDescriptionsItem label="value = 1">
            <DictText dict-code="gender" value="1" />
          </NDescriptionsItem>
          <NDescriptionsItem label="value = 2">
            <DictText dict-code="gender" value="2" />
          </NDescriptionsItem>
          <NDescriptionsItem label="value = 0">
            <DictText dict-code="gender" value="0" />
          </NDescriptionsItem>
        </NDescriptions>
      </NSpace>
    </NCard>

    <NCard :bordered="false" :title="$t('page.demo.dict.tableDemo')" class="card-wrapper">
      <NSpace vertical :size="12">
        <NText>{{ $t('page.demo.dict.tableLabel') }}</NText>
        <NDataTable :bordered="false" :columns="tableColumns" :data="tableData" />
      </NSpace>
    </NCard>
  </NSpace>
</template>
