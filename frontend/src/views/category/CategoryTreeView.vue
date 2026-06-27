<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import PageHeader from '@/components/common/PageHeader.vue'
import { createCategory, deleteCategory, listCategories, updateCategory } from '@/api/categories'
import type { Category } from '@/api/types'
import { ApiError } from '@/api/http'
import { applyServerErrors } from '@/utils/errors'
import { useAuthStore } from '@/stores/auth'
import EmptyState from '@/components/common/EmptyState.vue'
import { displayCategoryName } from '@/utils/categories'

interface TreeNode extends Category {
  children: TreeNode[]
}

const auth = useAuthStore()
const canWrite = () => auth.role === 'admin'

const loading = ref(false)
const flat = ref<Category[]>([])
const treeData = computed<TreeNode[]>(() => buildTree(flat.value))
const expandedKeys = ref<number[]>([])

function buildTree(list: Category[]): TreeNode[] {
  const map = new Map<number, TreeNode>()
  list.forEach((c) => map.set(c.category_id, { ...c, children: [] }))
  const roots: TreeNode[] = []
  map.forEach((node) => {
    const parentId = node.parent_category_id
    if (parentId && map.has(parentId)) {
      map.get(parentId)!.children.push(node)
    } else {
      roots.push(node)
    }
  })
  return roots
}

async function fetchList() {
  loading.value = true
  try {
    const first = await listCategories({ page: 1, page_size: 100 })
    const all = [...first.items]
    const totalPages = Math.ceil(first.total / first.page_size)
    for (let page = 2; page <= totalPages; page += 1) {
      const data = await listCategories({ page, page_size: 100 })
      all.push(...data.items)
    }
    flat.value = all
    expandedKeys.value = flat.value.map((c) => c.category_id)
  } finally {
    loading.value = false
  }
}

function categoryLabel(category: Category) {
  return displayCategoryName(category.category_name)
}

// Dialog
const dialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit' | 'child'>('create')
const dialogTitle = computed(() => {
  if (dialogMode.value === 'create') return '新增一级分类'
  if (dialogMode.value === 'child') return '新增子分类'
  return '编辑分类'
})
const formRef = ref<FormInstance | null>(null)
const submitting = ref(false)
const form = reactive<{
  category_id?: number
  category_name: string
  parent_category_id: number | null
}>({
  category_id: undefined,
  category_name: '',
  parent_category_id: null,
})

const rules: FormRules = {
  category_name: [{ required: true, message: '请输入分类名称', trigger: 'blur' }],
}

function openCreateRoot() {
  dialogMode.value = 'create'
  form.category_id = undefined
  form.category_name = ''
  form.parent_category_id = null
  dialogVisible.value = true
}

function openCreateChild(parent: TreeNode) {
  dialogMode.value = 'child'
  form.category_id = undefined
  form.category_name = ''
  form.parent_category_id = parent.category_id
  dialogVisible.value = true
}

function openEdit(node: TreeNode) {
  dialogMode.value = 'edit'
  form.category_id = node.category_id
  form.category_name = categoryLabel(node)
  form.parent_category_id = node.parent_category_id
  dialogVisible.value = true
}

async function onSubmit() {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    const payload = {
      category_name: form.category_name,
      parent_category_id: form.parent_category_id ?? null,
    }
    if (dialogMode.value === 'edit' && form.category_id) {
      await updateCategory(form.category_id, payload)
      ElMessage.success('分类已更新')
    } else {
      await createCategory(payload)
      ElMessage.success('分类已新增')
    }
    dialogVisible.value = false
    fetchList()
  } catch (error) {
    if (error instanceof ApiError && error.isValidation) applyServerErrors(formRef.value, error)
  } finally {
    submitting.value = false
  }
}

