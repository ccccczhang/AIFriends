/*
 *  JWT认证
 * 功能：在每个请求头里自动添加`access token`。
 * 然后拦截请求结果，如果返回结果是身份认证失败（401），
 * 则说明`access_token`过期了，
 * 那么先用`cookie`中的`refresh_token`刷新`access_token`。
 * 如果刷新失败则说明`refresh_token`也过期了，
 * 则调用`user.logout()`在浏览器内存中删除登录状态；
 * 如果刷新成功，则重新发送原请求。
*/

import axios from "axios"
import {useUserStore} from "@/stores/user.js";

const BASE_URL = 'http://127.0.0.1:8000'

const api = axios.create({
    baseURL: BASE_URL,
    withCredentials: true,
})

api.interceptors.request.use(config => {
    const user = useUserStore()
    if (user.accessToken) {
        config.headers.Authorization = `Bearer ${user.accessToken}`
    }
    return config
})

let isRefreshing = false
let refreshSubscribers = [] // 存储等待Token刷新的回调函数队列

function subscribeTokenRefresh(callback) {
    refreshSubscribers.push(callback) // callback一般是函数
}

function onRefreshed(token){ // Token刷新成功后，通知所有等待的请求
    refreshSubscribers.forEach(cb => cb(token)) // cb is callback
    refreshSubscribers = []
}

function onRefreshFailed(err) { // Token刷新失败后，通知所有等待的请求
    refreshSubscribers.forEach(cb => cb(null, err)) // 当刷新失败（如Refresh Token也过期）时调用
    refreshSubscribers = [] // 是否成功，都要清空
}

api.interceptors.response.use(
    response => response,
    async error => {
        const user = useUserStore()
        const originalRequest = error?.config // ?.：可选链操作符，表示“如果 error 存在且不是 null 或 undefined，才访问 .config；否则返回 undefined
        if (!originalRequest) {
            return Promise.reject(error)
        }

        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true

            return new Promise((resolve, reject) => {
                subscribeTokenRefresh((token, error) => {
                    if (error) {
                        reject(error)
                    } else {
                        originalRequest.headers.Authorization = `Bearer ${token}`
                        resolve(api(originalRequest))
                    }
                })

                if (!isRefreshing) {
                    isRefreshing = true
                    axios.post(
                        `${BASE_URL}/api/user/account/refresh_token/`,
                        {},
                        {withCredentials: true, timeout: 5000}
                    ).then(res => {
                        user.setAccessToken(res.data.access)
                        onRefreshed(res.data.access)
                    }).catch(error => {
                        user.logout()
                        onRefreshFailed(error)
                        reject(error)
                    }).finally(() => {
                        isRefreshing = false
                    })
                }
            })
        }

        return Promise.reject(error)
    }
)

export default api
