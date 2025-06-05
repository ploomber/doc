#!/usr/bin/env python3
"""
Microphone Recording Module

This module provides functionality to record audio from the microphone
with user-controlled start/stop.
"""

import sounddevice as sd
import soundfile as sf
import numpy as np
import threading
import time
from pathlib import Path

class MicrophoneRecorder:
    def __init__(self, sample_rate=16000, channels=1):
        """
        Initialize the microphone recorder.
        
        Args:
            sample_rate: Sample rate for recording (16kHz is good for Whisper)
            channels: Number of audio channels (1 = mono, 2 = stereo)
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.recording = False
        self.audio_data = []
        
    def list_audio_devices(self):
        """List available audio devices."""
        print("📋 Available Audio Devices:")
        devices = sd.query_devices()
        
        input_devices = []
        output_devices = []
        
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                input_devices.append((i, device['name'], device['max_input_channels']))
            if device['max_output_channels'] > 0:
                output_devices.append((i, device['name'], device['max_output_channels']))
        
        print("\n📥 Input Devices (Microphones):")
        for idx, name, channels in input_devices:
            print(f"  🎤 {idx}: {name} (channels: {channels})")
        
        print("\n📤 Output Devices (Speakers/Headphones):")
        for idx, name, channels in output_devices:
            print(f"  🔊 {idx}: {name} (channels: {channels})")
        
        return input_devices, output_devices
    
    def record_audio(self, device=None):
        """
        Record audio from microphone with real-time user control.
        
        Args:
            device: Device ID to use (None for default)
            
        Returns:
            numpy array of recorded audio data
        """
        self.audio_data = []
        self.recording = True
        
        def audio_callback(indata, frames, time, status):
            if status:
                print(f"Audio status: {status}")
            if self.recording:
                self.audio_data.append(indata.copy())
        
        print(f"🎤 Recording audio at {self.sample_rate}Hz...")
        print("Press ENTER to stop recording...")
        
        # Start recording in a separate thread
        with sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            callback=audio_callback,
            device=device
        ):
            # Wait for user to press Enter
            input()
        
        self.recording = False
        print("🛑 Recording stopped.")
        
        if self.audio_data:
            # Concatenate all recorded chunks
            recorded_audio = np.concatenate(self.audio_data, axis=0)
            return recorded_audio.flatten()  # Flatten to 1D array
        else:
            return np.array([])
    
    def save_recording(self, audio_data, output_path):
        """
        Save recorded audio to file.
        
        Args:
            audio_data: numpy array of audio data
            output_path: path to save the audio file
        """
        if len(audio_data) == 0:
            print("⚠️  No audio data to save.")
            return False
            
        sf.write(output_path, audio_data, self.sample_rate)
        print(f"💾 Audio saved to: {output_path}")
        return True
    
    def record_and_save(self, output_path, device=None):
        """
        Record audio and save it to a file.
        
        Args:
            output_path: path to save the recorded audio
            device: device ID to use (None for default)
            
        Returns:
            True if recording was successful, False otherwise
        """
        try:
            audio_data = self.record_audio(device)
            return self.save_recording(audio_data, output_path)
        except Exception as e:
            print(f"❌ Recording error: {e}")
            return False

def test_microphone():
    """Test function to check microphone recording."""
    recorder = MicrophoneRecorder()
    recorder.list_audio_devices()
    
    print("\nTesting microphone recording...")
    success = recorder.record_and_save("test_recording.wav")
    
    if success:
        print("✅ Microphone test successful!")
        # Clean up test file
        Path("test_recording.wav").unlink(missing_ok=True)
    else:
        print("❌ Microphone test failed!")

if __name__ == "__main__":
    test_microphone() 
