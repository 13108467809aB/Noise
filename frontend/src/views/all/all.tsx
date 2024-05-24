import React, {useState, useEffect} from "react";
import {Button, Card, Col, Form, Image, Input, message, Modal, Row, Upload} from 'antd';
import './all.css';
import {PlusOutlined} from "@ant-design/icons";
import http from "../../Axios";


const All: React.FC = () => {
    const [imgUrl, setImgUrl] = useState<{ url: string, alt: string, key: string }[]>([]);
    const [uploadVisible, setUploadVisible] = useState(false);
    const [fileList, setFileList] = useState<any[]>([]);
    const [allShow, setAllShow] = useState(false);

    useEffect(() => {
        fetchImages();
    }, []);

    const fetchImages = () => {
        setAllShow(false);
        http.get('/api/list/')
            .then(response => {
                const imagesData = response.data;
                const images = imagesData.map((image: any) => ({
                    url: image.image_file_url,
                    alt: image.image_name,
                    key: image.image_id.toString()
                }));
                setAllShow(true);
                setImgUrl(images);
            })
            .catch(error => {
                console.error('Error fetching images:', error);
            });
    };

    const handleUpload = () => {
        setUploadVisible(true);
    };

    const handleOk = () => {
        form
            .validateFields()
            .then((values) => {
                onFinish(values);
            })
            .catch((errorInfo) => {
                console.log('Validation failed:', errorInfo);
            });
    };

    const handleCancel = () => {
        form.resetFields();
        setUploadVisible(false);
        setFileList([]); // 清空fileList状态
    };

    const onFinish = (values: any) => {
        if (fileList.length === 0) {
            message.error('请上传文件',1);
            return;
        }
        const formData = new FormData();
        formData.append("image_name", values.imglabel);
        formData.append("image_file", fileList[0].originFileObj);
        formData.append("uploader", "1");
        http.post('/api/upload/', formData)
            .then(response => {
                message.success('图片上传成功！',1);
                form.resetFields();
                setUploadVisible(false);
                fetchImages()
            })
            .catch(error => {
                message.error('图片上传失败！',1);
                console.log(error)
            });
    };

    const [form] = Form.useForm();

    const normFile = (e: any) => {
        if (Array.isArray(e)) {
            return e;
        }
        return e && e.fileList;
    };

    const handleChange = (info: any) => {
        setFileList(info.fileList);
    };

    const imgDelete = (id: string) => {
        setAllShow(false);
        message.info('删除正在执行中···')
        http.delete(`/api/delete/${id}/`)
            .then(response => {
                 fetchImages();
                message.success('图片删除成功！',1);
             })
            .catch(error => {
                 message.error('图片删除失败！',1);
                setAllShow(true);
                console.log(error)
             });
    }

    const downloadImage = (imageUrl: string, imageName: string) => {
        // 使用 Fetch API 获取图片文件内容
        fetch(imageUrl)
            .then(response => response.blob())
            .then(blob => {
                // 创建 Blob URL
                const imageUrl = URL.createObjectURL(blob);
                // 创建一个虚拟的链接元素
                const link = document.createElement('a');
                // 设置链接的href属性为图片的Blob URL
                link.href = imageUrl;
                // 设置下载的文件名
                link.download = imageName;
                // 将链接添加到页面中，但不显示
                link.style.display = 'none';
                // 将链接添加到页面中
                document.body.appendChild(link);
                // 模拟点击链接，触发下载操作
                link.click();
                // 下载完成后，移除链接元素
                document.body.removeChild(link);
            })
            .catch(error => {
                console.error('Error downloading image:', error);
            });
    };

    return (
        <React.Fragment>
            <div className={"all"}>
                { allShow ? (
                <Row gutter={10} className={"all-main"}>
                    {imgUrl.map((item, index) => (
                        <Col span={6}
                             style={{
                                 margin: '10px 0',
                                 height: '40vh',
                             }}
                             key={item.key}>
                            <Card style={{width: '100%', height: '40vh'}} className={'all-card'}>
                                <Row gutter={16} className={"all-main-row"}>
                                    <Col span={24} style={{
                                        width: "100%",
                                        height: "60%",
                                        display: 'flex',
                                        justifyContent: 'center'
                                    }}>
                                        <Image key={index} height={'100%'} style={{objectFit: 'contain'}}
                                               src={item.url} alt={item.alt} className={'col-img'}/>
                                    </Col>
                                    <Col span={24} style={{height: '11%', marginTop: '2%', marginBottom: '2%',display:'flex',justifyContent:'center',gap:'10px',alignItems:'center'}}>
                                        <span className={'img-labels'}>图片id：{item.key}</span>
                                        <span className={'img-label'}>图片名称：{item.alt}</span>
                                    </Col>
                                    <Col span={24} style={{height: '21%', marginTop: '2%', marginBottom: '2%'}}>
                                        <div style={{width: "100%",height:'100%', display: "flex", justifyContent: "center",alignItems:"center",gap:'10px'}}>
                                            <Button type="primary" onClick={() => downloadImage(item.url, item.alt)}>保存图片</Button>
                                            <Button danger onClick={()=>imgDelete(item.key)}>删除图片</Button>
                                        </div>
                                    </Col>
                                </Row>
                            </Card>
                        </Col>
                    ))}
                    <Col span={6} style={{
                        margin: '10px 0',
                        height: '40vh'
                    }}>
                        <Card style={{width: '100%', height: '100%'}} className={"upload-ant-card-body"}>
                            <Col span={24} style={{
                                width: "100%",
                                height: "100%",
                                display: 'flex',
                                justifyContent: 'center',
                                alignItems: 'center'
                            }}>
                                <button className={'up-btn'} onClick={handleUpload}>上传图片</button>
                            </Col>
                        </Card>
                    </Col>
                </Row>
                ) : (
                    <div className={'bg-all'}>
                        <div className="loading-all">
                            <span></span>
                            <span></span>
                            <span></span>
                            <span></span>
                            <span></span>
                        </div>
                    </div>
                )
                }
            </div>
            <Modal
                title="上传图片"
                open={uploadVisible}
                onOk={handleOk}
                onCancel={handleCancel}
                footer={[
                    <Button key="back" onClick={handleCancel}>取消</Button>,
                    <Button key="submit" type="primary" onClick={handleOk}>
                        确认
                    </Button>, ]}
            >
                <Form
                    requiredMark={false}
                    form={form}
                    name="wrap"
                    labelCol={{flex: '110px'}}
                    labelAlign="left"
                    labelWrap
                    wrapperCol={{flex: 1}}
                    colon={false}
                    style={{maxWidth: 600}}
                    onFinish={onFinish}
                >
                    <Form.Item
                        label="图片名称"
                        name="imglabel"
                        rules={[{required: true, message: '请填写图片名称'}]}
                    >
                        <Input/>
                    </Form.Item>
                    <Form.Item
                        label="图片文件"
                        name="upload"
                        valuePropName="fileList"
                        getValueFromEvent={normFile}
                        rules={[{required: true, message: '请上传图片文件'}]}
                    >
                        <Upload
                            listType="picture-card"
                            fileList={fileList}
                            onChange={handleChange}
                        >
                            {fileList.length === 0 && <div>
                                <PlusOutlined/>
                                <div style={{marginTop: 8}}>上传</div>
                            </div>}
                        </Upload>
                    </Form.Item>
                </Form>
            </Modal>
        </React.Fragment>
    )
}

export default All;
