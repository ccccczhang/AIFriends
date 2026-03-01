<script setup>

import SendIcon from "@/components/character/icons/SendIcon.vue";
import MicIcon from "@/components/character/icons/MicIcon.vue";
</script>

<template>
  <div class="absolute bottom-4 left-2 h-12 w-86 flex items-center">
    <!-- backdrop-blur-sm:毛玻璃  rounded-2xl: 2xl像素越大越圆润 pr-20: 距离右边内边距20，留给发送语音符号 h-full:指的是输入框的高度-->
    <input
        class="input bg-black/30 backdrop-blur-sm text-white text-base w-full h-full rounded-2xl pr-20"
        type="text"
        placeholder="文本输入..."
    >
    <div class="absolute right-2 w-8 h-8 flex justify-center items-center cursor-pointer">
      <SendIcon />
    </div>
    <div class="absolute right-10 w-8 h-8 flex justify-center items-center cursor-pointer">
      <MicIcon />
    </div>

  </div>
</template>

<style scoped>

</style>