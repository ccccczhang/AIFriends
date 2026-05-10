<script setup>

import SendIcon from "@/components/character/icons/SendIcon.vue";
import MicIcon from "@/components/character/icons/MicIcon.vue";
import {onUnmounted, ref, useTemplateRef} from "vue";
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

let mediaSource = null;
let sourceBuffer = null;
let audioPlayer = new Audio(); // 全局播放器实例
let audioQueue = [];           // 待写入 Buffer 的二进制队列
let isUpdating = false;        // Buffer 是否正在写入

const initAudioStream = () => {
    audioPlayer.pause();
    audioQueue = [];
    isUpdating = false;

    mediaSource = new MediaSource();
    audioPlayer.src = URL.createObjectURL(mediaSource);

    mediaSource.addEventListener('sourceopen', () => {
        try {
            sourceBuffer = mediaSource.addSourceBuffer('audio/mpeg');
            sourceBuffer.addEventListener('updateend', () => {
                isUpdating = false;
                processQueue();
            });
        } catch (e) {
            console.error("MSE AddSourceBuffer Error:", e);
        }
    });

    audioPlayer.play().catch(e => console.error("等待用户交互以播放音频"));
};

const processQueue = () => {
    if (isUpdating || audioQueue.length === 0 || !sourceBuffer || sourceBuffer.updating) {
        return;
    }

    isUpdating = true;
    const chunk = audioQueue.shift();
    try {
        sourceBuffer.appendBuffer(chunk);
    } catch (e) {
        console.error("SourceBuffer Append Error:", e);
        isUpdating = false;
    }
};

const stopAudio = () => {
    audioPlayer.pause();
    audioQueue = [];
    isUpdating = false;

    if (mediaSource) {
        if (mediaSource.readyState === 'open') {
            try {
                mediaSource.endOfStream();
            } catch (e) {
            }
        }
        mediaSource = null;
    }

    if (audioPlayer.src) {
        URL.revokeObjectURL(audioPlayer.src);
        audioPlayer.src = '';
    }
};

const handleAudioChunk = (base64Data) => {  // 将语音片段添加到播放器队列中
    try {
        const binaryString = atob(base64Data);
        const len = binaryString.length;
        const bytes = new Uint8Array(len);
        for (let i = 0; i < len; i++) {
            bytes[i] = binaryString.charCodeAt(i);
        }

        audioQueue.push(bytes);
        processQueue();
    } catch (e) {
        console.error("Base64 Decode Error:", e);
    }
};

onUnmounted(() => {
    audioPlayer.pause();
    audioPlayer.src = '';
});

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

  initAudioStream()

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
      onmessage(data, isDone) { // 这个 onmessage, onerror都是streamApi.js中定义的
        if (curID !== processID) return

        if (data.content) { // 这个content是chat.py中的
          emit('addToLastMessage', data.content)
        }
        if (data.audio) {
          handleAudioChunk(data.audio)
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
  stopAudio()
}

function handleStop() {
  ++ processID
  stopAudio()
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