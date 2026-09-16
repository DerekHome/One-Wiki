<template>
  <div class="app-page min-h-full px-5 lg:px-8 py-8">
  <div class="max-w-6xl mx-auto pb-12">
    <div class="mb-7">
      <div class="kh-chip mb-3">
        <el-icon :size="13"><SearchIcon /></el-icon>
        <span>FULL TEXT SEARCH</span>
      </div>
      <h2 class="kh-title text-3xl">企业全文检索</h2>
      <p class="text-[var(--kh-text-muted)] text-sm mt-2">基于 PostgreSQL 联合检索知识标题、正文与摘要切片。</p>
    </div>

    <div class="linear-card p-4 lg:p-5 mb-6">
      <div class="flex flex-col sm:flex-row gap-3">
        <el-input
          v-model="queryStr"
          size="large"
          placeholder="输入搜索关键词（如：架构 / 规范 / FastAPI）..."
          clearable
          :prefix-icon="SearchIcon"
          @keyup.enter="handleSearch"
        />
        <button class="app-button app-button-primary h-10 px-5 shrink-0" type="button" :disabled="loading" @click="handleSearch">
          <el-icon :size="14"><SearchIcon /></el-icon>
          <span>{{ loading ? '搜索中' : '搜索' }}</span>
        </button>
      </div>

      <div class="flex flex-col sm:flex-row gap-3 mt-4 items-stretch sm:items-center">
        <el-select v-model="selectedSpace" placeholder="所有空间" clearable class="w-full sm:w-52">
          <el-option v-for="s in spaces" :key="s.id" :label="s.name" :value="s.id" />
        </el-select>
        <el-select v-model="selectedTag" placeholder="筛选标签" clearable class="w-full sm:w-52">
          <el-option v-for="t in tags" :key="t.id" :label="t.name" :value="t.name" />
        </el-select>
        <span class="hidden sm:inline-flex items-center text-xs text-[var(--kh-text-dim)]">
          {{ hasSearched ? `找到 ${total} 条结果` : '输入关键词后开始检索' }}
        </span>
      </div>
    </div>

    <div v-loading="loading">
      <div v-if="results.length > 0" class="space-y-3">
        <div
          v-for="item in results"
          :key="item.knowledge_id"
          class="linear-card p-5 cursor-pointer group"
          @click="goToKnowledge(item.knowledge_id)"
        >
          <div class="flex justify-between items-start gap-4 mb-3">
            <div class="flex items-start gap-3 min-w-0">
              <span class="w-9 h-9 kh-icon-tile shrink-0">
                <el-icon :size="17"><Document /></el-icon>
              </span>
              <div class="min-w-0">
                <h3 class="text-base font-bold text-[var(--kh-text)] group-hover:text-[var(--kh-primary)] transition-colors truncate">{{ item.title }}</h3>
                <div class="flex items-center gap-2 mt-1 text-[11px] text-[var(--kh-text-dim)]">
                  <span>最后更新: {{ formatDate(item.updated_at) }}</span>
                  <span>·</span>
                  <span>v{{ item.version || 1 }}</span>
                </div>
              </div>
            </div>
            <span class="linear-badge shrink-0">文档</span>
          </div>
          <p class="text-[var(--kh-text-muted)] text-sm leading-7 bg-[var(--kh-surface-soft)] border border-[var(--kh-border)] rounded-lg px-3 py-2">{{ item.snippet }}</p>
          <div class="text-xs text-[var(--kh-text-dim)] mt-3 flex justify-end">
            <span class="text-[var(--kh-primary)] font-semibold flex items-center gap-1 transition-transform group-hover:translate-x-0.5">
              查看详情
              <el-icon :size="13"><ArrowRight /></el-icon>
            </span>
          </div>
        </div>

        <div class="flex justify-center mt-6">
          <el-pagination
            background
            layout="prev, pager, next"
            :total="total"
            :page-size="pageSize"
            v-model:current-page="currentPage"
            @current-change="handleSearch"
          />
        </div>
      </div>

      <el-empty v-else-if="hasSearched && !loading" description="未找到匹配的知识内容" />
    </div>
  </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { apiClient } from '../../api/client'
import { ArrowRight, Document, Search as SearchIcon } from '@element-plus/icons-vue'

const router = useRouter()

const queryStr = ref('')
const selectedSpace = ref<number | null>(null)
const selectedTag = ref<string | null>(null)

const spaces = ref<any[]>([])
const tags = ref<any[]>([])
const results = ref<any[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const loading = ref(false)
const hasSearched = ref(false)

async function loadFilters() {
  const [sRes, tRes]: any = await Promise.all([
    apiClient.get('/spaces/'),
    apiClient.get('/tags/')
  ])
  spaces.value = sRes.data || []
  tags.value = tRes.data || []
}

async function handleSearch() {
  loading.value = true
  hasSearched.value = true
  try {
    const params: any = {
      q: queryStr.value,
      page: currentPage.value,
      page_size: pageSize.value
    }
    if (selectedSpace.value) params.space_id = selectedSpace.value
    if (selectedTag.value) params.tag = selectedTag.value

    const res: any = await apiClient.get('/search/', { params })
    results.value = res.data?.items || []
    total.value = res.data?.total || 0
  } finally {
    loading.value = false
  }
}

function goToKnowledge(id: number) {
  router.push(`/knowledge/${id}`)
}

function formatDate(val: string) {
  if (!val) return '-'
  return new Date(val).toLocaleString()
}

onMounted(() => {
  loadFilters()
})
</script>
