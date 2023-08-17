

def json_serial(obj):
    if type(obj) is date:
        return date.strftime(obj, "%Y-%m-%d")
    if type(obj) is datetime:
        return datetime.strftime(obj, "%Y-%m-%dT%H:%M:%S.%fZ")
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, time):
        return str(obj)
    if type(obj) is set:
        return list(obj)

def validate_analyzed_data_response(analyzed_data: dict) -> bool:
    """
    to ensure all dict keys has values greater than or equal to one
    :params -> analyzed_data 
    :return -> Boolean
    """
    return all(value >= 1 for value in analyzed_data.values()) and isinstance(analyzed_data, dict)