import platform
import uuid
import hashlib
import subprocess
import os
import requests

from checker.windows import WindowsChecker
from checker.linux import LinuxChecker
from checker.macos import MacOSChecker


def get_checker():
    os_name = platform.system()
    if os_name == "Windows":
        return WindowsChecker()
    elif os_name == "Linux":
        return LinuxChecker()
    elif os_name == "Darwin":
        return MacOSChecker()
    else:
        raise Exception("Unsupported OS")


def get_persistent_machine_id() -> str:
    os_name = platform.system()

    try:
        if os_name == "Windows":
            # Import winreg only on Windows
            import winreg
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                 r"SOFTWARE\Microsoft\Cryptography")
            machine_guid, _ = winreg.QueryValueEx(key, "MachineGuid")
            winreg.CloseKey(key)
            return hashlib.sha256(machine_guid.encode()).hexdigest()[:32]

        elif os_name == "Darwin":  # macOS
            result = subprocess.run(
                ["ioreg", "-rd1", "-c", "IOPlatformExpertDevice"],
                capture_output=True, text=True, check=True
            )
            for line in result.stdout.splitlines():
                if "IOPlatformUUID" in line:
                    uuid_str = line.split('"')[-2]
                    return hashlib.sha256(uuid_str.encode()).hexdigest()[:32]

        elif os_name == "Linux":
            with open("/etc/machine-id", 'r') as f:
                machine_id = f.read().strip()
                return hashlib.sha256(machine_id.encode()).hexdigest()[:32]

    except Exception as e:
        print(f"Error fetching hardware-based machine ID: {e}")

    # Fallback to stored or generated UUID
    fallback_file = ".machine_id"
    if os.path.exists(fallback_file):
        with open(fallback_file, "r") as f:
            return f.read().strip()

    new_id = hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()[:32]
    with open(fallback_file, "w") as f:
        f.write(new_id)
    return new_id


def run_checks():
    checker = get_checker()
    results = {}
    results['machine_id'] = get_persistent_machine_id()
    results['os_name'] = platform.system()
    results.update(checker.check_disk_encryption())
    results.update(checker.check_os_updates())
    results.update(checker.check_antivirus())
    results.update(checker.check_sleep_settings())
    print(results)
    return results


def send_to_backend(data):
    url = "http://localhost:5000/report"
    try:
        response = requests.post(url, json=data)
        if response.status_code in (200, 201):
            print("Report sent successfully!")
        else:
            print(f"Failed to send report. Status: {response.status_code}, Error: {response.text}")
    except Exception as e:
        print(f"Exception occurred while sending report: {e}")


if __name__ == "__main__":
    results = run_checks()
    send_to_backend(results)
