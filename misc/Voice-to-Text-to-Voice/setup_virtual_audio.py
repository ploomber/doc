#!/usr/bin/env python3
"""
Virtual Audio Device Setup Helper

This script helps users set up virtual audio devices for real-time voice transformation.
"""

import platform
import subprocess
import sys
import webbrowser
from pathlib import Path

def detect_os():
    """Detect the operating system."""
    system = platform.system().lower()
    if system == "windows":
        return "windows"
    elif system == "darwin":
        return "macos"
    elif system == "linux":
        return "linux"
    else:
        return "unknown"

def check_virtual_audio_windows():
    """Check for virtual audio software on Windows."""
    print("🔍 Checking for virtual audio software on Windows...")
    
    # Check for VB-Cable
    vb_cable_paths = [
        "C:\\Program Files\\VB\\CABLE",
        "C:\\Program Files (x86)\\VB\\CABLE"
    ]
    
    vb_cable_found = any(Path(path).exists() for path in vb_cable_paths)
    
    # Check for VoiceMeeter
    voicemeeter_paths = [
        "C:\\Program Files\\VB\\Voicemeeter",
        "C:\\Program Files (x86)\\VB\\Voicemeeter"
    ]
    
    voicemeeter_found = any(Path(path).exists() for path in voicemeeter_paths)
    
    return vb_cable_found, voicemeeter_found

def setup_windows():
    """Setup instructions for Windows."""
    print("\n🪟 Windows Virtual Audio Setup")
    print("=" * 40)
    
    vb_cable, voicemeeter = check_virtual_audio_windows()
    
    if vb_cable or voicemeeter:
        print("✅ Virtual audio software detected!")
        if vb_cable:
            print("  - VB-Cable is installed")
        if voicemeeter:
            print("  - VoiceMeeter is installed")
    else:
        print("❌ No virtual audio software detected.")
        print("\n📥 Recommended: Install VB-Cable (free and simple)")
        print("   Download: https://vb-audio.com/Cable/")
        
        choice = input("\nWould you like to open the download page? (y/n): ").lower().strip()
        if choice in ['y', 'yes']:
            webbrowser.open("https://vb-audio.com/Cable/")
    
    print("\n🔧 Setup Instructions:")
    print("1. After installing VB-Cable:")
    print("   - Run the real-time voice processor")
    print("   - Set output device to 'CABLE Input'")
    print("   - In Discord/Zoom/etc., select 'CABLE Output' as microphone")
    print("\n2. For VoiceMeeter (more advanced):")
    print("   - Set output device to 'VoiceMeeter Input'")
    print("   - In Discord/Zoom/etc., select 'VoiceMeeter Output' as microphone")

def setup_macos():
    """Setup instructions for macOS."""
    print("\n🍎 macOS Virtual Audio Setup")
    print("=" * 40)
    
    # Check for BlackHole using system_profiler (basic check)
    try:
        result = subprocess.run(
            ["system_profiler", "SPAudioDataType"], 
            capture_output=True, text=True, timeout=10
        )
        blackhole_found = "BlackHole" in result.stdout
    except:
        blackhole_found = False
    
    if blackhole_found:
        print("✅ BlackHole detected!")
    else:
        print("❌ BlackHole not detected.")
        print("\n📥 Recommended: Install BlackHole")
        print("   Download: https://github.com/ExistentialAudio/BlackHole")
        
        choice = input("\nWould you like to open the download page? (y/n): ").lower().strip()
        if choice in ['y', 'yes']:
            webbrowser.open("https://github.com/ExistentialAudio/BlackHole/releases")
    
    print("\n🔧 Setup Instructions:")
    print("1. After installing BlackHole:")
    print("   - Run the real-time voice processor")
    print("   - Set output device to 'BlackHole 2ch'")
    print("   - In Discord/Zoom/etc., select 'BlackHole 2ch' as microphone")
    print("\n2. Optional: Create Multi-Output Device")
    print("   - Open Audio MIDI Setup")
    print("   - Create Multi-Output Device with BlackHole + your speakers")
    print("   - This lets you hear the output while routing to apps")

