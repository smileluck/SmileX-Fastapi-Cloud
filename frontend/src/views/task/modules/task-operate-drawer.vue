<script setup lang="ts">
import { computed, h, onMounted, ref, watch } from 'vue';
import { jsonClone } from '@sa/utils';
import { NText, NTooltip } from 'naive-ui';
import { useNaiveForm } from '@/hooks/common/form';
import { $t } from '@/locales';
import { fetchCreateTask, fetchUpdateTask, fetchGetTask, fetchGetRobotList, fetchGetMapAnnotations } from '@/service/api';

defineOptions({ name: 'TaskOperateDrawer' });

interface Props {
  operateType: NaiveUI.TableOperateType;
  rowData?: Api.Task.Task | null;
}

const props = defineProps<Props>();

interface Emits {
  (e: 'submitted'): void;
}

const emit = defineEmits<Emits>();

const visible = defineModel<boolean>('visible', { default: false });
const { formRef, validate, restoreValidation } = useNaiveForm();

const title = computed(() => (props.operateType === 'add' ? '创建任务' : '编辑任务'));

/** 任务类型选项 */
const taskTypeOptions = [
  { label: '巡逻', value: 'patrol' },
  { label: '播报', value: 'broadcast' }
];

/** 运控动作选项 */
const actionOptions = [
  { label: '挥手', value: 'wave' },
  { label: '鞠躬', value: 'bow' },
  { label: '转身', value: 'turn' },
  { label: '停留等待', value: 'wait' },
  { label: '点头', value: 'nod' }
];

/** 播报次数选项 */
const broadcastCountOptions = [
  { label: '1 次', value: '1' },
  { label: '2 次', value: '2' },
  { label: '3 次', value: '3' },
  { label: '5 次', value: '5' },
  { label: '循环播报', value: 'loop' }
];

/** 重复周期选项（星期复选框） */
const weekdayOptions = [
  { label: '周一', value: 'mon' },
  { label: '周二', value: 'tue' },
  { label: '周三', value: 'wed' },
  { label: '周四', value: 'thu' },
  { label: '周五', value: 'fri' },
  { label: '周六', value: 'sat' },
  { label: '周日', value: 'sun' }
];

/** 机器人选项 */
interface RobotOption {
  label: string;
  value: number;
  status: string;
  map_id: number | null;
  map_name: string | null;
  disabled?: boolean;
}
const robotOptions = ref<RobotOption[]>([]);

async function loadRobotOptions() {
  const { data, error } = await fetchGetRobotList({ page: 1, page_size: 200 });
  if (!error && data) {
    robotOptions.value = (data.records || []).map(r => ({
      label: r.name + (r.status === 'online' ? ' (在线)' : r.status === 'offline' ? ' (离线)' : ' (未激活)'),
      value: r.id,
      status: r.status || 'inactive',
      map_id: r.map_id ?? null,
      map_name: r.map_name ?? null
    }));
  }
}

/** 场景点位（annotation）选项 */
interface AnnotationOption {
  label: string;
  value: number;
}
const annotationOptions = ref<AnnotationOption[]>([]);
const annotationMap = ref<Map<number, Api.Scene.SceneMapAnnotation>>(new Map());

async function loadAnnotations(mapId: number | null) {
  if (mapId === null) {
    annotationOptions.value = [];
    annotationMap.value = new Map();
    return;
  }
  const { data, error } = await fetchGetMapAnnotations(mapId);
  if (!error && data) {
    const list: Api.Scene.SceneMapAnnotation[] = Array.isArray(data) ? data : (data?.records ?? []);
    annotationMap.value = new Map(list.map(a => [a.id, a]));
    annotationOptions.value = list.map(a => ({
      label: `${a.name} (${a.x}, ${a.y})`,
      value: a.id
    }));
  } else {
    annotationOptions.value = [];
    annotationMap.value = new Map();
  }
}

/** 巡逻任务机器人约束 */
const isPatrol = computed(() => model.value.task_type === 'patrol');

const selectedMapId = computed<number | null>(() => {
  if (model.value.robot_ids.length === 0) return null;
  const firstRobot = robotOptions.value.find(r => r.value === model.value.robot_ids[0]);
  return firstRobot?.map_id ?? null;
});

