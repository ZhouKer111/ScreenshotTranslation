import easyocr

from ocr.body import OcrBody
from ocr.util import ImgUtil

class EasyOcrBody(OcrBody):
    def __init__(self, language):
        self.supported_languages = {
            'English': 'en',
            'Chinese (Simplified)': 'ch_sim',
            'Chinese (Traditional)': 'ch_tra',
            'Japanese': 'ja',
            'Korean': 'ko'
        }
        self.check_language_support(language)
        self.ocr = easyocr.Reader([self.supported_languages[language]])

    def get_ocr_text(self, img):
        img = ImgUtil.img_to_type(img, 'ndarray')
        result = self.ocr.readtext(img)
        return ' '.join([line[1] for line in result])

    def get_supported_languages(self):
        return list(self.supported_languages.keys())

    def set_language(self, language):
        self.check_language_support(language)
        self.ocr = easyocr.Reader([self.supported_languages[language]])
        
    def check_language_support(self, language):
        if language not in self.supported_languages:
            raise ValueError(f"Self easyOCR does not support language '{language}'.")
