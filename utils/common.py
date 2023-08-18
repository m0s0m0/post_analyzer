def validate_analyzed_data_response(analyzed_data: dict) -> bool:

    """
    to ensure all dict keys has values greater than or equal to one
    :params -> analyzed_data
    :return -> Boolean
    """

    return all(value >= 1 for value in analyzed_data.values()) and isinstance(analyzed_data, dict)