def setup_linux():
    """Setup instructions for Linux."""
    print("\n🐧 Linux Virtual Audio Setup")
    print("=" * 40)
    
    # Check for PulseAudio
    try:
        result = subprocess.run(["pulseaudio", "--version"], capture_output=True, text=True)
        pulseaudio_found = result.returncode == 0
    except:
        pulseaudio_found = False
    
    if pulseaudio_found:
        print("✅ PulseAudio detected!")
    else:
        print("❌ PulseAudio not detected. Install it first:")
        print("   Ubuntu/Debian: sudo apt install pulseaudio")
        print("   Fedora: sudo dnf install pulseaudio")
        print("   Arch: sudo pacman -S pulseaudio")
    
    print("\n🔧 Setup Instructions:")
    print("1. Create virtual audio device:")
    print("   pactl load-module module-null-sink sink_name=virtual_mic sink_properties=device.description=VirtualMic")
    print("\n2. Create loopback (to hear output):")
    print("   pactl load-module module-loopback source=virtual_mic.monitor sink=@DEFAULT_SINK@")
    print("\n3. Run the real-time voice processor:")
    print("   - Set output device to the virtual sink")
    print("   - In Discord/Zoom/etc., select the virtual source as microphone")
    print("\n4. To remove virtual device later:")
    print("   pactl unload-module module-null-sink")

def test_current_setup():
    """Test the current audio setup."""
    print("\n🧪 Testing Current Audio Setup")
    print("=" * 40)
    
    try:
        import sounddevice as sd
        
        print("📋 Available Audio Devices:")
        devices = sd.query_devices()
        
        input_devices = []
        output_devices = []
        virtual_devices = []
        
        virtual_keywords = [
            'cable', 'voicemeeter', 'blackhole', 'soundflower', 
            'virtual', 'null', 'monitor', 'loopback'
        ]
        
        for i, device in enumerate(devices):
            device_name_lower = device['name'].lower()
            is_virtual = any(keyword in device_name_lower for keyword in virtual_keywords)
            
            if device['max_input_channels'] > 0:
                input_devices.append((i, device['name'], is_virtual))
            if device['max_output_channels'] > 0:
                output_devices.append((i, device['name'], is_virtual))
            
            if is_virtual:
                virtual_devices.append((i, device['name'], device))
        
        print("\n📥 Input Devices:")
        for idx, name, is_virtual in input_devices:
            marker = "🔀" if is_virtual else "🎤"
            print(f"  {marker} {idx}: {name}")
        
        print("\n📤 Output Devices:")
        for idx, name, is_virtual in output_devices:
            marker = "🔀" if is_virtual else "🔊"
            print(f"  {marker} {idx}: {name}")
        
        if virtual_devices:
            print(f"\n✅ Found {len(virtual_devices)} virtual audio device(s)!")
            print("🎯 You can use these for real-time voice transformation.")
        else:
            print("\n⚠️  No virtual audio devices found.")
            print("🔧 Follow the setup instructions above to install virtual audio software.")
        
    except ImportError:
        print("❌ sounddevice not installed. Run: pip install sounddevice")
    except Exception as e:
        print(f"❌ Error testing audio setup: {e}")

def main():
    """Main setup function."""
    print("🎙️  Virtual Audio Device Setup Helper")
    print("=" * 50)
    print("This script helps you set up virtual audio devices for real-time voice transformation.")
    print("Virtual devices allow you to use transformed audio as a microphone in other apps.")
    
    # Detect OS
    os_type = detect_os()
    print(f"\n🖥️  Detected OS: {os_type.title()}")
    
    # OS-specific setup
    if os_type == "windows":
        setup_windows()
    elif os_type == "macos":
        setup_macos()
    elif os_type == "linux":
        setup_linux()
    else:
        print(f"\n❓ Unknown OS: {os_type}")
        print("Please check the documentation for manual setup instructions.")
    
    # Test current setup
    test_current_setup()
    
    print("\n🚀 Next Steps:")
    print("1. Install virtual audio software (if not already installed)")
    print("2. Test with: poetry run python voice_pipeline.py --real-time --list-devices")
    print("3. Start real-time processing: poetry run python voice_pipeline.py --real-time voice_prompt.wav")
    print("4. In your app (Discord, Zoom), select the virtual device as microphone")
    
    print("\n💡 Tips:")
    print("- Use shorter chunk durations (1-2s) for lower latency")
    print("- Make sure your voice prompt file has good audio quality")
    print("- Test audio levels before important calls/streams")

if __name__ == "__main__":
    main() 