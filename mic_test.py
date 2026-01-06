import pyaudio

p = pyaudio.PyAudio()
info = p.get_host_api_info_by_index(0)
numdevices = info.get('deviceCount')

print("\n--- AVAILABLE MICROPHONES ---")
for i in range(0, numdevices):
    if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
        name = p.get_device_info_by_host_api_device_index(0, i).get('name')
        print(f"Device ID {i}: {name}")

print("\n-----------------------------")
default_device = p.get_default_input_device_info()
print(f">> CURRENT DEFAULT: ID {default_device['index']} - {default_device['name']}")