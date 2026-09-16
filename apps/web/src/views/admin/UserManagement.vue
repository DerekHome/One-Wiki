<template>
  <div class="app-page max-w-5xl mx-auto px-4 lg:px-8 py-6 pb-12">
    <div class="flex justify-between items-center mb-6">
      <div>
        <h2 class="kh-title text-2xl">用户与系统角色</h2>
        <p class="text-[var(--kh-text-muted)] text-sm mt-1">全局统一 RBAC 用户账户管控与状态调度</p>
      </div>
      <el-button type="primary" @click="createDialog = true">添加用户</el-button>
    </div>

    <el-card shadow="never" class="rounded-xl" v-loading="loading">
      <el-table :data="users" class="w-full">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="username" label="用户名" font-weight="bold" />
        <el-table-column prop="role" label="系统角色">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'danger' : 'info'">{{ row.role }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="账号状态">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
              {{ row.is_active ? '正常使用' : '已禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" align="right">
          <template #default="{ row }">
            <el-button
              link
              :type="row.is_active ? 'danger' : 'success'"
              @click="toggleActive(row)"
            >
              {{ row.is_active ? '禁用' : '解禁' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="createDialog" title="添加新用户" width="400px">
      <el-form :model="form" label-position="top">
        <el-form-item label="用户名" required>
          <el-input v-model="form.username" placeholder="至少3位" />
        </el-form-item>
        <el-form-item label="初始密码" required>
          <el-input v-model="form.password" type="password" placeholder="至少6位" show-password />
        </el-form-item>
        <el-form-item label="系统角色">
          <el-select v-model="form.role" class="w-full">
            <el-option label="系统管理员 (admin)" value="admin" />
            <el-option label="普通用户 (viewer)" value="viewer" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreate">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { apiClient } from '../../api/client'
import { ElMessage } from 'element-plus'

const users = ref<any[]>([])
const loading = ref(false)
const createDialog = ref(false)

const form = ref({
  username: '',
  password: '',
  role: 'viewer'
})

async function fetchUsers() {
  loading.value = true
  try {
    const res: any = await apiClient.get('/users/')
    users.value = res.data || []
  } finally {
    loading.value = false
  }
}

async function handleCreate() {
  if (!form.value.username || !form.value.password) return
  try {
    await apiClient.post('/users/', form.value)
    ElMessage.success('用户创建成功')
    createDialog.value = false
    form.value = { username: '', password: '', role: 'viewer' }
    fetchUsers()
  } catch {}
}

async function toggleActive(row: any) {
  try {
    await apiClient.put(`/users/${row.id}`, { is_active: !row.is_active })
    ElMessage.success('用户状态已更新')
    fetchUsers()
  } catch {}
}

onMounted(() => {
  fetchUsers()
})
</script>
