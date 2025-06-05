#!/usr/bin/env python3
"""
Voice-to-Text-to-Voice Pipeline Utility

This script provides an interactive interface for transforming voice recordings
using the Whisper + ChatterboxTTS pipeline.
"""

import sys
import tempfile
from pathlib import Path
from main import voice_to_text_to_voice_pipeline
from microphone_recorder import MicrophoneRecorder
import numpy as np

def get_user_choice(prompt, options):
    """Get user choice from a list of options"""
    while True:
        print(f"\n{prompt}")
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")
        
        try:
            choice = input(f"\nEnter your choice (1-{len(options)}): ").strip()
            choice_num = int(choice)
            if 1 <= choice_num <= len(options):
                return choice_num - 1
            else:
                print(f"❌ Please enter a number between 1 and {len(options)}")
        except ValueError:
            print("❌ Please enter a valid number")

def get_file_path(prompt, must_exist=True):
    """Get a file path from user with validation"""
    while True:
        file_path = input(f"{prompt}: ").strip()
        if not file_path:
            print("❌ Please enter a file path")
            continue
        
        path = Path(file_path)
        if must_exist and not path.exists():
            print(f"❌ File '{file_path}' not found. Please check the path and try again.")
            continue
        
        return file_path

def filter_and_format_devices(devices, device_type):
    """Filter and format devices to show only the most relevant ones"""
    if not devices:
        return []
    
    # Filter out duplicates and less relevant devices
    filtered_devices = []
    seen_names = set()
    
    # Priority keywords for different device types
    if device_type == "input":
        priority_keywords = ["microphone", "mic", "cable output", "virtual", "input"]
        skip_keywords = ["mapper", "primary", "driver"]
    else:  # output
        priority_keywords = ["speakers", "headphones", "cable input", "virtual", "output"]
        skip_keywords = ["mapper", "primary", "driver", "spdif"]
    
    # First pass: collect priority devices
    priority_devices = []
    regular_devices = []
    
    for idx, name, info in devices:
        # Clean up the name
        clean_name = name.lower().strip()
        
        # Skip obvious duplicates
        if clean_name in seen_names:
            continue
        seen_names.add(clean_name)
        
        # Skip less useful devices
        if any(skip in clean_name for skip in skip_keywords):
            continue
        
        # Shorten long names
        display_name = name
        if len(display_name) > 50:
            display_name = display_name[:47] + "..."
        
        device_entry = (idx, display_name, info)
        
        # Check if it's a priority device
        if any(keyword in clean_name for keyword in priority_keywords):
            priority_devices.append(device_entry)
        else:
            regular_devices.append(device_entry)
    
    # Combine priority devices first, then regular ones (but limit total)
    filtered_devices = priority_devices + regular_devices
    
    # Limit to reasonable number
    return filtered_devices[:10]

