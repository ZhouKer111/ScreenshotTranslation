from ocr.body import OcrBody

class OcrContext:
    def __init__(self, body: OcrBody):
        self._body = body

    def set_body(self, body: OcrBody):
        self._body = body

    def get_ocr_text(self, img):
        return self._body.get_ocr_text(img)

    def get_supported_languages(self):
        return self._body.get_supported_languages()

    def set_language(self, language):
        self._body.set_language(language)
