import unittest
from unittest.mock import patch, MagicMock

# Add project root to the Python path
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai.openai_service import OpenAIService
from ai.gemini_service import GeminiService
import response_parser

class TestOpenAIService(unittest.TestCase):

    def setUp(self):
        self.service = OpenAIService()

    @patch('openai.OpenAI')
    def test_summarize_with_emojis(self, MockOpenAI):
        mock_client = MockOpenAI.return_value
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test summary. 😃"
        mock_client.chat.completions.create.return_value = mock_response

        self.service.client = mock_client
        summary = self.service.summarize_with_emojis("Test article")

        self.assertEqual(summary, "Test summary. 😃")
        mock_client.chat.completions.create.assert_called_once()
        call_args = mock_client.chat.completions.create.call_args
        self.assertIn("Test article", call_args.kwargs['messages'][1]['content'])

    @patch('openai.OpenAI')
    def test_summarize_with_emojis_and_evaluate(self, MockOpenAI):
        mock_client = MockOpenAI.return_value
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test summary. 🤔 Scores: E:8 M:7 P:6"
        mock_client.chat.completions.create.return_value = mock_response

        self.service.client = mock_client
        summary, score = self.service.summarize_with_emojis_and_evaluate("Test article")

        self.assertEqual(summary.strip(), "Test summary. 🤔")
        self.assertAlmostEqual(score, 7.0)
        mock_client.chat.completions.create.assert_called_once()

    @patch('openai.OpenAI')
    def test_evaluate_article(self, MockOpenAI):
        mock_client = MockOpenAI.return_value
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"expat_impact": 8, "event_weight": 7, "politics": 6, "timeliness": 9, "practical_utility": 5}'
        mock_client.chat.completions.create.return_value = mock_response

        self.service.client = mock_client
        score = self.service.evaluate_article("Test article")

        self.assertAlmostEqual(score, 7.0)
        mock_client.chat.completions.create.assert_called_once()

class TestGeminiService(unittest.TestCase):

    def setUp(self):
        # Mock genai configure and GenerativeModel
        self.patcher_configure = patch('google.generativeai.configure')
        self.patcher_model = patch('google.generativeai.GenerativeModel')
        self.mock_configure = self.patcher_configure.start()
        self.mock_model = self.patcher_model.start()

        self.service = GeminiService(api_key="test_key")

    def tearDown(self):
        self.patcher_configure.stop()
        self.patcher_model.stop()

    def test_summarize_with_emojis(self):
        mock_response = MagicMock()
        mock_response.text = "Test summary. 😃"
        self.service.model.generate_content.return_value = mock_response

        summary = self.service.summarize_with_emojis("Test article")

        self.assertEqual(summary, "Test summary. 😃")
        self.service.model.generate_content.assert_called_once()
        call_args = self.service.model.generate_content.call_args
        self.assertIn("Test article", call_args[0][0])

    def test_summarize_with_emojis_and_evaluate(self):
        mock_response = MagicMock()
        mock_response.text = "Test summary. 🤔 Scores: E:8 M:7 P:6"
        self.service.model.generate_content.return_value = mock_response

        summary, score = self.service.summarize_with_emojis_and_evaluate("Test article")

        self.assertEqual(summary.strip(), "Test summary. 🤔")
        self.assertAlmostEqual(score, 7.0)
        self.service.model.generate_content.assert_called_once()

    def test_evaluate_article(self):
        mock_response = MagicMock()
        mock_response.text = '{"expat_impact": 8, "event_weight": 7, "politics": 6, "timeliness": 9, "practical_utility": 5}'
        self.service.model.generate_content.return_value = mock_response

        score = self.service.evaluate_article("Test article")

        self.assertAlmostEqual(score, 7.0)
        self.service.model.generate_content.assert_called_once()

if __name__ == '__main__':
    unittest.main()
