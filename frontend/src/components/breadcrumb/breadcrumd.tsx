import React from 'react';
import { Breadcrumb } from 'antd';
import { Link, useLocation } from 'react-router-dom';
import {HomeOutlined} from "@ant-design/icons";

const breadcrumbNameMap: { [key: string]: string } = {
    '/home/frontpage': '首页',
    '/home/all': '所有图片',
    '/home/noise': '图像降噪',
};

const MyBreadcrumbs = () => {
    const location = useLocation();
    const pathSnippets = location.pathname.split('/').filter(i => i !== '');

    const breadcrumbItems = pathSnippets.map((_, index) => {
        const url = `/${pathSnippets.slice(0, index + 1).join('/')}`;
        return breadcrumbNameMap[url] ? (
            <Breadcrumb.Item key={url}>
                <Link to={url}>{breadcrumbNameMap[url]}</Link>
            </Breadcrumb.Item>
        ) : null;
    });

    return (
        <Breadcrumb style={{margin:'10px 0'}}>
            <Breadcrumb.Item>
                <Link to={'/home/frontpage'}><HomeOutlined /></Link>
            </Breadcrumb.Item>
            {breadcrumbItems}
        </Breadcrumb>
    );
};

export default MyBreadcrumbs;
