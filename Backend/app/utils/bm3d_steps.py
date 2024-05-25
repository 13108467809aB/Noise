import cv2
import numpy as np

# BM3D参数
sigma = 25
Threshold_Hard3D = 2.7 * sigma
First_Match_threshold = 2500
Step1_max_matched_cnt = 16
Step1_Blk_Size = 8
Step1_Blk_Step = 3
Step1_Search_Step = 3
Step1_Search_Window = 39

Second_Match_threshold = 400
Step2_max_matched_cnt = 32
Step2_Blk_Size = 8
Step2_Blk_Step = 3
Step2_Search_Step = 3
Step2_Search_Window = 39

Beta_Kaiser = 2.0


def init(img, blk_size, Beta_Kaiser):
    """初始化数组和凯撒窗"""
    m_shape = img.shape
    m_img = np.zeros(m_shape, dtype=float)
    m_wight = np.zeros(m_shape, dtype=float)
    K = np.kaiser(blk_size, Beta_Kaiser)
    m_Kaiser = np.outer(K, K)
    return m_img, m_wight, m_Kaiser


def Locate_blk(i, j, blk_step, block_Size, width, height):
    """保证blk不超出图像范围"""
    point_x = min(i * blk_step, width - block_Size)
    point_y = min(j * blk_step, height - block_Size)
    return np.array((point_x, point_y), dtype=int)


