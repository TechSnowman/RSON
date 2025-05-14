"""
Python Driver for AD7291 SAR ADC using smbus2
Adapted for Raspberry Pi

* Author(s): Thomas Damiani (original), Adapted by Assistant
"""

from smbus2 import SMBus, i2c_msg
import time

# Register addresses
_COMMAND_REGISTER = 0x00
_VOLTAGE_CONVERSION = 0x01
_T_SENSE_CONVERSION_RESULT = 0x02

_DEFAULT_ADDRESS = 0x2F

class AD7291:
    """Driver for the AD7291 SAR ADC (Raspberry Pi smbus version)"""
    
    def __init__(self, bus=1, addr=_DEFAULT_ADDRESS, 
                 active_channels=[False]*8,
                 enable_temp=False,
                 enable_noise_delay=False):
        """
        Initialize AD7291 ADC
        :param bus: I2C bus number (default 1 for Raspberry Pi)
        :param addr: Device address (default 0x2F)
        :param active_channels: List of 8 booleans for enabled channels
        :param enable_temp: Enable temperature sensor
        :param enable_noise_delay: Enable noise delay
        """
        self.bus = SMBus(bus)
        self.addr = addr
        self.active_channels = active_channels
        self.enable_temp = enable_temp
        self.enable_noise_delay = enable_noise_delay
        
        # Calculate active channels
        self.num_active_channels = sum(active_channels)
        
        # Build command register values
        command_high = 0x00
        command_low = 0x00
        
        # Temperature enable (bit 15)
        if enable_temp:
            command_high |= 0x80
            
        # Noise delay (bit 11)
        if enable_noise_delay:
            command_high |= 0x08
            
        # Channel enables (bits 7-0)
        command_low = self._channels_to_byte(active_channels)
        
        # Write configuration to command register
        self._write_register(_COMMAND_REGISTER, [command_high, command_low])
        time.sleep(0.1)  

    def _channels_to_byte(self, channels):
        """Convert boolean list to channel enable byte"""
        byte = 0
        for i, enabled in enumerate(channels):
            if enabled:
                byte |= 1 << (7 - i)  # MSB = CH0, LSB = CH7
        return byte

    def _write_register(self, register, data):
        """Write to a register"""
        msg = i2c_msg.write(self.addr, [register] + data)
        self.bus.i2c_rdwr(msg)

    def _read_register(self, register, length):
        """Read from a register"""
        msg = i2c_msg.write(self.addr, [register])
        self.bus.i2c_rdwr(msg)
        read_msg = i2c_msg.read(self.addr, length)
        self.bus.i2c_rdwr(read_msg)
        return list(read_msg)

    def read_voltages(self):
        """Read all active voltage channels"""
        if self.num_active_channels == 0:
            return []
            
        # Read voltage conversion register
        data = self._read_register(_VOLTAGE_CONVERSION, 2 * self.num_active_channels)
        
        results = []
        for i in range(0, len(data), 2):
            high = data[i]
            low = data[i+1]
            
            channel = (high >> 4) & 0x0F
            raw_value = ((high & 0x0F) << 8) | low
            
            # Validate channel number
            if channel > 7:
                raise ValueError(f"Invalid channel number {channel} in response")
                
            results.append((channel, raw_value))
            
        return results

    def read_temperature(self):
        """Read temperature sensor"""
        if not self.enable_temp:
            raise RuntimeError("Temperature sensor not enabled")
            
        data = self._read_register(_T_SENSE_CONVERSION_RESULT, 2)
        high = data[0]
        low = data[1]
        
        channel = (high >> 4) & 0x0F
        if channel != 8:
            raise ValueError("Temperature channel mismatch")
            
        raw = ((high & 0x0F) << 8) | low
        
        # Handle two's complement conversion
        if raw > 0x7FF:
            raw -= 0x1000
            
        return raw * 0.25  # 0.25°C per LSB

# Example usage:
if __name__ == "__main__":
    adc = AD7291(
        bus=1,
        active_channels=[True]*8,  # Enable all channels
        enable_temp=True
    )
    
    print("Voltages:", adc.read_voltages())
    print("Temperature:", adc.read_temperature(), "°C")