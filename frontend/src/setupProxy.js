const { createProxyMiddleware } = require("http-proxy-middleware");
const baseURL = 'http://127.0.0.1:8000/'
module.exports = function (app) {
    app.use(
        "/api",
        createProxyMiddleware({
            target: baseURL, // 后台服务地址以及端口号
            changeOrigin: true, // 是否开启代理
            pathRewrite: {
                "/api": "", // 代理名称
            },
        })
    );
};
