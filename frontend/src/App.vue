<script setup lang="ts">
import { RouterView } from 'vue-router'
</script>

<template>
  <!--
    顶层不加 transition / key，避免切换子路由时把整个 MainLayout 重新挂载，
    否则侧栏的滚动位置会被每次切页重置。子页面的过渡在 MainLayout 内部完成。
  -->
  <RouterView />
</template>
