<script setup lang="ts">
import { computed } from 'vue'

const active = computed({
  get: () => 'products',
  set: () => undefined,
})
</script>

<template>
  <el-tabs v-model="active" class="catalog-tabs">
    <el-tab-pane label="通用商品" name="products" />
  </el-tabs>
</template>
