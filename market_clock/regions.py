import pydantic
from pydantic import validator
import pendulum
from pendulum import timezone
from pendulum.period import Period
from datetime import datetime
from pendulum.tz.timezone import Timezone
from typing import List, Optional
from market_clock import holidays, weekends
from enum import Enum


class Holiday:
    @classmethod
    def from_string(cls, holiday):
        day, month = holiday.split(".")
        year = pendulum.now().year
        return pendulum.parse(f"{year}-{month}-{day}")


# https://en.wikipedia.org/wiki/List_of_tz_database_time_zones


class Region(pydantic.BaseModel):
    name: str
    timezone: Timezone
    begin_time: str
    end_time: str
    exchange: str
    is_open: Optional[bool]
    time_to_open: Optional[Period]
    seconds_to_open: Optional[int]
    time_to_close: Optional[Period]
    seconds_to_close: Optional[int]
    weekends: List[int] = weekends.NORMAL_WEEKEND
    holidays: List[datetime]

    @validator("name", pre=True)
    def validate_name(cls, value):
        return value.capitalize()

    @validator("timezone", pre=True)
    def validate_timezone(cls, value):
        return timezone(value)

    @validator("holidays", pre=True)
    def validate_holidays(cls, holidays):
        return sorted([Holiday.from_string(holiday) for holiday in holidays])

    def get_holidays(self):
        return [holiday.date() for holiday in self.holidays]

    def check_is_open(self):
        current_time = pendulum.now(tz=self.timezone)

        if current_time.day_of_week in self.weekends:
            return False

        if current_time.date() in self.get_holidays():
            return False

        start_time = pendulum.parse(self.begin_time, exact=True)
        end_time = pendulum.parse(self.end_time, exact=True)

        start_date = pendulum.datetime(
            current_time.year,
            current_time.month,
            current_time.day,
            start_time.hour,
            start_time.minute,
            tz=self.timezone,
        )

        end_date = pendulum.datetime(
            current_time.year,
            current_time.month,
            current_time.day,
            end_time.hour,
            end_time.minute,
            tz=self.timezone,
        )

        period = pendulum.period(start_date, end_date)

        if current_time in period:

            return True

        return False

    def update(self):
        self.is_open = self.check_is_open()
        if self.is_open:
            self.time_to_close = self.get_time_until_close()
            self.seconds_to_close = self.time_to_close.seconds

            self.time_to_open = None
            self.seconds_to_open = None

        if not self.is_open:
            self.time_to_open = self.get_time_until_open()
            self.seconds_to_open = self.time_to_open.seconds

            self.time_to_close = None
            self.seconds_to_close = None

    def get_time_until_close(self):
        current_time = pendulum.now(tz=self.timezone)
        next = self.get_next_trading_day()
        end_time = pendulum.parse(self.end_time, exact=True)

        if self.check_is_open():
            end_date = pendulum.datetime(
                current_time.year,
                current_time.month,
                current_time.day,
                end_time.hour,
                end_time.minute,
                tz=self.timezone,
            )
            return end_date - current_time

        else:
            end_date = pendulum.datetime(
                next.year,
                next.month,
                next.day,
                end_time.hour,
                end_time.minute,
                tz=self.timezone,
            )
            return end_date - current_time

    def get_time_until_open(self):
        current_time = pendulum.now(tz=self.timezone)
        next = self.get_next_trading_day()

        start_time = pendulum.parse(self.begin_time, exact=True)
        return next - current_time
        # return f"{period.in_words()} until {self.name.upper()} market is open."

    def get_next_trading_day(self):
        current_time = pendulum.now(tz=self.timezone)

        start_time = pendulum.parse(self.begin_time, exact=True)
        start_date = pendulum.datetime(
            current_time.year,
            current_time.month,
            current_time.day,
            start_time.hour,
            start_time.minute,
            tz=self.timezone,
        )

        if current_time < start_date:
            if current_time.date() == start_date.date():
                if current_time.day_of_week not in self.weekends:
                    return start_date

        for day in pendulum.period(start_date.add(days=1), start_date.add(days=7)):
            if day.day_of_week in self.weekends:
                continue
            if day.date() in self.get_holidays():
                continue
            return day

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {Timezone: lambda tz: tz.name, Period: lambda p: p.in_words()}


class MultipleRegions(pydantic.BaseModel):
    exchanges: List[Region]

    def update(self):
        for exchange in self.exchanges:
            exchange.update()

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {Timezone: lambda tz: tz.name, Period: lambda p: p.in_words()}


WELLINGTON = Region(
    name="Wellington",
    exchange="NZX Wellington",
    timezone="Pacific/Auckland",
    begin_time="10:00",
    end_time="16:45",
    holidays=holidays.WELLINGTON,
)

SYDNEY = Region(
    name="Sydney",
    exchange="ASX Sydney",
    timezone="Australia/Sydney",
    begin_time="10:00",
    end_time="16:00",
    holidays=holidays.SYNDNEY,
)


TOKYO = Region(
    name="Tokyo",
    exchange="JPX Tokyo",
    timezone="Asia/Tokyo",
    begin_time="09:00",
    end_time="15:00",
    holidays=holidays.TOKYO,
)


