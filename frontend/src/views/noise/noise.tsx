import React, {useCallback, useEffect, useState} from "react";
import './noise.css'
import {SearchOutlined} from "@ant-design/icons";
import {Button, Cascader, Col, Collapse, Form, Image, Input, message, Modal, Radio, Row} from "antd";
import http from "../../Axios";

interface FormValues {
    id: string;
    content: string;
}

interface PanelContentProps {
    formName: string;
    noiseType?: string; // Optional property
}

const PanelContent: React.FC<PanelContentProps> = ({formName, noiseType}) => {
    const [form] = Form.useForm<FormValues>();
    const [oldImgUrl, setOldImgUrl] = useState('')
    const [oldShow, setOldShow] = useState(false)
    const [uploading, setUploading] = useState(false)
    const [newShow, setNewShow] = useState('')
    const [endShow, setEndShow] = useState(false)
    const [newLoading, setNewLoading] = useState(false)
    const [noiseMsg, setNoiseMsg] = useState(false)
    const [psnr,setPsnr] = useState(0)
    const [ssim,setSsim] = useState(0)
    const [mse,setMse] = useState(0)
    const onFinish = (values: FormValues) => {
        setUploading(true)
        const imageId = values.id;
        http.get(`/api/get_image_url/${imageId}/`)
            .then(response => {
                const processedImageUrl = handleImageUrl(response.data.image_url);
                setOldImgUrl(processedImageUrl)
                setOldShow(true)
            })
            .catch(error => {
                message.error(error.message, 1)
                setOldShow(true)
            });
    };

    const fresh = () => {
        setUploading(false)
        setEndShow(false)
        form.resetFields()
        setOldImgUrl('')
        setOldShow(false)
    }

    const handleImageUrl = (imageUrl: string | URL) => {
        const url = new URL(imageUrl);
        // 将端口号添加到 URL 中
        url.port = "8000";
        // 返回添加了端口号的 URL 字符串
        return url.toString();
    };
    const handleNoise = (messageText: string, url: string, id: string, noiseMethod: string) => {
        if (id !== '') {
            setNewLoading(true);
            message.success(messageText, 1);
            http.post('/api' + url, {"image_id": id, "method": noiseMethod})
                .then(async response => {
                    message.success('执行成功！', 1);
                    await setNewShow(response.data.noisy_image_url); // 使用处理后的图片 URL
                    const denoisingUrls = [
                        '/gauss_denoising/',
                        '/little/',
                        '/many/',
                        '/NL/',
                        '/Total/',
                        '/bm3d/',
                        '/median/'
                    ];

                    if (denoisingUrls.includes(url)) {
                        setNoiseMsg(true);
                        setPsnr(Number(response.data.psnr))
                        setSsim(Number(response.data.ssim))
                        setMse(Number(response.data.mse))
                    }

                    setEndShow(true)
                    setNewLoading(false);
                })
                .catch(error => {
                    setNewLoading(false);
                    message.error('执行失败！', 1, error);
                    console.log(error);
                });
        } else {
            setNewLoading(false);
            message.error('请先选择图片！', 1);
        }
    };


    const noiseTypes: Record<string, { message: string, url: string }> = {
        Gauss: {message: '执行高斯加噪', url: '/gauss/'},
        little: {message: '执行小波变换去噪', url: '/little/'},
        many: {message: '执行多通道联合分析去噪', url: '/many/'},
        NL: {message: '执行非局部均值降噪', url: '/NL/'},
        Total: {message: '执行总差变换降噪', url: '/Total/'},
        BM3D: {message: '执行BM3D降噪', url: '/bm3d/'},
        pepper: {message: '执行椒噪声加噪', url: '/pepper/'},
        salt: {message: '执行盐噪声加噪', url: '/salt/'},
        Poisson: {message: '执行泊松噪声加噪', url: '/Poisson/'},
        uniform: {message: '执行均匀噪声加噪', url: '/uniform/'},
        motion_blur: {message: '执行运动模糊噪声加噪', url: '/motion_blur/'},
        Gauss_denoising: {message: '执行运高斯滤波降噪', url: '/gauss_denoising/'},
        Median: {message: '执行中值滤波降噪', url: '/median/'},
    };
    const noiseImg = (id: string, noiseType: any, noiseMethod: any) => {
        const contentValue = noiseType
        if (contentValue && contentValue.toString() in noiseTypes) {
            const newTypes = noiseTypes[contentValue.toString()];
            handleNoise(newTypes.message, newTypes.url, id, noiseMethod);
        }
    };

    const down_load_img = async () => {
        if (!newShow) {
            console.log('地址不存在');
            return;
        }

        try {
            const response = await fetch(newShow);
            if (!response.ok) {
                throw new Error('下载成功！');
            }
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = 'downloaded_image.jpg'; // You can set the downloaded file name here
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            console.log('Image downloaded and newShow set to empty string');
        } catch (error) {
            console.error('Error downloading the image:', error);
        }
    };
    const [noiseMethod, setNoiseMethod] = useState("0");
    const clear = () => {
        setEndShow(false)
        setNoiseMsg(false)
    }
    return (
        <div className={'panel-main'}>
            <div className={'noise-old'}>
                <Form
                    requiredMark={false}
                    layout={'vertical'}
                    form={form}
                    name={formName}  // 使用动态名称
                    onFinish={onFinish}
                    style={{maxWidth: 600}}
                    initialValues={{content: 'many', id: ''}}  // 确保这里的初始值类型和 FormValues 类型一致
                >
                    <div style={{display: 'flex', alignItems: 'start', marginBottom: '1rem'}}>
                        <Form.Item
                            label="请填写图片id (可在所有图片页面查询)"
                            name="id"
                            rules={[{required: true, message: '请输入图片id'}]}
                            style={{marginRight: '1rem', flex: 1}}
                        >
                            <Input/>
                        </Form.Item>
                        <Form.Item style={{marginTop: '30px'}}>
                            <Button type="primary" htmlType="submit">提交</Button>
                        </Form.Item>
                    </div>
                    <Form.Item style={{height: '25vh', display: 'flex', justifyContent: 'center'}}>
                        <div className={'old-img-show'}>
                            <div className="card__content" style={{position: 'relative'}}>
                                {oldShow ? (

                                    <Image height={'22vh'}
                                           src={oldImgUrl}
                                           style={{objectFit: 'contain'}}
                                           className={'old-img'}/>
                                ) : (
                                    uploading ? (
                                        <div className={'bg-noise'}>
                                            <div className="loading-noise">
                                                <span></span>
                                                <span></span>
                                                <span></span>
                                                <span></span>
                                                <span></span>
                                            </div>
                                        </div>
                                    ) : (
                                        <div className="placeholder-div">
                                            点击提交后此处预览图片
                                        </div>
                                    )
                                )}
                            </div>
                        </div>
                    </Form.Item>
                    <Form.Item style={{direction: 'rtl'}}>
                        <Button danger onClick={fresh}>清空所选</Button>
                    </Form.Item>
                </Form>
            </div>
            <div className={'noise-divider'}/>
            <div className={'noise-click'}>
                <Row gutter={16} style={{width:"100%"}}>
                    {
                        noiseType === 'many' ? (
                            <Col className="gutter-row" span={24} style={{marginBottom: "10px"}}>
                                <Form.Item
                                    label="选择滤波器（默认为BM3D）"
                                >
                                    <Radio.Group size="small" defaultValue="0" buttonStyle="solid"
                                                 style={{width: "100%"}}
                                                 onChange={(e) => setNoiseMethod(e.target.value)}>
                                        <Radio.Button value="0">BM3D</Radio.Button>
                                        <Radio.Button value="1">中值滤波</Radio.Button>
                                        <Radio.Button value="2">高斯滤波</Radio.Button>
                                        <Radio.Button value="3">非局部均值</Radio.Button>
                                        <Radio.Button value="4">小波变换</Radio.Button>
                                    </Radio.Group>
                                </Form.Item>
                            </Col>
                        ) : null
                    }
                    <Col className="gutter-row" span={24}>
                        <div className={"task-commit"}>
                            <Button type="primary"
                                    onClick={() => noiseImg(form.getFieldsValue().id, noiseType, noiseMethod)}>执行任务</Button>
                            <Button danger
                                    onClick={() => clear()}>清除结果</Button>
                            <Button onClick={() => down_load_img()}>结果保存</Button>
                        </div>
                    </Col>
                    {
                        noiseMsg ? (
                            <Col className="gutter-row" span={24} style={{marginTop:"10%"}}>
                                <div className={"task-msg"}>
                                    <Form.Item
                                        label="峰值信噪比(PSNR):"
                                    >
                                        <span style={{display:"block"}}>{psnr.toFixed(2)}</span>
                                    </Form.Item>
                                    <Form.Item
                                        label="结构相似性指数(SSIM):"
                                    >
                                        <span style={{display:"block"}}>{ssim.toFixed(2)}</span>
                                    </Form.Item>
                                    <Form.Item
                                        label="均方误差(MSE):"
                                    >
                                        <span style={{display:"block"}}>{mse.toFixed(2)}</span>
                                    </Form.Item>
                                </div>
                            </Col>
                        ) : null
                    }
                </Row>
                {/*{*/}
                {/*    noiseType?.[1] === 'Gauss' &&*/}
                {/*    <div></div>*/}
                {/*}*/}
            </div>
            <div className={'noise-divider'}/>
            <div className={'noise-new'}>
                <div className={'new-img-show'}>
                    <div className="card__content"
                         style={{position: "relative", display: 'flex', justifyContent: 'center'}}>
                        {
                            newLoading && (
                                <div style={{
                                    position: 'absolute',
                                    inset: '0',
                                    display: 'flex',
                                    justifyContent: 'center',
                                    alignItems: "center"
                                }}>
                                    <div className="spinner">
                                        <div className="spinner1"></div>
                                    </div>
                                </div>
                            )
                        }
                        {endShow ? (
                            <Image height={'100%'} src={newShow} style={{objectFit: 'contain'}} className={'old-img'}/>
                        ) : (
                            newLoading ? (
                                <div className={'bg-noise'}>
                                    <div className="loading-noise">
                                        <span></span>
                                        <span></span>
                                        <span></span>
                                        <span></span>
                                        <span></span>
                                    </div>
                                </div>
                            ) : (<div className="placeholder-div">执行任务后此处显示执行后的图片</div>)
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

interface Item {
    key: number;
    label: JSX.Element;
    children: JSX.Element;
}

const Noise: React.FC = () => {
    const contentMap = {
            'many': '多通道联合分析降噪',
            'little': '小波变换降噪',
            'NL': '非局部均值降噪',
            'Total': '总差变换降噪',
            'Gauss': '高斯噪声加噪',
            'pepper': '椒噪声加噪',
            'salt': '盐噪声加噪',
            'Poisson': '泊松噪声加噪',
            'uniform': '均匀噪声加噪',
            'motion_blur': '运动模糊噪声加噪',
            'BM3D': 'BM3D降噪',
            'Gauss_denoising': '高斯滤波降噪',
            'Median': '中值滤波降噪'
        },
        [allPanel, setAllPanel] = useState<number[]>([]),
        [isModalOpen, setIsModalOpen] = useState(false),
        [form] = Form.useForm(), [items, setItems] = useState<Item[]>([]),
        [isShow, setIsShow] = useState(false),
        loadPanel = useCallback(() => {
            http.get('/api/get_panels/')
                .then(response => {
                    const panels = response.data.panels;
                    if (panels.length === 0) {
                        message.info('暂无可用任务！', 1);
                    }
                    const initializedItems = panels.map((panel: any, index: number) => ({
                        key: index,
                        label: (
                            <div className={"task"}>
                            <span className={'panels-span'}>
                                <span className={"panels-title"}>{panel.note}</span>
                                {panel['content'][0] === 'Noise_reduction' ? (
                                    <span
                                        className={'panel-label'}>{contentMap[panel['content'][1] as keyof typeof contentMap]}</span>
                                ) : (
                                    <span
                                        className={'panel-labels'}>{contentMap[panel['content'][1] as keyof typeof contentMap]}</span>
                                )}
                            </span>
                                <button className="btn-item" style={{backgroundColor: "red"}}
                                        onClick={(e) => removePanel(index, e)}>
                                    删除
                                </button>
                            </div>
                        ),
                        children: <PanelContent formName={`control-hooks-${index}`} noiseType={panel.content[1]}/>,
                    }));
                    setItems(initializedItems);
                    const panelKeys = initializedItems.map((item: any) => item.key);
                    setAllPanel(panelKeys);
                    setIsShow(true);
                })
                .catch(error => {
                    setIsShow(true);
                    console.error('获取页面任务失败:', error);
                });
        }, []);  // 确保 `loadPanel` 仅在特定依赖变化时重新创建

    useEffect(() => {
        loadPanel();
    }, []);
    const showModal = () => {
        setIsModalOpen(true);
    };

    const handleCancel = () => {
        setIsModalOpen(false);
    };

    const handleChange = (value: (string | number)[]) => {
        console.log(value);
    };

    const onFinish = (values: any) => {
        const postMsg = {"note": values.note, "content": values.content}
        http.post('/api/save_panels/',
            postMsg
        )
            .then(response => {
                message.success('任务新建成功！', 1);
                loadPanel()
                // 关闭对话框
                setIsModalOpen(false);
            })
            .catch(error => {
                message.error('任务新建失败！', 1);
                console.log(error)
            });
        // 在此处执行表单数据验证
        // 如果验证通过，请继续提交数据
    };

    const handleOk = () => {
        form.validateFields().then(async () => {
            // 表单验证通过
            const values = await form.getFieldsValue();
            await onFinish(values);
            form.setFieldsValue({note: '', content: []});
        }).catch(errorInfo => {
            // 表单验证失败
            message.error('信息未完整录入，请检查输入。', 1, errorInfo);
        });
    };

    const removeItems = (panelCheck: number[]) => {
        message.info('正在删除···', 1)
        const deleteData = {
            indexes: panelCheck // 将索引数组放在请求的数据体中
        };
        http.delete('/api/delete_panels/', {data: deleteData}) // 将数据放在 data 属性中
            .then(response => {
                message.success('任务删除成功！', 1);
                loadPanel();
            })
            .catch(error => {
                message.error('任务删除失败！', 1);
                console.log(error)
            });
    };


    const removePanel = (key: number, event: React.MouseEvent<HTMLButtonElement>): void => {
        message.info('正在删除···', 1)
        event.stopPropagation(); // 阻止事件冒泡
        const deleteData = {
            indexes: [key]  // 将索引数组放在请求的数据体中
        };
        http.delete('/api/delete_panels/', {data: deleteData}) // 将数据放在 data 属性中
            .then(response => {
                message.success('任务删除成功！', 1);
                loadPanel();
            })
            .catch(error => {
                message.error('任务删除失败！', 1);
                console.log(error)
            });
    }
    const search = () => {
        message.error('接口还未实现', 1);
    }
    return (
        <React.Fragment>
            <Modal title="新建任务" open={isModalOpen} onOk={handleOk} onCancel={handleCancel}>
                <Form
                    requiredMark={false}
                    form={form}
                    name="control-hooks"
                    onFinish={onFinish}
                    style={{maxWidth: 600}}
                    initialValues={{note: '', content: []}} // 设置选择器默认值
                >
                    <Form.Item name="note" label="任务名称" rules={[{required: true, message: '请输入任务名称'}]}>
                        <Input name="note-input"/>
                    </Form.Item>
                    <Form.Item name="content" label="任务内容" rules={[{required: true, message: '请选择任务内容'}]}>
                        <Cascader
                            options={[
                                {
                                    value: 'Noise_reduction',
                                    label: '降噪',
                                    children: [
                                        {value: 'many', label: '多通道联合分析降噪'},
                                        {value: 'little', label: '小波变换'},
                                        {value: 'NL', label: '非局部均值降噪'},
                                        {value: 'Total', label: '总差变换降噪'},
                                        {value: 'BM3D', label: 'BM3D降噪'},
                                        {value: 'Gauss_denoising', label: '高斯滤波降噪'},
                                        {value: 'Median', label: '中值滤波降噪'},
                                    ]
                                },
                                {
                                    value: 'Noise',
                                    label: '加噪',
                                    children: [
                                        {value: 'Gauss', label: '高斯噪声'},
                                        {value: 'pepper', label: '椒噪声'},
                                        {value: 'salt', label: '盐噪声'},
                                        {value: 'Poisson', label: '泊松噪声'},
                                        {value: 'uniform', label: '均匀噪声'},
                                        {value: 'motion_blur', label: '运动模糊噪声'},
                                    ]
                                }
                            ]}
                            onChange={handleChange}
                            placeholder="请选择"
                        />
                    </Form.Item>
                </Form>
            </Modal>
            <div className={"noise-main"}>
                <div className={"noise-nav"}>
                    <div className={"nav-logo"}>
                    </div>
                    <div className={"nav-search"}>
                        <div className="form">
                            <input className="input" placeholder="请输入搜索信息" required type="text"/>
                            <span className="input-border"></span>
                        </div>
                        <Button type="primary" shape="circle" icon={<SearchOutlined/>} onClick={() => search()}/>
                    </div>
                    <div className={"nav-btn"}>
                        <button className="btn" style={{backgroundColor: "#61B591"}} onClick={showModal}>新建
                        </button>
                        <button className="btn" style={{backgroundColor: "red"}} onClick={() => removeItems(allPanel)}>
                            删除全部
                        </button>
                    </div>
                </div>
                <div className={"noise-container"}>
                    {isShow ? (
                        items.length > 0 ? (
                            <Collapse
                                accordion
                                items={items}
                                expandIconPosition={'end'}
                            />
                        ) : (
                            <div className={"task-null"}>空任务</div>
                        )
                    ) : (
                        <div className={'bg-noise'}>
                            <div className="loading-noise">
                                <span></span>
                                <span></span>
                                <span></span>
                                <span></span>
                                <span></span>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </React.Fragment>
    );
}
export default Noise;
