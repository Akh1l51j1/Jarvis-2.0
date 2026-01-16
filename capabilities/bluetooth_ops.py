import subprocess
import os
import time

class BluetoothOps:
    # HARDCODED PATHS
    BASE_PATH = r"C:\Program Files (x86)\Bluetooth Command Line Tools\bin"
    CONNECT_TOOL = os.path.join(BASE_PATH, "btcom.exe")

    KNOWN_DEVICES = {
        "jbl": "40:C1:F6:A6:38:BA",
        "speaker": "40:C1:F6:A6:38:BA",
        "charge 5": "40:C1:F6:A6:38:BA",
        "buds": "48:D8:45:DF:15:42",
        "enco": "48:D8:45:DF:15:42",
        "headphones": "E8:EE:CC:D4:9B:F3",
        "soundcore": "E8:EE:CC:D4:9B:F3",
        "home theater": "3C:A0:67:28:42:F5",
        "phone": "20:64:CB:E1:E8:A6",
    }

    @staticmethod
    def _try_enable_radio_winrt():
        """Attempts to wake Bluetooth Radio via PowerShell WinRT."""
        print("   [Bluetooth] Checking Radio State...")
        ps_script = r"""
        [Windows.Devices.Radios.Radio,Windows.System.Devices,ContentType=WindowsRuntime] | Out-Null
        $bt = [Windows.Devices.Radios.Radio]::GetRadiosAsync().GetResults() | Where-Object { $_.Kind -eq 'Bluetooth' }
        if ($bt -and $bt.State -ne 'On') { $bt.SetStateAsync('On').GetResults() }
        """
        try:
            subprocess.run(["powershell", "-Command", ps_script], capture_output=True)
        except:
            pass

    @staticmethod
    def connect_device(name_fragment):
        target = name_fragment.lower().strip()
        
        # 1. IDENTIFY TARGET
        target_mac = None
        target_name = None
        for name, mac in BluetoothOps.KNOWN_DEVICES.items():
            if target in name:
                target_mac = mac
                target_name = name
                break
        
        if not target_mac:
            return f"Device '{target}' not found."

        # 2. WAKE UP
        BluetoothOps._try_enable_radio_winrt()

        print(f"   [Bluetooth] Target: {target_name} ({target_mac})")

        # 3. THE RESET HANDSHAKE (Disconnect -> Wait -> Connect)
        # -r = remove connection (Disconnect)
        print(f"   [Bluetooth] Resetting connection...")
        subprocess.run(f'"{BluetoothOps.CONNECT_TOOL}" -r -b "{target_mac}"', shell=True, capture_output=True)
        
        time.sleep(2) # CRITICAL PAUSE

        # 4. CONNECT
        # Removed '-s 110B' to let Windows auto-negotiate the best audio path
        print(f"   [Bluetooth] Connecting...")
        cmd = f'"{BluetoothOps.CONNECT_TOOL}" -c -b "{target_mac}"'

        try:
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            output = res.stdout + res.stderr
            
            if "1168" in output or "10049" in output:
                 return f"Failed: {target_name} is not responding. Is it turned on?"

            if "Error" not in output:
                return f"Connected to {target_name}."
            
            return f"Command sent to {target_name}."

        except Exception as e:
            return f"System Error: {e}"