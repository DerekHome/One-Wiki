<template>
  <div v-loading="loading" class="h-full flex overflow-hidden app-page">
    <!-- 中间：Notion 沉浸式正文阅读区 -->
    <div class="flex-1 overflow-y-auto px-5 lg:px-8 py-8 lg:py-10">
      <div class="max-w-4xl mx-auto">
        <!-- 顶部面包屑与快捷返回 -->
        <div class="flex items-center justify-between text-xs text-[var(--kh-text-muted)] mb-8">
          <button
            @click="$router.push(`/spaces/${knowledge?.space_id}`)"
            class="app-button app-button-ghost px-3 py-2"
          >
            <el-icon :size="13"><Back /></el-icon>
            <span>返回空间目录</span>
          </button>
          <div class="flex items-center gap-2">
            <span class="kh-chip">
              v{{ knowledge?.current_version_id || 1 }}
            </span>
            <span class="text-[var(--kh-text-dim)]">·</span>
            <span>更新于 {{ formatDate(knowledge?.updated_at) }}</span>
          </div>
        </div>

        <!-- Notion 风格文档标题区 -->
        <div class="linear-card p-6 lg:p-7 mb-6">
          <div class="flex items-start justify-between gap-5">
            <div class="min-w-0">
              <div class="w-12 h-12 kh-icon-tile mb-4">
                <el-icon :size="23"><Document /></el-icon>
              </div>
              <h1 class="kh-title text-3xl leading-tight">
                {{ knowledge?.title }}
              </h1>
            </div>
            <div class="hidden sm:flex items-center gap-2 shrink-0">
              <button @click="goToEdit" class="app-button app-button-primary px-3.5 py-2">
                <el-icon :size="14"><EditPen /></el-icon>
                <span>编辑</span>
              </button>
              <el-dropdown trigger="click" @command="handleMoreCommand">
                <button class="app-button app-button-ghost px-2.5 py-2">
                  <el-icon :size="15"><MoreFilled /></el-icon>
                </button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="diff" :disabled="versions.length < 2">版本对比</el-dropdown-item>
                    <el-dropdown-item command="delete" divided>删除文档</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>

          <!-- Notion 风格紧凑属性元数据条 -->
          <div class="mt-6 pt-5 border-t border-[var(--kh-border)] grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs text-[var(--kh-text-muted)]">
            <div class="flex items-center gap-2">
              <span class="text-[var(--kh-text-dim)]">知识类型</span>
              <span class="font-medium text-[var(--kh-text-soft)] capitalize">{{ knowledge?.knowledge_type }}</span>
            </div>
            <div class="flex items-center gap-2">
              <span class="text-[var(--kh-text-dim)]">来源格式</span>
              <span class="font-medium text-[var(--kh-text-soft)] uppercase font-mono text-[11px]">{{ knowledge?.content_type }}</span>
            </div>
            <div class="flex items-center gap-1.5 flex-wrap" v-if="knowledge?.tags?.length">
              <span class="text-[var(--kh-text-dim)]">标签</span>
              <span
                v-for="t in knowledge.tags"
                :key="t"
                class="kh-chip"
              >
                #{{ t }}
              </span>
            </div>
          </div>
        </div>

        <!-- Notion 风格正文排版 -->
        <article class="linear-card notion-prose p-6 lg:p-8">
          <div v-html="renderedContent"></div>
        </article>

        <!-- 底部元数据与快捷操作 -->
        <div class="mt-8 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 text-xs text-[var(--kh-text-muted)]">
          <div>知识唯一标识: <span class="font-mono text-[var(--kh-text-soft)]">#{{ knowledge?.id }}</span></div>
          <div class="flex items-center gap-3">
            <button @click="goToEdit" class="text-[var(--kh-primary)] hover:text-[#8cc5ff] font-semibold transition-colors">编辑此文档</button>
            <button @click="handleDelete" class="text-rose-500 hover:text-rose-700 font-medium transition-colors">删除文档</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧：GitBook 风格目录与版本/附件抽屉栏 -->
    <aside class="w-80 bg-[var(--kh-surface-soft)] border-l border-[var(--kh-border)] p-5 overflow-y-auto shrink-0 hidden lg:block select-none">
      <div class="space-y-6">
        <!-- 快捷操作按钮组 (Linear 风格) -->
        <div class="flex items-center gap-2">
          <button
            @click="goToEdit"
            class="app-button app-button-primary flex-1 px-3 py-2"
          >
            <el-icon :size="14"><EditPen /></el-icon>
            <span>编辑文档</span>
          </button>
          <button
            @click="goToDiff"
            :disabled="versions.length < 2"
            class="app-button app-button-ghost px-3 py-2 disabled:opacity-40"
          >
            版本对比
          </button>
        </div>

        <!-- 版本历史记录 -->
        <div class="linear-card p-4">
          <div class="text-[11px] font-semibold text-[var(--kh-text-dim)] uppercase tracking-wider mb-3 font-mono">版本历史</div>
          <div class="space-y-2">
            <div
              v-for="v in versions"
              :key="v.id"
              class="p-2.5 rounded-lg border text-xs transition-colors"
              :class="v.version_number === knowledge?.current_version_id ? 'border-[var(--kh-border-strong)] bg-[var(--kh-primary-soft)] shadow-sm' : 'border-[var(--kh-border)] hover:border-[var(--kh-border-strong)]'"
            >
              <div class="flex justify-between items-center mb-1">
                <span class="font-semibold text-[var(--kh-text)]">v{{ v.version_number }}</span>
                <span class="text-[10px] text-[var(--kh-text-dim)]">{{ formatDate(v.created_at) }}</span>
              </div>
              <div class="text-[var(--kh-text-muted)] text-[11px] truncate">{{ v.change_summary || '常规修改' }}</div>
              <div class="mt-2 flex justify-end" v-if="v.version_number !== knowledge?.current_version_id">
                <button
                  @click="restoreVersion(v.version_number)"
                  class="text-[11px] text-amber-600 hover:text-amber-700 font-medium"
                >
                  回滚至此版
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 附件清单 -->
        <div class="linear-card p-4">
          <div class="flex justify-between items-center mb-2">
            <span class="text-[11px] font-semibold text-[var(--kh-text-dim)] uppercase tracking-wider font-mono">关联附件</span>
            <el-upload action="#" :http-request="handleUploadAttachment" :show-file-list="false">
              <button class="text-[11px] text-[var(--kh-primary)] hover:text-[#8cc5ff] font-medium">+ 上传</button>
            </el-upload>
          </div>
          <div class="space-y-1.5">
            <div
              v-for="a in attachments"
              :key="a.id"
              class="flex items-center justify-between p-2 rounded-md hover:bg-[var(--kh-fill)] text-xs text-[var(--kh-text-soft)] group border border-transparent hover:border-[var(--kh-border)] transition-colors"
            >
              <span class="truncate max-w-[140px]" :title="a.filename">{{ a.filename }}</span>
              <div class="flex items-center gap-2">
                <button @click="downloadAttachment(a.id)" class="text-[var(--kh-primary)] hover:text-[#8cc5ff] text-[11px]">下载</button>
                <button @click="deleteAttachment(a.id)" class="text-rose-500 hover:text-rose-700 text-[11px] opacity-0 group-hover:opacity-100 transition-opacity">×</button>
              </div>
            </div>
            <div v-if="!attachments.length" class="text-xs text-[var(--kh-text-dim)] py-2 italic text-center">暂无附件</div>
          </div>
        </div>
      </div>
    </aside>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { apiClient } from '../../api/client'
