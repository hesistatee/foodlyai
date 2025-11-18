def harris_benedict_formula(weight: int, height: int, age: int, gender: str) -> int:
    if gender == "М":
        return int(88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age))
    elif gender == "Ж":
        return int(447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age))
    else:
        raise ValueError("Invalid gender")
