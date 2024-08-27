from typing import cast

from .feeder import Feeder
import time
import requests

class OneRFIDPetFeeder(Feeder):
    async def refresh(self):
        await super().refresh()
        self.update_data({
            "grainStatus": await self.api.device_grain_status(self.serial),
            "realInfo": await self.api.device_real_info(self.serial)
        })

    @property
    def remaining_desiccant(self) -> str:
        return cast(str, self._data.get("remainingDesiccantDays"))

    @property
    def today_feeding_quantity(self) -> int:
        quantity = self._data.get("grainStatus", {}).get("todayFeedingQuantity")
        if not quantity:
            return 0

        return self.convert_unit(quantity)

    @property
    def today_feeding_times(self) -> int:
        return cast(int, self._data.get("grainStatus", {}).get("todayFeedingTimes"))

    @property
    def today_eating_time(self) -> int:
        eating_time_str = self._data.get("grainStatus", {}).get("eatingTime", "0'0''")
        if not eating_time_str:
            return 0

        try:
            minutes, seconds = map(int, eating_time_str.replace("''", "").split("'"))
            total_seconds = minutes * 60 + seconds
        except ValueError as e:
            return 0

        return total_seconds
    
    @property
    def today_eating_times(self) -> int:
        return cast(int, self._data.get("grainStatus", {}).get("todayEatingTimes"))

    @property
    def battery_state(self) -> str:
        return cast(str, self._data.get("realInfo", {}).get("batteryState"))
    
    @property
    def door_state(self) -> int:
        state = self._data.get("realInfo", {}).get("coverClosePosition")
        if not state:
            return "Unknown"
        elif state == 4:
            return "Closed"
        elif state == 1:
            return "Open"
        else:
            return "Unknown"