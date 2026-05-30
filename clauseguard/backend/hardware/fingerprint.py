import os
import platform
import psutil
from enum import Enum

class ProfileType(str, Enum):
    LAPTOP = "LAPTOP"
    RPI5 = "RPI5"
    RPI4 = "RPI4"

CACHE_FILE = ".clauseguard_profile"

def detect_profile() -> ProfileType:
    # 1. Check cache first
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                cached = f.read().strip()
                if cached in ProfileType.__members__:
                    return ProfileType(cached)
        except Exception:
            pass

    # 2. Fingerprinting logic
    system_type = platform.system().lower()
    machine = platform.machine().lower()
    processor = platform.processor().lower()
    
    total_ram_gb = psutil.virtual_memory().total / (1024 ** 3)
    
    profile = ProfileType.LAPTOP  # Default fallback
    
    if system_type == "linux":
        # Check Raspberry Pi specifics
        try:
            cpuinfo = ""
            if os.path.exists("/proc/cpuinfo"):
                with open("/proc/cpuinfo", "r") as f:
                    cpuinfo = f.read().lower()
            
            if "bcm2712" in cpuinfo:
                profile = ProfileType.RPI5
            elif "bcm2711" in cpuinfo:
                profile = ProfileType.RPI4
            elif "aarch64" in machine:
                # Secondary check by memory size if BCM label is missing
                if total_ram_gb > 6.0:
                    profile = ProfileType.RPI5
                else:
                    profile = ProfileType.RPI4
        except Exception:
            pass
    elif "arm" in machine or "aarch64" in machine:
        # macOS ARM (M1/M2/M3) or Windows on ARM - categorize as LAPTOP or balanced
        profile = ProfileType.LAPTOP
    else:
        # Standard x86_64 laptop/desktop
        profile = ProfileType.LAPTOP

    # Cache the result
    try:
        with open(CACHE_FILE, "w") as f:
            f.write(profile.value)
    except Exception:
        pass
        
    return profile
