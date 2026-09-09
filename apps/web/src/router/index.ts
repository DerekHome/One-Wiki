import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '../layouts/MainLayout.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('../views/Login.vue')
    },
    {
      path: '/',
      component: MainLayout,
      children: [
        { path: '', redirect: '/spaces' },
        { path: 'spaces', name: 'SpaceList', component: () => import('../views/spaces/SpaceList.vue') },
        { path: 'spaces/:id', name: 'SpaceDetail', component: () => import('../views/spaces/SpaceDetail.vue') },
        { path: 'knowledge/:id', name: 'KnowledgeDetail', component: () => import('../views/knowledge/KnowledgeDetail.vue') },
        { path: 'knowledge/create/:spaceId?', name: 'KnowledgeCreate', component: () => import('../views/knowledge/KnowledgeForm.vue') },
        { path: 'knowledge/:id/edit', name: 'KnowledgeEdit', component: () => import('../views/knowledge/KnowledgeForm.vue') },
        { path: 'knowledge/:id/diff', name: 'VersionDiff', component: () => import('../views/knowledge/VersionDiff.vue') },
        { path: 'search', name: 'Search', component: () => import('../views/search/SearchView.vue') },
        { path: 'tags', name: 'Tags', component: () => import('../views/tags/TagManagement.vue') },
        { path: 'audit', name: 'Audit', component: () => import('../views/audit/AuditLogView.vue') },
        { path: 'modules', name: 'Modules', component: () => import('../views/modules/ModuleManagement.vue') },
        { path: 'admin/users', name: 'UserManagement', component: () => import('../views/admin/UserManagement.vue') },
        { path: 'settings', name: 'SettingsHub', component: () => import('../views/settings/SettingsHub.vue') }
      ]
    }
  ]
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token')
  if (to.path !== '/login' && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router
