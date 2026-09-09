<template>
  <div class="h-screen flex bg-[var(--kh-bg)] overflow-hidden text-zinc-900 font-sans antialiased">
    <!-- 极简目录树侧边栏 (层次 0：灰度底色，衬托主内容画布) -->
    <aside class="w-64 soft-panel border-r border-zinc-200/80 flex flex-col justify-between select-none z-20 shrink-0">
      <div class="flex flex-col h-full overflow-hidden">
        <!-- 工作空间标题栏 -->
        <div class="h-14 px-4 border-b border-zinc-200/70 flex items-center justify-between bg-white/70">
          <div class="flex items-center gap-2.5">
            <div class="brand-mark w-8 h-8 rounded-xl font-bold text-xs tracking-wider">
              <span>KH</span>
            </div>
            <div>
              <div class="font-semibold text-sm text-zinc-900 leading-tight">企业知识中心</div>
              <div class="text-[11px] text-zinc-400 font-normal">Knowledge Hub</div>
            </div>
          </div>
        </div>

        <!-- 快捷操作区：全局搜索 -->
        <div class="px-3 pt-3 pb-1">
          <button
            @click="$router.push('/search')"
            class="w-full flex items-center justify-between px-3 py-2 text-xs text-zinc-500 bg-white hover:bg-zinc-50 border border-zinc-200/80 rounded-lg transition-colors group cursor-pointer shadow-sm"
          >
            <span class="flex items-center gap-2">
              <el-icon :size="13" class="text-zinc-400 group-hover:text-zinc-600"><Search /></el-icon>
              <span>全局搜索...</span>
            </span>
            <kbd class="text-[10px] bg-zinc-50 border border-zinc-200 px-1.5 py-0.5 rounded text-zinc-400 font-mono">⌘K</kbd>
          </button>
        </div>

        <!-- 左侧核心：目录树状导航 (Tree Navigation with Visual Connectors) -->
        <div class="flex-1 overflow-y-auto px-2.5 py-3">
          <div class="flex items-center justify-between px-2 pb-2 mb-1.5 border-b border-zinc-200/60">
            <div class="text-[11px] font-semibold tracking-wider text-zinc-400 uppercase flex items-center gap-1.5">
              <el-icon :size="12"><FolderOpened /></el-icon>
              <span>知识目录树</span>
            </div>
            <button
              @click="loadTreeData"
              class="text-zinc-400 hover:text-zinc-600 p-1 rounded hover:bg-zinc-200/50 transition-colors cursor-pointer"
              title="刷新目录"
            >
              <el-icon :size="12"><Refresh /></el-icon>
            </button>
          </div>

          <!-- 树形节点列表 -->
          <div v-loading="treeLoading" class="space-y-1">
            <div v-if="treeData.length === 0 && !treeLoading" class="text-center py-8 text-xs text-zinc-400">
              暂无知识空间
            </div>

            <div v-for="space in treeData" :key="space.id" class="space-y-0.5">
              <!-- 一级节点：知识空间 (Space Level) -->
              <div
                class="flex items-center justify-between px-2.5 py-2 rounded-lg text-xs font-medium cursor-pointer transition-colors group"
                :class="isSpaceActive(space.id) ? 'bg-blue-50 text-blue-700 font-semibold ring-1 ring-blue-100' : 'text-zinc-700 hover:bg-white hover:shadow-sm'"
                @click="toggleSpace(space)"
              >
                <div class="flex items-center gap-2 min-w-0 flex-1 mr-1">
                  <!-- 展开/收起箭头 -->
                  <el-icon
                    :size="10"
                    class="text-zinc-400 transition-transform duration-200 shrink-0"
                    :class="space.expanded ? 'rotate-90' : ''"
                  >
                    <ArrowRight />
                  </el-icon>
                  <!-- 空间图标徽章 -->
                  <span class="w-6 h-6 rounded-md bg-white border border-zinc-200/80 flex items-center justify-center shrink-0">
                    <el-icon :size="13" class="text-blue-600"><FolderOpened /></el-icon>
                  </span>
                  <span class="truncate">{{ space.name }}</span>
                </div>
                <span class="text-[10px] text-zinc-400 bg-white border border-zinc-200/80 px-1.5 py-0.5 rounded-full shrink-0 group-hover:border-zinc-300">
                  {{ space.topics?.length || 0 }}
                </span>
              </div>

              <!-- 二级节点：专题列表 (Topics Level with Tree Branch Line) -->
              <div v-show="space.expanded" class="ml-4 pl-2.5 border-l border-zinc-200/80 space-y-0.5 my-0.5">
                <div
                  v-for="topic in space.topics"
                  :key="topic.id"
                  class="flex items-center gap-2 px-2 py-1.5 rounded-md text-[11px] cursor-pointer transition-colors"
                  :class="isTopicActive(space.id, topic.id) ? 'bg-blue-100/70 text-blue-800 font-semibold shadow-sm' : 'text-zinc-600 hover:bg-white hover:text-zinc-900'"
                  @click="goToTopic(space.id, topic.id)"
                >
                  <span
                    class="w-1.5 h-1.5 rounded-full shrink-0"
                    :class="isTopicActive(space.id, topic.id) ? 'bg-blue-600' : 'bg-zinc-300'"
                  ></span>
                  <span class="truncate" :title="topic.name">{{ topic.name }}</span>
                </div>

                <div v-if="!space.topics || space.topics.length === 0" class="px-2 py-1 text-[10px] text-zinc-400 italic">
                  暂无下属专题
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 底部个人信息面板 -->
        <div class="p-3 border-t border-zinc-200/70 bg-white/70 flex items-center justify-between">
          <div class="flex items-center gap-2 min-w-0">
            <div class="w-7 h-7 rounded-full bg-blue-600 text-white flex items-center justify-center text-[10px] font-semibold shrink-0 shadow-sm">
              {{ auth.user?.username?.substring(0, 1).toUpperCase() || 'U' }}
            </div>
            <div class="min-w-0 flex-1">
              <div class="text-xs font-medium text-zinc-800 truncate">{{ auth.user?.username }}</div>
              <div class="text-[10px] text-zinc-400 capitalize">{{ auth.user?.role }}</div>
            </div>
          </div>
          <button @click="auth.logout()" title="退出登录" class="text-zinc-400 hover:text-zinc-700 p-1 rounded hover:bg-zinc-200/50 transition-colors cursor-pointer">
            <el-icon :size="14"><SwitchButton /></el-icon>
          </button>
        </div>
      </div>
    </aside>

    <!-- 主展示区 (层次 1：统一白底画布) -->
    <div class="flex-1 flex flex-col min-w-0 overflow-hidden bg-white">
      <!-- 顶栏：轻量透明顶栏，突出操作与面包屑 -->
      <header class="h-14 px-6 border-b border-zinc-200/80 flex items-center justify-between bg-white/90 backdrop-blur-md shrink-0 z-10">
        <!-- 左侧：面包屑 -->
        <div class="flex items-center gap-2 text-xs text-zinc-400 font-medium">
          <span class="hover:text-zinc-700 cursor-pointer" @click="$router.push('/spaces')">知识中心</span>
          <span>/</span>
          <span class="text-zinc-800 font-semibold">{{ currentRouteTitle }}</span>
        </div>

        <!-- 右侧：数据库状态 + 配置中心操作按钮 -->
        <div class="flex items-center gap-3">
          <span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium bg-emerald-50 text-emerald-700 border border-emerald-200/60">
            <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
            PostgreSQL 就绪
          </span>

          <!-- 配置中心按钮（右上角高亮操作） -->
          <button
            v-if="auth.isAdmin"
            @click="$router.push('/settings')"
            class="app-button px-3 py-1.5 rounded-lg border cursor-pointer"
            :class="$route.path.startsWith('/settings') ? 'bg-blue-50 text-blue-700 border-blue-200 font-semibold' : 'bg-white text-zinc-700 border-zinc-200 hover:bg-zinc-50 hover:text-zinc-900'"
            title="系统配置中心"
          >
            <el-icon :size="14" class="text-zinc-500"><Operation /></el-icon>
            <span>配置中心</span>
          </button>
        </div>
      </header>

      <!-- 动态路由内容页面：绑定 fullPath key 确保空间与专题切换时即时响应 -->
      <main class="flex-1 overflow-y-auto bg-white">
        <router-view :key="$route.fullPath" />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { apiClient } from '../api/client'
