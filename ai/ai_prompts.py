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
        "You are a helpful assistant. Summarize with details the following Spanish news article "
        f"in 3-4 sentences in {lang} with a slightly sarcastic or humorous style where it appropriate. "
        "End the summary with 1-3 emojis that match the tone of the news."
    )

def get_evaluate_article_prompt():
    """
    Returns the system prompt for evaluating an article.
    """
    return (
        "You are a news evaluation agent. Your role is to score local news stories based on how likely they are to interest a general audience, "
        "especially international readers and expats in Malaga. "
    )
