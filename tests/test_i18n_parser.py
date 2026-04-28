import unittest
from i18n_parser import I18NParser # 구현될 클래스

class TestI18NParser(unittest.TestCase):
    def setUp(self):
        self.parser = I18NParser()

    def test_full_data_parsing(self):
        """정상적인 다국어 데이터 파싱 테스트"""
        raw_data = {"ko": "안녕하세요", "en": "Hello"}
        result = self.parser.parse(raw_data)
        self.assertEqual(result["ko"], "안녕하세요")
        self.assertEqual(result["en"], "Hello")

    def test_missing_field_handling(self):
        """필드 누락 시 [MISSING_TRANSLATION] 태그 삽입 테스트"""
        raw_data = {"ko": "반갑습니다"} # en 누락
        result = self.parser.parse(raw_data)
        self.assertEqual(result["ko"], "반갑습니다")
        self.assertEqual(result["en"], "[MISSING_TRANSLATION]")

    def test_invalid_format_error(self):
        """잘못된 데이터 형식 입력 시 에러 발생 테스트"""
        raw_data = "invalid string" # dict가 아닌 경우
        with self.assertRaises(ValueError):
            self.parser.parse(raw_data)

if __name__ == "__main__":
    unittest.main()
