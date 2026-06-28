<script setup lang="ts">
import { computed } from 'vue'
import PageHeader from '@/components/common/PageHeader.vue'
import { useAuthStore } from '@/stores/auth'
import type { Role } from '@/api/types'

interface WelcomeAction {
  index: string
  title: string
  desc: string
  to: string
  icon: string
}

const auth = useAuthStore()

const displayName = computed(() => auth.user?.display_name || auth.user?.username || '用户')

const actionsByRole: Record<Role, WelcomeAction[]> = {
  operator: [
    { index: '01', title: '新开销售单', desc: '搜索商品、选择客户、收款并扣减库存', to: '/sales/new', icon: 'Plus' },
    { index: '02', title: '维护客户会员', desc: '新增客户，一键升级会员并维护联系方式', to: '/customers', icon: 'UserFilled' },
    { index: '03', title: '处理采购入库', desc: '创建采购单，按到货情况生成入库单', to: '/purchase-orders', icon: 'Van' },
    { index: '04', title: '查看库存预警', desc: '筛出低库存门店商品并发起补货', to: '/inventory?warning=1', icon: 'WarningFilled' },
  ],
  viewer: [
    { index: '01', title: '查看经营总览', desc: '关注销售趋势、热销商品与库存预警', to: '/dashboard', icon: 'Odometer' },
    { index: '02', title: '打开统计分析', desc: '按门店、商品、会员、分类钻取销售数据', to: '/analytics', icon: 'TrendCharts' },
    { index: '03', title: '查看商品排行', desc: '查看销售额 Top N 与订单明细入口', to: '/analytics', icon: 'Trophy' },
    { index: '04', title: '查看分类汇总', desc: '对照分类销量和销售额结构变化', to: '/analytics', icon: 'PieChart' },
  ],
  admin: [
    { index: '01', title: '处理库存预警', desc: '从预警商品直接发起采购补货', to: '/inventory?warning=1', icon: 'WarningFilled' },
    { index: '02', title: '采购与入库审核', desc: '推进采购单状态并审核入库增加库存', to: '/purchase-orders', icon: 'Van' },
    { index: '03', title: '维护商品中心', desc: '维护图书档案、供货关系与门店库存', to: '/books', icon: 'Goods' },
    { index: '04', title: '查看统计分析', desc: '导出门店、商品、会员、分类报表', to: '/analytics', icon: 'TrendCharts' },
  ],
}

const workflowActions = computed(() => {
  const role = auth.user?.role || 'viewer'
  return actionsByRole[role]
})
</script>

<template>
  <div class="page-wrapper welcome-page">
    <PageHeader :title="`你好， ${displayName}`" subtitle="今日业务概况与近 7 天趋势一览" />
    <div class="welcome-page__rule" />

    <section class="workflow-grid welcome-page__actions">
      <router-link
        v-for="action in workflowActions"
        :key="action.title"
        :to="action.to"
        class="workflow-card app-card app-card--hover"
      >
        <span class="workflow-card__index">{{ action.index }}</span>
        <span>
          <span class="workflow-card__title">{{ action.title }}</span>
          <span class="workflow-card__desc">{{ action.desc }}</span>
        </span>
        <el-icon><component :is="action.icon" /></el-icon>
      </router-link>
    </section>
  </div>
</template>

<style scoped>
.welcome-page {
  gap: 24px;
}

.welcome-page :deep(.page-header__title) {
  font-size: 40px;
}

.welcome-page :deep(.page-header__subtitle) {
  font-size: 18px;
}

.welcome-page__rule {
  height: 1px;
  background: var(--app-border);
  margin-top: -16px;
}

.welcome-page__actions {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

@media (max-width: 1100px) {
  .welcome-page__actions {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .welcome-page :deep(.page-header__title) {
    font-size: 30px;
  }

  .welcome-page :deep(.page-header__subtitle) {
    font-size: 14px;
  }

  .welcome-page__actions {
    grid-template-columns: 1fr;
  }
}
</style>
