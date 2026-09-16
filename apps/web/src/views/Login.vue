<template>
  <div class="kh-shell min-h-screen grid lg:grid-cols-[1fr_460px] bg-[var(--kh-bg)]">
    <section class="hidden lg:flex flex-col justify-between px-12 py-10 relative overflow-hidden">
      <div class="absolute inset-0 bg-[radial-gradient(circle_at_20%_15%,var(--kh-glow),transparent_26rem)]"></div>

      <div class="relative flex items-center gap-3">
        <div class="brand-mark w-9 h-9 rounded-xl text-xs tracking-wider">
          <span>KH</span>
        </div>
        <div>
          <div class="text-sm font-semibold text-[var(--kh-text)]">企业知识中心</div>
          <div class="text-[11px] text-[var(--kh-text-dim)]">Knowledge Hub</div>
        </div>
      </div>

      <div class="relative max-w-xl">
        <div class="kh-chip mb-5">
          <el-icon :size="13"><Collection /></el-icon>
          <span>统一知识资产管理平台</span>
        </div>
        <h1 class="kh-title text-4xl leading-tight">
          让制度、规范和经验沉淀为可检索的团队资产
        </h1>
        <p class="mt-4 text-sm leading-7 text-[var(--kh-text-muted)] max-w-lg">
          用空间隔离业务域，用专题整理知识脉络，用版本、附件和审计留住协作过程。
        </p>

        <div class="grid grid-cols-3 gap-3 mt-8">
          <div class="metric-card p-4">
            <div class="text-[11px] text-[var(--kh-text-muted)]">知识归档</div>
            <div class="text-lg font-bold text-[var(--kh-text)] mt-1">空间化</div>
          </div>
          <div class="metric-card p-4">
            <div class="text-[11px] text-[var(--kh-text-muted)]">协作管理</div>
            <div class="text-lg font-bold text-[var(--kh-text)] mt-1">权限化</div>
          </div>
          <div class="metric-card p-4">
            <div class="text-[11px] text-[var(--kh-text-muted)]">内容流转</div>
            <div class="text-lg font-bold text-[var(--kh-text)] mt-1">可追溯</div>
          </div>
        </div>
      </div>

      <p class="relative text-xs text-[var(--kh-text-dim)]">Built for internal knowledge operations.</p>
    </section>

    <main class="relative flex items-center justify-center p-5 lg:p-8">
      <div class="w-full max-w-md">
        <div class="lg:hidden flex items-center justify-center gap-3 mb-7">
          <div class="brand-mark w-10 h-10 rounded-xl text-xs tracking-wider">
            <span>KH</span>
          </div>
          <div>
            <div class="text-base font-semibold text-[var(--kh-text)]">企业知识中心</div>
            <div class="text-xs text-[var(--kh-text-dim)]">Knowledge Hub</div>
          </div>
        </div>

        <el-card class="login-card w-full rounded-2xl border border-[var(--kh-border)] shadow-[var(--kh-shadow-sm)]">
          <div class="text-center mb-6">
            <div class="brand-mark w-12 h-12 rounded-2xl text-sm tracking-wider mx-auto mb-4">
              <span>KH</span>
            </div>
            <h1 class="kh-title text-2xl">欢迎回来</h1>
            <p class="text-sm text-[var(--kh-text-muted)] mt-1">登录后继续管理团队知识资产</p>
          </div>

          <el-tabs v-model="activeTab" class="w-full kh-tabs">
            <el-tab-pane label="账号登录" name="login">
              <el-form :model="loginForm" label-position="top" @submit.prevent="handleLogin">
                <el-alert
                  v-if="loginError"
                  :title="loginError"
                  type="error"
                  :closable="false"
                  show-icon
                  class="mb-4"
                />
                <el-form-item label="用户名">
                  <el-input v-model="loginForm.username" placeholder="请输入用户名" size="large" :prefix-icon="User" />
                </el-form-item>
                <el-form-item label="密码">
                  <el-input v-model="loginForm.password" type="password" placeholder="请输入密码" size="large" show-password :prefix-icon="Lock" @keyup.enter="handleLogin" />
                </el-form-item>
                <button
                  type="submit"
                  class="app-button app-button-primary w-full h-11 mt-4 text-sm"
                  :disabled="loading"
                >
                  <span>{{ loading ? '登录中' : '登录' }}</span>
                  <el-icon v-if="!loading" :size="15"><ArrowRight /></el-icon>
                </button>
              </el-form>
            </el-tab-pane>

            <el-tab-pane label="注册新用户" name="register">
              <el-form :model="regForm" label-position="top" @submit.prevent="handleRegister">
                <el-form-item label="设置用户名">
                  <el-input v-model="regForm.username" placeholder="至少3位字符" size="large" :prefix-icon="User" />
                </el-form-item>
                <el-form-item label="设置密码">
                  <el-input v-model="regForm.password" type="password" placeholder="至少6位密码" size="large" show-password :prefix-icon="Lock" />
                </el-form-item>
                <button
                  type="button"
                  class="app-button app-button-ghost w-full h-11 mt-4 text-sm border border-[var(--kh-border)]"
                  :disabled="loading"
                  @click="handleRegister"
                >
                  <span>{{ loading ? '注册中' : '注册并登录' }}</span>
                  <el-icon v-if="!loading" :size="15"><ArrowRight /></el-icon>
                </button>
              </el-form>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { apiClient } from '../api/client'
import { ElMessage } from 'element-plus'
import { ArrowRight, Collection, Lock, User } from '@element-plus/icons-vue'

const router = useRouter()
const auth = useAuthStore()

const activeTab = ref('login')
const loading = ref(false)
const loginError = ref('')

const loginForm = ref({ username: '', password: '' })
const regForm = ref({ username: '', password: '' })

async function handleLogin() {
  if (loading.value) return
  loginError.value = ''
  if (!loginForm.value.username || !loginForm.value.password) {
    loginError.value = '请输入用户名和密码'
    return
  }
  loading.value = true
  try {
    await auth.login(loginForm.value)
    ElMessage.success('登录成功')
    await router.push('/spaces')
  } catch (err: any) {
    loginError.value = err?.response?.data?.error?.message || err?.message || '登录失败，请检查用户名和密码'
  } finally {
    loading.value = false
  }
}

async function handleRegister() {
  if (!regForm.value.username || !regForm.value.password) {
    ElMessage.warning('请填写注册信息')
    return
  }
  loading.value = true
  try {
    await apiClient.post('/auth/register', regForm.value)
    ElMessage.success('注册成功，正在登录...')
    await auth.login(regForm.value)
    router.push('/spaces')
  } catch (err) {
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-card :deep(.el-card__body) {
  padding: 28px;
}

.kh-tabs :deep(.el-tabs__nav-wrap::after) {
  height: 1px;
  background: var(--kh-border);
}

.kh-tabs :deep(.el-tabs__item) {
  color: var(--kh-text-muted);
  font-weight: 600;
}

.kh-tabs :deep(.el-tabs__item.is-active) {
  color: var(--kh-primary);
}

.kh-tabs :deep(.el-tabs__active-bar) {
  height: 2px;
  background: var(--kh-primary);
}

button:disabled {
  cursor: not-allowed;
  opacity: 0.72;
}
</style>
