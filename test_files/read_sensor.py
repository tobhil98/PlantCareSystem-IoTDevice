import smbus
bus = smbus.SMBus(1)
raw_temp = bus.read_i2c_block_data(0x40,0xE3,2)
raw_humid = bus.read_i2c_block_data(0x40,0xE5,2)
Temperature = 175.72*(raw_temp[0]<<8 | raw_temp[1])/65536.0 - 46.85
Humidity    = 125*(raw_humid[0]<<8 | raw_humid[1])/65536.0 - 6.0

print("Temp:", Temperature)
print("Humid:", Humidity)
