import React, {useState} from 'react';
import './login.css';
import {Button, Card, Checkbox, Form, type FormProps, Input, message} from 'antd';
import FadeInOut from "../../components/transform/animation";
import {useNavigate} from "react-router-dom";
import axios from "axios";
import {setBasicAuth} from "../../Axios/auth";

type FieldType = {
    username?: string;
    password?: string;
    remember?: string;
};

const Login: React.FC = () => {
    const [isLogin, SetIsLogin] = useState(false);
    const navigate = useNavigate();
    const onFinish: FormProps<FieldType>["onFinish"] = (values) => {
        const basicAuth = 'Basic ' + btoa(`${values.username}:${values.password}`);
        message.info('登陆中...')
        SetIsLogin(true);
        axios.post(
            '/api/login/',
            {"username": values.username, "password": values.password},
            {
                headers: {
                    Authorization: basicAuth,
                }, withCredentials: true
            } // Include credentials (cookies) in the request
        )
            .then(response => {
                if (response.data.message === 'Login successful') {
                    SetIsLogin(false);
                    setBasicAuth(basicAuth, 604800);
                    message.success('账号成功登录！',1)
                    navigate('/home/frontpage')
                }
            })
            .catch(error => {
                if (error.response) {
                    SetIsLogin(false);
                    message.error(error.response.data,1);
                } else {
                    SetIsLogin(false);
                    message.error('Error:', error.message);
                }
            })
    };

    const onFinishFailed: FormProps<FieldType>["onFinishFailed"] = (errorInfo) => {
        console.log('Failed:', errorInfo);
    };
    return (
        <div className="login">
            {
                isLogin &&
                <div className={'bg'}>
                    <div className="loading">
                        <span></span>
                        <span></span>
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
            }
            <div className={"login-left"}></div>
            <div className={"login-right"}>
                <FadeInOut>
                    <Card style={{width: '30vw', maxWidth: '768px'}}>
                        <span>用户登录</span>
                        <Form
                            requiredMark={false}
                            name="basic"
                            labelCol={{span: 8}}
                            wrapperCol={{span: 16}}
                            style={{maxWidth: 600}}
                            initialValues={{remember: true}}
                            onFinish={onFinish}
                            onFinishFailed={onFinishFailed}
                            autoComplete="off"
                        >
                            <Form.Item<FieldType>
                                label="用户名"
                                name="username"
                                required={false}
                                rules={[{required: true, message: '请输入用户名!'}]}
                            >
                                <Input/>
                            </Form.Item>

                            <Form.Item<FieldType>
                                label="密码"
                                name="password"
                                required={false}
                                rules={[{required: true, message: '请输入密码!'}]}
                            >
                                <Input.Password/>
                            </Form.Item>

                            <Form.Item<FieldType>
                                name="remember"
                                valuePropName="checked"
                                wrapperCol={{offset: 8, span: 16}}
                            >
                                <Checkbox>记住账号</Checkbox>
                            </Form.Item>

                            <Form.Item wrapperCol={{offset: 8, span: 16}}>
                                <Button type="primary" htmlType="submit">
                                    登录
                                </Button>
                            </Form.Item>
                        </Form>
                    </Card>
                </FadeInOut>
            </div>
        </div>
    );
}

export default Login;
