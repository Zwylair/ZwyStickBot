def is_str_empty(string: str):
    return string is None or len(string) == 0


def process_fetchone(fetching_result):
    return None if fetching_result is None else next(iter(fetching_result), None)
