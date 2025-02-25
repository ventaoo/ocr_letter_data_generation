"""
@Dataset: SVHN http://ufldl.stanford.edu/housenumbers/
"""


import os
import h5py
import argparse
from tqdm import tqdm
from PIL import Image

def load_annotations(mat_path):
    """加载.mat文件的标注信息"""
    annotations = []
    with h5py.File(mat_path, 'r') as f:
        digit_struct = f['digitStruct']
        names = digit_struct['name']
        bboxs = digit_struct['bbox']
        num_items = names.shape[0]
        for i in range(num_items):
            # 解析文件名
            name_ref = names[i][0]
            filename = ''.join(chr(c) for c in f[name_ref][()].flatten())
            
            # 解析bbox信息
            bbox_ref = bboxs[i].item()
            bbox_info = f[bbox_ref]
            labels = []
            lefts = []
            tops = []
            widths = []
            heights = []
            for key in ['label', 'left', 'top', 'width', 'height']:
                attr = bbox_info[key]
                # 处理单值和多值情况
                if attr.shape[0] == 1:
                    values = [int(attr[0][0])]
                else:
                    values = [int(f[attr[j][0]][()][0][0]) for j in range(attr.shape[0])]
                # 存储对应属性
                if key == 'label':
                    labels = values
                elif key == 'left':
                    lefts = values
                elif key == 'top':
                    tops = values
                elif key == 'width':
                    widths = values
                elif key == 'height':
                    heights = values
            annotations.append({
                'filename': filename,
                'labels': labels,
                'lefts': lefts,
                'tops': tops,
                'widths': widths,
                'heights': heights
            })
    return annotations

def convert_to_yolo(annotations, images_dir, labels_dir):
    """将标注信息转换为YOLO格式并保存"""
    os.makedirs(labels_dir, exist_ok=True)
    for ann in tqdm(annotations):
        img_path = os.path.join(images_dir, ann['filename'])
        if not os.path.exists(img_path):
            continue  # 跳过缺失的图像
        # 获取图像尺寸
        with Image.open(img_path) as img:
            img_width, img_height = img.size
        # 处理每个标注
        yolo_lines = []
        for label, left, top, width, height in zip(ann['labels'], ann['lefts'], ann['tops'], ann['widths'], ann['heights']):
            # 转换类别ID（10 -> 0）
            class_id = int(label) % 10
            # 转换为0-based坐标
            x_min = left - 1
            y_min = top - 1
            # 计算中心点并归一化
            x_center = (x_min + width / 2) / img_width
            y_center = (y_min + height / 2) / img_height
            w_norm = width / img_width
            h_norm = height / img_height
            # 格式化为YOLO行
            yolo_line = f"{class_id} {x_center:.6f} {y_center:.6f} {w_norm:.6f} {h_norm:.6f}"
            yolo_lines.append(yolo_line)
        # 写入标签文件
        txt_name = os.path.splitext(ann['filename'])[0] + '.txt'
        txt_path = os.path.join(labels_dir, txt_name)
        with open(txt_path, 'w') as f:
            f.write('\n'.join(yolo_lines))


def parse_arguments():
    parser = argparse.ArgumentParser(description="Generate images with random text")

    parser.add_argument('--mat_path', type=str, required=True, help="Path to the mat file")
    parser.add_argument('--images_dir', type=str, required=True, help="Path to the folder containing images")
    parser.add_argument('--labels_dir', type=str, required=True, help="Path to the folder, where you wanna to save labels.")

    return parser.parse_args()


if __name__ == '__main':
    args = parse_arguments()

    print(args)

    annotations = load_annotations(args.mat_path)
    convert_to_yolo(annotations, args.images_dir, args.labels_dir)