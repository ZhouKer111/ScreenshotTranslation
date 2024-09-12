from ocr.body import PaddleOcrBody, EasyOcrBody, MangaOcrBody

class OcrBodyFactory:
    @staticmethod
    def create_ocr_Body(ocr_type, language):
        if ocr_type == 'paddleocr':
            return PaddleOcrBody(language)
        elif ocr_type == 'easyocr':
            return EasyOcrBody(language)
        elif ocr_type == 'mangaocr':
            return MangaOcrBody(language)
        else:
            raise ValueError(f"Unsupported OCR type: {ocr_type}")
