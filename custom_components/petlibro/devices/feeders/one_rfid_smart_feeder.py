from typing import cast
from logging import getLogger

from .granary_feeder import GranaryFeeder

# Configure the logger
_LOGGER = getLogger(__name__)

class OneRFIDSmartFeeder(GranaryFeeder):
    async def refresh(self):
        await super().refresh()

        # Fetch data from API
        grain_status = await self.api.device_grain_status(self.serial)
        real_info = await self.api.device_real_info(self.serial)

        # Update internal data
        self.update_data({
            "grainStatus": grain_status or {},  # Ensure a fallback to an empty dict if None
            "realInfo": real_info or {}  # Ensure a fallback to an empty dict if None
        })

    # Property for todayFeedingQuantities (list of quantities fed today)
    @property
    def today_feeding_quantities(self) -> list[int]:
        return self._data.get("grainStatus", {}).get("todayFeedingQuantities", [])  # Default to an empty list

    # Property for todayFeedingQuantity (total quantity fed today)
    @property
    def today_feeding_quantity(self) -> int:
        return self._data.get("grainStatus", {}).get("todayFeedingQuantity", 0)  # Default to 0

    # Property for todayFeedingTimes (total times the feeder dispensed food today)
    @property
    def today_feeding_times(self) -> int:
        return self._data.get("grainStatus", {}).get("todayFeedingTimes", 0)  # Default to 0

    # Property for todayEatingTimes (total times pet has eaten today)
    @property
    def today_eating_times(self) -> int:
        return self._data.get("grainStatus", {}).get("todayEatingTimes", 0)  # Default to 0

    # Property for todayEatingTime (total time spent eating today)
    @property
    def today_eating_time(self) -> int:
        eating_time_str = self._data.get("grainStatus", {}).get("eatingTime", "0'0''")
        if not eating_time_str:
            return 0

        try:
            minutes, seconds = map(int, eating_time_str.replace("''", "").split("'"))
            total_seconds = minutes * 60 + seconds
        except ValueError:
            return 0

        return total_seconds

    @property
    def battery_state(self) -> str:
        return cast(str, self._data.get("realInfo", {}).get("batteryState", "unknown"))  # Default to 'unknown'

    @property
    def door_state(self) -> bool:
        return bool(self._data.get("realInfo", {}).get("barnDoorState", False))  # Default to False

    @property
    def door_error_state(self) -> str:
        return cast(str, self._data.get("realInfo", {}).get("doorErrorState", "NORMAL"))  # Default to 'NORMAL'

    @property
    def food_dispenser_state(self) -> bool:
        return not bool(self._data.get("realInfo", {}).get("grainOutletState", True))  # Default to True

    @property
    def door_blocked(self) -> bool:
        return bool(self._data.get("realInfo", {}).get("barnDoorError", False))  # Default to False

    @property
    def food_low(self) -> bool:
        return not bool(self._data.get("realInfo", {}).get("surplusGrain", True))  # Default to True

    @property
    def unit_type(self) -> int:
        return self._data.get("realInfo", {}).get("unitType", 1)  # Default to 1 (assuming a standard unit type)

    @property
    def battery_display_type(self) -> str:
        return cast(str, self._data.get("realInfo", {}).get("batteryDisplayType", "percentage"))

    # New binary sensors for connectivity and state

    @property
    def online(self) -> bool:
        return bool(self._data.get("realInfo", {}).get("online", False))  # Default to False

    @property
    def running_state(self) -> bool:
        return self._data.get("realInfo", {}).get("runningState", "IDLE") == "RUNNING"  # Default to 'IDLE'

    @property
    def whether_in_sleep_mode(self) -> bool:
        return bool(self._data.get("realInfo", {}).get("whetherInSleepMode", False))  # Default to False

    @property
    def enable_low_battery_notice(self) -> bool:
        return bool(self._data.get("realInfo", {}).get("enableLowBatteryNotice", False))  # Default to False

    @property
    def enable_power_change_notice(self) -> bool:
        return bool(self._data.get("realInfo", {}).get("enablePowerChangeNotice", False))  # Default to False

    @property
    def enable_grain_outlet_blocked_notice(self) -> bool:
        return bool(self._data.get("realInfo", {}).get("enableGrainOutletBlockedNotice", False))  # Default to False

    # Switch methods for managing features

    async def set_feeding_plan(self, value: bool) -> None:
        """Enable or disable the feeding plan."""
        _LOGGER.debug(f"Setting feeding plan to {value} for {self.serial}")
        await self.api.set_feeding_plan(self.serial, value)

    async def set_child_lock(self, value: bool) -> None:
        """Enable or disable the child lock."""
        _LOGGER.debug(f"Setting child lock to {value} for {self.serial}")
        await self.api.set_child_lock(self.serial, value)

    async def set_light_enable(self, value: bool) -> None:
        """Enable or disable the light functionality."""
        _LOGGER.debug(f"Setting light enable to {value} for {self.serial}")
        await self.api.set_light_enable(self.serial, value)

    async def set_light_switch(self, value: bool) -> None:
        """Turn the light on or off."""
        _LOGGER.debug(f"Setting light switch to {value} for {self.serial}")
        await self.api.set_light_switch(self.serial, value)

    async def set_sound_enable(self, value: bool) -> None:
        """Enable or disable the sound functionality."""
        _LOGGER.debug(f"Setting sound enable to {value} for {self.serial}")
        await self.api.set_sound_enable(self.serial, value)

    async def set_sound_switch(self, value: bool) -> None:
        """Turn the sound on or off."""
        _LOGGER.debug(f"Setting sound switch to {value} for {self.serial}")
        await self.api.set_sound_switch(self.serial, value)
