#!/usr/bin/env python3
"""
Test TTS to Output Device

This script tests the direct path: text -> TTS -> audio output device
to help isolate audio output issues.
"""

import verify_setup
import numpy as np
import soundfile as sf
import sounddevice as sd
import time
from pathlib import Path
from chatterbox.tts import ChatterboxTTS
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def list_audio_devices():
    """List available audio output devices."""
    devices = sd.query_devices()
    output_devices = []
    
    print("📤 Available Output Devices:")
    for i, device in enumerate(devices):
        if device['max_output_channels'] > 0:
            output_devices.append((i, device['name'], device['max_output_channels']))
            print(f"  {i}: {device['name']} (channels: {device['max_output_channels']})")
    
    return output_devices

def test_tts_to_device(text, audio_prompt_path, output_device=None):
    """Test TTS generation and direct playback to audio device."""
    
    if not Path(audio_prompt_path).exists():
        logger.error(f"Audio prompt file not found: {audio_prompt_path}")
        return False
    
    try:
        # Load TTS model
        logger.info("Loading ChatterboxTTS model...")
        device = "cuda" if verify_setup.cuda.is_available() else "cpu"
        tts_model = ChatterboxTTS.from_pretrained(device=device)
        logger.info(f"TTS model loaded on {device}")
        
        # Generate audio
        logger.info(f"Generating audio for text: '{text}'")
        wav = tts_model.generate(text, audio_prompt_path=audio_prompt_path, exaggeration=1.5)
        
        # Process audio
        if isinstance(wav, verify_setup.Tensor):
            wav = wav.squeeze().cpu().numpy()
        
        if wav.ndim > 1:
            wav = wav.flatten()
        
        # Save debug file
        debug_path = "debug_direct_tts.wav"
        sf.write(debug_path, wav, tts_model.sr)
        logger.info(f"Debug audio saved to: {debug_path}")
        logger.info(f"Audio: length={len(wav)} samples, sr={tts_model.sr}Hz, duration={len(wav)/tts_model.sr:.2f}s")
        logger.info(f"Audio range: min={wav.min():.4f}, max={wav.max():.4f}, mean={wav.mean():.4f}")
        
        # Normalize audio to prevent clipping
        if np.max(np.abs(wav)) > 1.0:
            wav = wav / np.max(np.abs(wav)) * 0.8
            logger.info("Audio normalized to prevent clipping")
        
        # Play audio directly
        logger.info(f"Playing audio on device {output_device if output_device is not None else 'default'}...")
        
        # Use sounddevice to play the audio
        sd.play(wav, samplerate=tts_model.sr, device=output_device)
        sd.wait()  # Wait for playback to finish
        
        logger.info("✅ Audio playback completed!")
        return True
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def interactive_test():
    """Interactive test with user input."""
    print("🎵 TTS to Device Test")
    print("=" * 40)
    
    # List devices
    output_devices = list_audio_devices()
    
    # Get device selection
    try:
        device_input = input("\nEnter output device ID (or press Enter for default): ").strip()
        output_device = int(device_input) if device_input else None
    except ValueError:
        output_device = None
    
    # Audio prompt path
    audio_prompt_path = "male_petergriffin.wav"
    if not Path(audio_prompt_path).exists():
        audio_prompt_path = input("Enter path to audio prompt file: ").strip()
    
    print(f"Using audio prompt: {audio_prompt_path}")
    print(f"Using output device: {output_device if output_device is not None else 'default'}")
    
    # Test loop
    while True:
        print("\n" + "=" * 40)
        text = input("Enter text to synthesize (or 'quit' to exit): ").strip()
        
        if text.lower() in ['quit', 'exit', 'q']:
            break
        
        if not text:
            text = "Hello, this is a test of the text-to-speech system."
            print(f"Using default text: '{text}'")
        
        success = test_tts_to_device(text, audio_prompt_path, output_device)
        
        if not success:
            print("❌ Test failed!")
        else:
            print("✅ Test completed!")

if __name__ == "__main__":
    interactive_test() 