<template>
  <div
    v-loading="loading"
    class="app-page editor-page max-w-5xl mx-auto px-4 py-6 lg:px-8 pb-12 relative"
    @dragenter.prevent="handleDragEnter"
    @dragover.prevent="handleDragOver"
    @dragleave.prevent="handleDragLeave"
    @drop.prevent="handleFileDrop"
  >
    <!-- 全屏拖拽吸附遮罩 (Linear / Notion 动效) -->
    <transition name="el-fade-in">
      <div
        v-if="isDragging"
        class="fixed inset-0 z-50 bg-blue-600/10 backdrop-blur-xs flex items-center justify-center select-none pointer-events-none"
      >
        <div class="bg-white p-8 rounded-2xl border-2 border-dashed border-blue-500 shadow-2xl flex flex-col items-center">
          <div class="text-5xl mb-3">📥</div>
          <h3 class="text-lg font-bold text-zinc-900">松开鼠标，即可自动导入并解析</h3>
          <p class="text-xs text-zinc-500 mt-1">支持 .md、.markdown、.html、.htm，将自动提炼文章标题与正文</p>
        </div>
      </div>
    </transition>

    <div class="mb-6">
      <p class="text-sm font-medium text-blue-600 mb-2">知识创作</p>
      <h1 class="text-3xl font-bold tracking-tight text-zinc-900">{{ isEdit ? '编辑知识' : '记录新的知识' }}</h1>
      <p class="text-sm text-zinc-500 mt-2">专注内容，让经验成为可以共享的知识。</p>
    </div>
    <div class="editor-actions mb-4 flex flex-wrap gap-3 items-center justify-between sticky top-0 z-20 bg-white/95 border border-zinc-200 rounded-xl p-3">
      <el-button link @click="$router.back()">← 取消返回</el-button>
      <div class="hidden xl:flex items-center gap-2">
        <span class="text-xs text-zinc-400 bg-zinc-100 px-2.5 py-1 rounded-full border border-zinc-200 flex items-center gap-1.5">
          <span>💡</span>
          <span>支持将本地 .md / .html 文件直接拖拽至此页面自动填充</span>
        </span>
      </div>
      <el-button type="primary" size="large" :loading="saving" @click="saveKnowledge">
        {{ isEdit ? '更新发布新版本' : '正式发布' }}
      </el-button>
    </div>

    <div class="metric-card p-5 lg:p-8 mb-4 relative" :class="{ 'border-blue-500 bg-blue-50/20': isDragging }">
      <el-form label-position="top">
        <el-form-item label="知识标题" required>
          <el-input v-model="form.title" size="large" placeholder="请输入知识标题或拖拽文件自动解析..." />
        </el-form-item>

        <details class="editor-metadata mb-6 rounded-xl border border-zinc-200 bg-zinc-50/60 p-4" :open="!isEdit">
          <summary class="cursor-pointer text-sm font-medium text-zinc-700">分类与版本信息 <span class="text-xs font-normal text-zinc-500 ml-2">空间、类型、标签{{ isEdit ? '与变更说明' : '' }}</span></summary>
        <el-row :gutter="20" class="mt-4">
          <el-col :xs="24" :sm="12">
            <el-form-item label="所属空间" required>
              <el-select v-model="form.space_id" placeholder="选择归属空间" class="w-full" :disabled="isEdit">
                <el-option v-for="s in spaces" :key="s.id" :label="s.name" :value="s.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item label="知识类型">
              <el-select v-model="form.knowledge_type" class="w-full">
                <el-option label="技术文档 (article)" value="article" />
                <el-option label="制度规范 (policy)" value="policy" />
                <el-option label="常见问答 (faq)" value="faq" />
                <el-option label="技术备忘 (note)" value="note" />
                <el-option label="导入文档 (document)" value="document" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="标签分类 (支持手动输入后回车)">
          <el-select
            v-model="form.tags"
            multiple
            filterable
            allow-create
            default-first-option
            placeholder="绑定标签分类"
            class="w-full"
          />
        </el-form-item>

        <el-form-item label="变更说明 (本次版本快照日志)" v-if="isEdit">
          <el-input v-model="form.change_summary" placeholder="简述本次修改内容，如：更新第 3 节系统配置" />
        </el-form-item>

        </details>

        <el-form-item label="知识正文" required>
          <div class="relative w-full">
            <el-input
              v-model="form.content"
              type="textarea"
              :rows="18"
              placeholder="# 章节标题&#10;&#10;输入正文内容，或直接将电脑中的 .md / .html 文件拖拽至此框内..."
              class="editor-content font-mono text-sm leading-relaxed"
            />
          </div>
        </el-form-item>
        <div class="flex flex-wrap justify-between gap-2 text-xs text-zinc-500" aria-live="polite">
          <span>支持 Markdown / HTML，也可拖入本地文件</span>
          <span>{{ form.content.length.toLocaleString() }} 字符 · {{ saving ? '正在保存…' : '点击发布后保存' }}</span>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { apiClient } from '../../api/client'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()

