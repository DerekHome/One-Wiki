<template>
  <div v-loading="loading" class="max-w-5xl mx-auto pb-12">
    <div class="mb-4 flex items-center justify-between">
      <el-button link @click="$router.push(`/knowledge/${knowledgeId}`)">← 返回知识详情</el-button>
      <h2 class="text-xl font-bold text-slate-800">版本差异对比 (Version Diff)</h2>
      <div class="flex items-center gap-2">
        <span class="text-xs text-slate-500">对比版本:</span>
        <el-tag size="small" type="info">v{{ vFrom }}</el-tag>
        <span class="text-xs text-slate-400">vs</span>
        <el-tag size="small" type="primary">v{{ vTo }}</el-tag>
      </div>
    </div>

    <el-card shadow="never" class="border border-slate-200 rounded-xl mb-4 p-4">
      <h3 class="font-bold text-slate-700 mb-2">标题差异</h3>
      <div class="text-sm bg-slate-50 p-3 rounded border border-slate-100 font-mono">
        <div class="text-red-600">- 原标题 (v{{ vFrom }}): {{ diffData?.title_diff?.from }}</div>
        <div class="text-green-600">+ 新标题 (v{{ vTo }}): {{ diffData?.title_diff?.to }}</div>
      </div>
    </el-card>

    <el-card shadow="never" class="border border-slate-200 rounded-xl p-4">
      <h3 class="font-bold text-slate-700 mb-2">正文差异 (Unified Diff)</h3>
      <div class="bg-slate-900 text-slate-100 p-4 rounded-lg font-mono text-xs overflow-x-auto whitespace-pre leading-5">
        <div
          v-for="(line, idx) in diffData?.content_diff"
          :key="idx"
          :class="line.startsWith('+') ? 'text-green-400 bg-green-950/40' : line.startsWith('-') ? 'text-red-400 bg-red-950/40' : 'text-slate-400'"
        >
          {{ line }}
        </div>
        <div v-if="!diffData?.content_diff || diffData.content_diff.length === 0" class="text-slate-500">
          两个版本的正文完全一致。
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { apiClient } from '../../api/client'

const route = useRoute()
const knowledgeId = Number(route.params.id)
const vFrom = Number(route.query.v_from || 1)
const vTo = Number(route.query.v_to || 2)

const diffData = ref<any>(null)
const loading = ref(false)

async function fetchDiff() {
  loading.value = true
  try {
    const res: any = await apiClient.get(`/knowledge/${knowledgeId}/diff?v_from=${vFrom}&v_to=${vTo}`)
    diffData.value = res.data
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchDiff()
})
</script>
