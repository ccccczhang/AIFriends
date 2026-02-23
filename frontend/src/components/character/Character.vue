<script setup>

//defineProps这个组件可以接收父组件SpaceIndex传进来的数据
import {ref} from "vue";
import UpdateIcon from "@/components/character/icons/UpdateIcon.vue";
import {useUserStore} from "@/stores/user.js";
import RemoveIcon from "@/components/character/icons/RemoveIcon.vue";
import api from "@/js/http/api.js";

const props = defineProps(['character', 'canEdit'])
const isHover = ref(false) // Hover: 悬停，鼠标是否悬停在某处
const user = useUserStore()
// 接受父组件的remove操作
const emit = defineEmits(['remove'])

// 实现在后端删除的逻辑
async function handleRemoveCharacter() {
  try{
    const res = await api.post('/api/create/character/remove/', {
      character_id: props.character.id,
    })
    if (res.data.result === 'success') {
      emit('remove', props.character.id)
    }
  } catch (err) {
  }
}
</script>

<template>
  <!-- 用一个div包起来两个div为了展示角色和作者，防止到同一行展示    -->
  <div>
    <div class="avatar cursor-pointer" @mouseover="isHover=true" @mouseout="isHover=false">
      <div class="w-60 h-100 rounded-2xl relative">       <!--transition：过渡，当元素的 transform 发生变化时用 300ms 的时间，平滑地过渡到新状态 -->
        <img :src="character.background_image" class="transition-transform duration-300" :class="{'scale-120': isHover}" alt="">
        <!-- 后面代码是过渡色的意思 -->
        <div class="absolute left-0 top-50 w-60 h-50 bg-linear-to-t from-black/40 to-transparent"></div>
        <!-- 修改character -->
        <div v-if="canEdit && character.author.user_id === user.id" class="absolute right-0 top-50">
          <RouterLink :to="{name: 'update-character', params:{character_id: character.id}}", class="btn btn-circle btn-ghost bg-transparent">
          <UpdateIcon />
          </RouterLink>
          <!-- transparent: 透明的 -->
          <button @click="handleRemoveCharacter"  class="btn btn-circle btn-ghost bg-transparent">
            <RemoveIcon />
          </button>
        </div>
        <!-- 添加角色信息 -->
        <div class="absolute left-4 top-54 avatar">
          <div class="w-16 rounded-full ring-3 ring-white">
            <img :src="character.photo" alt="">
          </div>
        </div>
        <div class="absolute left-24 top-58 right-2 text-white font-bold line-clamp-1 break-all">
          {{ character.name }}
        </div>
        <div class="absolute left-4 top-72 right-2 text-white line-clamp-4 break-all">
          {{ character.profile }}
        </div>
      </div>
    </div>
    <RouterLink :to="{name: 'user-space-index', params:{user_id: character.author.user_id}}" class="flex items-center mt-4 gap-2 w-60">
      <div class="avatar">
        <div class="w-7 rounded-full">
          <img :src="character.author.photo" alt="">
        </div>
      </div>
      <div class="text-sm line-clamp-1 break-all">{{ character.author.username }}</div>
    </RouterLink>
  </div>
</template>

<style scoped>

</style>