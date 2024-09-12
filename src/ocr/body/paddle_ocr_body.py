from paddleocr import PaddleOCR

from ocr.body import OcrBody
from ocr.util import ImgUtil

class PaddleOcrBody(OcrBody):
    def __init__(self, language):
        self.supported_languages = {
            'English': 'en',
            'Chinese(Simplified)': 'ch',
            'Chinese(Traditional)': 'chinese_cht',
            'Japanese': 'japan',
            'Korean': 'korean',
        }
        self.check_language_support(language)
        self.ocr = PaddleOCR(use_angle_cls=True, lang=language, max_text_length=1000)

    def get_ocr_text(self, img):
        img = ImgUtil.img_to_type(img, 'ndarray')
        result = self.ocr.ocr(img, cls=True)
        texts = [line[1][0] for line in result[0]]
        return ' '.join(texts)

    def get_supported_languages(self):
        return list(self.supported_languages.keys())

    def set_language(self, language):
        self.check_language_support(language)
        self.ocr = PaddleOCR(use_angle_cls=True, lang=self.supported_languages[language], max_text_length=1000)
        
    def check_language_support(self, language):
        if language not in self.supported_languages:
            raise ValueError(f"Self mangaOCR does not support language '{language}'.")