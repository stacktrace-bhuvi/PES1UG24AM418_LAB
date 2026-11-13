import math


def parse_setpoint(text):
    """Parse a setpoint such as '21.5C' or '70F' and return Celsius (1 d.p.).

    Returns None for any invalid input (non-string, empty, missing/unknown
    unit, non-numeric value, nan/inf or overflow).
    """
    if not isinstance(text, str):
        return None
    text = text.strip()
    if len(text) < 2:
        return None
    unit = text[-1].upper()
    if unit not in ('C', 'F'):
        return None
    try:
        value = float(text[:-1])
    except ValueError:
        return None
    if not math.isfinite(value):
        return None
    if unit == 'F':
        value = (value - 32) * 5 / 9
    if not math.isfinite(value):
        return None
    return round(value, 1)


def average_temperature(readings_csv):
    """Average a comma separated list of readings.

    Returns None for any invalid input (non-string, empty, blank/non-numeric
    entries, nan/inf or overflow).
    """
    if not isinstance(readings_csv, str):
        return None
    try:
        values = [float(r) for r in readings_csv.split(',')]
    except ValueError:
        return None
    if not values or not all(math.isfinite(v) for v in values):
        return None
    result = sum(values) / len(values)
    if not math.isfinite(result):
        return None
    return result


def schedule_slot(time_text):
    """Label a 'HH:MM' time as 'night <minute>' (before 06:00) or 'day <minute>'.

    Returns None for invalid input (non-string, wrong format, hour outside
    0-23 or minute outside 0-59).
    """
    if not isinstance(time_text, str):
        return None
    parts = time_text.split(':')
    if len(parts) != 2:
        return None
    try:
        hour = int(parts[0])
        minute = int(parts[1])
    except ValueError:
        return None
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        return None
    if hour < 6:
        return 'night ' + str(minute)
    return 'day ' + str(minute)


def main():
    print("==== Running parse_setpoint ====")
    user_input = input("Enter a setpoint (e.g. 21.5C or 70F): ")
    result = parse_setpoint(user_input)
    print("Setpoint in Celsius:", result)

    print("\n==== Running average_temperature ====")
    user_input = input("Enter sensor readings as CSV (e.g. 20.5,21,22.5): ")
    result = average_temperature(user_input)
    print("Average Temperature:", result)

    print("\n==== Running schedule_slot ====")
    user_input = input("Enter a time as HH:MM (e.g. 07:30): ")
    result = schedule_slot(user_input)
    print("Schedule Slot:", result)


if __name__ == "__main__":
    main()
