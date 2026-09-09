<template>
  <div v-loading="loading" class="app-page space-detail flex flex-col min-h-full bg-white rounded-2xl border border-zinc-200 overflow-hidden">
    <!-- 层次 1：空间概览主栏 (Surface 1: 空间层级信息与空间级管理操作) -->
    <div class="px-4 lg:px-8 py-6 border-b border-zinc-200/80 bg-white flex flex-wrap gap-4 justify-between items-center shrink-0">
      <div class="flex items-center gap-4 min-w-0 flex-1 mr-6">
        <!-- 空间视觉锚点图标徽章 -->
        <div class="w-12 h-12 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center text-xl shrink-0">
          <el-icon><FolderOpened /></el-icon>
        </div>

        <div class="min-w-0">
          <div class="flex flex-wrap items-center gap-2.5">
            <h2 class="text-xl font-bold text-zinc-900 tracking-tight">{{ space?.name }}</h2>
            <span class="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-semibold bg-zinc-100 text-zinc-600 border border-zinc-200/80 capitalize">
              {{ space?.visibility === 'public' ? '公开' : space?.visibility === 'private' ? '私有' : '内部' }}
            </span>
          </div>
          <p class="text-sm text-zinc-500 mt-1 break-words">{{ space?.description || '在这里整理和共享团队知识' }}</p>
        </div>
      </div>

      <!-- 空间级操作按钮 -->
      <div class="flex items-center gap-2.5 shrink-0">
        <button
          @click="showMembersDrawer = true"
          class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-zinc-700 bg-white hover:bg-zinc-50 border border-zinc-200/90 rounded-md transition cursor-pointer shadow-2xs"
        >
          <el-icon :size="13" class="text-zinc-500"><User /></el-icon>
          <span>成员授权 ({{ members.length }})</span>
        </button>

        <button
          @click="createTopicDialog = true"
          class="inline-flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-medium text-zinc-800 bg-zinc-100 hover:bg-zinc-200/80 border border-zinc-200/80 rounded-md transition cursor-pointer"
        >
          <el-icon :size="13" class="text-zinc-600"><Plus /></el-icon>
          <span>新建专题</span>
        </button>
      </div>
    </div>

    <!-- 层次 2：当前专题工具栏 (Surface 2: 略带灰阶底色，清晰锚定当前专注的业务专题) -->
    <div class="px-4 lg:px-8 py-4 border-b border-zinc-200/70 bg-zinc-50/75 flex flex-wrap gap-4 justify-between items-center shrink-0">
      <div class="flex items-center gap-3 min-w-0 mr-4">
        <!-- 专题名称标识 -->
        <div class="inline-flex items-center gap-2 px-2.5 py-1 rounded-md bg-white border border-zinc-200/80 shadow-2xs shrink-0">
          <el-icon :size="14" class="text-blue-600"><FolderOpened /></el-icon>
          <span class="text-xs font-bold text-zinc-900">{{ currentTopicTitle }}</span>
        </div>

        <span class="text-[11px] font-medium text-blue-700 bg-blue-50 border border-blue-200/70 px-2 py-0.5 rounded-full shrink-0">
          {{ filteredKnowledgeList.length }} 篇文档
        </span>

        <span class="text-xs text-zinc-400 truncate max-w-lg hidden lg:inline">
          {{ currentTopicDescription }}
        </span>
      </div>

      <!-- 专题级动作栏：搜索 + 新建文档 + 删除专题 -->
      <div class="flex flex-wrap items-center gap-3 min-w-0">
        <el-input
          v-model="searchQuery"
          placeholder="在当前专题下过滤..."
          prefix-icon="Search"
          clearable
          size="small"
          class="space-filter"
        />

        <!-- 新建知识（鲜明高权重主按钮） -->
        <button
          @click="goToCreateKnowledge"
          class="inline-flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md transition shadow-xs cursor-pointer"
        >
          <el-icon :size="13"><Plus /></el-icon>
          <span>新建知识</span>
        </button>

        <!-- 删除专题（轻量次要破坏性操作） -->
        <button
          v-if="selectedTopicId !== null"
          @click="handleDeleteCurrentTopic"
          class="inline-flex items-center gap-1 px-2.5 py-1.5 text-xs text-zinc-400 hover:text-red-600 hover:bg-red-50/80 rounded-md transition cursor-pointer"
          title="删除当前专题"
        >
          <span>删除专题</span>
        </button>
      </div>
    </div>

    <!-- 层次 3：文档数据展示画布 (Surface 3: 纯平白底、精细数据表头与行交互) -->
    <div class="flex-1 min-w-0 px-4 lg:px-8 py-5 bg-white">
      <el-table
        v-if="filteredKnowledgeList.length > 0"
        :data="filteredKnowledgeList"
        class="w-full"
        stripe
        :header-cell-style="{ background: '#f8fafc', color: '#475569', fontSize: '12px', fontWeight: '600', padding: '10px 0' }"
        :row-style="{ fontSize: '13px' }"
      >
        <el-table-column prop="title" label="文档标题" min-width="280">
          <template #default="{ row }">
            <div class="flex items-center gap-2 py-0.5">
              <span v-if="row.source_type === 'file_import'" class="text-[10px] px-1.5 py-0.2 rounded bg-amber-50 text-amber-700 border border-amber-200/80 font-medium">
                导入
              </span>
              <button class="text-left font-medium text-zinc-900 hover:text-blue-600 hover:underline cursor-pointer" @click="goToKnowledge(row.id)">
                {{ row.title }}
              </button>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="content_type" label="格式" width="100">
          <template #default="{ row }">
            <span class="text-xs px-2 py-0.5 rounded bg-zinc-100 text-zinc-600 border border-zinc-200/80 font-mono">
              {{ row.content_type }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="标签" min-width="150">
          <template #default="{ row }">
            <span v-for="t in row.tags" :key="t" class="text-xs mr-1 text-zinc-500 bg-zinc-50 border border-zinc-200/70 px-1.5 py-0.5 rounded">
              #{{ t }}
            </span>
            <span v-if="!row.tags || row.tags.length === 0" class="text-zinc-300 text-xs">-</span>
          </template>
        </el-table-column>
        <el-table-column label="版本" width="90">
          <template #default="{ row }">
            <span class="text-xs text-zinc-400 font-mono">v{{ row.current_version_id || 1 }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="updated_at" label="最后更新" width="170">
          <template #default="{ row }">
            <span class="text-xs text-zinc-400">{{ formatDate(row.updated_at) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" align="right">
          <template #default="{ row }">
            <button class="text-xs font-medium text-blue-600 hover:text-blue-800 mr-3 cursor-pointer" @click="goToEdit(row.id)">编辑</button>
            <button class="text-xs font-medium text-red-500 hover:text-red-700 cursor-pointer" @click="deleteKnowledge(row.id)">删除</button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 空数据状态：精致指引 -->
      <div v-if="!loading && filteredKnowledgeList.length === 0" class="py-16 text-center">
        <div class="w-12 h-12 rounded-2xl bg-zinc-100 text-zinc-400 flex items-center justify-center mx-auto mb-3 text-xl">
          📑
        </div>
        <div class="text-sm font-semibold text-zinc-700 mb-1">{{ searchQuery ? '没有找到匹配的文档' : '当前专题下暂无知识文档' }}</div>
        <p class="text-xs text-zinc-400 mb-4 max-w-sm mx-auto">
          {{ searchQuery ? '试试其他关键词，或清除筛选查看全部文档。' : '创建第一篇文档，开始积累这个专题的知识。' }}
        </p>
        <button
          @click="searchQuery ? searchQuery = '' : goToCreateKnowledge()"
          class="app-button app-button-primary px-4 py-2 text-sm"
        >
          <el-icon :size="13"><Plus /></el-icon>
          <span>{{ searchQuery ? '清除筛选' : '新建第一篇文档' }}</span>
        </button>
      </div>
    </div>

    <!-- 新建专题弹窗 -->
    <el-dialog v-model="createTopicDialog" title="新建知识专题" width="min(460px, calc(100vw - 32px))">
      <el-form label-position="top">
        <el-form-item label="专题名称" required>
          <el-input v-model="newTopicName" placeholder="例如：车辆与转向架维保、通信信号" />
        </el-form-item>
        <el-form-item label="专题简介">
          <el-input
            v-model="newTopicDesc"
            type="textarea"
            :rows="3"
            placeholder="简要描述该专题收录的业务规范或技术资产..."
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createTopicDialog = false">取消</el-button>
        <el-button type="primary" @click="submitCreateTopic">创建专题</el-button>
      </template>
    </el-dialog>

    <!-- 成员与权限抽屉 -->
    <el-drawer v-model="showMembersDrawer" title="空间成员与权限授权" size="min(500px, 100vw)">
      <div class="flex justify-between items-center mb-4">
        <span class="text-xs text-zinc-500">已授权成员共 {{ members.length }} 人</span>
        <el-button v-if="auth.isAdmin" size="small" type="primary" @click="addMemberDialog = true">
          <el-icon class="mr-1"><Plus /></el-icon> 添加成员
        </el-button>
      </div>

      <el-table :data="members" class="w-full">
        <el-table-column prop="user.username" label="用户名" />
        <el-table-column prop="role" label="空间角色">
          <template #default="{ row }">
            <el-tag :type="row.role === 'owner' ? 'danger' : row.role === 'admin' ? 'warning' : row.role === 'editor' ? 'success' : 'info'" size="small">
              {{ row.role }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80" align="right">
          <template #default="{ row }">
            <el-button v-if="auth.isAdmin && row.role !== 'owner'" link type="danger" size="small" @click="removeMember(row.user_id)">移除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-drawer>

    <!-- 添加成员弹窗 -->
    <el-dialog v-model="addMemberDialog" title="添加成员授权" width="400px" append-to-body>
      <el-form label-position="top">
        <el-form-item label="用户 ID" required>
          <el-input v-model.number="memberUserId" placeholder="请输入用户 ID" />
        </el-form-item>
        <el-form-item label="赋予角色">
          <el-select v-model="memberRole" class="w-full">
            <el-option label="管理权限 (admin)" value="admin" />
            <el-option label="编辑权限 (editor)" value="editor" />
            <el-option label="只读权限 (viewer)" value="viewer" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addMemberDialog = false">取消</el-button>
        <el-button type="primary" @click="submitMember">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { apiClient } from '../../api/client'
import { ElMessage, ElMessageBox } from 'element-plus'
import { User, Plus, FolderOpened, Search } from '@element-plus/icons-vue'
import { useAuthStore } from '../../stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const spaceId = computed(() => Number(route.params.id))

const space = ref<any>(null)
const topics = ref<any[]>([])
const knowledgeList = ref<any[]>([])
const members = ref<any[]>([])
const loading = ref(false)

const selectedTopicId = ref<number | null>(
  route.query.topic_id ? Number(route.query.topic_id) : null
)

// 监听空间 ID 切换（如从地铁切换至火车），自动重新拉取数据
watch(
  () => route.params.id,
  (newId) => {
    if (newId) {
      selectedTopicId.value = route.query.topic_id ? Number(route.query.topic_id) : null
      loadData()
    }
  }
)

// 监听路由中专题参数的变化，支持左侧目录树直接联动切换
watch(
  () => route.query.topic_id,
  (newTopicId) => {
    selectedTopicId.value = newTopicId ? Number(newTopicId) : null
  }
)

const currentTopicTitle = computed(() => {
  if (selectedTopicId.value === null) return '全部知识'
  const t = topics.value.find(item => item.id === selectedTopicId.value)
  return t ? t.name : '全部知识'
})

const currentTopicDescription = computed(() => {
  if (selectedTopicId.value === null) return '展示该空间下的所有技术规程与知识文档。'
  const t = topics.value.find(item => item.id === selectedTopicId.value)
  return t?.description || '暂无专题简介。'
})

const filteredKnowledgeList = computed(() => {
  return knowledgeList.value.filter(item => {
    if (selectedTopicId.value !== null && item.topic_id !== selectedTopicId.value) {
      return false
    }
    if (searchQuery.value.trim()) {
      const q = searchQuery.value.trim().toLowerCase()
      const titleMatch = item.title?.toLowerCase().includes(q)
      const tagMatch = item.tags?.some((t: string) => t.toLowerCase().includes(q))
      return titleMatch || tagMatch
    }
    return true
  })
})

const searchQuery = ref('')
const showMembersDrawer = ref(false)
const addMemberDialog = ref(false)
const memberUserId = ref<number | null>(null)
const memberRole = ref('viewer')

async function submitMember() {
  if (!memberUserId.value) {
    ElMessage.warning('请输入用户 ID')
    return
  }
  try {
    await apiClient.post(`/spaces/${spaceId.value}/members`, {
      user_id: memberUserId.value,
      role: memberRole.value
    })
    ElMessage.success('成员授权成功')
    addMemberDialog.value = false
    memberUserId.value = null
    memberRole.value = 'viewer'
    const result: any = await apiClient.get(`/spaces/${spaceId.value}/members`)
    members.value = result.data || []
  } catch {}
}

async function removeMember(userId: number) {
  try {
    await ElMessageBox.confirm('确定移除该空间成员吗？', '确认操作', { type: 'warning' })
    await apiClient.delete(`/spaces/${spaceId.value}/members/${userId}`)
    ElMessage.success('成员已移除')
    members.value = members.value.filter(member => member.user_id !== userId)
  } catch {}
}

const createTopicDialog = ref(false)
const newTopicName = ref('')
const newTopicDesc = ref('')

async function loadData() {
  loading.value = true
  try {
    const id = spaceId.value
    const [sRes, kRes, mRes, tRes]: any = await Promise.all([
      apiClient.get(`/spaces/${id}`),
      apiClient.get(`/knowledge/?space_id=${id}`),
      apiClient.get(`/spaces/${id}/members`),
      apiClient.get(`/spaces/${id}/topics`)
    ])
    space.value = sRes.data
    knowledgeList.value = kRes.data || []
    members.value = mRes.data || []
    topics.value = tRes.data || []
  } catch (err: any) {
    console.error('加载空间数据失败', err)
  } finally {
    loading.value = false
  }
}

async function submitCreateTopic() {
  if (!newTopicName.value.trim()) {
    ElMessage.warning('请输入专题名称')
    return
  }
  try {
    const id = spaceId.value
    await apiClient.post(`/spaces/${id}/topics`, {
      name: newTopicName.value.trim(),
      description: newTopicDesc.value.trim()
    })
    ElMessage.success('专题创建成功')
    createTopicDialog.value = false
    newTopicName.value = ''
    newTopicDesc.value = ''
    const tRes: any = await apiClient.get(`/spaces/${id}/topics`)
    topics.value = tRes.data || []
  } catch (err: any) {
    ElMessage.error(err.response?.data?.message || '创建专题失败')
  }
}

async function handleDeleteCurrentTopic() {
  if (selectedTopicId.value === null) return
  const topic = topics.value.find(t => t.id === selectedTopicId.value)
  if (!topic) return
  try {
    const id = spaceId.value
    await ElMessageBox.confirm(`确定要删除专题「${topic.name}」吗？`, '提示', { type: 'warning' })
    await apiClient.delete(`/spaces/${id}/topics/${topic.id}`)
    ElMessage.success('专题已删除')
    selectedTopicId.value = null
    const tRes: any = await apiClient.get(`/spaces/${id}/topics`)
    topics.value = tRes.data || []
  } catch {}
}

function goToCreateKnowledge() {
  const id = spaceId.value
  if (selectedTopicId.value !== null) {
    router.push({ path: `/knowledge/create/${id}`, query: { topic_id: selectedTopicId.value } })
  } else {
    router.push(`/knowledge/create/${id}`)
  }
}

function goToKnowledge(id: number) {
  router.push(`/knowledge/${id}`)
}

function goToEdit(id: number) {
  router.push(`/knowledge/${id}/edit`)
}

async function deleteKnowledge(id: number) {
  try {
    await ElMessageBox.confirm('确定要删除该知识对象吗？', '提示', { type: 'warning' })
    await apiClient.delete(`/knowledge/${id}`)
    ElMessage.success('删除成功')
    loadData()
  } catch {}
}

function formatDate(val: string) {
  if (!val) return '-'
  return new Date(val).toLocaleString()
}

onMounted(() => {
  loadData()
})
</script>
