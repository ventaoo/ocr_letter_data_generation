import os
import sys
import argparse
import datetime
import numpy as np
from PIL import Image, ImageFilter, ImageDraw, ImageFont


def generate_unique_name(prefix="file", extension=".txt"):
    current_time = datetime.datetime.now()
    timestamp = current_time.strftime("%Y%m%d_%H%M%S_%f")
    unique_name = f"{prefix}_{timestamp}{extension}"

    return unique_name

def bg_generate(texture_path, w=320, h=320, alpha=50):
    texture_path = os.path.join(texture_path, np.random.choice(os.listdir(texture_path)))
    with Image.open(texture_path) as bg:
        bg_w, bg_h = bg.size

        if bg_w > (w + alpha) and bg_h > (h + alpha):
            start_x = np.random.randint(0, int(bg_w - w))
            end_x = start_x + w
            start_y = np.random.randint(0, int(bg_h - h))
            end_y = start_y + h
            bg = bg.crop((start_x, start_y, end_x, end_y))
        else: bg = bg.resize((w, h))

        # transform
        bg = bg.rotate(np.random.choice([0, 90, 180, 270]))
        if np.random.random() <= 0.5:
            bg = bg.filter(np.random.choice([
                ImageFilter.BLUR, 
                ImageFilter.DETAIL, 
                ImageFilter.EDGE_ENHANCE,
                ImageFilter.GaussianBlur,
            ]))

        return bg

def number_generate(letter_num=10):
    russian_alphabet = [
        'А', 'Б', 'В', 'Г', 'Д', 'Е', 'Ё', 'Ж', 'З', 'И', 'Й', 'К', 'Л', 'М', 'Н', 'О', 'П', 'Р', 'С', 'Т', 'У', 'Ф', 'Х', 'Ц', 'Ч', 'Ш', 'Щ', 'Ъ', 'Ы', 'Ь', 'Э', 'Ю', 'Я',  # 大写字母
        'а', 'б', 'в', 'г', 'д', 'е', 'ё', 'ж', 'з', 'и', 'й', 'к', 'л', 'м', 'н', 'о', 'п', 'р', 'с', 'т', 'у', 'ф', 'х', 'ц', 'ч', 'ш', 'щ', 'ъ', 'ы', 'ь', 'э', 'ю', 'я'   # 小写字母
    ]

    english_alphabet = [
        'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',  # 大写字母
        'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'   # 小写字母
    ]

    numbers = [
        1, 0, 2, 3, 4, 5, 6, 7, 8, 9, '-', '/'
    ]

    numbers.extend(english_alphabet)
    numbers.extend(russian_alphabet)
    return ' '.join(np.random.choice(numbers, letter_num))

