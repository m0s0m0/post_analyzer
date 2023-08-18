from exceptions.service_error import ServiceException
from exceptions.error_codes import ErrorCodes
from rest_framework import status
from functools import reduce
from django.conf import settings


def calculate_parts(text_length,
                    cutoff_parts=settings.CUTOFF_PARTS,
                    margin_words=settings.PARTS_SIZE_MARGIN):
    """
    Calculate the number of parts in which a text can be divided while satisfying certain criteria.

    Args:
        text (str): The input text to be divided.
        cutoff_parts (int, optional): The maximum number of parts the text can be divided into. Default is 10.
        margin_words (int, optional): The margin of words allowed in the length of each part. Default is 100.

    Returns:
        int: The calculated number of parts that satisfy the given criteria.

    Notes:
        This function attempts to divide the input text into parts, ensuring that each part has a length not less than 500 characters and not more than 3000 characters.
        The length of each part is also adjusted to have a margin of +-100 words from the target length.
        The function may return fewer parts if the input text is very short (less than 500 characters) or if a valid division cannot be found within the given constraints.

    Example:
        input_text = "This is an example text that you want to divide into parts with similar length."
        num_parts = calculate_parts(input_text)
        print("Input string can be divided into", num_parts, "parts.")
    """
    total_chars = text_length
    if total_chars < settings.MIN_PART_LENGTH:
        return 1

    if total_chars > settings.MAX_SUPPORTED_LENGTH:
        raise ServiceException(
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, ErrorCodes.LARGE_STRING,
            'Payload too big to analyze')

    min_chars_per_part = settings.MIN_PART_LENGTH
    max_chars_per_part = min(settings.MAX_PART_LENGTH, total_chars)

    num_parts = 2
    while num_parts <= cutoff_parts:
        target_length = total_chars // num_parts
        if min_chars_per_part <= target_length <= max_chars_per_part:
            part_length_with_margin = target_length * num_parts
            if part_length_with_margin <= max_chars_per_part * cutoff_parts:
                return num_parts
        num_parts += 1

    return cutoff_parts


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


def divide_text(text: str):
    """
    Divide a text into multiple parts.

    :param text: Input text.
    :param number_of_parts: Number of parts to divide the text into.
    :yield: Generator yielding text parts.
    """
    remaining_text = text
    total_length = len(text)
    number_of_parts = calculate_parts(total_length)
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
        space_count = 0
        in_word = False

        for char in text:
            if char == ' ':
                space_count += 1
                in_word = False
            else:
                if not in_word:
                    in_word = True
                    total_words += 1
                total_word_length += 1

        if total_words == 0:
            total_word_length = 0

        return {
            "total_words": total_words,
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
