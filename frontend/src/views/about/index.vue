<script setup lang="ts">
import { computed } from 'vue';
import dayjs from 'dayjs';
import gitLog from 'virtual:smilex-git-log';
import SystemLogo from '@/components/common/system-logo.vue';
import { $t } from '@/locales';

/** 技术栈标签(专有名词,直接维护) */
const techStack = ['Vue 3', 'FastAPI', 'SQLAlchemy 2.0', 'PostgreSQL', 'Redis', 'NaiveUI', 'Vite 7', 'UnoCSS'];

/** 核心特性(文案走 i18n) */
const features = computed(() => [
  $t('page.about.feat1'),
  $t('page.about.feat2'),
  $t('page.about.feat3'),
  $t('page.about.feat4'),
  $t('page.about.feat5'),
  $t('page.about.feat6')
]);

function formatDate(date: string) {
  return dayjs(date).format('YYYY-MM-DD HH:mm');
}
</script>

<template>
  <NGrid :cols="24" :x-gap="16" :y-gap="16" responsive="screen" item-responsive>
    <!-- 左栏:项目介绍 -->
    <NGi span="24 m:9">
      <NCard :bordered="false" class="h-full card-wrapper">
        <div class="flex flex-col items-center gap-12px py-16px">
          <div class="size-80px">
            <SystemLogo />
          </div>
          <div class="text-22px font-600">SmileX-Fastapi-Cloud</div>
          <div class="text-center text-14px opacity-70">{{ $t('page.about.subtitle') }}</div>
        </div>
        <NDivider />
        <p class="text-14px leading-7 opacity-80">{{ $t('page.about.intro') }}</p>
        <div class="mt-20px">
          <div class="mb-10px font-500">{{ $t('page.about.techStackTitle') }}</div>
          <NSpace>
            <NTag v-for="tech in techStack" :key="tech" type="primary" size="small" round>{{ tech }}</NTag>
          </NSpace>
        </div>
        <div class="mt-20px">
          <div class="mb-10px font-500">{{ $t('page.about.featuresTitle') }}</div>
          <ul class="list-disc pl-20px text-14px leading-7 opacity-80">
            <li v-for="(feat, i) in features" :key="i">{{ feat }}</li>
          </ul>
        </div>
      </NCard>
    </NGi>

    <!-- 右栏:Git 提交历史 -->
    <NGi span="24 m:15">
      <NCard :bordered="false" class="h-full card-wrapper" :title="$t('page.about.gitHistory')">
        <template #header-extra>
          <span v-if="gitLog.available" class="text-12px opacity-60">
            {{ $t('page.about.commitsCount', { count: gitLog.commits.length }) }}
          </span>
        </template>
        <NEmpty v-if="!gitLog.available" :description="$t('page.about.gitUnavailable')" />
        <NScrollbar v-else style="max-height: calc(100vh - 220px)">
          <NTimeline>
            <NTimelineItem v-for="c in gitLog.commits" :key="c.hash" type="info">
              <template #header>
                <div class="flex items-center justify-between gap-8px">
                  <span class="font-500">{{ c.message }}</span>
                  <NTag size="tiny" :bordered="false">{{ c.shortHash }}</NTag>
                </div>
              </template>
              <div class="text-12px opacity-60">{{ c.author }} · {{ formatDate(c.date) }}</div>
            </NTimelineItem>
          </NTimeline>
        </NScrollbar>
      </NCard>
    </NGi>
  </NGrid>
</template>

<style scoped></style>
