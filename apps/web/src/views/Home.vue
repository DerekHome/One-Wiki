<template>
  <div>
    <h1 class="text-2xl font-bold mb-4">知识列表</h1>
    <el-table :data="knowledgeList" class="w-full">
      <el-table-column prop="title" label="标题" />
      <el-table-column prop="created_at" label="创建时间" />
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { apiClient } from '../api/client'
const knowledgeList = ref([])

onMounted(async () => {
    const res = await apiClient.get('/knowledge')
    knowledgeList.value = res.data
})
</script>
