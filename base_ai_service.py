from abc import ABC, abstractmethod

class BaseAIService(ABC):
    """
    Abstract base class for AI services. It defines the interface that all AI provider-specific
    services must implement.
    """

    @abstractmethod
    def summarize_with_emojis(self, article_text, target_language='en'):
        """
        Summarizes the given article text with emojis.

        :param article_text: The text of the article to summarize.
        :param target_language: The target language for the summary.
        :return: The summarized text with emojis.
        """
        pass

    @abstractmethod
    def summarize_with_emojis_and_evaluate(self, article_text, target_language='en'):
        """
        Summarizes the article with emojis and provides an evaluation score.

        :param article_text: The text of the article to summarize and evaluate.
        :param target_language: The target language for the summary.
        :return: A tuple containing the summary text and the evaluation score.
        """
        pass

    @abstractmethod
    def evaluate_article(self, article_text):
        """
        Evaluates the article based on predefined criteria.

        :param article_text: The text of the article to evaluate.
        :return: The evaluation score for the article.
        """
        pass
