<script setup lang="ts">
import { ref } from 'vue';
import { $t } from '@/locales';

defineOptions({
  name: 'ComponentPreview'
});

defineProps<{
  /** Component name (GlobalThemeOverrides top-level key) */
  name: string;
}>();

// shared interaction state
const switchVal = ref(true);
const checkboxVal = ref(true);
const radioVal = ref('1');
const selectVal = ref('apple');
const sliderVal = ref(40);
const rateVal = ref(3);
const tabsVal = ref('first');
const collapseVal = ref<string[]>(['1']);
const modalShow = ref(false);
const drawerShow = ref(false);
const autoCompleteVal = ref('');
const dynamicTagsVal = ref<string[]>(['Tag A', 'Tag B']);

const fruitOptions = [
  { label: 'Apple', value: 'apple' },
  { label: 'Banana', value: 'banana' },
  { label: 'Cherry', value: 'cherry' }
];

const tableColumns = [
  { title: 'Name', key: 'name' },
  { title: 'Age', key: 'age' }
];
const tableData = [
  { name: 'Alice', age: 24 },
  { name: 'Bob', age: 30 }
];

const treeOptions = [
  {
    key: '1',
    label: 'Node 1',
    children: [{ key: '1-1', label: 'Node 1-1' }]
  }
];

function showMessage() {
  window.$message?.success('This is a message');
}
function showNotification() {
  window.$notification?.success({ title: 'Notification', content: 'This is a notification', duration: 2500 });
}
function showDialog() {
  window.$dialog?.info({ title: 'Dialog', content: 'This is a dialog', positiveText: 'OK' });
}
function startLoadingBar() {
  window.$loadingBar?.start();
  setTimeout(() => window.$loadingBar?.finish(), 1200);
}
</script>