def Define_SearchWindow(_noisyImg, _BlockPoint, _WindowSize, Blk_Size):
    """定义搜索窗口"""
    point_x, point_y = _BlockPoint
    LX = max(point_x + Blk_Size // 2 - _WindowSize // 2, 0)
    LY = max(point_y + Blk_Size // 2 - _WindowSize // 2, 0)
    RX = min(LX + _WindowSize, _noisyImg.shape[0])
    RY = min(LY + _WindowSize, _noisyImg.shape[1])
    return np.array((LX, LY), dtype=int)


def Step1_fast_match(_noisyImg, _BlockPoint):
    """快速匹配"""
    present_x, present_y = _BlockPoint
    Blk_Size = Step1_Blk_Size
    Search_Step = Step1_Search_Step
    Threshold = First_Match_threshold
    max_matched = Step1_max_matched_cnt
    Window_size = Step1_Search_Window

    blk_positions = np.zeros((max_matched, 2), dtype=int)
    Final_similar_blocks = np.zeros((max_matched, Blk_Size, Blk_Size), dtype=float)

    img = _noisyImg[present_x:present_x + Blk_Size, present_y:present_y + Blk_Size]
    dct_img = cv2.dct(img.astype(np.float64))

    Final_similar_blocks[0, :, :] = dct_img
    blk_positions[0, :] = _BlockPoint

    Window_location = Define_SearchWindow(_noisyImg, _BlockPoint, Window_size, Blk_Size)
    blk_num = (Window_size - Blk_Size) // Search_Step
    blk_num = int(blk_num)
    present_x, present_y = Window_location

    similar_blocks = np.zeros((blk_num ** 2, Blk_Size, Blk_Size), dtype=float)
    m_Blkpositions = np.zeros((blk_num ** 2, 2), dtype=int)
    Distances = np.zeros(blk_num ** 2, dtype=float)

    matched_cnt = 0
    for i in range(blk_num):
        for j in range(blk_num):
            tem_img = _noisyImg[present_x:present_x + Blk_Size, present_y:present_y + Blk_Size]
            if tem_img.shape != (Blk_Size, Blk_Size):
                continue
            dct_Tem_img = cv2.dct(tem_img.astype(np.float64))
            m_Distance = np.linalg.norm((dct_img - dct_Tem_img)) ** 2 / (Blk_Size ** 2)

            if 0 < m_Distance < Threshold:
                similar_blocks[matched_cnt, :, :] = dct_Tem_img
                m_Blkpositions[matched_cnt, :] = (present_x, present_y)
                Distances[matched_cnt] = m_Distance
                matched_cnt += 1
            present_y += Search_Step
        present_x += Search_Step
        present_y = Window_location[1]

    Distances = Distances[:matched_cnt]
    Sort = Distances.argsort()

    Count = min(matched_cnt + 1, max_matched)

    for i in range(1, Count):
        Final_similar_blocks[i, :, :] = similar_blocks[Sort[i - 1], :, :]
        blk_positions[i, :] = m_Blkpositions[Sort[i - 1], :]

    return Final_similar_blocks, blk_positions, Count


def Step1_3DFiltering(_similar_blocks):
    """3D变换及滤波处理"""
    statis_nonzero = 0
    m_Shape = _similar_blocks.shape

    for i in range(m_Shape[1]):
        for j in range(m_Shape[2]):
            tem_Vct_Trans = cv2.dct(_similar_blocks[:, i, j])
            tem_Vct_Trans[np.abs(tem_Vct_Trans[:]) < Threshold_Hard3D] = 0.
            statis_nonzero += tem_Vct_Trans.nonzero()[0].size
            _similar_blocks[:, i, j] = cv2.idct(tem_Vct_Trans)[0]

    return _similar_blocks, statis_nonzero


def Aggregation_hardthreshold(_similar_blocks, blk_positions, m_basic_img, m_wight_img, _nonzero_num, Count, Kaiser):
    """加权累加，得到初步滤波的图片"""
    _shape = _similar_blocks.shape
    block_wight = (1. / _nonzero_num) * Kaiser

    for i in range(Count):
        point = blk_positions[i, :]
        tem_img = (1. / _nonzero_num) * cv2.idct(_similar_blocks[i, :, :]) * Kaiser
        m_basic_img[point[0]:point[0] + _shape[1], point[1]:point[1] + _shape[2]] += tem_img
        m_wight_img[point[0]:point[0] + _shape[1], point[1]:point[1] + _shape[2]] += block_wight


def BM3D_1st_step(_noisyImg):
    """第一步,基本去噪"""
    (width, height) = _noisyImg.shape
    block_Size = Step1_Blk_Size
    blk_step = Step1_Blk_Step
    Width_num = (width - block_Size) // blk_step
    Height_num = (height - block_Size) // blk_step

    Basic_img, m_Wight, m_Kaiser = init(_noisyImg, Step1_Blk_Size, Beta_Kaiser)

    for i in range(int(Width_num + 2)):
        for j in range(int(Height_num + 2)):
            m_blockPoint = Locate_blk(i, j, blk_step, block_Size, width, height)
            Similar_Blks, Positions, Count = Step1_fast_match(_noisyImg, m_blockPoint)
            Similar_Blks, statis_nonzero = Step1_3DFiltering(Similar_Blks)
            Aggregation_hardthreshold(Similar_Blks, Positions, Basic_img, m_Wight, statis_nonzero, Count, m_Kaiser)

    Basic_img[:, :] /= m_Wight[:, :]
    return Basic_img.astype(np.uint8)


def Step2_fast_match(_Basic_img, _noisyImg, _BlockPoint):
    """快速匹配，返回相似的block"""
    present_x, present_y = _BlockPoint
    Blk_Size = Step2_Blk_Size
    Threshold = Second_Match_threshold
    Search_Step = Step2_Search_Step
    max_matched = Step2_max_matched_cnt
    Window_size = Step2_Search_Window

    blk_positions = np.zeros((max_matched, 2), dtype=int)
    Final_similar_blocks = np.zeros((max_matched, Blk_Size, Blk_Size), dtype=float)
    Final_noisy_blocks = np.zeros((max_matched, Blk_Size, Blk_Size), dtype=float)

    img = _Basic_img[present_x:present_x + Blk_Size, present_y:present_y + Blk_Size]
    dct_img = cv2.dct(img.astype(np.float32))
    Final_similar_blocks[0, :, :] = dct_img

    n_img = _noisyImg[present_x:present_x + Blk_Size, present_y:present_y + Blk_Size]
    dct_n_img = cv2.dct(n_img.astype(np.float32))
    Final_noisy_blocks[0, :, :] = dct_n_img

    blk_positions[0, :] = _BlockPoint

    Window_location = Define_SearchWindow(_noisyImg, _BlockPoint, Window_size, Blk_Size)
    blk_num = (Window_size - Blk_Size) // Search_Step
    blk_num = int(blk_num)
    present_x, present_y = Window_location

    similar_blocks = np.zeros((blk_num ** 2, Blk_Size, Blk_Size), dtype=float)
    m_Blkpositions = np.zeros((blk_num ** 2, 2), dtype=int)
    Distances = np.zeros(blk_num ** 2, dtype=float)

    matched_cnt = 0
    for i in range(blk_num):
        for j in range(blk_num):
            tem_img = _Basic_img[present_x:present_x + Blk_Size, present_y:present_y + Blk_Size]
            if tem_img.shape != (Blk_Size, Blk_Size):
                continue
            dct_Tem_img = cv2.dct(tem_img.astype(np.float32))
            m_Distance = np.linalg.norm((dct_img - dct_Tem_img)) ** 2 / (Blk_Size ** 2)

            if 0 < m_Distance < Threshold:
                similar_blocks[matched_cnt, :, :] = dct_Tem_img
                m_Blkpositions[matched_cnt, :] = (present_x, present_y)
                Distances[matched_cnt] = m_Distance
                matched_cnt += 1
            present_y += Search_Step
        present_x += Search_Step
        present_y = Window_location[1]

    Distances = Distances[:matched_cnt]
    Sort = Distances.argsort()

    Count = min(matched_cnt + 1, max_matched)

    for i in range(1, Count):
        Final_similar_blocks[i, :, :] = similar_blocks[Sort[i - 1], :, :]
        blk_positions[i, :] = m_Blkpositions[Sort[i - 1], :]

        present_x, present_y = m_Blkpositions[Sort[i - 1], :]
        n_img = _noisyImg[present_x:present_x + Blk_Size, present_y:present_y + Blk_Size]
        Final_noisy_blocks[i, :, :] = cv2.dct(n_img.astype(np.float64))

    return Final_similar_blocks, Final_noisy_blocks, blk_positions, Count


def Step2_3DFiltering(_Similar_Bscs, _Similar_Imgs):
    """3D维纳变换的协同滤波"""
    m_Shape = _Similar_Bscs.shape
    Wiener_wight = np.zeros((m_Shape[1], m_Shape[2]), dtype=float)

    for i in range(m_Shape[1]):
        for j in range(m_Shape[2]):
            tem_vector = _Similar_Bscs[:, i, j]
            tem_Vct_Trans = np.matrix(cv2.dct(tem_vector))
            Norm_2 = np.float64(tem_Vct_Trans.T * tem_Vct_Trans)
            m_weight = Norm_2 / (Norm_2 + sigma ** 2)
            if m_weight != 0:
                Wiener_wight[i, j] = 1. / (m_weight ** 2 * sigma ** 2)
            tem_vector = _Similar_Imgs[:, i, j]
            tem_Vct_Trans = m_weight * cv2.dct(tem_vector)
            _Similar_Bscs[:, i, j] = cv2.idct(tem_Vct_Trans)[0]

    return _Similar_Bscs, Wiener_wight


def Aggregation_Wiener(_Similar_Blks, _Wiener_wight, blk_positions, m_basic_img, m_wight_img, Count, Kaiser):
    """加权累加，得到滤波后的图片"""
    _shape = _Similar_Blks.shape
    block_wight = _Wiener_wight

    for i in range(Count):
        point = blk_positions[i, :]
        tem_img = _Wiener_wight * cv2.idct(_Similar_Blks[i, :, :])
        m_basic_img[point[0]:point[0] + _shape[1], point[1]:point[1] + _shape[2]] += tem_img
        m_wight_img[point[0]:point[0] + _shape[1], point[1]:point[1] + _shape[2]] += block_wight


def BM3D_2nd_step(_basicImg, _noisyImg):
    """第二步,改进后的分组及协同维纳滤波"""
    (width, height) = _noisyImg.shape
    block_Size = Step2_Blk_Size
    blk_step = Step2_Blk_Step
    Width_num = (width - block_Size) // blk_step
    Height_num = (height - block_Size) // blk_step

    m_img, m_Wight, m_Kaiser = init(_noisyImg, block_Size, Beta_Kaiser)

    for i in range(int(Width_num + 2)):
        for j in range(int(Height_num + 2)):
            m_blockPoint = Locate_blk(i, j, blk_step, block_Size, width, height)
            Similar_Blks, Similar_Imgs, Positions, Count = Step2_fast_match(_basicImg, _noisyImg, m_blockPoint)
            Similar_Blks, Wiener_wight = Step2_3DFiltering(Similar_Blks, Similar_Imgs)
            Aggregation_Wiener(Similar_Blks, Wiener_wight, Positions, m_img, m_Wight, Count, m_Kaiser)

    m_img[:, :] /= m_Wight[:, :]
    return m_img.astype(np.uint8)
