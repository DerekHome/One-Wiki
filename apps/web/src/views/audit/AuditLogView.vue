<template>
  <div class="app-page max-w-6xl mx-auto px-4 lg:px-8 py-6 pb-12">
    <div class="mb-6">
        <h2 class="kh-title text-2xl">安全审计日志</h2>
      <p class="text-[var(--kh-text-muted)] text-sm mt-1">记录用户登录、空间创建、知识版本变更、附件传输与 Agent 访问全流程流水</p>
    </div>

    <el-card shadow="never" class="rounded-xl mb-6 p-4">
      <div class="flex gap-4">
        <el-input v-model="filterAction" placeholder="筛选操作动作 (如 login / create_knowledge)..." clearable class="w-64" />
        <el-input v-model="filterUsername" placeholder="筛选操作人用户名..." clearable class="w-64" />
        <el-button type="primary" @click="fetchLogs">查 询</el-button>
      </div>
    </el-card>

    <el-card shadow="never" class="rounded-xl" v-loading="loading">
      <el-table :data="logs" class="w-full" stripe>
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="username" label="操作人" width="120">
          <template #default="{ row }">
            <span class="font-medium text-[var(--kh-text-soft)]">{{ row.username || '匿名/系统' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="action" label="操作行为" width="160">
          <template #default="{ row }">
            <el-tag size="small">{{ row.action }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="resource" label="涉及资源" width="180" />
        <el-table-column prop="details" label="动作详情 (Payload)">
          <template #default="{ row }">
            <span class="text-xs text-[var(--kh-text-muted)] font-mono">{{ JSON.stringify(row.details) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="操作时间" width="180">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
      </el-table>

      <div class="flex justify-center mt-6">
        <el-pagination
          background
          layout="prev, pager, next"
          :total="total"
          :page-size="pageSize"
          v-model:current-page="currentPage"
          @current-change="fetchLogs"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { apiClient } from '../../api/client'

const logs = ref<any[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(15)
const loading = ref(false)

const filterAction = ref('')
const filterUsername = ref('')

async function fetchLogs() {
  loading.value = true
  try {
    const params: any = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    if (filterAction.value) params.action = filterAction.value
    if (filterUsername.value) params.username = filterUsername.value

    const res: any = await apiClient.get('/audit/', { params })
    logs.value = res.data?.items || []
    total.value = res.data?.total || 0
  } finally {
    loading.value = false
  }
}

function formatDate(val: string) {
  if (!val) return '-'
  return new Date(val).toLocaleString()
}

onMounted(() => {
  fetchLogs()
})
</script>
