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
    <div class="login__mark">
      <el-icon :size="32"><Reading /></el-icon>
    </div>
    <h1 class="login__title">登录 Bookstore</h1>

    <section class="login__card">
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

    <section class="login__card login__demo">
      <div class="login__demo-title">演示账号</div>
      <ul class="login__demo-list">
        <li v-for="acc in demoAccounts" :key="acc.name">
          <button type="button" class="login__demo-btn" @click="useDemoAccount(acc)">
            <span class="login__demo-name">{{ acc.name }}</span>
            <span class="login__demo-desc">{{ acc.desc }}</span>
          </button>
        </li>
      </ul>
    </section>

    <p class="login__footer text-muted">
      网上综合书店销售数据库项目 · 复旦大学课程作业
    </p>
  </div>
</template>

<style scoped>
.login {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  gap: 16px;
  padding: 56px 20px 40px;
  background: var(--app-bg);
}

.login__mark {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  background: var(--brand);
  color: #fff;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.login__title {
  margin: 0;
  font-size: 22px;
  font-weight: 300;
  letter-spacing: -0.01em;
  color: var(--app-text);
}

.login__card {
  width: 100%;
  max-width: 340px;
  background: var(--app-surface-solid);
  border: 1px solid var(--app-border);
  border-radius: var(--app-radius-lg);
  padding: 16px;
}

.login__label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: var(--app-text);
  margin-bottom: 4px;
}

.login__demo {
  padding: 0;
  overflow: hidden;
}

.login__demo-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--app-text-muted);
  padding: 12px 16px 6px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.login__demo-list {
  list-style: none;
  margin: 0;
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
  padding: 10px 16px;
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
  font-weight: 600;
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
</style>