import { ElMessage, ElMessageBox } from 'element-plus'
import { marked } from 'marked'
import { sanitizeHtml } from '../../utils/sanitize'
import { Back, Document, EditPen, MoreFilled } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const knowledgeId = Number(route.params.id)

const knowledge = ref<any>(null)
const versions = ref<any[]>([])
const attachments = ref<any[]>([])
const loading = ref(false)

// 配置 marked 解析规则
marked.setOptions({
  gfm: true,
  breaks: true
})

const renderedContent = computed(() => {
  if (!knowledge.value?.content) return ''
  const text = knowledge.value.content
  if (knowledge.value.content_type === 'html') {
    return sanitizeHtml(text)
  }
  // 使用专业 Markdown 引擎解析粗体、无序列表、代码块与表格
  try {
    return sanitizeHtml(marked.parse(text) as string)
  } catch (err) {
    console.error('Markdown 解析失败', err)
    return sanitizeHtml(text)
  }
})

async function fetchKnowledge() {
  loading.value = true
  try {
    const [kRes, vRes, aRes]: any = await Promise.all([
      apiClient.get(`/knowledge/${knowledgeId}`),
      apiClient.get(`/knowledge/${knowledgeId}/versions`),
      apiClient.get(`/attachments/knowledge/${knowledgeId}`)
    ])
    knowledge.value = kRes.data
    versions.value = vRes.data || []
    attachments.value = aRes.data || []
  } finally {
    loading.value = false
  }
}

function goToEdit() {
  router.push(`/knowledge/${knowledgeId}/edit`)
}

function goToDiff() {
  if (versions.value.length >= 2) {
    const vFrom = versions.value[1].version_number
    const vTo = versions.value[0].version_number
    router.push(`/knowledge/${knowledgeId}/diff?v_from=${vFrom}&v_to=${vTo}`)
  }
}

function handleMoreCommand(command: string) {
  if (command === 'diff') {
    goToDiff()
    return
  }
  if (command === 'delete') {
    handleDelete()
  }
}

