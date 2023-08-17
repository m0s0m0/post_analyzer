from django.conf import settings
from exceptions.service_error import ServiceException
from exceptions.error_codes import ErrorCodes
from functools import reduce


def find_text_split(text: str, text_length: int) -> int:
    """
    Find the optimal split point for dividing a text into parts.

    :param text: Input text.
    :param max_length: Maximum length for the entire text.
    :param max_part_length(optional): Maximum length for each part.
    :return: Optimal split point.
    """
    if len(text) <= text_length:
        return len(text)
    
    split_point = text_length
    while split_point > 0 and not text[split_point - 1].isspace():
        split_point -= 1
    return split_point


def divide_text(text: str, number_of_parts: int):
    """
    Divide a text into multiple parts.

    :param text: Input text.
    :param number_of_parts: Number of parts to divide the text into.
    :yield: Generator yielding text parts.
    """
    remaining_text = text
    total_length = len(text)
    # max_part_length = settings.MAX_PART_LENGTH
    part_length = (total_length // number_of_parts)

    for _ in range(number_of_parts - 1):
        split_point = find_text_split(remaining_text, part_length)
        if split_point > 0:
            yield remaining_text[:split_point].rstrip()
            remaining_text = remaining_text[split_point:].lstrip()

    if remaining_text:
        yield remaining_text


def analyze_text(text, **kwargs):
    """
    Analyze the given text and calculate word-related metrics.

    :param text: Input text.
    :param kwargs: Additional keyword arguments.
    :return: Dictionary containing word-related metrics.
    :raises ServiceException: If an error occurs during analysis.
    """
    try:
        total_words = 0
        total_word_length = 0
        word_start = None

        for i, char in enumerate(text):
            if char.isalpha():
                if word_start is None:
                    word_start = i
            elif word_start is not None:
                total_words += 1
                total_word_length += i - word_start
                word_start = None

        if word_start is not None:
            total_words += 1
            total_word_length += len(text) - word_start

        return {
            "total_words": total_words,
            "text": text,
            "total_word_length": total_word_length
        }
    except Exception as e:
        raise ServiceException(500, ErrorCodes.INTERNAL_SERVER_ERROR, "Error during analysis", {'error': str(e)})


def process_subtext_results(subtext_results: list, **kwargs: dict):
    """
    Process subtext analysis results and calculate aggregated metrics.

    :param subtext_results: List of subtext analysis results.
    :param kwargs: Additional keyword arguments.
    :return: Dictionary containing aggregated metrics.
    :raises ServiceException: If an error occurs during processing.
    """
    try:
        total_words = reduce(lambda acc, result: acc + result.get('total_words', 0), subtext_results, 0)
        total_word_length = reduce(lambda acc, result: acc + result.get('total_word_length', 0), subtext_results, 0)

        average_word_length = round(total_word_length / total_words if total_words > 0 else 0, 2)

        return {
            "total_words": total_words,
            "average_word_length": average_word_length
        }
    except Exception as e:
        raise ServiceException(500, ErrorCodes.INTERNAL_SERVER_ERROR, "Error during subtext processing", {'error': str(e)})
