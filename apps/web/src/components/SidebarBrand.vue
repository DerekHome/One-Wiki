<template>
  <div class="sidebar-brand" :class="{ 'sidebar-brand--compact': compact }">
    <div class="sidebar-brand__inner">
      <div class="brand-mark w-8 h-8 rounded-xl text-xs tracking-wider shrink-0">
        <span>KH</span>
      </div>
      <div class="sidebar-brand__copy">
        <div class="sidebar-brand__title">企业知识中心</div>
        <div class="sidebar-brand__subtitle">Knowledge Hub</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  compact?: boolean
}>(), {
  compact: false
})
</script>
