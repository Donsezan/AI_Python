def get_summarize_with_emojis_prompt(target_language='en'):
    """
    Returns the system prompt for summarizing an article with emojis.
    """
    if target_language.lower() == 'en':
        lang = 'English B2 level'
    elif target_language.lower() == 'es':
        lang = 'Spanish'
    elif target_language.lower() == 'ru':
        lang = 'Russian'
    else:
        lang = 'English'

    return (
        "You are a helpful assistant. Summarize the following Spanish news article "
        f"in 2-3 sentences in {lang} with a slightly sarcastic or humorous style where it appropriate. "
        "End the summary with 1-3 emojis that match the tone of the news."
    )

def get_summarize_with_emojis_and_evaluate_prompt(target_language='en'):
    """
    Returns the system prompt for summarizing an article with emojis and evaluating it.
    """
    if target_language.lower() == 'en':
        lang = 'English'
    elif target_language.lower() == 'es':
        lang = 'Spanish'
    elif target_language.lower() == 'ru':
        lang = 'Russian'
    else:
        lang = 'English'

    return (
        "You are a helpful assistant. Summarize the following Spanish news article "
        f"in 2-3 sentences in {lang} with a slightly sarcastic style. End the summary with 1-3 emojis that match the tone of the news."
        "After the summary and emojis, provide an evaluation of the article on three dimensions, each on a scale of 1 to 10. "
        "Use the format: Scores: E:X M:Y P:Z where X is 'expat impact', Y is 'Malaga capital relevance', and Z is 'political vs. new feature' (1 for internal politics, 10 for cool new stuff)."
        "Example: Summary of the article... 🤔 Scores: E:7 M:9 P:4"
    )

def get_evaluate_article_prompt():
    """
    Returns the system prompt for evaluating an article.
    """
    return (
        "You are a news evaluation agent. Your role is to score local news stories based on how likely they are to interest a general audience, "
        "especially international readers and expats in Malaga. "
    )
