<script setup lang="ts">
import { useRouter } from 'vue-router'
const router = useRouter()
</script>

<template>
  <div class="not-found">
    <div class="not-found__inner">
      <div class="not-found__code">404</div>
      <h2>页面走丢了</h2>
      <p class="text-muted">请检查链接是否正确，或返回首页继续操作。</p>
      <el-button type="primary" @click="router.replace('/')">返回首页</el-button>
    </div>
  </div>
</template>

<style scoped>
.not-found {
  min-height: 70vh;
  display: grid;
  place-items: center;
}
.not-found__inner {
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 8px;
  align-items: center;
}
.not-found__code {
  font-size: 96px;
  font-weight: 800;
  letter-spacing: -0.04em;
  background: linear-gradient(135deg, var(--brand), var(--accent));
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  line-height: 1;
}
</style>
