import React from 'react';
import { Routes, Route, BrowserRouter } from 'react-router-dom';
import Login from '../views/login/login';
import Home from '../views/home/home';
import MyBreadcrumb from '../components/breadcrumb/breadcrumd';
import Frontpage from '../views/frontpage/frontpage';
import Noise from '../views/noise/noise';
import All from '../views/all/all';

function RouterView() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<Login />} />
                <Route path="/home" element={<Home />}>
                    {/* 嵌套路由 */}
                    <Route path="frontpage" element={<Frontpage />} /> {/* 相对路径 */}
                    <Route path="all" element={<All />} />
                    <Route path="noise" element={<Noise />} />
                </Route>
                <Route path="/:path" element={<MyBreadcrumb />} />
                {/* 其他路由配置 */}
            </Routes>
        </BrowserRouter>
    );
}

export default RouterView;