const filteredRobotOptions = computed(() => {
  if (!isPatrol.value) {
    return robotOptions.value;
  }
  return robotOptions.value.map(opt => {
    const noScenario = opt.map_id === null;
    const differentScenario = selectedMapId.value !== null && opt.map_id !== selectedMapId.value;
    return {
      ...opt,
      disabled: noScenario || differentScenario
    };
  });
});

function renderRobotLabel(option: RobotOption) {
  if (option.disabled && isPatrol.value) {
    const tip = option.map_id === null ? '需要分配场景' : '该机器人与已选机器人不在同一场景';
    return h(
      NTooltip,
      { placement: 'right' },
      {
        trigger: () =>
          h(NText, { depth: 3, style: 'text-decoration: line-through' }, { default: () => option.label }),
        default: () => tip
      }
    );
  }
  return option.label;
}

/** 表单模型 */
interface PointItem {
  sort_order: number;
  point_name: string | null;
  annotation_id: number | null;
  action: Api.Task.TaskAction;
  voice_text: string | null;
}

interface FormModel {
  name: string;
  task_type: Api.Task.TaskType;
  points: PointItem[];
  broadcast_text: string | null;
  broadcast_count: string | null;
  robot_ids: number[];
  schedule_enabled: boolean;
  schedule_date: number | null;
  schedule_start_time: number | null;
  schedule_repeat_cycles: string[];
}

function createDefaultModel(): FormModel {
  return {
    name: '',
    task_type: 'patrol',
    points: [],
    broadcast_text: null,
    broadcast_count: '1',
    robot_ids: [],
    schedule_enabled: false,
    schedule_date: null,
    schedule_start_time: null,
    schedule_repeat_cycles: []
  };
}

const model = ref<FormModel>(createDefaultModel());

/** 点位管理 */
function addPoint() {
  model.value.points.push({
    sort_order: model.value.points.length,
    point_name: null,
    annotation_id: null,
    action: 'wave',
    voice_text: null
  });
}

function removePoint(index: number) {
  model.value.points.splice(index, 1);
  model.value.points.forEach((p, i) => {
    p.sort_order = i;
  });
}

/** 校验规则 */
const rules = computed(() => ({
  name: [
    { required: true, message: '请输入任务名称', trigger: 'blur' },
    { min: 2, max: 20, message: '任务名称为 2-20 字', trigger: 'blur' }
  ],
  task_type: { required: true, message: '请选择任务类型', trigger: 'change' },
  robot_ids: {
    required: true,
    type: 'array' as const,
    min: 1,
    message: '至少选择一台机器人',
    trigger: 'change'
  }
}));

const taskId = computed(() => props.rowData?.id || -1);
const isEdit = computed(() => props.operateType === 'edit');

async function handleInitModel() {
  model.value = createDefaultModel();
  annotationOptions.value = [];
  annotationMap.value = new Map();

  if (props.operateType === 'edit' && props.rowData) {
    const cloned = jsonClone(props.rowData) as Api.Task.Task;
    model.value.name = cloned.name || '';
    model.value.task_type = cloned.task_type || 'patrol';
    model.value.broadcast_text = cloned.broadcast_text || null;
    model.value.broadcast_count = cloned.broadcast_count || '1';
    model.value.schedule_enabled = cloned.schedule_enabled || false;
    model.value.schedule_repeat_cycles = cloned.schedule_repeat_cycle
      ? cloned.schedule_repeat_cycle.split(',').filter(v => v && v !== 'none')
      : [];
    model.value.robot_ids = cloned.robots?.map(r => r.id) || [];

    if (selectedMapId.value !== null) {
      await loadAnnotations(selectedMapId.value);
    }

    if (cloned.points && cloned.points.length > 0) {
      model.value.points = cloned.points.map((p, i) => ({
        sort_order: i,
        point_name: p.point_name || null,
        annotation_id: p.annotation_id ?? null,
        action: p.action || 'wave',
        voice_text: p.voice_text || null
      }));
    }

    if (cloned.id) {
      const { data: detail } = await fetchGetTask(cloned.id);
      if (detail) {
        model.value.robot_ids = detail.robots?.map(r => r.id) || [];
        if (selectedMapId.value !== null) {
          await loadAnnotations(selectedMapId.value);
        }
        if (detail.points && detail.points.length > 0) {
          model.value.points = detail.points.map((p, i) => ({
            sort_order: i,
            point_name: p.point_name || null,
            annotation_id: p.annotation_id ?? null,
            action: p.action || 'wave',
            voice_text: p.voice_text || null
          }));
        }
      }
    }
  }
}

