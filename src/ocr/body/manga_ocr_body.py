from manga_ocr import MangaOcr
from ocr.body import OcrBody
from ocr.util import ImgUtil

class MangaOcrBody(OcrBody):
    def __init__(self,language):
        self.supported_languages = {
            'Japanese': 'japan'
        }
        self.check_language_support(language)
        self.ocr = MangaOcr()

    def get_ocr_text(self, img):
        img = ImgUtil.img_to_type(img, 'image')
        return self.ocr(img)

    def get_supported_languages(self):
        return list(self.supported_languages.keys())

    def set_language(self, language):
        self.check_language_support(language)
        
    def check_language_support(self, language):
        if language not in self.supported_languages:
            raise ValueError(f"Self mangaOCR does not support language '{language}'.")
