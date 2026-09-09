<template>
  <div class="max-w-5xl mx-auto pb-12">
    <div class="mb-6">
      <h2 class="text-2xl font-bold text-slate-800">模块扩展中心</h2>
      <p class="text-slate-500 text-sm mt-1">微内核积木式架构：管理各类检索、解析与连接器模块生命周期</p>
    </div>

    <el-row :gutter="20" v-loading="loading">
      <el-col :xs="24" :sm="12" v-for="mod in modules" :key="mod.id" class="mb-5">
        <el-card shadow="hover" class="border border-slate-200 rounded-xl">
          <div class="flex justify-between items-start mb-3">
            <div>
              <h3 class="font-bold text-lg text-slate-800">{{ mod.name }}</h3>
              <span class="text-xs text-slate-400 font-mono">id: {{ mod.id }} | v{{ mod.version }}</span>
            </div>
            <el-tag :type="mod.status === 'enabled' ? 'success' : 'info'" size="small">
              {{ mod.status === 'enabled' ? '已启用' : '已停用' }}
            </el-tag>
          </div>

          <p class="text-sm text-slate-600 mb-4 min-h-[40px]">{{ mod.description }}</p>

          <div class="text-xs text-slate-500 mb-4 flex items-center justify-between border-t pt-3">
            <span>扩展点: <el-tag size="small" type="warning">{{ mod.extension_point }}</el-tag></span>
            <span>健康状态: <el-tag size="small" :type="mod.healthy ? 'success' : 'danger'">{{ mod.healthy ? '正常' : '异常' }}</el-tag></span>
          </div>

          <div class="flex justify-end gap-2 border-t pt-3">
            <el-button
              size="small"
              :type="mod.status === 'enabled' ? 'danger' : 'success'"
              plain
              @click="toggleModule(mod)"
            >
              {{ mod.status === 'enabled' ? '停用模块' : '启用模块' }}
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { apiClient } from '../../api/client'
import { ElMessage } from 'element-plus'

const modules = ref<any[]>([])
const loading = ref(false)

async function fetchModules() {
  loading.value = true
  try {
    const res: any = await apiClient.get('/modules/')
    modules.value = res.data || []
  } finally {
    loading.value = false
  }
}

async function toggleModule(mod: any) {
  const action = mod.status === 'enabled' ? 'disable' : 'enable'
  try {
    await apiClient.post(`/modules/${mod.id}/${action}`)
    ElMessage.success(`模块 ${mod.name} 已${action === 'enable' ? '启用' : '停用'}`)
    fetchModules()
  } catch {}
}

onMounted(() => {
  fetchModules()
})
</script>
