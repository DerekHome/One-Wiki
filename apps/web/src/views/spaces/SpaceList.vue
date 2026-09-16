<template>
  <div class="app-page min-h-full">
  <div class="p-6 lg:p-8 max-w-7xl mx-auto">
    <!-- 顶栏标题与统计指标 -->
    <div class="flex flex-col lg:flex-row lg:justify-between lg:items-end gap-5 mb-7">
      <div>
        <div class="kh-chip mb-3">
          <el-icon :size="13"><FolderOpened /></el-icon>
          <span>KNOWLEDGE SPACES</span>
        </div>
        <h1 class="kh-title text-3xl">知识空间</h1>
        <p class="text-sm text-[var(--kh-text-muted)] mt-2 max-w-2xl">组织与隔离业务知识的核心工作区，支持细粒度权限管控与成员协作。</p>
      </div>
      <button
        @click="openCreateDialog"
        class="app-button app-button-primary px-4 py-2.5 cursor-pointer"
      >
        <el-icon :size="14"><Plus /></el-icon>
        <span>新建知识空间</span>
      </button>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-7">
      <div class="metric-card p-4">
        <div class="text-[11px] text-[var(--kh-text-muted)]">空间总数</div>
        <div class="text-2xl font-bold text-[var(--kh-text)] mt-1">{{ spaces.length }}</div>
      </div>
      <div class="metric-card p-4">
        <div class="text-[11px] text-[var(--kh-text-muted)]">公开空间</div>
        <div class="text-2xl font-bold text-[var(--kh-cyan)] mt-1">{{ publicSpaceCount }}</div>
      </div>
      <div class="metric-card p-4">
        <div class="text-[11px] text-[var(--kh-text-muted)]">私有空间</div>
        <div class="text-2xl font-bold text-[var(--kh-text)] mt-1">{{ privateSpaceCount }}</div>
      </div>
    </div>

    <!-- Linear 风格精细卡片网格 -->
    <div v-loading="loading">
      <div v-if="spaces.length > 0" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
        <div
          v-for="space in spaces"
          :key="space.id"
          class="linear-card p-5 flex flex-col justify-between min-h-52 cursor-pointer group"
          @click="enterSpace(space.id)"
        >
          <div>
            <div class="flex items-start justify-between gap-3 mb-4">
              <div class="flex items-center gap-3 min-w-0">
                <span class="w-10 h-10 kh-icon-tile shrink-0">
                  <el-icon :size="18"><FolderOpened /></el-icon>
                </span>
                <h3 class="font-semibold text-base text-[var(--kh-text)] truncate group-hover:text-[var(--kh-primary)] transition-colors">
                  {{ space.name }}
                </h3>
              </div>
              <span
                class="linear-badge text-[10px] shrink-0"
                :class="visibilityClass(space.visibility)"
              >
                {{ visibilityLabel(space.visibility) }}
              </span>
            </div>
            <p class="text-sm text-[var(--kh-text-muted)] line-clamp-3 leading-6">
              {{ space.description || '暂无详细描述信息' }}
            </p>
          </div>

          <div>
            <div class="grid grid-cols-2 gap-2 pt-4 mt-4 border-t border-[var(--kh-border)] text-[11px]">
              <div class="rounded-lg bg-[var(--kh-surface-soft)] border border-[var(--kh-border)] p-2">
                <div class="text-[var(--kh-text-dim)]">创建日期</div>
                <div class="font-medium text-[var(--kh-text-soft)] mt-0.5">{{ formatDate(space.created_at) }}</div>
              </div>
              <div class="rounded-lg bg-[var(--kh-surface-soft)] border border-[var(--kh-border)] p-2">
                <div class="text-[var(--kh-text-dim)]">空间编号</div>
                <div class="font-mono font-medium text-[var(--kh-text-soft)] mt-0.5">#{{ space.id }}</div>
              </div>
            </div>
            <div class="flex items-center justify-between text-xs text-[var(--kh-text-muted)] pt-4">
              <span class="inline-flex items-center gap-1.5">
                <el-icon :size="13"><Document /></el-icon>
                <span>进入后查看文档</span>
              </span>
              <span class="text-[var(--kh-primary)] font-semibold flex items-center gap-1 transition-transform group-hover:translate-x-0.5">
                进入
                <el-icon :size="13"><ArrowRight /></el-icon>
              </span>
            </div>
          </div>
        </div>
      </div>

      <el-empty v-else-if="!loading" description="尚未建立任何知识空间，点击右上角开始创建" />
    </div>

    <!-- 新建空间对话框 -->
    <el-dialog v-model="createDialog" title="创建新知识空间" width="460px">
      <el-form :model="form" label-position="top">
        <el-form-item label="空间名称" required>
          <el-input v-model="form.name" placeholder="例如：核心架构设计 / 研发制度" />
        </el-form-item>
        <el-form-item label="空间说明">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="描述此空间的知识定位与归档范围..." />
        </el-form-item>
        <el-form-item label="可见性级别">
          <el-radio-group v-model="form.visibility" class="flex flex-col gap-2">
            <el-radio label="internal">内部公开 (Internal - 企业全员默认只读)</el-radio>
            <el-radio label="private">严格私有 (Private - 仅显式授权成员可访问)</el-radio>
            <el-radio label="public">全员开放 (Public - 全员可见并检索)</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialog = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleCreate">立即创建</el-button>
      </template>
    </el-dialog>
  </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { apiClient } from '../../api/client'
import { ElMessage } from 'element-plus'
import { ArrowRight, Document, FolderOpened, Plus } from '@element-plus/icons-vue'

const router = useRouter()
const spaces = ref<any[]>([])
const loading = ref(false)
const submitting = ref(false)
const createDialog = ref(false)

const form = ref({
  name: '',
  description: '',
  visibility: 'internal'
})

const publicSpaceCount = computed(() => spaces.value.filter(item => item.visibility === 'public').length)
const privateSpaceCount = computed(() => spaces.value.filter(item => item.visibility === 'private').length)

function openCreateDialog() {
  form.value = { name: '', description: '', visibility: 'internal' }
  createDialog.value = true
}

async function fetchSpaces() {
  loading.value = true
  try {
    const res: any = await apiClient.get('/spaces/')
    spaces.value = res.data || []
  } finally {
    loading.value = false
  }
}

async function handleCreate() {
  if (!form.value.name.trim()) {
    ElMessage.warning('空间名称不能为空')
    return
  }
  submitting.value = true
  try {
    await apiClient.post('/spaces/', form.value)
    ElMessage.success('知识空间创建成功')
    createDialog.value = false
    fetchSpaces()
  } finally {
    submitting.value = false
  }
}

function enterSpace(id: number) {
  router.push(`/spaces/${id}`)
}

function formatDate(val: string) {
  if (!val) return '-'
  return new Date(val).toLocaleDateString()
}

function visibilityLabel(value: string) {
  const labels: Record<string, string> = {
    public: '公开',
    private: '私有',
    internal: '内部'
  }
  return labels[value] || value
}

function visibilityClass(value: string) {
  if (value === 'public') return 'text-[var(--kh-cyan)] bg-[rgba(94,234,212,0.08)] border-[rgba(94,234,212,0.22)]'
  if (value === 'private') return 'text-rose-300 bg-rose-950/40 border-rose-500/30'
  return 'text-[var(--kh-primary)] bg-[var(--kh-primary-soft)] border-[var(--kh-border)]'
}

onMounted(() => {
  fetchSpaces()
})
</script>
