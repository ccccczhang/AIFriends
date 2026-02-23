<script setup>
import UserInfoField from "@/views/user/space/components/UserInfoField.vue";
import {nextTick, onBeforeUnmount, onMounted, ref, useTemplateRef} from "vue";
import {useRoute} from "vue-router";
import api from "@/js/http/api.js";

const userProfile = ref(null) // 用户信息
const characters = ref([])
const isloading = ref(false) // 如果正在加载，就不要再加载了，处理多个请求
const hasCharacters = ref(true) // 判断是否还有角色
const sentinelRef = useTemplateRef('sentinel-ref') // 引用哨兵
const route = useRoute()

function checkSentinelVisible() {  // 判断哨兵是否能被看到
  if (!sentinelRef.value) return false

  const rect = sentinelRef.value.getBoundingClientRect()
  return rect.top < window.innerHeight && rect.bottom > 0
  // rect.top是哨兵的上边界，rect.bottom是下边界， 0是视窗的上边界， window.innerHeight是视窗的高度
}

// 实现加载逻辑循环
async function loadMore() {
  if(isloading.value || !hasCharacters.value) return
  isloading.value = true

  // 临时变量
  let newCharacters = []
  try {
    const res = await api.get('/api/create/character/get_list/', {
      params: {
        items_count: characters.value.length, // 存储当前有多少角色
        user_id: route.params.user_id// 传当前在谁的个人空间内
      }
    })
    const data = res.data
    if(data.result === 'success') {
      userProfile.value = data.user_profile // 这两个数据对应后端
      newCharacters = data.characters
    }
  } catch (err){
    console.log(err)
  } finally {
    isloading.value = false // 最终都要把加载改为false
    if(newCharacters.length === 0) {
      hasCharacters.value = false
    } else {
      characters.value.push(...newCharacters) // js里的展开语法
      await nextTick() // Vue 提供的 API，作用是：等 Vue 把 DOM 更新完成，再执行后面的代码

      if(checkSentinelVisible()) {
        await loadMore()
      }
    }
  }
}

let observer = null // 监听器也就是哨兵
// 挂载 固定写法，刷新页面
onMounted(async() => {
  await loadMore()

  observer = new IntersectionObserver(
    entries => {
      entries.forEach(entry => {
        if(entry.isIntersecting) { // Intersect: 是否有交叉，因为只有一个哨兵，所以交叉了就说明要更新页面了
          loadMore()
        }
      })
  },
   {root: null, rootMargin: '2px', threshold: 0} // 视窗与监听器是否交叉，rootMargin:是外边界，2px往外扩展2像素与监听器判断是否交叉，threshold表示交叉长度达多少就触发，0就代表碰到就触发
  )
  observer.observe(sentinelRef.value)
})
// 释放资源
onBeforeUnmount(() => {
  observer?.disconnect()
})


</script>

<template>
  <!-- 水平居中 据下边界12 -->
  <div class="flex flex-col items-center mb-12">
    <UserInfoField :userProfile="userProfile" />
    <!-- 角色列表布局：网格布局：可以根据屏幕宽度自动决定每行的元素数量，并将元素均匀排列在屏幕上；当最后一行元素不足时会左对齐。 -->
    <div class="grid grid-cols-[repeat(auto-fill,minmax(240px,1fr))] gap-9 mt-12 justify-items-center w-full px-9">

    </div>
    <!-- 流式布局：sentinel哨兵 通过判断一个哨兵出现在视图中，来控制刷新 -->
    <div ref="sentinel-ref" class="h-2 mt-8 w-100 bg-red-500"></div>
    <div v-if="isloading" class="text-gray-500 mt-4">加载中...</div>
    <div v-else-if="!hasCharacters" class="text-gray-500 mt-4">没有更多角色了</div>
  </div>
</template>

<style scoped>

</style>