def generate(font_path, texture_path, save_path, names, width=320, height=320, alpha=50, letter_num=10, show=False, save=False):
    bg = bg_generate(texture_path, width, height, alpha)
    draw = ImageDraw.Draw(bg)    
    
    font_path = os.path.join(font_path, np.random.choice(os.listdir(font_path)))
    try:
        font = ImageFont.truetype(font_path, (min(bg.size) // 13))  # 设置字体大小
    except IOError:
        font = ImageFont.load_default()  # 如果字体加载失败，则使用默认字体
    
    text = number_generate(np.random.randint(letter_num // 2, letter_num))
    bbox = draw.textbbox((0, 0), text, font=font) # left top (x, y) right bottom (x, y)
    all_w, all_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    start_x, start_y = np.random.randint(alpha // 5, bg.size[0] - all_w - alpha), np.random.randint(alpha // 5, bg.size[1] - all_h - alpha)
    
    random_color = (np.random.randint(0, 255), np.random.randint(0, 255), np.random.randint(0, 255))
    draw.text((start_x, start_y), text, font=font, fill=random_color)

    text_, w = '', 0
    unique_name = generate_unique_name('number', '.txt')
    label_file_name = os.path.join(save_path, 'label', unique_name)
    img_file_name = os.path.join(save_path, 'image', unique_name[:-3] + 'jpg')
    for t in text:
        bbox_padding = 1
        bbox = draw.textbbox((start_x + w, start_y), t, font=font)

        if show and t != ' ':
            draw.rectangle(
                [bbox[0] - bbox_padding, bbox[1] - bbox_padding, bbox[2] + bbox_padding, bbox[3] + bbox_padding],
                outline="red", width=1
            )
        
        if save and t != ' ' and not show:
            if not os.path.exists(os.path.join(save_path, 'label')): 
                os.makedirs(os.path.join(save_path, 'label'))
            if not os.path.exists(os.path.join(save_path, 'image')): 
                os.makedirs(os.path.join(save_path, 'image'))
            with open(label_file_name, 'a') as f:
                label = names.index(t)
                b_w = (bbox[2] + 2 * bbox_padding - bbox[0])
                b_h = (bbox[3] + 2 * bbox_padding - bbox[1])
                b_x = bbox[0] - bbox_padding + b_w * 0.5
                b_y = bbox[1] - bbox_padding + b_h * 0.5
                f.write(f'{label} {b_x / width} {b_y / height} {b_w / width} {b_h / height}\n')

        
        text_ += t
        bbox_ = draw.textbbox((start_x, start_y), text_, font=font)
        w, _ = bbox_[2] - bbox_[0], bbox_[3] - bbox_[1]
    
    if save and not show: 
        bg.save(img_file_name)
    
    return bg

def parse_arguments():
    parser = argparse.ArgumentParser(description="Generate images with random text")

    parser.add_argument('--count', type=int, default=100, help="Count of the generated image")
    parser.add_argument('--font_path', type=str, required=True, help="Path to the folder containing fonts")
    parser.add_argument('--texture_path', type=str, required=True, help="Path to the folder containing texture images")
    parser.add_argument('--save_path', type=str, required=True, help="Path to the folder where images will be saved")
    parser.add_argument('--width', type=int, default=240, help="Width of the generated image (default: 240)")
    parser.add_argument('--height', type=int, default=240, help="Height of the generated image (default: 240)")
    parser.add_argument('--letter_num', type=int, default=8, help="Number of letters for the generated text (default: 8)")
    parser.add_argument('--show', action='store_true', help="Whether to display the generated image (default: False)")
    parser.add_argument('--save', type=bool, default=True, help="Whether to save the generated image (default: True)")

    return parser.parse_args()

if __name__ == '__main__':
    names = [
        '1', '0', '2', '3', '4', '5', '6', '7', '8', '9', '-', '/',
        'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',  # 大写字母
        'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',   # 小写字母
        'А', 'Б', 'В', 'Г', 'Д', 'Е', 'Ё', 'Ж', 'З', 'И', 'Й', 'К', 'Л', 'М', 'Н', 'О', 'П', 'Р', 'С', 'Т', 'У', 'Ф', 'Х', 'Ц', 'Ч', 'Ш', 'Щ', 'Ъ', 'Ы', 'Ь', 'Э', 'Ю', 'Я',  # 大写字母
        'а', 'б', 'в', 'г', 'д', 'е', 'ё', 'ж', 'з', 'и', 'й', 'к', 'л', 'м', 'н', 'о', 'п', 'р', 'с', 'т', 'у', 'ф', 'х', 'ц', 'ч', 'ш', 'щ', 'ъ', 'ы', 'ь', 'э', 'ю', 'я',   # 小写字母
    ]

    args = parse_arguments()

    print(args)

    for _ in range(args.count):
        generate(
            font_path=args.font_path,
            texture_path=args.texture_path,
            save_path=args.save_path,
            names=names,
            width=args.width,
            height=args.height,
            letter_num=args.letter_num,
            show=args.show,
            save=args.save
        )
