<template>
  <div class="p-4">
    <h1 class="text-2xl font-bold mb-4">空间管理</h1>
    <div class="grid gap-4">
      <div v-for="space in spaces" :key="space.id" class="p-4 bg-white rounded shadow">
        {{ space.name }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const { data: spaces } = await useFetchApi<any[]>('/spaces')
</script>
