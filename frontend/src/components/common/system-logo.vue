<template>
  <div class="app-logo">
    <svg width="100%" height="100%" viewBox="0 0 1000 1000" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="smilexCloudBody" x1="220" y1="200" x2="800" y2="840" gradientUnits="userSpaceOnUse">
          <stop offset="0" stop-color="var(--logo-color-300)" />
          <stop offset="0.5" stop-color="var(--logo-color-500)" />
          <stop offset="1" stop-color="var(--logo-color-700)" />
        </linearGradient>
      </defs>
      <!-- 云体:圆角底座 + 三处隆起 -->
      <g fill="url(#smilexCloudBody)">
        <rect x="160" y="440" width="680" height="380" rx="190" />
        <circle cx="320" cy="460" r="170" />
        <circle cx="680" cy="460" r="170" />
        <circle cx="500" cy="410" r="210" />
      </g>
      <!-- 笑脸:眼睛 + 微笑 -->
      <g fill="#ffffff">
        <circle cx="425" cy="600" r="32" />
        <circle cx="575" cy="600" r="32" />
      </g>
      <path d="M 395,665 Q 500,770 605,665" fill="none" stroke="#ffffff" stroke-width="34" stroke-linecap="round" />
    </svg>
  </div>
</template>

<style scoped>
.app-logo {
  --logo-color-300: rgb(var(--primary-300-color));
  --logo-color-400: rgb(var(--primary-400-color));
  --logo-color-500: rgb(var(--primary-500-color));
  --logo-color-600: rgb(var(--primary-600-color));
  --logo-color-700: rgb(var(--primary-700-color));
}
</style>
