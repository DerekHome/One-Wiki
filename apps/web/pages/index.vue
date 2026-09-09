<template>
  <div>
    <h1 class="text-2xl font-bold mb-6">知识库列表</h1>
    <div v-if="pending">加载中...</div>
    <div v-else-if="error">加载失败</div>
    <div v-else class="grid gap-4">
      <div v-for="item in knowledge" :key="item.id" class="p-4 bg-white rounded shadow">
        <h2 class="font-bold text-lg">{{ item.title }}</h2>
        <p class="text-gray-600">{{ item.summary }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const { pending, data: knowledge, error } = await useFetchApi<any[]>('/knowledge')
</script>
