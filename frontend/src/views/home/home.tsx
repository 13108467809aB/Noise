import React, {useState} from 'react';
import {ClusterOutlined, CompressOutlined, DesktopOutlined} from '@ant-design/icons';
import './home.css';
import {Link, Outlet, useLocation, useNavigate} from 'react-router-dom'; // 使用 Link 替换 Menu.Item
import {Button, message, Modal} from 'antd';
import http from "../../Axios";

const mainMenu = [
    {label: '首页', key: 'frontpage', path: '/home/frontpage', icon: <DesktopOutlined/>},
    {label: '所有图片', key: 'all', path: '/home/all', icon: <CompressOutlined/>},
    {label: '图片处理', key: 'noise', path: '/home/noise', icon: <ClusterOutlined/>},
];

const Home: React.FC = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const [userState,setUserState] = useState(false);
    const showModal = () => {
        setUserState(true);
    };

    const handleOk = () => {
        setUserState(false);
    };

    const handleCancel = () => {
        setUserState(false);
    };
    const logout = () => {
        message.info('正在退出账号...');
        http.post(
            '/api/logout/',
            null, // 在这里传递 null 作为请求主体
            {
                headers: {},
                withCredentials: true,
            }
        )
            .then(response => {
                // 清空 localStorage
                localStorage.clear();

                // 清空 cookie
                document.cookie = '';

                // 跳转到首页
                navigate('/');

                // 显示成功退出的消息
                message.success(response.data.message);
            })
            .catch(error => {
                if (error.response) {
                    message.error(error.response.data.detail);
                } else {
                    message.error(error.message);
                }
            });
    }

    return (
        <div className="home-main">
            <nav className="navbar">
                <div className="logo"></div>
                <div className={"menu"}>
                    <ul className={"menu-ul"}>
                        {mainMenu.map((item) => (
                            <li className={location.pathname === item.path ? 'active' : ''} key={item.key}>
                                <Link to={item.path} style={{display:"flex",alignItems:"end"}}>
                                    {item.icon}
                                    <span className={'menu-span'}>{item.label}</span>
                                </Link>
                            </li>
                        ))}
                    </ul>
                </div>
                <div className="user">
                    <Button shape="circle" onClick={showModal}>User</Button>
                </div>
                <Modal
                    title="当前登录用户信息"
                    open={userState}
                    onOk={handleOk}
                    onCancel={handleCancel}
                    footer={[
                        <Button key="back" onClick={logout}>退出登录</Button>,
                        <Button key="submit" type="primary" >
                            保存信息
                        </Button>, ]}
                >
                    <p>用户信息页面</p>
                </Modal>
            </nav>
            <div className="home-body">
                <div className={"body-main"}>
                    <Outlet/>
                </div>
            </div>
        </div>
    );
};

export default Home;
