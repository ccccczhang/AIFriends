<script setup>
defineProps(['character'])
</script>

<template>
  <!-- px: 左右边距都为2 h-10:框的高度为10 w-fit:自适应实现以下内容的最小宽度 -->
  <div class="absolute left-2 right-22 top-6 h-10 w-fit rounded-full bg-black/50 flex items-center gap-2 px-2">
    <div class="avatar">
      <div class="w-8 rounded-full">
        <img :src="character.photo" alt="">
      </div>
    </div>
    <div class="text-white text-sm line-clamp-1 break-all">
      {{ character.name }}啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊
    </div>
  </div>
</template>

<style scoped>

</style>