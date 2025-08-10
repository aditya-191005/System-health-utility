import subprocess
import re
import ctypes
from .base import SystemChecker

def is_admin():
    """Check if the script is running with administrative privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

class WindowsChecker(SystemChecker):
    def check_disk_encryption(self):
        if not is_admin():
            return {"disk_encrypted": False, "error": "Administrator privileges required to check BitLocker status."}

        try:
            output = subprocess.check_output(["manage-bde", "-status", "C:"], encoding="utf-8")

            # Parse output using regex to extract conversion and protection status
            conversion_match = re.search(r"Conversion Status:\s+(.*)", output)
            protection_match = re.search(r"Protection Status:\s+(.*)", output)

            conversion_status = conversion_match.group(1).strip() if conversion_match else "Unknown"
            protection_status = protection_match.group(1).strip() if protection_match else "Unknown"

            # Consider drive encrypted only if both conditions are met
            is_encrypted = (
                conversion_status.lower() == "fully encrypted" and
                protection_status.lower() == "protection on"
            )

            return {"disk_encrypted": is_encrypted}

        except subprocess.CalledProcessError as e:
            return {"disk_encrypted": False, "error": f"Failed to execute manage-bde: {e}"}
        except Exception as e:
            return {"disk_encrypted": False, "error": str(e)}


    def check_os_updates(self):
        try:
            ps_script = """
            $Session = New-Object -ComObject Microsoft.Update.Session
            $Searcher = $Session.CreateUpdateSearcher()
            $results = $Searcher.Search("IsInstalled=0 and Type='Software'")
            if ($results.Updates.Count -gt 0) {
                Write-Output "False"
            } else {
                Write-Output "True"
            }
            """
            completed = subprocess.run(["powershell", "-Command", ps_script], capture_output=True, text=True)
            result = completed.stdout.strip()
            return {"os_up_to_date": result == "True"}
        except Exception as e:
            return {"os_up_to_date": False, "error": str(e)}

    def check_antivirus(self):
        try:
            ps_script = """
            $avProducts = Get-CimInstance -Namespace root/SecurityCenter2 -ClassName AntiVirusProduct
            if ($avProducts) {
                $avProducts.Count
            } else {
                0
            }
            """
            completed = subprocess.run(["powershell", "-Command", ps_script], capture_output=True, text=True)
            output = completed.stdout.strip()

            # If PowerShell returns an empty string, treat as 0
            count = int(output) if output.isdigit() else 0

            return {"antivirus_present": count > 0}
        except Exception as e:
            return {"antivirus_present": False, "error": str(e)}

    def check_firewall(self):
        try:
            ps_script = """
            $firewall = Get-NetFirewallProfile | Where-Object { $_.Enabled -eq 'True' }
            if ($firewall) {
                $firewall.Count
            } else {
                0
            }
            """
            completed = subprocess.run(["powershell", "-Command", ps_script], capture_output=True, text=True)
            output = completed.stdout.strip()

            # If PowerShell returns an empty string, treat as 0
            count = int(output) if output.isdigit() else 0

            return {"firewall_enabled": count > 0}
        except Exception as e:
            return {"firewall_enabled": False, "error": str(e)}

    def check_sleep_settings(self):
        try:
            import re

            # Get the active power scheme
            completed = subprocess.run(["powercfg", "/getactivescheme"], capture_output=True, text=True)
            output = completed.stdout.strip()

            # Extract GUID
            m = re.search(r"Power Scheme GUID: ([a-f0-9\-]+)", output, re.I)
            if not m:
                return {"sleep_timeout": -1, "error": "Could not find active power scheme GUID"}

            scheme_guid = m.group(1)

            # Query sleep settings for that scheme
            completed2 = subprocess.run(
                ["powercfg", "/query", scheme_guid, "SUB_SLEEP", "STANDBYIDLE"],
                capture_output=True, text=True)
            query_output = completed2.stdout

            # Extract the AC (plugged-in) sleep timeout
            m2 = re.search(r"Current AC Power Setting Index: 0x([0-9a-f]+)", query_output, re.I)
            if not m2:
                return {"sleep_timeout": -1, "error": "Could not find sleep timeout setting"}

            timeout_seconds = int(m2.group(1), 16)
            timeout_minutes = timeout_seconds // 60

            return {
                "sleep_timeout": timeout_minutes
            }

        except Exception as e:
            return {"sleep_timeout": -1, "error": str(e)}
