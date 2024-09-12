

import os
from PIL import Image
import numpy as np


class ImgUtil:
    @staticmethod
    def img_to_type(img, to_type):
        """
        转换图片格式
        """
        # 先将传进来的图片统一成Image
        if os.path.isfile(img):
            img = Image.open(img)
        elif isinstance(img, np.ndarray) and img.ndim == 3 and img.shape[2] in [3, 4]:
            img = Image.fromarray(img)
        elif isinstance(img, Image.Image):
            img = img
        else:
            print('Image not supported.')
            return None
        
        # 根据to_type转为所需要的图片格式
        match to_type:
            case 'image':
                return img
            case 'ndarray':
                img_np = np.array(img)
                return img_np
            case _:
                print(f'Can not convert to type:{to_type}.')
                return None