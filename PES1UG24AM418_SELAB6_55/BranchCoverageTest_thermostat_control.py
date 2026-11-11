import pytest
from thermostat_control import target_temperature, hvac_action, energy_alert


# --- Starter test cases ---
def test_away_mode():
    assert target_temperature("away", True, 12) == 16


def test_no_readings():
    assert energy_alert([], 10) == "ok"


# --- Branch Coverage & Boundary Value Tests: target_temperature ---

def test_target_temperature_away_branch_true():
    # mode == 'away' returns 16 regardless of other parameters
    assert target_temperature("away", False, 0) == 16
    assert target_temperature("away", True, 23) == 16


def test_target_temperature_sleep_boundaries():
    # mode == 'sleep', testing compound condition: hour < 6 or hour >= 22
    # At lower boundary: hour == 0 (< 6 -> True)
    assert target_temperature("sleep", True, 0) == 18
    # Just below 6: hour == 5 (< 6 -> True)
    assert target_temperature("sleep", True, 5) == 18
    # Exactly at 6: hour == 6 (False or False -> False) -> returns 20
    assert target_temperature("sleep", True, 6) == 20
    # Between 6 and 22: hour == 12 -> returns 20
    assert target_temperature("sleep", True, 12) == 20
    # Just below 22: hour == 21 (False or False -> False) -> returns 20
    assert target_temperature("sleep", True, 21) == 20
    # Exactly at upper boundary: hour == 22 (False or True -> True) -> returns 18
    assert target_temperature("sleep", True, 22) == 18
    # Above 22: hour == 23 (False or True -> True) -> returns 18
    assert target_temperature("sleep", True, 23) == 18


def test_target_temperature_not_occupied():
    # mode != 'away' and mode != 'sleep', not occupied -> True returns 18
    assert target_temperature("normal", False, 12) == 18
    assert target_temperature("eco", False, 7) == 18


def test_target_temperature_morning_peak_boundaries():
    # occupied == True, 6 <= hour < 9 returns 22
    # Just below morning range: hour == 5 -> falls to default 20
    assert target_temperature("auto", True, 5) == 20
    # At lower boundary: hour == 6 -> returns 22
    assert target_temperature("auto", True, 6) == 22
    # Within morning peak: hour == 7 -> returns 22
    assert target_temperature("auto", True, 7) == 22
    # Just below upper boundary: hour == 8 -> returns 22
    assert target_temperature("auto", True, 8) == 22
    # At upper boundary: hour == 9 -> falls through to default 20
    assert target_temperature("auto", True, 9) == 20


def test_target_temperature_evening_peak_boundaries():
    # occupied == True, 17 <= hour < 22 returns 21
    # Just below evening range: hour == 16 -> falls to default 20
    assert target_temperature("auto", True, 16) == 20
    # At lower boundary: hour == 17 -> returns 21
    assert target_temperature("auto", True, 17) == 21
    # Within evening peak: hour == 20 -> returns 21
    assert target_temperature("auto", True, 20) == 21
    # Just below upper boundary: hour == 21 -> returns 21
    assert target_temperature("auto", True, 21) == 21
    # At upper boundary: hour == 22 -> falls to default 20
    assert target_temperature("auto", True, 22) == 20


def test_target_temperature_off_peak_fallback():
    # Covers hours falling through all if statements to line 14 (return 20)
    assert target_temperature("auto", True, 12) == 20
    assert target_temperature("auto", True, 2) == 20


# --- Branch Coverage & Boundary Value Tests: hvac_action ---

def test_hvac_action_deadband_idle():
    # abs(diff) < 1 branch evaluates to True -> returns 'idle'
    # Exactly zero difference
    assert hvac_action(20.0, 20.0, 15.0) == "idle"
    # Positive difference just inside deadband: diff = 0.99
    assert hvac_action(20.0, 20.99, 15.0) == "idle"
    # Negative difference just inside deadband: diff = -0.99
    assert hvac_action(20.99, 20.0, 15.0) == "idle"


def test_hvac_action_heat_boundaries():
    # diff = 1.0 (abs(diff) < 1 is False; diff > 0 is True)
    # Outside temperature just below 5 -> heat_boost
    assert hvac_action(20.0, 21.0, 4.9) == "heat_boost"
    # Outside temperature exactly at 5 -> heat (standard)
    assert hvac_action(20.0, 21.0, 5.0) == "heat"
    # Outside temperature just above 5 -> heat
    assert hvac_action(20.0, 21.0, 5.1) == "heat"


def test_hvac_action_cool_boundaries():
    # diff = -1.0 (abs(diff) < 1 is False; diff > 0 is False -> cooling)
    # Outside temperature just above 30 -> cool_boost
    assert hvac_action(22.0, 21.0, 30.1) == "cool_boost"
    # Outside temperature exactly at 30 -> cool (standard)
    assert hvac_action(22.0, 21.0, 30.0) == "cool"
    # Outside temperature just below 30 -> cool
    assert hvac_action(22.0, 21.0, 29.9) == "cool"


# --- Branch Coverage & Boundary Value Tests: energy_alert ---

def test_energy_alert_loop_zero_times():
    # Loop over readings runs 0 times; over == 0 -> True -> 'ok'
    assert energy_alert([], 10) == "ok"


def test_energy_alert_loop_one_time():
    # Loop runs exactly once
    # Reading <= limit (over == 0) -> 'ok'
    assert energy_alert([10], 10) == "ok"
    # Reading > limit (over == 1, 1 * 2 > 1) -> 'critical'
    assert energy_alert([11], 10) == "critical"


def test_energy_alert_loop_many_times_and_boundaries():
    # Loop runs multiple times
    # Exact threshold boundary test: reading == limit is not strictly greater
    assert energy_alert([10, 10, 10], 10) == "ok"
    assert energy_alert([10.01, 5, 5], 10) == "warning"

    # Boundary test for over * 2 > len(readings):
    # Case: over * 2 == len(readings) (e.g. 2 over out of 4: 2 * 2 = 4, not > 4) -> 'warning'
    assert energy_alert([15, 15, 5, 5], 10) == "warning"

    # Case: over * 2 > len(readings) (e.g. 3 over out of 4: 3 * 2 = 6 > 4) -> 'critical'
    assert energy_alert([15, 15, 15, 5], 10) == "critical"

    # Case: over * 2 < len(readings) (e.g. 1 over out of 4: 1 * 2 = 2 < 4) -> 'warning'
    assert energy_alert([15, 5, 5, 5], 10) == "warning"


# --- Exception and Invalid Input Handling Tests ---

def test_invalid_inputs_exceptions():
    # None passed to energy_alert (TypeError on iterate)
    with pytest.raises(TypeError):
        energy_alert(None, 10)

    # Incompatible types comparison in target_temperature hour
    with pytest.raises(TypeError):
        target_temperature("home", True, "seven")

    # Incompatible types in hvac_action diff
    with pytest.raises(TypeError):
        hvac_action("warm", 20, 15)
