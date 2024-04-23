import { message } from "antd";

const BASIC_AUTH_KEY = 'basicAuth';
const EXPIRATION_KEY = 'authExpiration';

export const setBasicAuth = (auth, durationSeconds) => {
    const expiration = Date.now() + durationSeconds * 1000; // 过期时间戳
    localStorage.setItem(BASIC_AUTH_KEY, auth);
    localStorage.setItem(EXPIRATION_KEY, expiration);
};

export const getBasicAuth = () => {
    const expiration = localStorage.getItem(EXPIRATION_KEY);
    if (expiration && Date.now() < expiration) {
        return localStorage.getItem(BASIC_AUTH_KEY) || '';
    } else {
        // 登录已过期
        message.error('登录已过期，请重新登录！');
        window.location.replace('/'); // 修正重定向
        clearAuth();
        return '';
    }
};

export const clearAuth = () => { // 将 clearAuth 设置为全局函数
    localStorage.removeItem(BASIC_AUTH_KEY);
    localStorage.removeItem(EXPIRATION_KEY);
};
