
import requests


class TranslationUtil:
    supported_languages = {
        "English": "en",
        "Chinese(Simplified)": "zh-cn",
        "Chinese(Traditional)": "zh-tw",
        "French": "fr",
        "German": "de",
        "Japanese": "ja",
        "Korean": "ko",
        "Spanish": "es"
    }
    @staticmethod
    def translate_text(text, source_lang='',target_lang=''):
            """
            文本翻译,调用外部的翻译api
            """
            source_lang = TranslationUtil.convert_language(source_lang)
            target_lang = TranslationUtil.convert_language(target_lang)
            url = f"https://findmyip.net/api/translate.php?text={text}&source_lang={source_lang}&target_lang={target_lang}"
            response = requests.get(url)
            try:
                data = response.json()
                print(data)
                if response.status_code == 200:
                    if data['code']== 200:
                        translation = data['data']['translate_result']
                        return translation
                    elif data['code'] == 400:
                        return data['error']
                    else:
                        return "Internal interface is incorrect, contact the developer"
                else:
                    return "Internal interface is incorrect, contact the developer"    
            except requests.JSONDecodeError as e:
                    return f"JSON decoding error: {e}"
            except requests.RequestException as e:
                    return f"Request error: {e}"

    @staticmethod
    def get_supported_languages():
        return list(TranslationUtil.supported_languages.keys())
    
    @staticmethod
    def convert_language(language):
        TranslationUtil.check_supported_language(language)
        return TranslationUtil.supported_languages[language]
    
    @staticmethod
    def check_supported_language(language):
        if language not in TranslationUtil.supported_languages:
            raise ValueError(f"Translate util does not support language '{language}'.")
        