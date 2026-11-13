import math

from hypothesis import given, strategies as st
from thermostat_control import parse_setpoint, average_temperature, schedule_slot


# ---------- Fuzz tests: arbitrary input must never crash ----------

@given(st.text() | st.none())
def test_parse_setpoint_no_crash(s):
    try:
        parse_setpoint(s)
    except Exception as e:
        assert False, f"parse_setpoint crashed with: {e!r} for input {s!r}"


@given(st.text() | st.none())
def test_average_temperature_no_crash(s):
    try:
        average_temperature(s)
    except Exception as e:
        assert False, f"average_temperature crashed with: {e!r} for input {s!r}"


@given(st.text() | st.none())
def test_schedule_slot_no_crash(s):
    try:
        schedule_slot(s)
    except Exception as e:
        assert False, f"schedule_slot crashed with: {e!r} for input {s!r}"


# ---------- Fuzz tests: result must always be sane ----------

@given(st.text() | st.none())
def test_parse_setpoint_result_is_none_or_finite_float(s):
    result = parse_setpoint(s)
    assert result is None or (isinstance(result, float) and math.isfinite(result))


@given(st.text() | st.none())
def test_average_temperature_result_is_none_or_finite_float(s):
    result = average_temperature(s)
    assert result is None or (isinstance(result, float) and math.isfinite(result))


@given(st.text() | st.none())
def test_schedule_slot_result_is_none_or_label(s):
    result = schedule_slot(s)
    assert result is None or result.startswith(('night ', 'day '))


# ---------- Properties on valid input ----------

@given(st.floats(min_value=-100, max_value=100, allow_nan=False))
def test_parse_setpoint_celsius_roundtrip(v):
    assert parse_setpoint(f"{v}C") == round(v, 1)
    assert parse_setpoint(f"{v}c") == round(v, 1)


@given(st.floats(min_value=-200, max_value=200, allow_nan=False))
def test_parse_setpoint_fahrenheit_conversion(v):
    assert parse_setpoint(f"{v}F") == round((v - 32) * 5 / 9, 1)


@given(st.lists(st.floats(min_value=-100, max_value=100, allow_nan=False),
                min_size=1, max_size=20))
def test_average_is_between_min_and_max(values):
    csv = ",".join(repr(v) for v in values)
    avg = average_temperature(csv)
    assert avg is not None
    assert min(values) - 1e-9 <= avg <= max(values) + 1e-9


@given(st.integers(0, 23), st.integers(0, 59))
def test_schedule_slot_valid_times(h, m):
    expected = ('night ' if h < 6 else 'day ') + str(m)
    assert schedule_slot(f"{h:02d}:{m:02d}") == expected


@given(st.integers(24, 99) | st.integers(-99, -1), st.integers(0, 59))
def test_schedule_slot_rejects_bad_hour(h, m):
    assert schedule_slot(f"{h}:{m:02d}") is None


@given(st.integers(0, 23), st.integers(60, 999) | st.integers(-99, -1))
def test_schedule_slot_rejects_bad_minute(h, m):
    assert schedule_slot(f"{h:02d}:{m}") is None


# ---------- Known crash inputs found by fuzzing (regression tests) ----------

def test_regression_known_bad_inputs():
    assert parse_setpoint(None) is None
    assert parse_setpoint("") is None
    assert parse_setpoint("C") is None
    assert parse_setpoint("215") is None        # no unit
    assert parse_setpoint("21.5X") is None      # unknown unit
    assert parse_setpoint("nanC") is None
    assert parse_setpoint("infC") is None
    assert parse_setpoint("1e999F") is None
    assert average_temperature(None) is None
    assert average_temperature("") is None
    assert average_temperature("1,,2") is None
    assert average_temperature("nan") is None
    assert average_temperature("1e308,1e308") is None
    assert schedule_slot(None) is None
    assert schedule_slot("0730") is None
    assert schedule_slot("7:30:1") is None
    assert schedule_slot("03:abc") is None
    assert schedule_slot("25:61") is None


def test_known_good_values():
    assert parse_setpoint("21.5C") == 21.5
    assert parse_setpoint("70F") == 21.1
    assert average_temperature("20.5,21,22.5") == (20.5 + 21 + 22.5) / 3
    assert schedule_slot("07:30") == "day 30"
    assert schedule_slot("03:05") == "night 5"
    assert schedule_slot("06:00") == "day 0"
    assert schedule_slot("05:59") == "night 59"
