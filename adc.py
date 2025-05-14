from time import sleep
from ad7291 import AD7291  # Save the previous code as ad7291.py

# Initialize the ADC with configuration
adc = AD7291(
    bus=1,                # I2C bus 1 (default on Raspberry Pi 4)
    active_channels=[
        True,   # CH0 enabled
        True,   # CH1 enabled
        False,  # CH2 disabled
        True,   # CH3 enabled
        False,  # CH4 disabled
        False,  # CH5 disabled
        False,  # CH6 disabled
        True    # CH7 enabled
    ],
    enable_temp=True,      # Enable temperature sensor
    enable_noise_delay=False
)

try:
    while True:
        # Read voltage channels
        voltages = adc.read_voltages()
        
        # Convert raw values to voltage (2.5V reference, 12-bit resolution)
        # Voltage = (raw_value / 4096) * 2.5
        converted = []
        for channel, raw in voltages:
            voltage = (raw / 4096) * 2.5
            converted.append((channel, f"{voltage:.3f}V"))
        
        print("\nVoltage Readings:")
        for ch, val in converted:
            print(f"CH{ch}: {val}")
        
        # Read temperature
        try:
            temp = adc.read_temperature()
            print(f"Temperature: {temp:.2f}°C")
        except RuntimeError as e:
            print(e)
        
        sleep(1)  # Wait 1 second between readings

except KeyboardInterrupt:
    print("\nExiting...")