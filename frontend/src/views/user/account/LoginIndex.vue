<script setup>

import {ref} from "vue";
import {useUserStore} from "@/stores/user.js";
import {useRouter} from "vue-router";
import api from "@/js/http/api.js";

const username = ref('') //ref是响应式变量，根据后面内容调整输出
const password = ref('')
const errorMassage = ref('')

const user = useUserStore()
const router = useRouter() //跳转,不同于route

async function handleLogin(){
  errorMassage.value = ''
  if(!username.value.trim()){
    errorMassage.value = ref('用户名不能为空')
  }else if(!password.value.trim()){
    errorMassage.value = ref('密码不能为空')
  }else{
    try{
      const res = await api.post('/api/user/account/login/',{
        username: username.value,
        password: password.value
      })
      const data = res.data

      if(data.result === 'success') { //登录成功后页面跳转到主页
        user.setAccessToken(data.access)
        user.setUserInfo(data)
        await router.push({
          name: 'homepage-index'
        })
      }
      else{
        errorMassage.value = data.result
      }
    }catch (err){
      console.log(err)
    }
  }
}
</script>


<template>
  <div class="flex justify-center mt-30">
    <form @submit.prevent="handleLogin" class="fieldset bg-base-200 border-base-300 rounded-box w-xs border p-4">
      <label class="label">用户名</label>
      <input v-model="username" type="text" class="input" placeholder="用户名" />

      <label class="label">密码</label>
      <input v-model="password" type="password" class="input" placeholder="密码" />

      <p v-if="errorMassage" class="text-sm text-red-500 mt-1">{{errorMassage}}</p>

      <button class="btn btn-neutral mt-4">登录</button>

      <div class="flex justify-end">
        <RouterLink :to="{name: 'user-account-register-index'}" class="btn btn-sm btn-ghost text-gray-500">
          注册
        </RouterLink>
      </div>
    </form>
  </div>
</template>

<style scoped>

</style>