def get_device_choice(devices, device_type):
    """Get device choice from user with simplified interface"""
    if not devices:
        print(f"❌ No {device_type} devices found!")
        return None
    
    # Filter and format devices
    filtered_devices = filter_and_format_devices(devices, device_type)
    
    if not filtered_devices:
        print(f"❌ No suitable {device_type} devices found!")
        return None
    
    print(f"\n🎧 Select {device_type.title()} Device:")
    for i, (idx, name, info) in enumerate(filtered_devices, 1):
        # Highlight virtual devices
        if "virtual" in name.lower() or "cable" in name.lower():
            print(f"  {i}. 🔀 {name}")
        elif device_type == "input" and ("mic" in name.lower() or "microphone" in name.lower()):
            print(f"  {i}. 🎤 {name}")
        elif device_type == "output" and ("speaker" in name.lower() or "headphone" in name.lower()):
            print(f"  {i}. 🔊 {name}")
        else:
            print(f"  {i}. 📱 {name}")
    
    # Add option to show all devices
    print(f"  {len(filtered_devices) + 1}. 📋 Show all {device_type} devices")
    
    while True:
        try:
            choice = input(f"\nChoose {device_type} device (1-{len(filtered_devices) + 1}): ").strip()
            choice_num = int(choice)
            
            if choice_num == len(filtered_devices) + 1:
                # Show all devices
                print(f"\n📋 All Available {device_type.title()} Devices:")
                for i, (idx, name, info) in enumerate(devices, 1):
                    short_name = name[:60] + "..." if len(name) > 60 else name
                    print(f"  {i}. [{idx}] {short_name}")
                print(f"\nEnter device number (1-{len(devices)}) or 0 to go back:")
                
                while True:
                    try:
                        all_choice = input().strip()
                        if all_choice == "0":
                            break
                        all_choice_num = int(all_choice)
                        if 1 <= all_choice_num <= len(devices):
                            device_idx, device_name, _ = devices[all_choice_num - 1]
                            print(f"✅ Selected: {device_name}")
                            return device_idx
                        else:
                            print(f"❌ Please enter 1-{len(devices)} or 0 to go back")
                    except ValueError:
                        print("❌ Please enter a valid number")
                continue
            
            elif 1 <= choice_num <= len(filtered_devices):
                device_idx, device_name, _ = filtered_devices[choice_num - 1]
                print(f"✅ Selected: {device_name}")
                return device_idx
            else:
                print(f"❌ Please enter a number between 1 and {len(filtered_devices) + 1}")
        except ValueError:
            print("❌ Please enter a valid number")

