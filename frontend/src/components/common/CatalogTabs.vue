<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const active = computed({
  get: () => (route.path.startsWith('/books') ? 'books' : 'products'),
  set: (value: string) => {
    router.push(value === 'books' ? '/books' : '/products')
  },
})
</script>

<template>
  <el-tabs v-model="active" class="catalog-tabs">
    <el-tab-pane label="通用商品" name="products" />
    <el-tab-pane label="图书档案" name="books" />
  </el-tabs>
</template>