const isEdit = computed(() => route.name === 'KnowledgeEdit')
const knowledgeId = route.params.id ? Number(route.params.id) : null
const defaultSpaceId = route.params.spaceId ? Number(route.params.spaceId) : null

const spaces = ref<any[]>([])
const loading = ref(false)
const saving = ref(false)
const isDragging = ref(false)

const form = ref({
  title: '',
  content: '',
  space_id: defaultSpaceId,
  knowledge_type: 'article',
  tags: [] as string[],
  change_summary: ''
})

let dragCounter = 0

function handleDragEnter(e: DragEvent) {
  dragCounter++
  if (e.dataTransfer?.types?.includes('Files')) {
    isDragging.value = true
  }
}

function handleDragOver(e: DragEvent) {
  if (e.dataTransfer?.types?.includes('Files')) {
    isDragging.value = true
  }
}

function handleDragLeave(e: DragEvent) {
  dragCounter--
  if (dragCounter <= 0) {
    isDragging.value = false
    dragCounter = 0
  }
}

async function handleFileDrop(e: DragEvent) {
  isDragging.value = false
  dragCounter = 0
  const files = e.dataTransfer?.files
  if (!files || files.length === 0) return

  const file = files[0]
  const ext = file.name.substring(file.name.lastIndexOf('.')).toLowerCase()

  if (!['.md', '.markdown', '.html', '.htm'].includes(ext)) {
    ElMessage.warning('仅支持拖拽导入 .md、.markdown、.html、.htm 文件')
    return
  }

  const reader = new FileReader()
  reader.onload = (event) => {
    const rawText = event.target?.result as string
    if (!rawText) return

    let title = ''
    const baseName = file.name.replace(/\.[^/.]+$/, '')

    if (['.md', '.markdown'].includes(ext)) {
      // 提取 Markdown 首个 # 标题
      const match = rawText.match(/^\s*#\s+(.+)$/m)
      title = match ? match[1].trim() : baseName
      form.value.content = rawText
      form.value.knowledge_type = 'article'
      if (!form.value.tags.includes('Markdown')) form.value.tags.push('Markdown')
    } else {
      // 提取 HTML title 或 h1
      const matchTitle = rawText.match(/<title[^>]*>([^<]+)<\/title>/i)
      const matchH1 = rawText.match(/<h1[^>]*>([^<]+)<\/h1>/i)
      title = matchTitle ? matchTitle[1].trim() : (matchH1 ? matchH1[1].trim() : baseName)
      form.value.content = rawText
      form.value.knowledge_type = 'document'
      if (!form.value.tags.includes('HTML')) form.value.tags.push('HTML')
    }

    form.value.title = title
    if (!form.value.tags.includes('文件导入')) form.value.tags.push('文件导入')
    ElMessage.success(`已自动解析并导入《${file.name}》的标题与内容！`)
  }
  reader.readAsText(file, 'utf-8')
}

async function fetchSpaces() {
  const res: any = await apiClient.get('/spaces/')
  spaces.value = res.data || []
  if (!form.value.space_id && spaces.value.length > 0) {
    form.value.space_id = spaces.value[0].id
  }
}

async function fetchKnowledge() {
  if (!isEdit.value || !knowledgeId) return
  loading.value = true
  try {
    const res: any = await apiClient.get(`/knowledge/${knowledgeId}`)
    const k = res.data
    form.value = {
      title: k.title,
      content: k.content,
      space_id: k.space_id,
      knowledge_type: k.knowledge_type,
      tags: k.tags || [],
      change_summary: ''
    }
  } finally {
    loading.value = false
  }
}

async function saveKnowledge() {
  if (!form.value.title.trim()) {
    ElMessage.warning('知识标题不能为空')
    return
  }
  if (!form.value.space_id) {
    ElMessage.warning('请选择知识所属空间')
    return
  }
  if (!form.value.content.trim()) {
    ElMessage.warning('知识正文不能为空')
    return
  }

  saving.value = true
  try {
    if (isEdit.value) {
      await apiClient.put(`/knowledge/${knowledgeId}`, form.value)
      ElMessage.success('更新成功，已自动生成新版本快照')
      router.push(`/knowledge/${knowledgeId}`)
    } else {
      const res: any = await apiClient.post('/knowledge/', form.value)
      ElMessage.success('发布成功，已生成首发版本 v1')
      router.push(`/knowledge/${res.data.id}`)
    }
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  fetchSpaces()
  fetchKnowledge()
})
</script>
