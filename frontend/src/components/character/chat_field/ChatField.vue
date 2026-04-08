<script setup>
import {computed, nextTick, ref, useTemplateRef} from "vue";
import InputField from "@/components/character/chat_field/input_field/InputField.vue";
import CharacterPhotoField from "@/components/character/chat_field/character_photo_field/CharacterPhotoField.vue";
import ChatHistory from "@/components/character/chat_field/chat_history/ChatHistory.vue";


const props = defineProps(['friend']) // defineProps： 从父组件接收哪些参数
const inputRef = useTemplateRef('input-ref')
const modalRef = useTemplateRef('modal-ref')
const chatHistoryRef = useTemplateRef('chat-history-ref')
const history = ref([])


// 暴露模态框
async function showModal() {
  modalRef.value.showModal()

  await nextTick()
  inputRef.value.focus() // 聚焦输入框，就不用每次先点一下输入框了
}
//将模态框背景图片设置成聊天背景
const modalStyle = computed(() => {
  if (props.friend) {
    return {
      backgroundImage: `url(${props.friend.character.background_image})`,
      backgroundSize: 'cover',
      backgroundPosition: 'center',
      backgroundRepeat: 'no-repeat',
    }
  } else {
    return {}
  }
})
// 定义一些函数，给子组件调用修改父组件内容
function handlePushBackMessage(msg) {
  history.value.push(msg)
  chatHistoryRef.value.scrollToBottom()
}

function handleAddToLastMessage(delta) {
  history.value.at(-1).content += delta
  chatHistoryRef.value.scrollToBottom()
}
// 这段是为了实现消息的流式加载（就是刷新以前的消息就像微信）
function handlePushFrontMessage(msg) {
  history.value.unshift(msg)
}

function handclose() {
  inputRef.value.close()
}

defineExpose({
  showModal,
})
</script>

<template>
  <dialog ref="modal-ref" class="modal" @close="handclose">
    <div class="modal-box w-90 h-150" :style="modalStyle">
      <!-- transparent: 透明的 -->
      <button @click="modalRef.close()" class="btn btn-sm btn-circle btn-ghost bg-transparent absolute top-1 right-1">✕</button>
      <ChatHistory
          ref="chat-history-ref"
          v-if="friend"
          :history="history"
          :friendId="friend.id"
          :character="friend.character"
          @pushFrontMessage="handlePushFrontMessage"
      />
      <InputField
          v-if="friend"
          ref="input-ref"
          :friendId="friend.id"
          @pushBackMessage="handlePushBackMessage"
          @addToLastMessage="handleAddToLastMessage"

      />
      <CharacterPhotoField v-if="friend" :character="friend.character" />
    </div>
  </dialog>
</template>

<style scoped>

</style>