import {
  FolderOpened,
  ArrowRight,
  Refresh,
  Search,
  Operation,
  SwitchButton
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const treeData = ref<any[]>([])
const treeLoading = ref(false)

const currentRouteTitle = computed(() => {
  const name = route.name as string
  const map: Record<string, string> = {
    SpaceList: '空间概览',
    SpaceDetail: '空间详情',
    KnowledgeDetail: '知识阅读',
    KnowledgeCreate: '新建知识',
    KnowledgeEdit: '编辑知识',
    VersionDiff: '版本比对',
    Search: '全文检索',
    Audit: '安全审计',
    UserManagement: '用户管理',
    SettingsHub: '系统配置中心'
  }
  return map[name] || '控制台'
})

function isSpaceActive(spaceId: number) {
  return route.path === `/spaces/${spaceId}` && !route.query.topic_id
}

function isTopicActive(spaceId: number, topicId: number) {
  return route.path === `/spaces/${spaceId}` && Number(route.query.topic_id) === topicId
}

function toggleSpace(space: any) {
  space.expanded = !space.expanded
  router.push(`/spaces/${space.id}`)
}

function goToTopic(spaceId: number, topicId: number) {
  router.push({
    path: `/spaces/${spaceId}`,
    query: { topic_id: topicId }
  })
}

async function loadTreeData() {
  treeLoading.value = true
  try {
    const sRes: any = await apiClient.get('/spaces')
    const spaces = sRes.data || []

    const fullTree = await Promise.all(
      spaces.map(async (s: any) => {
        try {
          const tRes: any = await apiClient.get(`/spaces/${s.id}/topics`)
          return {
            ...s,
            expanded: true,
            topics: tRes.data || []
          }
        } catch {
          return { ...s, expanded: true, topics: [] }
        }
      })
    )
    treeData.value = fullTree
  } catch (err) {
    console.error('加载知识目录树失败', err)
  } finally {
    treeLoading.value = false
  }
}

onMounted(() => {
  loadTreeData()
})
</script>