async function onDelete(node: TreeNode) {
  try {
    await ElMessageBox.confirm(
      `确定删除分类「${categoryLabel(node)}」？若存在关联商品将无法删除。`,
      '删除确认',
      { type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消' },
    )
  } catch {
    return
  }
  try {
    await deleteCategory(node.category_id)
    ElMessage.success('已删除')
    fetchList()
  } catch {
    /* 409 */
  }
}

async function onDrop(
  draggingNode: { data: TreeNode },
  dropNode: { data: TreeNode } | null,
  dropType: 'inner' | 'before' | 'after',
) {
  const movedId = draggingNode.data.category_id
  let newParent: number | null = null
  if (dropType === 'inner' && dropNode) {
    newParent = dropNode.data.category_id
  } else if (dropNode) {
    newParent = dropNode.data.parent_category_id
  }
  try {
    await updateCategory(movedId, { parent_category_id: newParent })
    ElMessage.success('父分类已更新')
    fetchList()
  } catch {
    fetchList()
  }
}

function canDrop(
  draggingNode: { data: TreeNode },
  dropNode: { data: TreeNode },
  dropType: 'inner' | 'before' | 'after',
): boolean {
  if (!canWrite()) return false
  // 不能把节点拖到自己的子孙下
  if (draggingNode.data.category_id === dropNode.data.category_id) return false
  if (dropType === 'inner') {
    let cursor: TreeNode | undefined = dropNode.data
    while (cursor) {
      if (cursor.category_id === draggingNode.data.category_id) return false
      cursor = flat.value.find((c) => c.category_id === cursor?.parent_category_id) as TreeNode | undefined
    }
  }
  return true
}

onMounted(fetchList)
</script>

<template>
  <div class="page-wrapper">
    <PageHeader title="分类管理" subtitle="支持多级分类，拖拽即可调整父子关系">
      <template #extra>
        <el-button v-if="canWrite()" type="primary" @click="openCreateRoot">
          <el-icon><Plus /></el-icon>新增一级分类
        </el-button>
      </template>
    </PageHeader>

    <div class="app-card" style="min-height: 360px">
      <el-skeleton v-if="loading" :rows="4" animated />
      <EmptyState
        v-else-if="!treeData.length"
        icon="Menu"
        title="尚未建立任何分类"
        description="先新增一级分类再在其下拖拽挂载子分类"
      >
        <el-button v-if="canWrite()" type="primary" @click="openCreateRoot">新增一级分类</el-button>
      </EmptyState>
      <el-tree
        v-else
        :data="treeData"
        node-key="category_id"
        :draggable="canWrite()"
        :allow-drop="canDrop"
        @node-drop="onDrop"
        :default-expanded-keys="expandedKeys"
        :expand-on-click-node="false"
      >
        <template #default="{ node, data }">
          <div class="category-row">
            <span class="category-row__name">
              <el-icon><component :is="data.children?.length ? 'FolderOpened' : 'Menu'" /></el-icon>
              {{ categoryLabel(data) }}
              <el-tag size="small" effect="plain" round>ID {{ data.category_id }}</el-tag>
            </span>
            <span class="category-row__actions" v-if="canWrite()">
              <el-button text type="primary" size="small" @click.stop="openCreateChild(data)">+ 子分类</el-button>
              <el-button text type="primary" size="small" @click.stop="openEdit(data)">编辑</el-button>
              <el-button text type="danger" size="small" @click.stop="onDelete(data)">删除</el-button>
            </span>
          </div>
        </template>
      </el-tree>
    </div>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="440" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="名称" prop="category_name">
          <el-input v-model="form.category_name" placeholder="例如：文学" />
        </el-form-item>
        <el-form-item v-if="dialogMode === 'edit'" label="父分类">
          <el-select v-model="form.parent_category_id" clearable placeholder="无（一级分类）" style="width: 100%">
            <el-option
              v-for="c in flat.filter((x) => x.category_id !== form.category_id)"
              :key="c.category_id"
              :label="categoryLabel(c)"
              :value="c.category_id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="onSubmit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.category-row {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding-right: 8px;
}

.category-row__name {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
}

.category-row__actions {
  opacity: 0;
  transition: opacity 0.15s ease;
}

:deep(.el-tree-node__content:hover) .category-row__actions {
  opacity: 1;
}

:deep(.el-tree-node__content) {
  height: 40px;
}
</style>
