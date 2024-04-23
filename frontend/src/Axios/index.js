import axios from 'axios';
import Cookies from 'js-cookie';
import { getBasicAuth } from './auth'; // 导入 getBasicAuth 函数

const http = axios.create({
    baseURL: '/', // 修改为根路径
    withCredentials: true,
});

// 在发送请求之前添加CSRF Token和Basic Auth
http.interceptors.request.use((config) => {
    const csrftoken = Cookies.get('csrftoken');
    config.headers['X-CSRFToken'] = csrftoken;
    // 获取并添加basicAuth到请求头
    const basicAuth = getBasicAuth();
    if (basicAuth) {
        config.headers['Authorization'] = basicAuth;
    }
    return config;
}, (error) => {
    return Promise.reject(error);
});

export default http;
