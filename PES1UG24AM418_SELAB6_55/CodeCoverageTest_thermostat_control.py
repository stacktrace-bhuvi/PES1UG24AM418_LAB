import pytest
from thermostat_control import target_temperature, hvac_action, energy_alert


# --- Starter test cases ---
def test_away_mode():
    assert target_temperature("away", True, 12) == 16


def test_no_readings():
    assert energy_alert([], 10) == "ok"


# --- Additional line coverage test cases ---

def test_target_temperature_sleep_night():
    # Covers mode == 'sleep' and hour < 6
    assert target_temperature("sleep", True, 3) == 18
    # Covers mode == 'sleep' and hour >= 22
    assert target_temperature("sleep", True, 22) == 18


def test_target_temperature_sleep_day():
    # Covers mode == 'sleep' and 6 <= hour < 22
    assert target_temperature("sleep", True, 10) == 20


def test_target_temperature_unoccupied():
    # Covers not occupied (when mode is not away or sleep)
    assert target_temperature("comfort", False, 12) == 18


def test_target_temperature_morning_peak():
    # Covers occupied, 6 <= hour < 9
    assert target_temperature("auto", True, 7) == 22


def test_target_temperature_evening_peak():
    # Covers occupied, 17 <= hour < 22
    assert target_temperature("auto", True, 19) == 21


def test_target_temperature_occupied_off_peak():
    # Covers occupied, default fallback hour (e.g., afternoon 12)
    assert target_temperature("auto", True, 12) == 20


def test_hvac_action_idle():
    # Covers abs(diff) < 1
    assert hvac_action(20.0, 20.5, 15) == "idle"


def test_hvac_action_heat_boost():
    # Covers diff > 0 and outside < 5
    assert hvac_action(18.0, 22.0, 2) == "heat_boost"


def test_hvac_action_heat_normal():
    # Covers diff > 0 and outside >= 5
    assert hvac_action(18.0, 22.0, 10) == "heat"


def test_hvac_action_cool_boost():
    # Covers diff < 0 (diff <= -1) and outside > 30
    assert hvac_action(26.0, 22.0, 35) == "cool_boost"


def test_hvac_action_cool_normal():
    # Covers diff < 0 (diff <= -1) and outside <= 30
    assert hvac_action(26.0, 22.0, 25) == "cool"


def test_energy_alert_ok_with_readings():
    # Covers loop with readings <= limit and over == 0
    assert energy_alert([5, 8, 9], 10) == "ok"


def test_energy_alert_critical():
    # Covers readings > limit and over * 2 > len(readings)
    assert energy_alert([15, 20, 5], 10) == "critical"


def test_energy_alert_warning():
    # Covers readings > limit and over * 2 <= len(readings)
    assert energy_alert([15, 5], 10) == "warning"