/** 用户主动切换机器人选择：清空已填点位（依赖 watch selectedMapId 重新加载点位选项） */
function handleRobotIdsChange() {
  model.value.points = [];
}

function closeDrawer() {
  visible.value = false;
}

async function handleSubmit() {
  await validate();

  // Custom validations
  if (model.value.task_type === 'patrol' && model.value.points.length === 0) {
    window.$message?.warning('巡逻任务至少添加一个巡逻点位');
    return;
  }
  if (model.value.task_type === 'broadcast' && !model.value.broadcast_text) {
    window.$message?.warning('请填写播报文本');
    return;
  }
  if (model.value.task_type === 'patrol') {
    const selectedRobots = robotOptions.value.filter(r => model.value.robot_ids.includes(r.value));
    const nullMap = selectedRobots.some(r => r.map_id === null);
    if (nullMap) {
      window.$message?.warning('巡逻任务的机器人必须已分配场景');
      return;
    }
    const mapIds = [...new Set(selectedRobots.map(r => r.map_id))];
    if (mapIds.length > 1) {
      window.$message?.warning('巡逻任务不能选择不同场景的机器人');
      return;
    }
  }

  const submitData: Api.Task.TaskCreate = {
    name: model.value.name,
    task_type: model.value.task_type,
    robot_ids: model.value.robot_ids,
    schedule_enabled: model.value.schedule_enabled,
    schedule_repeat_cycle: model.value.schedule_repeat_cycles.length > 0
      ? model.value.schedule_repeat_cycles.join(',')
      : null,
    points: model.value.task_type === 'patrol' ? model.value.points : undefined,
    broadcast_text: model.value.task_type === 'broadcast' ? model.value.broadcast_text : undefined,
    broadcast_count: model.value.task_type === 'broadcast' ? model.value.broadcast_count : undefined
  };

  let error: unknown = null;
  if (isEdit.value) {
    const result = await fetchUpdateTask(taskId.value, submitData);
    error = result.error;
  } else {
    const result = await fetchCreateTask(submitData);
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

watch(selectedMapId, newMapId => {
  loadAnnotations(newMapId);
});

watch(
  () => model.value.task_type,
  () => {
    if (model.value.task_type === 'patrol' && model.value.robot_ids.length > 0) {
      const validIds = model.value.robot_ids.filter(id => {
        const robot = robotOptions.value.find(r => r.value === id);
        return robot && robot.map_id !== null;
      });
      if (validIds.length > 0) {
        const firstMapId = robotOptions.value.find(r => r.value === validIds[0])?.map_id;
        model.value.robot_ids = validIds.filter(id => {
          const robot = robotOptions.value.find(r => r.value === id);
          return robot?.map_id === firstMapId;
        });
      } else {
        model.value.robot_ids = [];
      }
    }
  }
);

onMounted(() => {
  loadRobotOptions();
});
</script>

<template>
  <NDrawer v-model:show="visible" display-directive="show" :width="640">
    <NDrawerContent :title="title" :native-scrollbar="false" closable>
      <NForm ref="formRef" :model="model" :rules="rules" label-placement="top">
        <!-- 基础信息 -->
        <NGrid :cols="2" :x-gap="16">
          <NFormItemGi :span="2" label="任务名称" path="name">
            <NInput v-model:value="model.name" placeholder="请输入任务名称（2-20字）" :maxlength="20" show-count />
          </NFormItemGi>
          <NFormItemGi :span="2" label="任务类型" path="task_type">
            <NRadioGroup v-model:value="model.task_type">
              <NRadioButton v-for="opt in taskTypeOptions" :key="opt.value" :value="opt.value" :label="opt.label" />
            </NRadioGroup>
          </NFormItemGi>
        </NGrid>

        <!-- 机器人绑定 -->
        <NDivider title-placement="left">执行机器人</NDivider>
        <NFormItem label="绑定机器人" path="robot_ids">
          <NSelect
            v-model:value="model.robot_ids"
            :options="filteredRobotOptions"
            placeholder="至少选择一台机器人"
            multiple
            filterable
            :render-label="renderRobotLabel"
            @update:value="handleRobotIdsChange"
          />
        </NFormItem>

        <!-- 巡逻点位配置 -->
        <template v-if="model.task_type === 'patrol'">
          <NDivider title-placement="left">巡逻点位配置</NDivider>
          <div v-if="selectedMapId === null" class="mb-12px text-13px" style="color: var(--n-text-color-3, #999);">
            请先选择已绑定场景的机器人，才能选择巡逻点位
          </div>
          <div v-for="(point, index) in model.points" :key="index" class="mb-12px">
            <NCard size="small" embedded>
              <template #header>
                <NSpace align="center">
                  <span>点位 {{ index + 1 }}</span>
                  <NButton type="error" ghost size="tiny" @click="removePoint(index)">移除</NButton>
                </NSpace>
              </template>
              <NGrid :cols="3" :x-gap="12">
                <NFormItemGi label="巡逻点位">
                  <NSelect
                    v-model:value="point.annotation_id"
                    :options="annotationOptions"
                    :placeholder="selectedMapId === null ? '请先选择机器人' : '请选择场景点位'"
                    :disabled="selectedMapId === null"
                    filterable
                    @update:value="(val: number | null) => {
                      const ann = val === null ? undefined : annotationMap.get(val);
                      point.point_name = ann?.name ?? null;
                    }"
                  />
                </NFormItemGi>
                <NFormItemGi label="运控动作">
                  <NSelect v-model:value="point.action" :options="actionOptions" placeholder="选择动作" />
                </NFormItemGi>
                <NFormItemGi label="语音文本">
                  <NInput v-model:value="point.voice_text" placeholder="语音播报文本" />
                </NFormItemGi>
              </NGrid>
            </NCard>
          </div>
          <NButton dashed block :disabled="selectedMapId === null" @click="addPoint">
            <template #icon>
              <icon-ic-round-plus class="text-icon" />
            </template>
            添加点位
          </NButton>
        </template>

        <!-- 播报配置 -->
        <template v-if="model.task_type === 'broadcast'">
          <NDivider title-placement="left">播报配置</NDivider>
          <NFormItem label="播报文本">
            <NInput v-model:value="model.broadcast_text" type="textarea" placeholder="请输入播报文本" :rows="3" />
          </NFormItem>
          <NFormItem label="播报次数">
            <NSelect v-model:value="model.broadcast_count" :options="broadcastCountOptions" placeholder="选择播报次数" />
          </NFormItem>
        </template>

        <!-- 定时配置 -->
        <NDivider title-placement="left">定时配置（可选）</NDivider>
        <NFormItem label="启用定时执行">
          <NSwitch v-model:value="model.schedule_enabled" />
        </NFormItem>
        <template v-if="model.schedule_enabled">
          <NGrid :cols="2" :x-gap="16">
            <NFormItemGi label="调度日期">
              <NDatePicker v-model:value="model.schedule_date" type="date" class="w-full" />
            </NFormItemGi>
            <NFormItemGi label="开始时间">
              <NTimePicker v-model:value="model.schedule_start_time" format="HH:mm" class="w-full" />
            </NFormItemGi>
          </NGrid>
          <NFormItem label="重复周期（未选择则不重复）">
            <NCheckboxGroup v-model:value="model.schedule_repeat_cycles">
              <NSpace>
                <NCheckbox v-for="opt in weekdayOptions" :key="opt.value" :value="opt.value" :label="opt.label" />
              </NSpace>
            </NCheckboxGroup>
          </NFormItem>
        </template>
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

<style scoped></style>
