<script setup lang="ts">
import { computed } from 'vue';
import { createReusableTemplate } from '@vueuse/core';
import { useThemeStore } from '@/store/modules/theme';
import { $t } from '@/locales';

defineOptions({
  name: 'CardData'
});

/** 统计卡片数据项 */
interface CardItem {
  key: string;
  title: string;
  value: number;
  color: {
    start: string;
    end: string;
  };
  icon: string;
}

const props = defineProps<{
  /** 用户总数 */
  userCount: number;
  /** 角色总数 */
  roleCount: number;
  /** 在线用户数 */
  onlineCount: number;
  /** 今日登录次数 */
  todayLoginCount: number;
}>();

/** 根据真实统计数据构造卡片配置 */
const cardData = computed<CardItem[]>(() => [
  {
    key: 'userCount',
    title: $t('page.home.userCount'),
    value: props.userCount,
    color: {
      start: '#ec4786',
      end: '#b955a4'
    },
    icon: 'ant-design:user-outlined'
  },
  {
    key: 'roleCount',
    title: $t('page.home.roleCount'),
    value: props.roleCount,
    color: {
      start: '#56cdf3',
      end: '#719de3'
    },
    icon: 'ant-design:team-outlined'
  },
  {
    key: 'onlineCount',
    title: $t('page.home.onlineCount'),
    value: props.onlineCount,
    color: {
      start: '#5acdb5',
      end: '#3ca370'
    },
    icon: 'ant-design:online-outlined'
  },
  {
    key: 'todayLoginCount',
    title: $t('page.home.todayLoginCount'),
    value: props.todayLoginCount,
    color: {
      start: '#fcbc25',
      end: '#f68057'
    },
    icon: 'ant-design:login-outlined'
  }
]);

interface GradientBgProps {
  gradientColor: string;
}

const [DefineGradientBg, GradientBg] = createReusableTemplate<GradientBgProps>();

const themeStore = useThemeStore();

/** 生成渐变背景色样式 */
function getGradientColor(color: CardItem['color']) {
  return `linear-gradient(to bottom right, ${color.start}, ${color.end})`;
}
</script>

<template>
  <NCard :bordered="false" size="small" class="card-wrapper">
    <!-- define component start: GradientBg -->
    <DefineGradientBg v-slot="{ $slots, gradientColor }">
      <div
        class="px-16px pb-4px pt-8px text-white"
        :style="{ backgroundImage: gradientColor, borderRadius: themeStore.themeRadius + 'px' }"
      >
        <component :is="$slots.default" />
      </div>
    </DefineGradientBg>
    <!-- define component end: GradientBg -->

    <NGrid cols="s:1 m:2 l:4" responsive="screen" :x-gap="16" :y-gap="16">
      <NGi v-for="item in cardData" :key="item.key">
        <GradientBg :gradient-color="getGradientColor(item.color)" class="flex-1">
          <h3 class="text-16px">{{ item.title }}</h3>
          <div class="flex justify-between pt-12px">
            <SvgIcon :icon="item.icon" class="text-32px" />
            <CountTo
              :start-value="0"
              :end-value="item.value"
              class="text-30px text-white dark:text-dark"
            />
          </div>
        </GradientBg>
      </NGi>
    </NGrid>
  </NCard>
</template>

<style scoped></style>
