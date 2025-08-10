import subprocess
from .base import SystemChecker

class MacOSChecker(SystemChecker):
    def check_disk_encryption(self):
        try:
            # Check FileVault status
            output = subprocess.check_output("fdesetup status", shell=True, encoding="utf-8").strip()
            is_encrypted = "On" in output
            return {"disk_encrypted": is_encrypted}
        except Exception as e:
            return {"disk_encrypted": False, "error": str(e)}

    def check_os_updates(self):
        try:
            # Check for available updates
            output = subprocess.check_output("softwareupdate -l", shell=True, encoding="utf-8")
            up_to_date = "No new software available." in output
            return {"os_up_to_date": up_to_date}
        except Exception as e:
            return {"os_up_to_date": False, "error": str(e)}

    def check_antivirus(self):
        try:
            # Check for common antivirus processes (example: Symantec, Sophos, Avast, etc.)
            av_processes = ["Symantec", "Sophos", "Avast", "McAfee", "Norton", "Malwarebytes"]
            output = subprocess.check_output("ps aux", shell=True, encoding="utf-8")
            found = any(av.lower() in output.lower() for av in av_processes)
            return {"antivirus_present": found}
        except Exception as e:
            return {"antivirus_present": False, "error": str(e)}

    def check_sleep_settings(self):
        try:
            # Get sleep timeout (in minutes)
            output = subprocess.check_output("pmset -g | grep sleep", shell=True, encoding="utf-8")
            # Example line:  sleep 10 (value in minutes)
            import re
            match = re.search(r"sleep\s+(\d+)", output)
            timeout_minutes = int(match.group(1)) if match else None
            return {"sleep_timeout": timeout_minutes}
        except Exception as e:
            return {"sleep_timeout": None, "error": str(e)}