import {defineStore} from "pinia";
import {ref} from "vue";

export const useUserStore = defineStore('user', () => {
    const id = ref(0)
    const username = ref('')
    const photo = ref('http://127.0.0.1:8000/media/user/photos/default.png')
    const profile = ref('')
    const accessToken = ref('')
    const hasPulledUserInfo = ref(false)

    function isLogin(){
        return !!accessToken.value //这里切记一定要带value，不带不会报错，条件就会永真
    }

    function setAccessToken(token){
        accessToken.value = token
    }

    function setUserInfo(data){
        id.value = data.user_id
        username.value = data.username
        photo.value = data.photo
        profile.value = data.profile
    }

    function logout(){
        id.value = 0
        username.value = ''
        photo.value = ''
        profile.value = ''
        accessToken.value = ''
    }

    function setHasPulledUserInfo(newStatus){
        hasPulledUserInfo.value = newStatus
    }

    return {
        id,
        username,
        photo,
        profile,
        accessToken, //千万不要忘了！！！不会报错
        isLogin,
        setAccessToken,
        setUserInfo,
        logout,
        hasPulledUserInfo,
        setHasPulledUserInfo
    }

})