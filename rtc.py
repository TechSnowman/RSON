import DS32131 as rtc
from datetime import datetime

rtc_device = rtc.SDL_DS3231(twi=1, addr=0x68, at24c32_addr=0x57)

rtc_time_utc = rtc_device.read_datetime()
print(f"time is {rtc_time_utc}")

temperature_celsius = rtc_device.getTemp()
print(f"temperature is {temperature_celsius}°")