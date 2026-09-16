<template>
  <div class="kh-shell h-screen flex bg-[var(--kh-bg)] overflow-hidden text-[var(--kh-text)] font-sans antialiased">
    <aside class="relative z-20 w-64 bg-[var(--kh-surface)] border-r border-[var(--kh-border)] flex flex-col justify-between select-none shrink-0">
      <div class="flex flex-col h-full overflow-hidden">
        <SidebarBrand class="shrink-0" />

        <div class="flex-1 overflow-y-auto px-2.5 py-3 pt-3">
          <div class="flex items-center justify-between px-2 pb-2 mb-1.5 border-b border-[var(--kh-border)]">
            <div class="text-[10px] font-semibold tracking-[0.12em] text-[var(--kh-text-dim)] uppercase flex items-center gap-1.5">
              <el-icon :size="12"><FolderOpened /></el-icon>
              <span>知识目录</span>
            </div>
            <button
              @click="loadTreeData"
              class="text-[var(--kh-text-dim)] hover:text-[var(--kh-text)] p-1 rounded hover:bg-[var(--kh-fill)] transition-colors cursor-pointer"
              title="刷新目录"
            >
              <el-icon :size="12"><Refresh /></el-icon>
            </button>
          </div>

          <div v-loading="treeLoading" class="space-y-1">
            <div v-if="treeData.length === 0 && !treeLoading" class="text-center py-8 text-xs text-[var(--kh-text-dim)]">
              暂无知识空间
            </div>

            <div v-for="space in treeData" :key="space.id" class="space-y-0.5">
              <div
                class="flex items-center justify-between px-2.5 py-2 rounded-lg text-xs font-medium cursor-pointer transition-colors group"
                :class="isSpaceActive(space.id) ? 'bg-[var(--kh-primary-soft)] text-[var(--kh-primary)] font-semibold ring-1 ring-[var(--kh-border-strong)]' : 'text-[var(--kh-text-soft)] hover:bg-[var(--kh-fill)]'"
                @click="toggleSpace(space)"
              >
                <div class="flex items-center gap-2 min-w-0 flex-1 mr-1">
                  <el-icon
                    :size="10"
                    class="text-[var(--kh-text-dim)] transition-transform duration-200 shrink-0"
                    :class="space.expanded ? 'rotate-90' : ''"
                  >
                    <ArrowRight />
                  </el-icon>
                  <span class="w-6 h-6 rounded-md kh-icon-tile shrink-0">
                    <el-icon :size="13"><FolderOpened /></el-icon>
                  </span>
                  <span class="truncate">{{ space.name }}</span>
                </div>
                <span class="text-[10px] text-[var(--kh-text-dim)] bg-[var(--kh-surface-soft)] border border-[var(--kh-border)] px-1.5 py-0.5 rounded-full shrink-0 font-mono">
                  {{ space.topics?.length || 0 }}
                </span>
              </div>

              <div v-show="space.expanded" class="ml-4 pl-2.5 border-l border-[var(--kh-border)] space-y-0.5 my-0.5">
                <div
                  v-for="topic in space.topics"
                  :key="topic.id"
                  class="flex items-center gap-2 px-2 py-1.5 rounded-md text-[11px] cursor-pointer transition-colors"
                  :class="isTopicActive(space.id, topic.id) ? 'bg-[var(--kh-primary-soft)] text-[var(--kh-text)] font-semibold' : 'text-[var(--kh-text-muted)] hover:bg-[var(--kh-fill)] hover:text-[var(--kh-text)]'"
                  @click="goToTopic(space.id, topic.id)"
                >
                  <span
                    class="w-1.5 h-1.5 rounded-full shrink-0"
                    :class="isTopicActive(space.id, topic.id) ? 'bg-[var(--kh-primary)]' : 'bg-[var(--kh-text-dim)]'"
                  ></span>
                  <span class="truncate" :title="topic.name">{{ topic.name }}</span>
                </div>

                <div v-if="!space.topics || space.topics.length === 0" class="px-2 py-1 text-[10px] text-[var(--kh-text-dim)] italic">
                  暂无下属专题
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="p-3 border-t border-[var(--kh-border)] flex items-center justify-between">
          <div class="flex items-center gap-2 min-w-0">
            <div class="w-7 h-7 rounded-full bg-[var(--kh-primary)] text-white flex items-center justify-center text-[10px] font-semibold shrink-0">
              {{ auth.user?.username?.substring(0, 1).toUpperCase() || 'U' }}
            </div>
            <div class="min-w-0 flex-1">
              <div class="text-xs font-medium truncate">{{ auth.user?.username }}</div>
              <div class="text-[10px] text-[var(--kh-text-dim)] capitalize">{{ auth.user?.role }}</div>
            </div>
          </div>
          <button @click="auth.logout()" title="退出登录" class="text-[var(--kh-text-dim)] hover:text-[var(--kh-text)] p-1 rounded hover:bg-[var(--kh-fill)] transition-colors cursor-pointer">
            <el-icon :size="14"><SwitchButton /></el-icon>
          </button>
        </div>
      </div>
    </aside>

    <div class="relative flex-1 flex flex-col min-w-0 overflow-hidden bg-[var(--kh-bg)]">
      <header class="h-14 px-6 border-b border-[var(--kh-border)] flex items-center justify-between bg-[var(--kh-surface)] shrink-0">
        <div class="flex items-center gap-2 text-xs text-[var(--kh-text-dim)] font-medium">
          <span class="hover:text-[var(--kh-text)] cursor-pointer" @click="$router.push('/spaces')">知识中心</span>
          <span class="text-[var(--kh-text-dim)]">/</span>
          <span class="text-[var(--kh-text)] font-semibold">{{ currentRouteTitle }}</span>
        </div>

        <div class="flex items-center gap-2">
          <button
            @click="$router.push('/search')"
            class="app-button app-button-ghost w-9 h-9 p-0 rounded-lg cursor-pointer"
            :class="$route.path.startsWith('/search') ? 'bg-[var(--kh-primary-soft)] text-[var(--kh-primary)] border-[var(--kh-border-strong)]' : ''"
            title="全局搜索 (⌘K)"
          >
            <el-icon :size="16"><Search /></el-icon>
          </button>

          <button
            v-if="auth.isAdmin"
            @click="$router.push('/settings')"
            class="app-button px-3 py-1.5 rounded-lg border cursor-pointer"
            :class="$route.path.startsWith('/settings') ? 'bg-[var(--kh-primary-soft)] text-[var(--kh-primary)] border-[var(--kh-border-strong)] font-semibold' : 'app-button-ghost'"
            title="系统配置中心"
          >
            <el-icon :size="14"><Operation /></el-icon>
            <span>配置中心</span>
          </button>
        </div>
      </header>

      <main class="flex-1 overflow-y-auto">
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
import SidebarBrand from '../components/SidebarBrand.vue'
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
    const sRes: any = await apiClient.get('/spaces/')
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
