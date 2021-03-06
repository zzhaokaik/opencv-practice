# 对象检测与特征提取
> create by [afterloe](605728727@qq.com)
> version is 1.0
> MIT License

## OpenCV DNN使用OpenVINO加速
[OpenVINO](https://software.intel.com/en-us/openvino-toolkit), 支持raspberry、widnows、linux系统的CPU加速，对OpenCV DNN模块
，其它的API调用都进行了加速。通过DLIE(Deep Learning Inference Engine)对OpenCV进行重新编译。
最新的在线安装web installer, w_openvino_toolkit_p_2018.5.456_online 内置已经编译好的OpenCV4.0.1版本直接配置即可使用！
其配置方式与正常的OpenCV+VS2015开发配置相同，唯一不同的是需要把
`%install_dir%\inference_engine\bin\intel64\Debug`
加到环境变量中去, 然后在调用的时候，直接通过下面这句话就可以使用IE作为计算后台
```python
net.setPreferableBackend(DNN_BACKEND_INFERENCE_ENGINE)
```
对某些模型使用IE作为计算后台时，会报错，需要使用默认后台`net.setPreferableBackend(DNN_BACKEND_OPENCV)`即可

相关链接
[github源码](https://github.com/opencv/dldt)
[开发平台](https://software.intel.com/en-us/articles/OpenVINO-InferEngine)
OpenVINO还提供了一系列的API可以单独解析二进制的模型，实现调用，无须OpenCV DNN支持，安装以后可以去sample文件夹学习即可

## OpenCV DNN解析网络输出结果
### 常用结构
多数时候DNN模块中深度学习网络的输出结果，可能是二维、三维、四维，具体与网络结构有很大的关系，一般常见的图像分类网络，是一个1XN维的
向量，通过`cv.reshape`后就很容易解析。
```python
out = out.flatten()
classId = np.argmax(out)
confidence = out[classId]
```

### SSD/RCNN/Faster-RCNN
该对象检测网络输出为NX7的模式，其解析方式如下
```python
h, w, ch = image.shape
for detection in cv_out[0, 0, :, :]:
    score = float(detection[2])
    obj_index = int(detection[1])
    word = "score:%.2f, %s" % (score, objName[obj_index] if classes else "not_found")
    if 0.5 < score:
        left = detection[3] * w
        top = detection[4] * h
        right = detection[5] * w
        bottom = detection[6] * h
```

### Region
类似YOLO模型，解析方式为
```python
out_names = dnn.getUnconnectedOutLayersNames()
dnn.setInput(data)
outs = dnn.forward(out_names)
class_ids = []
confidences = []
boxes = []
for out in outs:
    for detection in out:
        scores = detection[5:]
        class_id = np.argmax(scores)
        confidence = scores[class_id]
        if 0.5 < confidence:
            center_x = int(detection[0] * w)
            center_y = int(detection[1] * h)
            width = int(detection[2] * w)
            height = int(detection[3] * h)
            left = int(center_x - width / 2)
            top = int(center_y - height / 2)
            class_ids.append(int(class_id))
            confidences.append(float(confidence))
            boxes.append([left, top, width, height])

indices = cv.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
for i in indices:
    i = i[0]
    box = boxes[i]
    left, top, width, height = box[:4]
```

### 图像分割网络
ENet这类，输出的是一个3通道 mask对象，解析方式如下：
```python
n, con, h, w = out.shape
for i in range(con):
    b = np.random.randint(0, 256)
    g = np.random.randint(0, 256)
    r = np.random.randint(0, 256)
    color_lut.append((b, g, r))
max_cl = np.zeros((h, w), dtype=np.int32)
max_val = np.zeros((h, w), dtype=np.float32)

for i in range(con):
    for row in range(h):
        for col in range(w):
            t = max_val[row, col]
            s = out[0, i, row, col]
            if s > t:
                max_val[row, col] = s
                max_cl[row, col] = i

segm = np.zeros((h, w, 3), dtype=np.uint8)
for row in range(h):
    for col in range(w):
        index = max_cl[row, col]
        segm[row, col] = color_lut[index]

h, w = image.shape[:2]
segm = cv.resize(segm, (w, h), None, 0, 0, cv.INTER_NEAREST)
```