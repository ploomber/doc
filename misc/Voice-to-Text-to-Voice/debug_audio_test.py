#!/usr/bin/env python3
"""
Debug Audio Test Script

This script tests the TTS audio generation separately from real-time processing
to help diagnose audio output issues.
"""

import torch
import numpy as np
import soundfile as sf
from pathlib import Path
from chatterbox.tts import ChatterboxTTS
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_tts_generation():
    """Test TTS audio generation with debug output."""
    
    # Test configuration
    audio_prompt_path = "male_petergriffin.wav"  # Update this path as needed
    test_text = "Hello, this is a test of the text-to-speech system."
    
    if not Path(audio_prompt_path).exists():
        logger.error(f"Audio prompt file not found: {audio_prompt_path}")
        return
    
    try:
        # Load TTS model
        logger.info("Loading ChatterboxTTS model...")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        tts_model = ChatterboxTTS.from_pretrained(device=device)
        logger.info(f"TTS model loaded on {device}")
        
        # Generate audio
        logger.info(f"Generating audio for text: '{test_text}'")
        wav = tts_model.generate(test_text, audio_prompt_path=audio_prompt_path)
        
        # Process audio
        if isinstance(wav, torch.Tensor):
            wav = wav.squeeze().cpu().numpy()
        
        if wav.ndim > 1:
            wav = wav.flatten()
        
        # Save original audio
        original_path = "debug_tts_original.wav"
        sf.write(original_path, wav, tts_model.sr)
        logger.info(f"Original TTS audio saved to: {original_path}")
        logger.info(f"Original audio: length={len(wav)} samples, sr={tts_model.sr}Hz, duration={len(wav)/tts_model.sr:.2f}s")
        logger.info(f"Original audio: min={wav.min():.4f}, max={wav.max():.4f}, mean={wav.mean():.4f}")
        
        # Test resampling to 16kHz (Whisper sample rate)
        target_sr = 16000
        if tts_model.sr != target_sr:
            import torchaudio as ta
            logger.info(f"Resampling from {tts_model.sr}Hz to {target_sr}Hz")
            wav_tensor = torch.tensor(wav, dtype=torch.float32).unsqueeze(0)
            resampler = ta.transforms.Resample(tts_model.sr, target_sr)
            wav_resampled = resampler(wav_tensor).squeeze().numpy()
            
            # Save resampled audio
            resampled_path = "debug_tts_resampled.wav"
            sf.write(resampled_path, wav_resampled, target_sr)
            logger.info(f"Resampled audio saved to: {resampled_path}")
            logger.info(f"Resampled audio: length={len(wav_resampled)} samples, sr={target_sr}Hz, duration={len(wav_resampled)/target_sr:.2f}s")
            logger.info(f"Resampled audio: min={wav_resampled.min():.4f}, max={wav_resampled.max():.4f}, mean={wav_resampled.mean():.4f}")
        
        logger.info("TTS test completed successfully!")
        logger.info("Check the generated audio files to verify they sound correct.")
        
    except Exception as e:
        logger.error(f"TTS test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    test_tts_generation() 