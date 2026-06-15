# 机器人参数配置选择机器人布局调整

## 需求描述

将参数配置中的“行走速度设置”和“电量报警阈值”Tab 从表格批量编辑布局调整为先下拉选择机器人，再读取所选机器人的当前配置并修改保存。

## 状态

已完成

## 涉及范围

### 后端

复用现有机器人管理详情与更新接口，无新增后端接口。

### 前端

- 参数配置页行走速度设置 Tab
- 参数配置页电量报警阈值 Tab
- 复用机器人列表、机器人详情、机器人更新 API

## 约束与备注

- 机器人选择使用下拉选择方式。
- 选择机器人后需读取该机器人最新配置，不仅依赖列表中的缓存值。
- 保存时仅提交当前 Tab 对应配置字段。

## 相关文件

- `frontend/src/views/settings/modules/walking-speed-tab.vue`
- `frontend/src/views/settings/modules/battery-threshold-tab.vue`
- `frontend/src/service/api/robot.ts`

## 记录日期

2026-06-11