def record_speaker_audio(input_devices, output_devices, output_path):
    """
    Record audio from speakers/output devices (capture what's playing through speakers).
    This captures the actual audio output (like YouTube, music, etc.).
    
    Args:
        input_devices: List of available input devices
        output_devices: List of available output devices  
        output_path: Path to save the recorded audio
        
    Returns:
        True if recording was successful, False otherwise
    """
    print("\n🔊 Recording Audio from Speaker Output")
    print("=" * 45)
    print("This will capture whatever is playing through your speakers")
    print("(YouTube videos, music, system sounds, etc.)")
    
    # Look for loopback/monitor devices in input devices first
    loopback_devices = []
    for idx, name, info in input_devices:
        name_lower = name.lower()
        # Look for devices that can capture speaker output
        if any(keyword in name_lower for keyword in [
            'stereo mix', 'what you hear', 'wave out mix', 'loopback',
            'monitor', 'cable output', 'virtual cable', 'vb-audio',
            'voicemeeter', 'obs', 'desktop audio', 'system audio'
        ]):
            loopback_devices.append((idx, name, info, 'loopback'))
    
    # Also check if any output devices support monitoring (less common but possible)
    for idx, name, info in output_devices:
        name_lower = name.lower()
        if 'monitor' in name_lower or 'loopback' in name_lower:
            loopback_devices.append((idx, name, info, 'monitor'))
    
    device_idx = None
    recording_mode = 'standard'
    
    if loopback_devices:
        print("✅ Found devices that can capture speaker audio:")
        for i, (idx, name, info, device_type) in enumerate(loopback_devices, 1):
            if device_type == 'loopback':
                print(f"  {i}. 🔄 {name} (Loopback)")
            else:
                print(f"  {i}. 📺 {name} (Monitor)")
        
        print(f"  {len(loopback_devices) + 1}. 🔧 Manual setup help")
        print(f"  {len(loopback_devices) + 2}. 📋 Show all devices anyway")
        
        while True:
            try:
                choice = input(f"\nChoose option (1-{len(loopback_devices) + 2}): ").strip()
                choice_num = int(choice)
                
                if choice_num == len(loopback_devices) + 1:
                    # Show manual setup help
                    show_speaker_capture_help()
                    continue
                elif choice_num == len(loopback_devices) + 2:
                    # Show all devices
                    print("\n📋 All Available Input Devices:")
                    for i, (idx, name, info) in enumerate(input_devices, 1):
                        print(f"  {i}. [{idx}] {name}")
                    
                    while True:
                        try:
                            all_choice = input(f"Choose device (1-{len(input_devices)}) or 0 to go back: ").strip()
                            if all_choice == "0":
                                break
                            all_choice_num = int(all_choice)
                            if 1 <= all_choice_num <= len(input_devices):
                                device_idx = input_devices[all_choice_num - 1][0]
                                print(f"✅ Selected: {input_devices[all_choice_num - 1][1]}")
                                recording_mode = 'standard'
                                break
                            else:
                                print(f"❌ Please enter 1-{len(input_devices)} or 0")
                        except ValueError:
                            print("❌ Please enter a valid number")
                    if device_idx is not None:
                        break
                elif 1 <= choice_num <= len(loopback_devices):
                    device_idx = loopback_devices[choice_num - 1][0]
                    device_name = loopback_devices[choice_num - 1][1]
                    recording_mode = 'loopback'
                    print(f"✅ Selected: {device_name}")
                    break
                else:
                    print(f"❌ Please enter 1-{len(loopback_devices) + 2}")
            except ValueError:
                print("❌ Please enter a valid number")
    else:
        print("⚠️  No loopback/monitor devices found automatically.")
        print("💡 You may need to enable speaker capture on your system:")
        show_speaker_capture_help()
        
        enable_choice = get_user_choice("\nWhat would you like to do?", [
            "Try to use any input device anyway",
            "Show manual setup instructions again", 
            "Cancel speaker recording"
        ])
        
        if enable_choice == 0:
            # Let user choose from all input devices
            device_idx = get_device_choice(input_devices, "input")
            if device_idx is None:
                return False
            recording_mode = 'standard'
        elif enable_choice == 1:
            show_speaker_capture_help()
            return False
        else:
            return False
    
    if device_idx is None:
        return False
    
    # Create recorder with specific settings for speaker capture
    if recording_mode == 'loopback':
        # For loopback devices, we might want stereo recording
        recorder = MicrophoneRecorder(sample_rate=44100, channels=2)  # Higher quality for music/video
    else:
        recorder = MicrophoneRecorder()
    
    print(f"\n🎵 Speaker Recording Instructions:")
    print("=" * 40)
    if recording_mode == 'loopback':
        print("✅ Using loopback device - this should capture speaker audio directly!")
    else:
        print("⚠️  Using standard input device - results may vary")
    
    print("\n📋 Steps:")
    print("1. Open your audio source (YouTube, Spotify, etc.)")
    print("2. Press ENTER to start recording")
    print("3. Play your desired audio (keep it 3-10 seconds)")
    print("4. Press ENTER to stop recording")
    print("\n💡 Tips:")
    print("- Choose a clear voice sample without background music")
    print("- Higher volume = better recording quality")
    print("- Avoid system notification sounds during recording")
    
    input("\n🔴 Press ENTER to start recording speaker audio...")
    
    success = recorder.record_and_save(output_path, device=device_idx)
    
    if success:
        print(f"✅ Speaker audio recorded successfully!")
        print(f"💾 Saved to: {output_path}")
        
        # Ask if user wants to hear the recording
        play_choice = get_user_choice("🔊 Would you like to play back the recorded prompt?", 
                                    ["No", "Yes"])
        if play_choice == 1:
            try:
                import sounddevice as sd
                import soundfile as sf
                data, fs = sf.read(output_path)
                
                # If stereo, convert to mono for playback
                if len(data.shape) > 1:
                    data = np.mean(data, axis=1)
                
                print("🔊 Playing recorded prompt...")
                sd.play(data, fs)
                sd.wait()
                print("✅ Playback finished")
            except Exception as e:
                print(f"⚠️  Could not play recording: {e}")
        
        return True
    else:
        print("❌ Speaker recording failed!")
        print("💡 Try enabling 'Stereo Mix' in Windows Sound settings or using a virtual audio cable")
        return False