SINGAPORE = Region(
    name="Singapore",
    exchange="SGX Singapore",
    timezone="Asia/Singapore",
    begin_time="09:00",
    end_time="17:00",
    holidays=holidays.SINGAPORE,
)


HONG_KONG = Region(
    name="Hong_Kong",
    exchange="HKEX Hong Kong",
    timezone="Asia/Hong_Kong",
    begin_time="09:30",
    end_time="16:00",
    holidays=holidays.HONGKONG,
)

SHANGHAI = Region(
    name="Shanghai",
    exchange="SSE Shanghai",
    timezone="Asia/Shanghai",
    begin_time="09:15",
    end_time="15:00",
    holidays=holidays.SHANGHAI,
)

INDIA = Region(
    name="India",
    exchange="NSE Mumbai",
    timezone="Asia/Kolkata",
    begin_time="09:15",
    end_time="15:30",
    holidays=holidays.MUMBAI,
)

DUBAI = Region(
    name="Dubai",
    exchange="DFM Dubai",
    timezone="Asia/Dubai",
    begin_time="10:00",
    end_time="13:50",
    weekends=weekends.DUBAI,
    holidays=holidays.DUBAI,
)

MOSCOW = Region(
    name="Moscow",
    exchange="MOEX Moscow",
    timezone="Europe/Moscow",
    begin_time="09:30",
    end_time="19:00",
    holidays=holidays.MOSCOW,
)

JOHANNESBURG = Region(
    name="Johannesburg",
    exchange="JSE Johannesburg",
    timezone="Africa/Johannesburg",
    begin_time="09:00",
    end_time="17:00",
    holidays=holidays.JOHANNESBURG,
)

SAUDI = Region(
    name="Saudi",
    exchange="TADAWUL Riyadh",
    timezone="Asia/Riyadh",
    begin_time="10:00",
    end_time="15:00",
    weekends=weekends.RIYADH,
    holidays=holidays.RIYADH,
)

LONDON = Region(
    name="London",
    exchange="LSE London",
    timezone="Europe/London",
    begin_time="08:00",
    end_time="16:30",
    holidays=holidays.LONDON,
)

SWISS = Region(
    name="Swiss",
    exchange="SIX Zurich",
    timezone="Europe/Zurich",
    begin_time="09:00",
    end_time="17:30",
    holidays=holidays.ZURICH,
)

FRANKFURT = Region(
    name="Frankfurt",
    exchange="FWB Frankfurt",
    timezone="Europe/Berlin",
    begin_time="08:00",
    end_time="17:30",
    holidays=holidays.FRANKFURT,
)

SAO_PAULO = Region(
    name="Sao_Paulo",
    exchange="BOVESPA Sao Paulo",
    timezone="America/Sao_Paulo",
    begin_time="10:00",
    end_time="16:55",
    holidays=holidays.SAU_PAULO,
)

NEW_YORK = Region(
    name="New_York",
    exchange="NYSE New York",
    timezone="America/New_York",
    begin_time="09:30",
    end_time="16:00",
    holidays=holidays.NEW_YORK,
)

TORONTO = Region(
    name="Toronto",
    exchange="TSX Toronto",
    timezone="America/Toronto",
    begin_time="09:30",
    end_time="16:00",
    holidays=holidays.TORONTO,
)


CHICAGO = Region(
    name="Chicago",
    exchange="NYSE Chicago",
    timezone="America/Chicago",
    begin_time="08:30",
    end_time="15:00",
    holidays=holidays.CHICAGO,
)

UTC = Region(
    name="UTC",
    exchange="UTC",
    timezone="Etc/UTC",
    begin_time="00:00",
    end_time="23:59",
    weekends=[],
    holidays=[],
)

EXCHANGES = [
    WELLINGTON,
    SYDNEY,
    TOKYO,
    SINGAPORE,
    HONG_KONG,
    SHANGHAI,
    INDIA,
    DUBAI,
    MOSCOW,
    JOHANNESBURG,
    SAUDI,
    LONDON,
    SWISS,
    FRANKFURT,
    SAO_PAULO,
    NEW_YORK,
    TORONTO,
    CHICAGO,
    UTC,
]

EXCHANGE_DICTIONARY = {}

for exchange in EXCHANGES:
    key = exchange.name.upper()
    value = exchange
    EXCHANGE_DICTIONARY[key] = value


class RegionEnum(str, Enum):
    wellington = "WELLINGTON"
    sydney = "SYDNEY"
    tokyo = "TOKYO"
    singapore = "SINGAPORE"
    hong_kong = "HONG_KONG"
    shanghai = "SHANGHAI"
    indai = "INDIA"
    dubai = "DUBAI"
    moscow = "MOSCOW"
    johannesburg = "JOHANNESBURG"
    saudi = "SAUDI"
    london = "LONDON"
    swiss = "SWISS"
    frankfurt = "FRANKFURT"
    sao_paulo = "SAO_PAULO"
    new_york = "NEW_YORK"
    toronto = "TORONTO"
    chicago = "CHICAGO"
    utc = "UTC"


def get_regions():
    return MultipleRegions(exchanges=EXCHANGES)
