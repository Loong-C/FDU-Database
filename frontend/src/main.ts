import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import zhCn from 'element-plus/es/locale/lang/zh-cn'

import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/auth'
import { configureHttp } from './api/http'
import { permissionDirective } from './directives/permission'

import './styles/index.scss'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(ElementPlus, { locale: zhCn })

// 全局注册 Element Plus 图标，便于按名字渲染（<el-icon><i-Odometer/></el-icon> 替代方式）
for (const [name, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(name, component as never)
}

app.directive('perm', permissionDirective)

// 绑定 http 层所需的 token 读取和刷新逻辑
const auth = useAuthStore()
configureHttp({
  getAccessToken: () => auth.accessToken,
  refreshAccessToken: () => auth.refresh(),
  onAuthExpired: () => {
    auth.clear()
    if (router.currentRoute.value.path !== '/login') {
      router.replace({ path: '/login', query: { redirect: router.currentRoute.value.fullPath } })
    }
  },
})

app.mount('#app')
