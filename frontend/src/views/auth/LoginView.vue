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
    const redirect = (route.query.redirect as string) || '/welcome'
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
    <section class="login__identity">
      <div class="swiss-kicker">Database and Implementation / 2026</div>
      <div class="login__brand-row">
        <div class="login__mark">
          <el-icon :size="30"><Reading /></el-icon>
        </div>
        <span>Bookstore</span>
      </div>
      <h1 class="login__title">
        <span>网上综合书店</span>
        <span>销售数据库</span>
      </h1>
      <p class="login__copy">
          
      </p>
    </section>

    <main class="login__panel">
      <section class="login__card">
        <div class="login__card-head">
          <div>
            <div class="swiss-kicker">Secure Login</div>
            <h2>登录后台</h2>
          </div>
        </div>

        <el-form ref="formRef" :model="form" :rules="rules" size="default" @submit.prevent="onSubmit">
          <label class="login__label" for="login-username">用户名</label>
          <el-form-item prop="username">
            <el-input
              id="login-username"
              v-model="form.username"
              placeholder="输入用户名"
              autocomplete="username"
            />
          </el-form-item>

          <label class="login__label" for="login-password">密码</label>
          <el-form-item prop="password">
            <el-input
              id="login-password"
              v-model="form.password"
              placeholder="输入密码"
              type="password"
              show-password
              autocomplete="current-password"
              @keyup.enter="onSubmit"
            />
          </el-form-item>

          <el-button
            type="primary"
            :loading="loading"
            style="width: 100%"
            @click="onSubmit"
          >
            登录
          </el-button>
        </el-form>
      </section>

      <details class="login__card login__demo">
        <summary>
          <span>演示登录</span>
        </summary>
        <ul class="login__demo-list">
          <li v-for="acc in demoAccounts" :key="acc.name">
            <button type="button" class="login__demo-btn" @click="useDemoAccount(acc)">
              <span class="login__demo-name">{{ acc.name }}</span>
              <span class="login__demo-desc">{{ acc.desc }}</span>
            </button>
          </li>
        </ul>
      </details>

    </main>
  </div>
</template>

<style scoped>
.login {
  min-height: 100vh;
  display: grid;
  grid-template-columns: minmax(320px, 1fr) minmax(360px, 460px);
  gap: 0;
  background: var(--app-bg);
}

.login__identity {
  min-height: 100vh;
  padding: 64px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  border-right: 1px solid var(--app-border-strong);
  background:
    linear-gradient(var(--app-border-muted) 1px, transparent 1px),
    linear-gradient(90deg, var(--app-border-muted) 1px, transparent 1px),
    var(--app-surface-solid);
  background-size: 64px 64px;
}

.login__brand-row {
  display: inline-flex;
  align-items: center;
  gap: 14px;
  font-weight: 900;
  font-size: 20px;
}

.login__mark {
  width: 54px;
  height: 54px;
  border-radius: 8px;
  background: var(--brand);
  color: #fff;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.login__title {
  margin: 0;
  max-width: 760px;
  font-size: clamp(48px, 8vw, 108px);
  font-weight: 900;
  line-height: 0.96;
  letter-spacing: 0;
  color: var(--app-text);
}

.login__title span {
  display: block;
}

.login__copy {
  margin: 0;
  max-width: 520px;
  color: var(--app-text-muted);
  font-size: 16px;
}

.login__panel {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 14px;
  padding: 48px;
}

.login__card {
  width: 100%;
  background: var(--app-surface-solid);
  border: 1px solid var(--app-border);
  border-radius: var(--app-radius-lg);
  padding: 20px;
}

.login__card-head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
}

.login__card-head h2 {
  margin: 0;
  font-size: 28px;
  line-height: 1;
}

.login__demo summary {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  cursor: pointer;
  font-weight: 800;
  list-style: none;
}

.login__demo summary::-webkit-details-marker {
  display: none;
}

.login__demo summary::after {
  content: '+';
  color: var(--brand);
  font-size: 18px;
  line-height: 1;
}

.login__demo[open] summary::after {
  content: '-';
}

.login__label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: var(--app-text);
  margin-bottom: 4px;
}

.login__demo {
  overflow: hidden;
}

.login__demo-list {
  list-style: none;
  margin: 14px -20px -20px;
  padding: 0;
  display: flex;
  flex-direction: column;
}

.login__demo-list li + li {
  border-top: 1px solid var(--app-border-muted);
}

.login__demo-btn {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 2px;
  width: 100%;
  padding: 12px 20px;
  background: transparent;
  border: none;
  cursor: pointer;
  text-align: left;
  transition: background 0.1s ease;
}

.login__demo-btn:hover {
  background: var(--app-surface-alt);
}

.login__demo-name {
  font-weight: 900;
  color: var(--brand);
  font-size: 13px;
}

.login__demo-desc {
  font-size: 12px;
  color: var(--app-text-muted);
}

.login__footer {
  margin: 12px 0 0;
  font-size: 12px;
}

:deep(.el-form-item) {
  margin-bottom: 12px;
}

@media (max-width: 860px) {
  .login {
    grid-template-columns: 1fr;
  }

  .login__identity {
    min-height: auto;
    gap: 48px;
    padding: 36px 24px;
    border-right: 0;
    border-bottom: 1px solid var(--app-border-strong);
  }

  .login__title {
    font-size: 42px;
  }

  .login__panel {
    padding: 24px;
  }
}
</style>
