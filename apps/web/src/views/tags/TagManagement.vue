<template>
  <div class="app-page max-w-4xl mx-auto px-4 lg:px-8 py-6 pb-12">
    <div class="flex justify-between items-center mb-6">
      <div>
        <h2 class="kh-title text-2xl">企业标签池</h2>
        <p class="text-[var(--kh-text-muted)] text-sm mt-1">跨空间维护统一分类与多维索引标准</p>
      </div>
      <div class="flex gap-2">
        <el-input v-model="newTagName" placeholder="输入新标签名..." class="w-48" @keyup.enter="handleCreateTag" />
        <el-button type="primary" @click="handleCreateTag">添加标签</el-button>
      </div>
    </div>

    <el-card shadow="never" class="rounded-xl" v-loading="loading">
      <el-table :data="tags" class="w-full">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="标签名称">
          <template #default="{ row }">
            <el-tag>{{ row.name }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="120" align="right">
          <template #default="{ row }">
            <el-button link type="danger" @click="handleDeleteTag(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="tags.length === 0 && !loading" description="暂无标签" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { apiClient } from '../../api/client'
import { ElMessage, ElMessageBox } from 'element-plus'

const tags = ref<any[]>([])
const newTagName = ref('')
const loading = ref(false)

async function fetchTags() {
  loading.value = true
  try {
    const res: any = await apiClient.get('/tags/')
    tags.value = res.data || []
  } finally {
    loading.value = false
  }
}

async function handleCreateTag() {
  if (!newTagName.value.trim()) return
  try {
    await apiClient.post('/tags/', { name: newTagName.value.trim() })
    ElMessage.success('标签创建成功')
    newTagName.value = ''
    fetchTags()
  } catch {}
}

async function handleDeleteTag(id: number) {
  try {
    await ElMessageBox.confirm('确定要删除该标签吗？', '提示', { type: 'warning' })
    await apiClient.delete(`/tags/${id}`)
    ElMessage.success('标签已删除')
    fetchTags()
  } catch {}
}

function formatDate(val: string) {
  if (!val) return '-'
  return new Date(val).toLocaleDateString()
}

onMounted(() => {
  fetchTags()
})
</script>
