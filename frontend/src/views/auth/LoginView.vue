<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { ApiError } from '@/api/http'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const formRef = ref<FormInstance | null>(null)
const form = reactive({
  username: '',
  password: '',
})
const loading = ref(false)

const rules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

const demoAccounts = [
  { name: 'admin', desc: '管理员，可执行全部操作', password: 'Admin123!' },
  { name: 'operator', desc: '操作员，可维护客户/销售', password: 'Operator123!' },
  { name: 'viewer', desc: '查询用户，仅可查看分析', password: 'Viewer123!' },
]

async function onSubmit() {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try {
    await auth.login(form.username.trim(), form.password)
    ElMessage.success('登录成功')
    const redirect = (route.query.redirect as string) || '/dashboard'
    router.replace(redirect)
  } catch (error) {
    if (error instanceof ApiError) {
      ElMessage.error(error.message)
    } else {
      ElMessage.error('登录失败，请稍后重试')
    }
  } finally {
    loading.value = false
  }
}

function useDemoAccount(account: { name: string; password: string }) {
  form.username = account.name
  form.password = account.password
}
</script>

<template>
  <div class="login">
    <div class="login__bg"></div>
    <div class="login__panel">
      <aside class="login__brand">
        <div class="brand-mark">
          <el-icon :size="28"><Reading /></el-icon>
        </div>
        <h1>Bookstore 管理平台</h1>
        <p>一站式覆盖门店、供应链、图书、会员与销售数据分析</p>
        <ul class="brand-feats">
          <li><el-icon><Check /></el-icon>角色权限精确到按钮</li>
          <li><el-icon><Check /></el-icon>POS 风格销售开单</li>
          <li><el-icon><Check /></el-icon>实时 KPI 与多维分析</li>
        </ul>
      </aside>

      <section class="login__form">
        <h2>欢迎回来</h2>
        <p class="login__hint text-muted">请使用下方账号登录系统</p>

        <el-form ref="formRef" :model="form" :rules="rules" size="large" @submit.prevent="onSubmit">
          <el-form-item prop="username">
            <el-input v-model="form.username" placeholder="用户名" :prefix-icon="'User'" autocomplete="username" />
          </el-form-item>
          <el-form-item prop="password">
            <el-input
              v-model="form.password"
              placeholder="密码"
              type="password"
              show-password
              :prefix-icon="'Lock'"
              autocomplete="current-password"
              @keyup.enter="onSubmit"
            />
          </el-form-item>
          <el-button type="primary" :loading="loading" style="width: 100%" size="large" @click="onSubmit">
            登录
          </el-button>
        </el-form>

        <div class="login__demo">
          <div class="login__demo-title text-muted">演示账号（点击填入）</div>
          <div class="login__demo-grid">
            <button
              v-for="acc in demoAccounts"
              :key="acc.name"
              type="button"
              class="demo-chip"
              @click="useDemoAccount(acc)"
            >
              <div class="demo-chip__name">{{ acc.name }}</div>
              <div class="demo-chip__desc">{{ acc.desc }}</div>
            </button>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.login {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 24px;
  position: relative;
  background: var(--app-bg);
}

.login__bg {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(60% 80% at 20% 20%, color-mix(in srgb, var(--brand) 18%, transparent), transparent 70%),
    radial-gradient(70% 80% at 80% 90%, color-mix(in srgb, var(--accent) 15%, transparent), transparent 60%),
    var(--app-bg);
  z-index: 0;
}

.login__panel {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 960px;
  background: var(--app-surface);
  border: 1px solid var(--app-border);
  border-radius: 20px;
  box-shadow: var(--app-shadow-lg);
  overflow: hidden;
  display: grid;
  grid-template-columns: 1.1fr 1fr;
}

.login__brand {
  padding: 48px 40px;
  background: linear-gradient(160deg, #1e1b4b 0%, #312e81 45%, #0f172a 100%);
  color: #e0e7ff;
  display: flex;
  flex-direction: column;
  gap: 18px;
  position: relative;
  overflow: hidden;
}

.login__brand::after {
  content: '';
  position: absolute;
  inset: -40% -40% auto auto;
  width: 280px;
  height: 280px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(129, 140, 248, 0.35), transparent 70%);
  pointer-events: none;
}

.brand-mark {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.14);
  border: 1px solid rgba(255, 255, 255, 0.18);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.login__brand h1 {
  font-size: 26px;
  margin: 0;
  letter-spacing: -0.01em;
}

.login__brand p {
  margin: 0;
  color: #c7d2fe;
  line-height: 1.6;
}

.brand-feats {
  list-style: none;
  padding: 0;
  margin: 18px 0 0;
  display: grid;
  gap: 8px;
}

.brand-feats li {
  display: flex;
  gap: 8px;
  align-items: center;
  color: #c7d2fe;
  font-size: 14px;
}

.brand-feats li .el-icon {
  color: #a5f3fc;
}

.login__form {
  padding: 48px 40px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  background: var(--app-surface);
}

.login__form h2 {
  margin: 0;
  font-size: 24px;
  letter-spacing: -0.01em;
}

.login__hint {
  margin: 0 0 12px;
}

.login__demo {
  margin-top: 14px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.login__demo-title {
  font-size: 12px;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.login__demo-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 8px;
}

.demo-chip {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: 10px 14px;
  border-radius: 10px;
  border: 1px solid var(--app-border);
  background: var(--app-surface-alt);
  cursor: pointer;
  transition: all 0.15s ease;
  text-align: left;
}

.demo-chip:hover {
  border-color: var(--brand);
  transform: translateY(-1px);
  box-shadow: var(--app-shadow-sm);
}

.demo-chip__name {
  font-weight: 600;
  color: var(--app-text);
}

.demo-chip__desc {
  font-size: 12px;
  color: var(--app-text-muted);
}

@media (max-width: 820px) {
  .login__panel {
    grid-template-columns: 1fr;
  }
  .login__brand {
    padding: 28px;
  }
  .login__form {
    padding: 28px;
  }
}
</style>