def show_speaker_capture_help():
    """Show help for setting up speaker audio capture."""
    print("\n🔧 Speaker Audio Capture Setup Help")
    print("=" * 45)
    
    import platform
    system = platform.system().lower()
    
    if 'windows' in system:
        print("🪟 WINDOWS SETUP:")
        print("Option 1 - Enable Stereo Mix:")
        print("  1. Right-click sound icon → 'Sounds'")
        print("  2. Go to 'Recording' tab")
        print("  3. Right-click empty space → 'Show Disabled Devices'")
        print("  4. Right-click 'Stereo Mix' → 'Enable'")
        print("  5. Set as default recording device")
        print("")
        print("Option 2 - Virtual Audio Cable (Recommended):")
        print("  1. Download VB-Audio Cable: https://vb-audio.com/Cable/")
        print("  2. Install and restart computer")
        print("  3. Set 'CABLE Input' as your default playback device")
        print("  4. Use 'CABLE Output' for recording")
        
    elif 'darwin' in system:  # macOS
        print("🍎 MACOS SETUP:")
        print("Install BlackHole (Virtual Audio):")
        print("  1. Download: https://github.com/ExistentialAudio/BlackHole")
        print("  2. Install BlackHole 2ch")
        print("  3. Create Multi-Output Device in Audio MIDI Setup")
        print("  4. Use BlackHole as recording source")
        
    elif 'linux' in system:
        print("🐧 LINUX SETUP:")
        print("PulseAudio Monitor:")
        print("  1. List sinks: pactl list short sinks")
        print("  2. Load monitor: pactl load-module module-loopback")
        print("  3. Use monitor device for recording")
        
    else:
        print("❓ GENERAL SETUP:")
        print("Look for 'Stereo Mix', 'What You Hear', or similar options")
        print("Consider installing virtual audio cable software")
    
    print("\n💡 Alternative: Use OBS Studio")
    print("  1. Install OBS Studio (free)")
    print("  2. Add 'Desktop Audio' source")
    print("  3. Use OBS Virtual Camera/Audio for capture")
    
    print("\n🎯 What to look for:")
    print("  - 'Stereo Mix' or 'What You Hear'")
    print("  - Virtual audio cable devices")
    print("  - Monitor/Loopback devices")
    print("  - Desktop audio capture options")

