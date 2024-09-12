from abc import ABC, abstractmethod

class OcrBody(ABC):
    @abstractmethod
    def get_ocr_text(self, img):
        pass

    @abstractmethod
    def get_supported_languages(self):
        pass

    @abstractmethod
    def set_language(self, language):
        pass
    @abstractmethod
    def check_language_support():
        pass