<template>
  <div class="app-page settings-page max-w-6xl mx-auto px-4 py-6 lg:px-8 pb-16">
    <div class="mb-8">
      <p class="kh-kicker mb-2">管理与设置</p>
      <h1 class="kh-title text-3xl">{{ auth.isAdmin ? '系统配置中心' : 'Agent 凭证' }}</h1>
      <p class="text-sm text-[var(--kh-text-muted)] mt-2">
        {{ auth.isAdmin ? '查看知识库概况，管理成员、存储与系统偏好。' : '为智能体签发只读 API Key，让 AI 在权限范围内取用已发布知识。' }}
      </p>
    </div>

    <el-tabs v-model="activeTab" class="settings-tabs metric-card p-4 lg:p-6">
      <!-- 1. 数据统计大盘 -->
      <el-tab-pane v-if="auth.isAdmin" label="数据大盘" name="stats">
        <div v-loading="loadingStats">
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            <div class="linear-card p-4 border border-[var(--kh-border)]">
              <div class="text-[11px] font-medium text-[var(--kh-text-dim)] uppercase tracking-wider">知识文档总量</div>
              <div class="text-2xl font-bold text-[var(--kh-text)] mt-2">{{ stats?.total_knowledge || 0 }}</div>
              <div class="text-[11px] text-emerald-600 mt-1">已发布正式文档</div>
            </div>
            <div class="linear-card p-4 border border-[var(--kh-border)]">
              <div class="text-[11px] font-medium text-[var(--kh-text-dim)] uppercase tracking-wider">历史版本快照</div>
              <div class="text-2xl font-bold text-[var(--kh-text)] mt-2">{{ stats?.total_versions || 0 }}</div>
              <div class="text-[11px] text-[var(--kh-text-dim)] mt-1">全量版本溯源记录</div>
            </div>
            <div class="linear-card p-4 border border-[var(--kh-border)]">
              <div class="text-[11px] font-medium text-[var(--kh-text-dim)] uppercase tracking-wider">知识空间数</div>
              <div class="text-2xl font-bold text-[var(--kh-text)] mt-2">{{ stats?.total_spaces || 0 }}</div>
              <div class="text-[11px] text-[var(--kh-primary)] mt-1">核心业务隔离区</div>
            </div>
            <div class="linear-card p-4 border border-[var(--kh-border)]">
              <div class="text-[11px] font-medium text-[var(--kh-text-dim)] uppercase tracking-wider">附件存储占用</div>
              <div class="text-2xl font-bold text-[var(--kh-text)] mt-2">{{ stats?.storage_size_mb || 0 }} <span class="text-xs font-normal text-[var(--kh-text-muted)]">MB</span></div>
              <div class="text-[11px] text-[var(--kh-text-dim)] mt-1">共计 {{ stats?.total_attachments || 0 }} 个附件文件</div>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="linear-card p-5 border border-[var(--kh-border)]">
              <h4 class="font-semibold text-sm text-[var(--kh-text-soft)] mb-3">用户与安全概览</h4>
              <div class="space-y-3 text-xs">
                <div class="flex justify-between py-1 border-b border-[var(--kh-border)]">
                  <span class="text-[var(--kh-text-muted)]">注册总用户数</span>
                  <span class="font-medium text-[var(--kh-text-soft)]">{{ stats?.total_users }} 人</span>
                </div>
                <div class="flex justify-between py-1 border-b border-[var(--kh-border)]">
                  <span class="text-[var(--kh-text-muted)]">当前活跃状态用户</span>
                  <span class="font-medium text-emerald-600">{{ stats?.active_users }} 人</span>
                </div>
                <div class="flex justify-between py-1">
                  <span class="text-[var(--kh-text-muted)]">累计操作审计流水</span>
                  <span class="font-medium text-[var(--kh-text-soft)]">{{ stats?.total_audit_logs }} 条</span>
                </div>
              </div>
            </div>

            <div class="linear-card p-5 border border-[var(--kh-border)]">
              <h4 class="font-semibold text-sm text-[var(--kh-text-soft)] mb-3">系统运行架构信息</h4>
              <div class="space-y-3 text-xs">
                <div class="flex justify-between py-1 border-b border-[var(--kh-border)]">
                  <span class="text-[var(--kh-text-muted)]">数据库底层</span>
                  <span class="font-mono text-[var(--kh-text-soft)]">MySQL 8 (Docker)</span>
                </div>
                <div class="flex justify-between py-1 border-b border-[var(--kh-border)]">
                  <span class="text-[var(--kh-text-muted)]">全文检索机制</span>
                  <span class="font-medium text-[var(--kh-text-soft)]">关键词检索（标题 / 摘要 / 正文）</span>
                </div>
                <div class="flex justify-between py-1">
                  <span class="text-[var(--kh-text-muted)]">Agent 接入</span>
                  <span class="font-mono text-emerald-600">REST /api/v1/agent + API Key</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane label="Agent 凭证" name="agent-keys">
        <div class="flex flex-wrap gap-3 justify-between items-center mb-4">
          <span class="text-xs text-[var(--kh-text-muted)]">给智能体签发独立 API Key。Key 只能读 /api/v1/agent，可选绑定一个空间。明文只显示一次。</span>
          <el-button size="small" type="primary" @click="openCreateKeyDialog">签发 Key</el-button>
        </div>
        <el-alert
          v-if="createdApiKey"
          type="success"
          :closable="false"
          class="mb-4"
          title="请立即复制并妥善保存，关闭后无法再查看明文"
        />
        <el-input v-if="createdApiKey" :model-value="createdApiKey" readonly class="mb-4 font-mono" />
        <el-table :data="agentKeys" class="w-full" stripe>
          <el-table-column prop="name" label="名称" />
          <el-table-column prop="key_prefix" label="前缀" width="140">
            <template #default="{ row }">
              <span class="font-mono text-xs">{{ row.key_prefix }}…</span>
            </template>
          </el-table-column>
          <el-table-column label="空间范围" width="140">
            <template #default="{ row }">{{ row.space_id ? `空间 #${row.space_id}` : '授权范围内全部' }}</template>
          </el-table-column>
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag size="small" :type="row.is_active ? 'success' : 'info'">{{ row.is_active ? '有效' : '已撤销' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" align="right">
            <template #default="{ row }">
              <el-button v-if="row.is_active" link size="small" type="danger" @click="revokeKey(row.id)">撤销</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- 2. 存储与文件配置 -->
      <el-tab-pane v-if="auth.isAdmin" label="存储配置" name="storage">
        <div class="max-w-2xl py-4" v-loading="loadingSettings">
          <el-form :model="settingsForm" label-position="top">
            <el-form-item label="存储驱动模式">
              <el-radio-group v-model="settingsForm.storage_type">
                <el-radio label="local">本地安全目录 (Local FileSystem - 当前模式)</el-radio>
                <el-radio label="s3" disabled>S3 / MinIO 对象存储 (生产预留接口)</el-radio>
              </el-radio-group>
            </el-form-item>

            <el-form-item label="本地物理存储路径">
              <el-input v-model="settingsForm.storage_path" disabled class="font-mono text-xs" />
              <div class="text-[11px] text-[var(--kh-text-dim)] mt-1">存储路径由后端系统配置隔离，严格防止路径穿越漏洞</div>
            </el-form-item>

            <el-form-item label="单文件上传大小限制 (MB)">
              <el-input-number v-model="settingsForm.max_upload_size_mb" :min="1" :max="500" />
            </el-form-item>

            <el-form-item label="允许上传与拖拽解析的文件类型">
              <el-select
                v-model="settingsForm.allowed_extensions"
                multiple
                filterable
                allow-create
                default-first-option
                class="w-full"
              />
              <div class="text-[11px] text-[var(--kh-text-dim)] mt-1">支持输入回车自定义扩展名，如 .md, .html, .pdf 等</div>
            </el-form-item>

            <el-button type="primary" class="mt-4" :loading="savingSettings" @click="saveSettings">
              保存存储配置
            </el-button>
          </el-form>
        </div>
      </el-tab-pane>

      <!-- 3. 用户管理 -->
      <el-tab-pane v-if="auth.isAdmin" label="用户管理" name="users">
        <div class="flex flex-wrap gap-3 justify-between items-center mb-4">
          <span class="text-xs text-[var(--kh-text-muted)]">统一管控系统注册账户、账号可用状态与系统分配角色</span>
          <el-button size="small" type="primary" @click="openCreateUserDialog">添加用户</el-button>
        </div>
        <el-table :data="users" class="w-full" stripe>
          <el-table-column prop="id" label="ID" width="70" />
          <el-table-column prop="username" label="用户名" font-weight="bold" />
          <el-table-column prop="role" label="系统角色">
            <template #default="{ row }">
              <el-tag size="small" :type="row.role === 'admin' ? 'danger' : 'info'">{{ row.role }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="is_active" label="账号状态" width="120">
            <template #default="{ row }">
              <el-tag size="small" :type="row.is_active ? 'success' : 'danger'">
                {{ row.is_active ? '正常使用' : '已禁用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="160" align="right">
            <template #default="{ row }">
              <el-button
                link
                size="small"
                :type="row.is_active ? 'danger' : 'success'"
                @click="toggleUserActive(row)"
              >
                {{ row.is_active ? '禁用账号' : '启用账号' }}
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- 4. 角色与权限矩阵 (RBAC) -->
      <el-tab-pane v-if="auth.isAdmin" label="权限与角色" name="roles">
        <div class="mb-4 text-xs text-[var(--kh-text-muted)]">系统内置的标准四级角色权限定义矩阵 (RBAC + Resource ACL)</div>
        <el-table :data="rolesMatrix" class="w-full" border>
          <el-table-column prop="role" label="角色标识" width="120" />
          <el-table-column prop="name" label="角色名称" width="140" font-weight="bold" />
          <el-table-column prop="description" label="定位说明" min-width="240" />
          <el-table-column label="拥有的关键操作特权" min-width="300">
            <template #default="{ row }">
              <div class="flex flex-wrap gap-1">
                <el-tag v-for="p in row.permissions" :key="p" size="small" type="info">{{ p }}</el-tag>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- 5. 安全操作审计 -->
      <el-tab-pane v-if="auth.isAdmin" label="操作日志" name="audit">
        <div class="flex flex-wrap gap-3 mb-4">
          <el-input v-model="auditActionFilter" placeholder="操作动作 (如 register / create_knowledge)..." clearable size="small" class="w-64" />
          <el-button size="small" type="primary" @click="fetchAuditLogs">检索日志</el-button>
        </div>
        <el-table :data="auditLogs" class="w-full" size="small" stripe>
          <el-table-column prop="id" label="ID" width="60" />
          <el-table-column prop="username" label="操作人" width="120" />
          <el-table-column prop="action" label="操作动作" width="160">
            <template #default="{ row }">
              <el-tag size="small">{{ row.action }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="resource" label="涉及资源" width="160" />
          <el-table-column prop="details" label="动作详细上下文">
            <template #default="{ row }">
              <span class="font-mono text-[11px] text-[var(--kh-text-muted)]">{{ JSON.stringify(row.details) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="时间" width="170">
            <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- 6. 系统偏好设置 -->
      <el-tab-pane v-if="auth.isAdmin" label="系统偏好" name="preferences">
        <div class="max-w-xl py-4" v-loading="loadingSettings">
          <el-form :model="settingsForm" label-position="top">
            <el-form-item label="系统站点标题">
              <el-input v-model="settingsForm.site_name" />
            </el-form-item>
            <el-form-item label="允许自主开放注册账号">
              <el-switch v-model="settingsForm.allow_registration" />
            </el-form-item>
            <el-form-item label="默认新建知识空间可见性">
              <el-select v-model="settingsForm.default_space_visibility" class="w-full">
                <el-option label="内部公开 (internal)" value="internal" />
                <el-option label="全员公开 (public)" value="public" />
                <el-option label="私有隔离 (private)" value="private" />
              </el-select>
            </el-form-item>
            <el-button type="primary" :loading="savingSettings" @click="saveSettings">
              保存偏好设置
            </el-button>
          </el-form>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 添加用户对话框 -->
    <el-dialog v-model="createUserDialog" title="添加新用户" width="min(400px, calc(100vw - 32px))">
      <el-form :model="userForm" label-position="top">
        <el-form-item label="用户名" required>
          <el-input v-model="userForm.username" placeholder="至少3位字符" />
        </el-form-item>
        <el-form-item label="初始登录密码" required>
          <el-input v-model="userForm.password" type="password" placeholder="至少6位" show-password />
        </el-form-item>
        <el-form-item label="系统角色">
          <el-select v-model="userForm.role" class="w-full">
            <el-option label="系统管理员 (admin)" value="admin" />
            <el-option label="普通用户 (viewer)" value="viewer" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createUserDialog = false">取消</el-button>
        <el-button type="primary" @click="submitCreateUser">确定添加</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="createKeyDialog" title="签发 Agent API Key" width="min(440px, calc(100vw - 32px))">
      <el-form :model="keyForm" label-position="top">
        <el-form-item label="名称" required>
          <el-input v-model="keyForm.name" placeholder="例如：客服机器人" />
        </el-form-item>
        <el-form-item label="限定知识空间（可选）">
          <el-select v-model="keyForm.space_id" clearable placeholder="不选则使用签发人可见的全部空间" class="w-full">
            <el-option v-for="s in keySpaces" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createKeyDialog = false">取消</el-button>
        <el-button type="primary" @click="submitCreateKey">签发</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { apiClient } from '../../api/client'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../../stores/auth'

const auth = useAuthStore()
const activeTab = ref(auth.isAdmin ? 'stats' : 'agent-keys')

// 1. 数据统计
const stats = ref<any>(null)
const loadingStats = ref(false)

// 2. 存储与系统配置
const settingsForm = ref<any>({})
const loadingSettings = ref(false)
const savingSettings = ref(false)

// 3. 用户
const users = ref<any[]>([])
const createUserDialog = ref(false)
const userForm = ref({ username: '', password: '', role: 'viewer' })

// 4. 角色矩阵
const rolesMatrix = ref<any[]>([])

// 5. 审计日志
const auditLogs = ref<any[]>([])
const auditActionFilter = ref('')

const agentKeys = ref<any[]>([])
const createdApiKey = ref('')
const createKeyDialog = ref(false)
const keySpaces = ref<any[]>([])
const keyForm = ref<{ name: string; space_id: number | null }>({ name: '', space_id: null })

async function fetchStats() {
  loadingStats.value = true
  try {
    const res: any = await apiClient.get('/system/stats')
    stats.value = res.data
  } finally {
    loadingStats.value = false
  }
}

async function fetchSettings() {
  loadingSettings.value = true
  try {
    const res: any = await apiClient.get('/system/settings')
    settingsForm.value = res.data || {}
  } finally {
    loadingSettings.value = false
  }
}

async function saveSettings() {
  savingSettings.value = true
  try {
    await apiClient.put('/system/settings', settingsForm.value)
    ElMessage.success('配置已保存生效')
    fetchSettings()
  } finally {
    savingSettings.value = false
  }
}

async function fetchUsers() {
  const res: any = await apiClient.get('/users/')
  users.value = res.data || []
}

function openCreateUserDialog() {
  userForm.value = { username: '', password: '', role: 'viewer' }
  createUserDialog.value = true
}

async function submitCreateUser() {
  if (!userForm.value.username || !userForm.value.password) return
  await apiClient.post('/users/', userForm.value)
  ElMessage.success('用户创建成功')
  createUserDialog.value = false
  fetchUsers()
}

async function toggleUserActive(row: any) {
  await apiClient.put(`/users/${row.id}`, { is_active: !row.is_active })
  ElMessage.success('用户状态已更新')
  fetchUsers()
}

async function fetchRoles() {
  const res: any = await apiClient.get('/system/roles-matrix')
  rolesMatrix.value = res.data || []
}

async function fetchAuditLogs() {
  const params: any = { page: 1, page_size: 20 }
  if (auditActionFilter.value) params.action = auditActionFilter.value
  const res: any = await apiClient.get('/audit/', { params })
  auditLogs.value = res.data?.items || []
}

async function fetchAgentKeys() {
  const res: any = await apiClient.get('/agent-keys/')
  agentKeys.value = res.data || []
}

function openCreateKeyDialog() {
  createdApiKey.value = ''
  keyForm.value = { name: '', space_id: null }
  createKeyDialog.value = true
}

async function submitCreateKey() {
  if (!keyForm.value.name.trim()) {
    ElMessage.warning('请填写名称')
    return
  }
  const res: any = await apiClient.post('/agent-keys/', {
    name: keyForm.value.name.trim(),
    space_id: keyForm.value.space_id || null
  })
  createdApiKey.value = res.data?.api_key || ''
  createKeyDialog.value = false
  ElMessage.success('Key 已签发，请立即复制明文')
  fetchAgentKeys()
}

async function revokeKey(id: number) {
  await apiClient.delete(`/agent-keys/${id}`)
  ElMessage.success('已撤销')
  fetchAgentKeys()
}

async function fetchKeySpaces() {
  const res: any = await apiClient.get('/spaces/')
  keySpaces.value = res.data || []
}

function formatDate(val: string) {
  if (!val) return '-'
  return new Date(val).toLocaleString()
}

onMounted(() => {
  fetchAgentKeys()
  fetchKeySpaces()
  if (!auth.isAdmin) return
  fetchStats()
  fetchSettings()
  fetchUsers()
  fetchRoles()
  fetchAuditLogs()
})
</script>