def setup_realtime_mode():
    """Setup and run real-time voice processing"""
    print("\n🚀 Real-time Voice Transformation Setup")
    print("=" * 50)
    
    # Import here to avoid loading if not needed
    from real_time_voice_processor import RealTimeVoiceProcessor, VirtualMicrophoneManager
    
    # Create temporary processor for device listing
    temp_processor = RealTimeVoiceProcessor("dummy.wav")
    input_devices, output_devices = temp_processor.list_audio_devices()
    
    # Show virtual device summary
    virtual_devices = VirtualMicrophoneManager.find_virtual_devices()
    if virtual_devices:
        print(f"\n💡 Found {len(virtual_devices)} virtual audio device(s) - perfect for real-time transformation!")
    else:
        print("\n⚠️  No virtual devices detected. Consider setting up VB-Audio Cable for best results.")
        print("💡 Run with --setup-help flag to see setup instructions.")
    
    # Get input device
    input_device = get_device_choice(input_devices, "input")
    if input_device is None:
        return False
    
    # Get output device
    output_device = get_device_choice(output_devices, "output")
    if output_device is None:
        return False
    
    # Get prompt file - now with option to record from speakers
    prompt_choice = get_user_choice("\n📁 Voice Prompt Setup:", 
                                  ["Use existing voice prompt file", 
                                   "Record new voice prompt from speaker output"])
    
    prompt_file = None
    temp_prompt_file = None
    
    if prompt_choice == 0:  # Use existing file
        prompt_file = get_file_path("📁 Enter path to voice prompt file (.wav)")
    else:  # Record from speakers
        # Create temporary file for the recorded prompt
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            temp_prompt_file = tmp_file.name
        
        success = record_speaker_audio(input_devices, output_devices, temp_prompt_file)
        if not success:
            print("❌ Failed to record speaker audio. Please try using an existing file.")
            prompt_file = get_file_path("📁 Enter path to voice prompt file (.wav)")
        else:
            prompt_file = temp_prompt_file
    
    # Get chunk duration
    while True:
        try:
            chunk_input = input("\n⏱️  Enter chunk duration in seconds (default: 3.0): ").strip()
            if not chunk_input:
                chunk_duration = 3.0
                break
            chunk_duration = float(chunk_input)
            if chunk_duration > 0:
                break
            else:
                print("❌ Chunk duration must be positive")
        except ValueError:
            print("❌ Please enter a valid number")
    
    # Ask about debug mode
    debug_choice = get_user_choice("🐛 Enable debug mode? (saves generated audio to debug files)", 
                                 ["No", "Yes"])
    debug_mode = debug_choice == 1
    
    print(f"\n🎯 Configuration Summary:")
    print(f"  🎤 Input Device: {input_device}")
    print(f"  🔊 Output Device: {output_device}")
    if temp_prompt_file:
        print(f"  📁 Voice Prompt: Recorded from speakers")
    else:
        print(f"  📁 Voice Prompt: {prompt_file}")
    print(f"  ⏱️  Chunk Duration: {chunk_duration}s")
    print(f"  🐛 Debug Mode: {'Enabled' if debug_mode else 'Disabled'}")
    
    # Confirm before starting
    confirm = get_user_choice("\n🚀 Start real-time processing?", ["No", "Yes"])
    if confirm == 0:
        print("❌ Real-time processing cancelled.")
        # Clean up temporary file if created
        if temp_prompt_file:
            try:
                Path(temp_prompt_file).unlink()
            except:
                pass
        return True
    
    # Start processing
    print("\n🚀 Starting real-time voice transformation...")
    print("🔴 Speak into your microphone - your voice will be transformed in real-time!")
    print("🛑 Press Ctrl+C to stop")
    
    processor = RealTimeVoiceProcessor(
        audio_prompt_path=prompt_file,
        chunk_duration=chunk_duration,
        debug_output=debug_mode
    )
    
    try:
        processor.start_real_time_processing(
            input_device=input_device,
            output_device=output_device
        )
    except KeyboardInterrupt:
        print("\n🛑 Real-time processing stopped by user")
    except Exception as e:
        print(f"❌ Real-time processing error: {e}")
        return False
    finally:
        # Clean up temporary prompt file if created
        if temp_prompt_file:
            try:
                Path(temp_prompt_file).unlink()
                print("🗑️  Cleaned up temporary prompt recording")
            except Exception as e:
                print(f"⚠️  Warning: Could not delete temporary prompt file: {e}")
    
    return True

