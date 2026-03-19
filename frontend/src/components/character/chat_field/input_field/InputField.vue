<script setup>

import SendIcon from "@/components/character/icons/SendIcon.vue";
import MicIcon from "@/components/character/icons/MicIcon.vue";
import {ref, useTemplateRef} from "vue";
import api from "@/js/http/api.js";
import streamApi from "@/js/http/streamApi.js";
import {c} from "vue-router/dist/devtools-EWN81iOl.mjs";
import Microphone from "@/components/character/chat_field/input_field/Microphone.vue";


const inputRef = useTemplateRef('input-ref')
const message = ref('')
const props = defineProps(['friendId']) // 接收从父组件ChatField传来的friendId
const emit = defineEmits(['pushBackMessage', 'addToLastMessage']) // 父组件ChatField的函数

// let isProcessing = false // 判断是否正在输出，输入输出一段话不能中途再输入，更改为版本号
let processID = 0 // 记录一个版本号，用于随时打断AI说话
const showMic = ref(false)

function focus() { // 聚焦函数，使得直接聚焦聊天输入框
  inputRef.value.focus()
}

async function handleSend(event, audio_msg) {
  let content
  if(audio_msg) {
    content = audio_msg.trim()
  } else {
    content = message.value.trim()
  }
  if(!content) return

  const curID = ++ processID // 记录当前版本号

  message.value = ''

  emit('pushBackMessage', {role: 'user', content: content, id: crypto.randomUUID()})
  emit('pushBackMessage', {role: 'ai', content: '', id: crypto.randomUUID()})

  try {
    await streamApi('/api/friend/message/chat/', {
      body: {
        friend_id: props.friendId,
        message: content,
      },
      onmessage(data, isDone) { // 这个onmessage, onerror都是streamApi.js中定义的
        if(curID !== processID) return
        else if(data.content) { // 这个content是chat.py中的
          emit('addToLastMessage', data.content)
        }
      },
      onerror(err) {
      },
    })
  } catch (err) {
  }
}

function close() {
  ++ processID
  showMic.value = false
}

function handleStop() {
    ++ processID
}

// 子组件给父组件调用，要暴露出去
defineExpose({
  focus,
  close,
})

</script>

<template>
  <!-- 这里.prevent的功能是防止页面刷新 -->
  <form v-if="!showMic" @submit.prevent="handleSend" class="absolute bottom-4 left-2 h-12 w-86 flex items-center">
    <!-- backdrop-blur-sm:毛玻璃  rounded-2xl: 2xl像素越大越圆润 pr-20: 距离右边内边距20，留给发送语音符号 h-full:指的是输入框的高度-->
    <input
        ref="input-ref"
        v-model="message" 
        class="input bg-black/30 backdrop-blur-sm text-white text-base w-full h-full rounded-2xl pr-20"
        type="text"
        placeholder="文本输入..."
    >
    <div @click="handleSend" class="absolute right-2 w-8 h-8 flex justify-center items-center cursor-pointer">
      <SendIcon />
    </div>
    <div @click="showMic = true" class="absolute right-10 w-8 h-8 flex justify-center items-center cursor-pointer">
      <MicIcon />
    </div>
  </form>
  <Microphone
      v-else
      @close="showMic = false"
      @send="handleSend"
      @stop="handleStop"
  />
</template>

<style scoped>

</style>