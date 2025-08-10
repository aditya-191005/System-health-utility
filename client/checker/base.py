from abc import ABC, abstractmethod

class SystemChecker(ABC):
    @abstractmethod
    def check_disk_encryption(self): pass

    @abstractmethod
    def check_os_updates(self): pass

    @abstractmethod
    def check_antivirus(self): pass

    @abstractmethod
    def check_sleep_settings(self): pass