def setup_batch_mode():
    """Setup and run batch voice processing"""
    print("\n📁 Batch Voice Transformation Setup")
    print("=" * 50)
    
    # Ask if user wants to record or use existing file
    input_choice = get_user_choice("🎤 Audio Input Method:", 
                                 ["Use existing audio file", "Record from microphone"])
    
    input_audio_file = None
    
    if input_choice == 1:  # Record from microphone
        print("\n🎤 Microphone Recording Setup")
        
        # Get devices for recording
        recorder = MicrophoneRecorder()
        # Get the device info from recorder
        input_devices = []
        try:
            # This is a simplified approach - we'll let the user choose from available devices
            import pyaudio
            p = pyaudio.PyAudio()
            for i in range(p.get_device_count()):
                try:
                    info = p.get_device_info_by_index(i)
                    if info['maxInputChannels'] > 0:  # Input device
                        input_devices.append((i, info['name'], info))
                except:
                    continue
            p.terminate()
        except:
            print("⚠️  Could not enumerate audio devices. Using default device.")
            input_devices = []
        
        device_id = None
        if input_devices:
            print("\n📋 Available Input Devices for Recording:")
            filtered_devices = filter_and_format_devices(input_devices, "input")
            
            if filtered_devices:
                for i, (idx, name, info) in enumerate(filtered_devices, 1):
                    if "mic" in name.lower() or "microphone" in name.lower():
                        print(f"  {i}. 🎤 {name}")
                    else:
                        print(f"  {i}. 📱 {name}")
                
                while True:
                    try:
                        device_input = input(f"\nSelect device (1-{len(filtered_devices)}) or Enter for default: ").strip()
                        if not device_input:
                            device_id = None
                            break
                        device_choice = int(device_input)
                        if 1 <= device_choice <= len(filtered_devices):
                            device_id = filtered_devices[device_choice - 1][0]
                            print(f"✅ Selected: {filtered_devices[device_choice - 1][1]}")
                            break
                        else:
                            print(f"❌ Please enter 1-{len(filtered_devices)} or Enter for default")
                    except ValueError:
                        print("❌ Please enter a valid number")
        
        # Record audio
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            temp_audio_path = tmp_file.name
        
        print(f"\n🔴 Ready to record!")
        print("🎤 Speak into your microphone and press ENTER when done...")
        input("Press ENTER to start recording...")
        
        success = recorder.record_and_save(temp_audio_path, device=device_id)
        if not success:
            print("❌ Recording failed!")
            return False
        
        input_audio_file = temp_audio_path
        print(f"✅ Recording saved")
        
    else:  # Use existing file
        input_audio_file = get_file_path("📁 Enter path to input audio file (.wav)")
    
    # Get prompt file
    prompt_file = get_file_path("📁 Enter path to voice prompt file (.wav)")
    
    # Get output file
    output_file = get_file_path("📁 Enter path for output audio file (.wav)", must_exist=False)
    
    print(f"\n🎯 Configuration Summary:")
    print(f"  🎤 Input Audio: {Path(input_audio_file).name}")
    print(f"  📁 Voice Prompt: {Path(prompt_file).name}")
    print(f"  💾 Output File: {Path(output_file).name}")
    
    # Confirm before processing
    confirm = get_user_choice("\n🚀 Start batch processing?", ["No", "Yes"])
    if confirm == 0:
        print("❌ Batch processing cancelled.")
        return True
    
    # Process audio
    print("\n🚀 Starting voice-to-text-to-voice pipeline...")
    
    try:
        transcribed_text, final_output_file = voice_to_text_to_voice_pipeline(
            input_audio_file,
            prompt_file,
            output_file
        )
        
        print("\n✅ Pipeline completed successfully!")
        print(f"📝 Transcribed Text: '{transcribed_text}'")
        print(f"🔊 Transformed audio saved to: {final_output_file}")
        
    except Exception as e:
        print(f"❌ Error in pipeline: {e}")
        return False
    
    finally:
        # Clean up temporary recording file if created
        if input_choice == 1:  # Was recorded
            try:
                Path(input_audio_file).unlink()
                print(f"🗑️  Cleaned up temporary recording file")
            except Exception as e:
                print(f"⚠️  Warning: Could not delete temporary file: {e}")
    
    return True

def show_setup_help():
    """Show virtual microphone setup instructions"""
    from real_time_voice_processor import VirtualMicrophoneManager
    VirtualMicrophoneManager.setup_virtual_device_instructions()

def main():
    print("🎤 Voice-to-Text-to-Voice Pipeline")
    print("=" * 40)
    print("Transform your voice using AI-powered speech processing!")
    
    # Check for special help flag
    if len(sys.argv) > 1 and sys.argv[1] in ['--setup-help', '-s']:
        show_setup_help()
        return
    
    # Main mode selection
    mode_choice = get_user_choice(
        "🔧 Select Processing Mode:",
        [
            "Real-time Voice Transformation (live processing)",
            "Batch Voice Transformation (process audio files)",
            "Show Virtual Microphone Setup Help",
            "Exit"
        ]
    )
    
    if mode_choice == 0:  # Real-time
        if not setup_realtime_mode():
            sys.exit(1)
    elif mode_choice == 1:  # Batch
        if not setup_batch_mode():
            sys.exit(1)
    elif mode_choice == 2:  # Setup help
        show_setup_help()
    else:  # Exit
        print("👋 Goodbye!")
        return
    
    print("\n✨ Thank you for using the Voice Pipeline!")

if __name__ == "__main__":
    main() 