async function restoreVersion(versionNum: number) {
  try {
    await ElMessageBox.confirm(`确定要将文档内容回滚到版本 v${versionNum} 吗？系统将自动创建新版本。`, '确认回滚', { type: 'warning' })
    await apiClient.post(`/knowledge/${knowledgeId}/restore/${versionNum}`)
    ElMessage.success('历史版本恢复成功')
    fetchKnowledge()
  } catch {}
}

async function handleDelete() {
  try {
    await ElMessageBox.confirm('确定要彻底删除该文档吗？', '删除提示', { type: 'error' })
    await apiClient.delete(`/knowledge/${knowledgeId}`)
    ElMessage.success('文档已删除')
    router.push(`/spaces/${knowledge.value.space_id}`)
  } catch {}
}

async function handleUploadAttachment(options: any) {
  const formData = new FormData()
  formData.append('file', options.file)
  try {
    await apiClient.post(`/attachments/${knowledgeId}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    ElMessage.success('附件上传成功')
    const aRes: any = await apiClient.get(`/attachments/knowledge/${knowledgeId}`)
    attachments.value = aRes.data || []
  } catch {}
}

async function downloadAttachment(id: number) {
  try {
    const response: any = await apiClient.get(`/attachments/${id}/download`, { responseType: 'blob' })
    const blob = response.data instanceof Blob ? response.data : new Blob([response.data])
    const disposition = response.headers?.['content-disposition'] || ''
    const encoded = disposition.match(/filename\*=UTF-8''([^;]+)/i)?.[1]
    const plain = disposition.match(/filename="?([^";]+)"?/i)?.[1]
    const filename = encoded ? decodeURIComponent(encoded) : (plain || 'attachment')
    const url = URL.createObjectURL(blob)
    const anchor = document.createElement('a')
    anchor.href = url
    anchor.download = filename
    anchor.click()
    URL.revokeObjectURL(url)
  } catch {}
}

async function deleteAttachment(id: number) {
  await apiClient.delete(`/attachments/${id}`)
  ElMessage.success('附件已删除')
  const aRes: any = await apiClient.get(`/attachments/knowledge/${knowledgeId}`)
  attachments.value = aRes.data || []
}

function formatDate(val: string) {
  if (!val) return '-'
  return new Date(val).toLocaleDateString()
}

onMounted(() => {
  fetchKnowledge()
})
</script>

<style scoped>
:deep(.notion-prose) {
  color: var(--kh-text-soft);
  line-height: 1.75;
  font-size: 14px;
}

:deep(.notion-prose h1) {
  font-size: 22px;
  font-weight: 700;
  color: var(--kh-text);
  margin-top: 24px;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--kh-border);
}

:deep(.notion-prose h2) {
  font-size: 17px;
  font-weight: 700;
  color: var(--kh-text);
  margin-top: 20px;
  margin-bottom: 10px;
  padding-bottom: 6px;
  border-bottom: 1px solid var(--kh-border);
}

:deep(.notion-prose h3) {
  font-size: 15px;
  font-weight: 600;
  color: var(--kh-text);
  margin-top: 16px;
  margin-bottom: 8px;
}

:deep(.notion-prose p) {
  margin-top: 8px;
  margin-bottom: 8px;
}

:deep(.notion-prose ul) {
  list-style-type: disc;
  padding-left: 22px;
  margin-top: 8px;
  margin-bottom: 8px;
}

:deep(.notion-prose ol) {
  list-style-type: decimal;
  padding-left: 22px;
  margin-top: 8px;
  margin-bottom: 8px;
}

:deep(.notion-prose li) {
  margin-top: 4px;
  margin-bottom: 4px;
}

:deep(.notion-prose strong) {
  font-weight: 700;
  color: var(--kh-text);
}

:deep(.notion-prose code) {
  font-family: var(--font-mono);
  font-size: 12px;
  background-color: var(--kh-primary-soft);
  color: #1d4ed8;
  padding: 2px 6px;
  border-radius: 4px;
  border: 1px solid #dbeafe;
}

:deep(.notion-prose pre) {
  background-color: #18181b;
  color: #f4f4f5;
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
  font-size: 12px;
  margin-top: 16px;
  margin-bottom: 16px;
}

:deep(.notion-prose blockquote) {
  border-left: 3px solid var(--kh-primary);
  padding-left: 14px;
  color: var(--kh-text-muted);
  background-color: var(--kh-fill);
  margin-top: 12px;
  margin-bottom: 12px;
  padding-top: 4px;
  padding-bottom: 4px;
  border-radius: 0 4px 4px 0;
}

:deep(.notion-prose table) {
  width: 100%;
  border-collapse: collapse;
  margin-top: 16px;
  margin-bottom: 16px;
  font-size: 13px;
}

:deep(.notion-prose th),
:deep(.notion-prose td) {
  border: 1px solid var(--kh-border);
  padding: 8px 12px;
  text-align: left;
}

:deep(.notion-prose th) {
  background-color: #f4f4f5;
  font-weight: 600;
  color: var(--kh-text-soft);
}
</style>
