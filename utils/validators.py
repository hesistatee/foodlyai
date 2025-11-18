def validate_weight(weight: int | str) -> bool:
    if isinstance(weight, int):
        return weight > 0 and weight < 300
    elif isinstance(weight, str):
        try:
            weight = int(weight)
            return weight > 0 and weight < 300
        except ValueError:
            return False
    return False


def validate_height(height: int | str) -> bool:
    if isinstance(height, int):
        return height > 0 and height < 230
    elif isinstance(height, str):
        try:
            height = int(height)
            return height > 0 and height < 230
        except ValueError:
            return False
    return False


def validate_age(age: int | str) -> bool:
    if isinstance(age, int):
        return age > 0 and age < 120
    elif isinstance(age, str):
        try:
            age = int(age)
            return age > 0 and age < 120
        except ValueError:
            return False
    return False


def validate_gender(gender: str) -> bool:
    if isinstance(gender, str):
        return gender in ["М", "Ж"]
    return False
