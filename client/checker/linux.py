import subprocess
from .base import SystemChecker

class LinuxChecker(SystemChecker):
    def check_disk_encryption(self):
        try:
            # Check for LUKS encrypted partitions
            output = subprocess.check_output("lsblk -o NAME,TYPE,MOUNTPOINT | grep crypt", shell=True, encoding="utf-8")
            is_encrypted = bool(output.strip())
            return {"disk_encrypted": is_encrypted}
        except Exception as e:
            return {"disk_encrypted": False, "error": str(e)}

    def check_os_updates(self):
        try:
            # Check for available updates (Debian/Ubuntu)
            output = subprocess.check_output("apt list --upgradable 2>/dev/null | grep -v Listing", shell=True, encoding="utf-8")
            up_to_date = not bool(output.strip())
            return {"os_up_to_date": up_to_date}
        except Exception as e:
            return {"os_up_to_date": False, "error": str(e)}

    def check_antivirus(self):
        try:
            # Check for ClamAV service
            output = subprocess.check_output("systemctl is-active clamav-daemon", shell=True, encoding="utf-8").strip()
            is_active = output == "active"
            return {"antivirus_present": is_active}
        except Exception as e:
            return {"antivirus_present": False, "error": str(e)}

    def check_sleep_settings(self):
        try:
            # Check inactivity sleep timeout (GNOME)
            output = subprocess.check_output(
                "gsettings get org.gnome.settings-daemon.plugins.power sleep-inactive-ac-timeout",
                shell=True, encoding="utf-8"
            ).strip()
            # Value is in seconds
            timeout_minutes = int(output) // 60
            return {"sleep_timeout": timeout_minutes}
        except Exception as e:
            return {"sleep_timeout": None, "error": str(e)}