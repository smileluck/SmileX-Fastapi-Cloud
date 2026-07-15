// @unocss-include
import { getColorPalette, getRgb } from '@sa/color';
import { DARK_CLASS } from '@/constants/app';
import { localStg } from '@/utils/storage';
import { toggleHtmlClass } from '@/utils/common';
import { $t } from '@/locales';

export function setupLoading() {
  const themeColor = localStg.get('themeColor') || '#646cff';
  const darkMode = localStg.get('darkMode') || false;
  const palette = getColorPalette(themeColor);

  const { r, g, b } = getRgb(themeColor);

  const primaryColor = `--primary-color: ${r} ${g} ${b}`;

  const svgCssVars = Array.from(palette.entries())
    .map(([key, value]) => `--logo-color-${key}: ${value}`)
    .join(';');

  const cssVars = `${primaryColor}; ${svgCssVars}`;

  if (darkMode) {
    toggleHtmlClass(DARK_CLASS).add();
  }

  const loadingClasses = [
    'left-0 top-0',
    'left-0 bottom-0 animate-delay-500',
    'right-0 top-0 animate-delay-1000',
    'right-0 bottom-0 animate-delay-1500'
  ];

  const dot = loadingClasses
    .map(item => {
      return `<div class="absolute w-16px h-16px bg-primary rounded-8px animate-pulse ${item}"></div>`;
    })
    .join('\n');

  const loading = `
<div class="fixed-center flex-col bg-layout" style="${cssVars}">
  <div class="w-128px h-128px">
    ${getLogoSvg()}
  </div>
  <div class="w-56px h-56px my-36px">
    <div class="relative h-full animate-spin">
      ${dot}
    </div>
  </div>
  <h2 class="text-28px font-500 text-primary">${$t('system.title')}</h2>
</div>`;

  const app = document.getElementById('app');

  if (app) {
    app.innerHTML = loading;
  }
}

function getLogoSvg() {
  const logoSvg = `<svg
        width="100%"
        height="100%"
        viewBox="0 0 1000 1000"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          <linearGradient id="smilexCloudBody" x1="220" y1="200" x2="800" y2="840" gradientUnits="userSpaceOnUse">
            <stop offset="0" stop-color="var(--logo-color-300)" />
            <stop offset="0.5" stop-color="var(--logo-color-500)" />
            <stop offset="1" stop-color="var(--logo-color-700)" />
          </linearGradient>
        </defs>
        <g fill="url(#smilexCloudBody)">
          <rect x="160" y="440" width="680" height="380" rx="190" />
          <circle cx="320" cy="460" r="170" />
          <circle cx="680" cy="460" r="170" />
          <circle cx="500" cy="410" r="210" />
        </g>
        <g fill="#ffffff">
          <circle cx="425" cy="600" r="32" />
          <circle cx="575" cy="600" r="32" />
        </g>
        <path d="M 395,665 Q 500,770 605,665" fill="none" stroke="#ffffff" stroke-width="34" stroke-linecap="round" />
      </svg>
  `;

  return logoSvg;
}