<template>
  <div class="preview-box">
    <div class="mb-8px text-12px font-500 opacity-60">{{ $t('theme.componentConfig.preview') }}</div>
    <div class="flex-center flex-wrap gap-12px py-12px">
      <!-- Button -->
      <template v-if="name === 'Button'">
        <NButton size="small">Default</NButton>
        <NButton size="small" type="primary">Primary</NButton>
        <NButton size="small" type="info">Info</NButton>
        <NButton size="small" type="success">Success</NButton>
        <NButton size="small" type="warning">Warning</NButton>
        <NButton size="small" type="error">Error</NButton>
      </template>

      <!-- ButtonGroup -->
      <NButtonGroup v-else-if="name === 'ButtonGroup'">
        <NButton size="small">Prev</NButton>
        <NButton size="small">Mid</NButton>
        <NButton size="small">Next</NButton>
      </NButtonGroup>

      <!-- Card -->
      <NCard v-else-if="name === 'Card'" size="small" class="w-full">
        Card content — observes borderRadius / padding.
      </NCard>

      <!-- Input -->
      <NInput v-else-if="name === 'Input'" size="small" placeholder="Type here" class="w-160px" />

      <!-- InputNumber -->
      <NInputNumber v-else-if="name === 'InputNumber'" size="small" class="w-140px" />

      <!-- AutoComplete -->
      <NAutoComplete
        v-else-if="name === 'AutoComplete'"
        v-model:value="autoCompleteVal"
        size="small"
        :options="['@vue', '@naive', '@vite']"
        placeholder="email"
        class="w-180px"
      />

      <!-- Mentions -->
      <NMention
        v-else-if="name === 'Mentions' || name === 'Mention'"
        size="small"
        :options="[{ label: 'Naive UI', value: 'naive' }]"
        placeholder="@mention"
        class="w-200px"
      />

      <!-- Tag -->
      <template v-else-if="name === 'Tag'">
        <NTag size="small">Default</NTag>
        <NTag size="small" type="primary">Primary</NTag>
        <NTag size="small" type="success">Success</NTag>
        <NTag size="small" type="warning">Warning</NTag>
        <NTag size="small" type="error">Error</NTag>
      </template>

      <!-- Avatar / AvatarGroup -->
      <NAvatar v-else-if="name === 'Avatar'" size="small" round>N</NAvatar>
      <NAvatarGroup v-else-if="name === 'AvatarGroup'" size="small" :max="2">
        <NAvatar>A</NAvatar>
        <NAvatar>B</NAvatar>
        <NAvatar>C</NAvatar>
      </NAvatarGroup>

      <!-- Badge -->
      <NBadge v-else-if="name === 'Badge'" :value="9">
        <NButton size="small">Mail</NButton>
      </NBadge>

      <!-- Checkbox -->
      <NCheckbox v-else-if="name === 'Checkbox'" v-model:checked="checkboxVal">Checkbox</NCheckbox>

      <!-- Radio -->
      <NRadioGroup v-else-if="name === 'Radio'" v-model:value="radioVal" size="small">
        <NRadio value="1">A</NRadio>
        <NRadio value="2">B</NRadio>
      </NRadioGroup>

      <!-- Switch -->
      <NSwitch v-else-if="name === 'Switch'" v-model:value="switchVal" size="small" />

      <!-- Select -->
      <NSelect
        v-else-if="name === 'Select'"
        v-model:value="selectVal"
        size="small"
        :options="fruitOptions"
        class="w-140px"
      />

      <!-- Cascader -->
      <NCascader
        v-else-if="name === 'Cascader'"
        size="small"
        :options="[{ label: 'A', value: 'a', children: [{ label: 'A1', value: 'a1' }] }]"
        placeholder="select"
        class="w-140px"
      />

      <!-- TreeSelect -->
      <NTreeSelect
        v-else-if="name === 'TreeSelect'"
        size="small"
        :options="treeOptions"
        placeholder="select"
        class="w-160px"
      />

      <!-- Popselect -->
      <NPopselect v-else-if="name === 'Popselect'" :options="fruitOptions" trigger="click">
        <NButton size="small">Popselect</NButton>
      </NPopselect>

      <!-- Slider -->
      <NSlider v-else-if="name === 'Slider'" v-model:value="sliderVal" class="w-160px" />

      <!-- Rate -->
      <NRate v-else-if="name === 'Rate'" v-model:value="rateVal" size="small" />

      <!-- Progress -->
      <NProgress v-else-if="name === 'Progress'" type="line" :percentage="60" class="w-180px" />

      <!-- Alert -->
      <NAlert v-else-if="name === 'Alert'" type="info" :show-icon="true" class="w-full">Alert content</NAlert>

      <!-- Tabs -->
      <NTabs v-else-if="name === 'Tabs'" v-model:value="tabsVal" size="small" type="line" class="w-full">
        <NTabPane name="first" tab="First">Content 1</NTabPane>
        <NTabPane name="second" tab="Second">Content 2</NTabPane>
      </NTabs>

      <!-- DataTable / Table -->
      <NDataTable
        v-else-if="name === 'DataTable' || name === 'Table'"
        size="small"
        :columns="tableColumns"
        :data="tableData"
        :bordered="true"
        :single-line="false"
        class="w-full"
      />

      <!-- Pagination -->
      <NPagination v-else-if="name === 'Pagination'" :page-count="5" :page="1" size="small" />

      <!-- Steps -->
      <NSteps v-else-if="name === 'Steps'" :current="2">
        <NStep title="Start" />
        <NStep title="Mid" />
        <NStep title="End" />
      </NSteps>

      <!-- Breadcrumb -->
      <NBreadcrumb v-else-if="name === 'Breadcrumb'">
        <NBreadcrumbItem>Home</NBreadcrumbItem>
        <NBreadcrumbItem>Page</NBreadcrumbItem>
      </NBreadcrumb>

      <!-- Menu -->
      <NMenu
        v-else-if="name === 'Menu'"
        mode="horizontal"
        :options="[
          { label: 'Item A', key: 'a' },
          { label: 'Item B', key: 'b' }
        ]"
        class="w-full"
      />

      <!-- Tree -->
      <NTree v-else-if="name === 'Tree'" :data="treeOptions" block-line class="w-full" />

      <!-- Empty -->
      <NEmpty v-else-if="name === 'Empty'" size="small" />

      <!-- Result -->
      <NResult v-else-if="name === 'Result'" status="info" title="Result" class="w-full" />

      <!-- Spin -->
      <NSpin v-else-if="name === 'Spin'" size="small" />

      <!-- Skeleton -->
      <NSkeleton v-else-if="name === 'Skeleton'" size="small" :width="160" />

      <!-- Tooltip -->
      <NTooltip v-else-if="name === 'Tooltip'">
        <template #trigger>
          <NButton size="small">Hover me</NButton>
        </template>
        Tooltip text
      </NTooltip>

      <!-- Popover -->
      <NPopover v-else-if="name === 'Popover'" trigger="hover">
        <template #trigger>
          <NButton size="small">Hover me</NButton>
        </template>
        Popover content
      </NPopover>

      <!-- Popconfirm -->
      <NPopconfirm v-else-if="name === 'Popconfirm'">
        <template #trigger>
          <NButton size="small">Delete</NButton>
        </template>
        Are you sure?
      </NPopconfirm>

      <!-- Typography -->
      <NSpace v-else-if="name === 'Typography'" vertical class="w-full">
        <NText>Text</NText>
        <NText strong>Bold</NText>
        <NText type="primary">Primary</NText>
      </NSpace>

      <!-- GradientText -->
      <NGradientText v-else-if="name === 'GradientText'" type="info" size="small">Gradient Text</NGradientText>

      <!-- Descriptions -->
      <NDescriptions
        v-else-if="name === 'Descriptions'"
        size="small"
        label-placement="left"
        bordered
        :column="2"
        class="w-full"
      >
        <NDescriptionsItem label="Name">Alice</NDescriptionsItem>
        <NDescriptionsItem label="Age">24</NDescriptionsItem>
      </NDescriptions>

      <!-- Statistic -->
      <NStatistic v-else-if="name === 'Statistic'" label="Users" :value="1024" />

      <!-- Timeline -->
      <NTimeline v-else-if="name === 'Timeline'">
        <NTimelineItem content="Event A" />
        <NTimelineItem type="success" content="Event B" />
      </NTimeline>

      <!-- DatePicker -->
      <NDatePicker v-else-if="name === 'DatePicker'" size="small" type="date" class="w-160px" />

      <!-- TimePicker -->
      <NTimePicker v-else-if="name === 'TimePicker'" size="small" class="w-140px" />

      <!-- Calendar -->
      <NCalendar v-else-if="name === 'Calendar'" class="w-full border rd-4px" :is-date-disabled="() => false" />

      <!-- Upload -->
      <NUpload v-else-if="name === 'Upload'" :default-upload="false">
        <NButton size="small">Upload</NButton>
      </NUpload>

      <!-- Watermark -->
      <NWatermark
        v-else-if="name === 'Watermark'"
        content="Naive UI"
        :height="90"
        :width="120"
        :font-size="14"
        class="w-full"
      >
        <div class="h-120px w-full rd-4px bg-#f7f7f7 dark:bg-#1e1e1e"></div>
      </NWatermark>

      <!-- Carousel -->
      <NCarousel v-else-if="name === 'Carousel'" class="h-100px w-full rd-4px">
        <div class="h-full flex-center bg-primary-200 text-13px">Slide 1</div>
        <div class="h-full flex-center bg-primary-300 text-13px">Slide 2</div>
      </NCarousel>

      <!-- Collapse -->
      <NCollapse v-else-if="name === 'Collapse'" v-model:expanded-names="collapseVal" class="w-full">
        <NCollapseItem title="Header" name="1">Content</NCollapseItem>
      </NCollapse>

      <!-- ColorPicker -->
      <NColorPicker v-else-if="name === 'ColorPicker'" size="small" class="w-140px" />

      <!-- Code -->
      <NCode v-else-if="name === 'Code'" code="const x = 1;" language="javascript" />

      <!-- List -->
      <NList v-else-if="name === 'List'" hoverable bordered size="small" class="w-full">
        <NListItem>Item A</NListItem>
        <NListItem>Item B</NListItem>
      </NList>

      <!-- Image -->
      <NImage
        v-else-if="name === 'Image'"
        width="80"
        src="https://07akioni.oss-cn-beijing.aliyuncs.com/07akioni.jpeg"
      />

      <!-- QrCode -->
      <NQrCode v-else-if="name === 'QrCode'" value="https://www.naiveui.com" :size="90" error-correction-level="M" />

      <!-- Message / Notification / Dialog -->
      <template v-else-if="name === 'Message'">
        <NButton size="small" @click="showMessage">Show message</NButton>
      </template>
      <template v-else-if="name === 'Notification'">
        <NButton size="small" @click="showNotification">Show notification</NButton>
      </template>
      <template v-else-if="name === 'Dialog'">
        <NButton size="small" @click="showDialog">Show dialog</NButton>
      </template>

      <!-- Modal / Drawer -->
      <template v-else-if="name === 'Modal'">
        <NButton size="small" @click="modalShow = true">Open modal</NButton>
        <NModal v-model:show="modalShow" preset="card" title="Modal" class="max-w-360px">Modal content</NModal>
      </template>
      <template v-else-if="name === 'Drawer'">
        <NButton size="small" @click="drawerShow = true">Open drawer</NButton>
        <NDrawer v-model:show="drawerShow" :width="280">
          <NDrawerContent title="Drawer" closable>Drawer content</NDrawerContent>
        </NDrawer>
      </template>

      <!-- FloatButton -->
      <NFloatButton v-else-if="name === 'FloatButton'" size="small">+</NFloatButton>

      <!-- Form -->
      <NForm v-else-if="name === 'Form'" inline size="small" :show-feedback="false">
        <NFormItem label="Name"><NInput placeholder="name" /></NFormItem>
        <NFormItem label="Age"><NInputNumber /></NFormItem>
      </NForm>

      <!-- PageHeader -->
      <NPageHeader v-else-if="name === 'PageHeader'" subtitle="subtitle" class="w-full">Page header</NPageHeader>

      <!-- Anchor -->
      <NAnchor v-else-if="name === 'Anchor'" :show-rail="true">
        <NAnchorLink title="Section A" />
        <NAnchorLink title="Section B" />
      </NAnchor>

      <!-- Ellipsis -->
      <NEllipsis v-else-if="name === 'Ellipsis'" class="w-160px" :line="1">
        A very long text that should be ellipsized when it overflows the container width.
      </NEllipsis>

      <!-- Space -->
      <NSpace v-else-if="name === 'Space'" size="small">
        <NTag size="small">A</NTag>
        <NTag size="small">B</NTag>
      </NSpace>

      <!-- Flex -->
      <NFlex v-else-if="name === 'Flex'" size="small">
        <NTag size="small">A</NTag>
        <NTag size="small">B</NTag>
      </NFlex>

      <!-- DynamicTags -->
      <NDynamicTags v-else-if="name === 'DynamicTags'" v-model:value="dynamicTagsVal" size="small" />

      <!-- Icon -->
      <NIcon v-else-if="name === 'Icon'" size="20">
        <svg viewBox="0 0 24 24"><path fill="currentColor" d="M12 2l2 6h6l-5 4l2 6l-5-4l-5 4l2-6l-5-4h6z" /></svg>
      </NIcon>

      <!-- LoadingBar: trigger via button -->
      <template v-else-if="name === 'LoadingBar'">
        <NButton size="small" @click="startLoadingBar">Start bar</NButton>
      </template>

      <!-- Default: comprehensive panel (also used by `common`) -->
      <template v-else>
        <NButton size="small" type="primary">Primary</NButton>
        <NButton size="small">Default</NButton>
        <NTag size="small" type="info">Tag</NTag>
        <NInput size="small" placeholder="Input" class="w-120px" />
        <NSwitch v-model:value="switchVal" size="small" />
        <NCheckbox v-model:checked="checkboxVal" size="small">Check</NCheckbox>
        <NRate v-model:value="rateVal" size="small" />
        <NProgress type="line" :percentage="60" class="w-120px" />
        <NSlider v-model:value="sliderVal" class="w-120px" />
        <NBadge :value="3"><NButton size="small">Mail</NButton></NBadge>
      </template>
    </div>
  </div>
</template>

<style scoped>
.preview-box {
  padding: 8px 12px;
  border: 1px solid rgba(0, 0, 0, 0.09);
  border-radius: 6px;
  background-color: #f7f7f7;
}

html.dark .preview-box {
  border-color: rgba(255, 255, 255, 0.09);
  background-color: #1e1e1e;
}
</style>
