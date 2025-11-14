<template>
  <div class="page-header">
    <div class="page-header-content">
      <div class="page-header-info">
        <h1 class="page-header-title">{{ title }}</h1>
        <p v-if="subtitle" class="page-header-subtitle">{{ subtitle }}</p>
      </div>
      <div v-if="$slots.actions" class="page-header-actions">
        <slot name="actions"></slot>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  subtitle?: string
}>()
</script>

<style scoped lang="scss">
.page-header {
  margin-bottom: 24px;
  padding: 24px 0;
  border-bottom: 1px solid var(--el-border-color);

  &-content {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
  }

  &-info {
    flex: 1;
  }

  &-title {
    margin: 0;
    font-size: 24px;
    font-weight: 600;
    color: var(--el-text-color-primary);
    line-height: 1.3;
  }

  &-subtitle {
    margin: 8px 0 0;
    font-size: 14px;
    color: var(--el-text-color-secondary);
    line-height: 1.5;
  }

  &-actions {
    display: flex;
    gap: 12px;
    align-items: center;
  }
}
</style>
