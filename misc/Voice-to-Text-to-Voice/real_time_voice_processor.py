#!/usr/bin/env python3
"""
Real-time Voice Processor with Virtual Microphone Output

This module provides real-time voice transformation that can output to a virtual
microphone device for use by other applications (Discord, Zoom, OBS, etc.).
"""

import numpy as np
import sounddevice as sd
import torch
import torchaudio as ta
import threading
import queue
import time
import tempfile
import os
from pathlib import Path
from transformers import WhisperProcessor, WhisperForConditionalGeneration
from chatterbox.tts import ChatterboxTTS
import logging
import soundfile as sf

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealTimeVoiceProcessor:
    def __init__(self, audio_prompt_path, chunk_duration=3.0, overlap_duration=0.5, 
                 sample_rate=16000, device_name_prefix="BetterVoice", debug_output=True):
        """
        Initialize the real-time voice processor.
        
        Args:
            audio_prompt_path: Path to audio file for voice style cloning
            chunk_duration: Duration of audio chunks to process (seconds)
            overlap_duration: Overlap between chunks for smoother processing
            sample_rate: Audio sample rate (16kHz for Whisper)
            device_name_prefix: Prefix for virtual device name
            debug_output: Whether to save debug audio files
        """
        self.audio_prompt_path = audio_prompt_path
        self.chunk_duration = chunk_duration
        self.overlap_duration = overlap_duration
        self.sample_rate = sample_rate
        self.device_name_prefix = device_name_prefix
        self.debug_output = debug_output
        
        # Audio buffers and queues
        self.input_buffer = queue.Queue()
        self.output_buffer = queue.Queue()
        self.processing_queue = queue.Queue()
        
        # Control flags
        self.running = False
        self.processing = False
        
        # Models (will be loaded lazily)
        self.whisper_processor = None
        self.whisper_model = None
        self.tts_model = None
        
        # Audio chunk tracking
        self.chunk_size = int(chunk_duration * sample_rate)
        self.overlap_size = int(overlap_duration * sample_rate)
        self.audio_accumulator = np.array([])
        
        # Debug tracking
        self.debug_counter = 0
        self.debug_directory = Path("debug_audio")
        if self.debug_output:
            self.debug_directory.mkdir(exist_ok=True)
            logger.info(f"Debug audio files will be saved to: {self.debug_directory}")
        
        # Audio output management
        self.output_audio_buffer = np.array([])  # Continuous buffer for audio output
        self.output_sample_rate = None  # Will be set when TTS model loads
        self.buffer_lock = threading.Lock()  # Thread safety for buffer access
        
    def load_models(self):
        """Load Whisper and TTS models."""
        logger.info("Loading Whisper model...")
        self.whisper_processor = WhisperProcessor.from_pretrained("openai/whisper-base")
        self.whisper_model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-base")
        
        logger.info("Loading ChatterboxTTS model...")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tts_model = ChatterboxTTS.from_pretrained(device=device)
        
        # Set output sample rate to TTS model's sample rate for better quality
        self.output_sample_rate = self.tts_model.sr
        logger.info(f"Output sample rate set to: {self.output_sample_rate}Hz")
        
        logger.info("Models loaded successfully!")
    
    def transcribe_chunk(self, audio_chunk):
        """
        Transcribe an audio chunk using Whisper.
        
        Args:
            audio_chunk: numpy array of audio data
            
        Returns:
            Transcribed text string
        """
        if len(audio_chunk) < self.sample_rate * 0.5:  # Skip very short chunks
            return ""
        
        try:
            # Convert to torch tensor and ensure correct format
            audio_tensor = torch.tensor(audio_chunk, dtype=torch.float32)
            
            # Process with Whisper
            input_features = self.whisper_processor(
                audio_tensor.numpy(), 
                sampling_rate=self.sample_rate, 
                return_tensors="pt"
            ).input_features
            
            # Generate transcription
            with torch.no_grad():
                predicted_ids = self.whisper_model.generate(input_features)
            
            transcribed_text = self.whisper_processor.batch_decode(
                predicted_ids, skip_special_tokens=True
            )[0].strip()
            
            return transcribed_text
            
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return ""
    
    def synthesize_speech(self, text):
        """
        Generate speech from text using ChatterboxTTS.
        
        Args:
            text: Text to synthesize
            
        Returns:
            numpy array of synthesized audio
        """
        if not text.strip():
            return np.array([])
            
        try:
            # Generate speech with voice cloning
            wav = self.tts_model.generate(text, audio_prompt_path=self.audio_prompt_path)
            
            # Convert to numpy and ensure correct format
            if isinstance(wav, torch.Tensor):
                # Flatten the tensor to 1D and convert to numpy
                wav = wav.squeeze().cpu().numpy()
            
            # Ensure we have a 1D array
            if wav.ndim > 1:
                wav = wav.flatten()
            
            # Save debug audio file
            if self.debug_output:
                debug_filename = self.debug_directory / f"debug_{self.debug_counter:04d}_original.wav"
                # Save at original sample rate first
                sf.write(str(debug_filename), wav, self.tts_model.sr)
                logger.info(f"Debug: Original TTS audio saved to {debug_filename}")
            
            # No resampling - use TTS model's native sample rate for better quality
            # The output stream will be configured to match this rate
            
            # Save debug audio file
            if self.debug_output:
                debug_filename_final = self.debug_directory / f"debug_{self.debug_counter:04d}_final.wav"
                sf.write(str(debug_filename_final), wav, self.tts_model.sr)
                logger.info(f"Debug: Final audio saved to {debug_filename_final}")
                logger.info(f"Debug: Audio length = {len(wav)} samples ({len(wav)/self.tts_model.sr:.2f}s)")
                self.debug_counter += 1
            
            return wav.astype(np.float32)
            
        except Exception as e:
            logger.error(f"Speech synthesis error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return np.array([])
    
    def process_audio_chunk(self, audio_chunk):
        """
        Process a single audio chunk through the complete pipeline.
        
        Args:
            audio_chunk: numpy array of input audio
            
        Returns:
            numpy array of transformed audio
        """
        # Step 1: Transcribe
        text = self.transcribe_chunk(audio_chunk)
        if not text:
            return np.array([])  # Return empty array instead of zeros
        
        logger.info(f"Transcribed: '{text}'")
        
        # Step 2: Synthesize
        transformed_audio = self.synthesize_speech(text)
        
        if len(transformed_audio) == 0:
            logger.warning("No audio generated from TTS")
            return np.array([])
        
        logger.info(f"Generated audio: {len(transformed_audio)} samples ({len(transformed_audio)/self.tts_model.sr:.2f}s)")
        
        # Return the full generated audio - preserve natural speech timing
        return transformed_audio
    
    def audio_input_callback(self, indata, frames, time, status):
        """Callback for audio input stream."""
        if status:
            logger.warning(f"Input status: {status}")
        
        if self.running:
            # Add to input buffer
            audio_data = indata[:, 0] if len(indata.shape) > 1 else indata
            self.input_buffer.put(audio_data.copy())
    
    def audio_output_callback(self, outdata, frames, time, status):
        """Callback for audio output stream."""
        if status:
            logger.warning(f"Output status: {status}")
        
        try:
            with self.buffer_lock:
                # Initialize output with zeros
                outdata.fill(0)
                
                # Check if we have enough audio in our continuous buffer
                if len(self.output_audio_buffer) >= frames:
                    # Extract the required frames
                    audio_chunk = self.output_audio_buffer[:frames]
                    
                    # Remove consumed audio from buffer
                    self.output_audio_buffer = self.output_audio_buffer[frames:]
                    
                    # Normalize audio to prevent clipping
                    if np.max(np.abs(audio_chunk)) > 1.0:
                        audio_chunk = audio_chunk / np.max(np.abs(audio_chunk)) * 0.8
                    
                    # Output the audio
                    outdata[:, 0] = audio_chunk
                    
                    # logger.debug(f"Playing {frames} samples, buffer remaining: {len(self.output_audio_buffer)}")
                
                elif len(self.output_audio_buffer) > 0:
                    # Use remaining audio and pad with zeros
                    remaining = len(self.output_audio_buffer)
                    audio_chunk = self.output_audio_buffer
                    self.output_audio_buffer = np.array([])
                    
                    # Normalize audio
                    if np.max(np.abs(audio_chunk)) > 1.0:
                        audio_chunk = audio_chunk / np.max(np.abs(audio_chunk)) * 0.8
                    
                    outdata[:remaining, 0] = audio_chunk
                    # The rest remains zero-filled
                    
                    logger.debug(f"Playing final {remaining} samples")
                
        except Exception as e:
            logger.error(f"Audio output error: {e}")
    
    def processing_worker(self):
        """Worker thread for audio processing."""
        while self.running:
            try:
                # Accumulate input audio
                while not self.input_buffer.empty():
                    chunk = self.input_buffer.get_nowait()
                    self.audio_accumulator = np.concatenate([self.audio_accumulator, chunk])
                
                # Process when we have enough audio
                if len(self.audio_accumulator) >= self.chunk_size:
                    # Extract chunk for processing
                    processing_chunk = self.audio_accumulator[:self.chunk_size]
                    
                    # Keep overlap for next chunk
                    self.audio_accumulator = self.audio_accumulator[self.chunk_size - self.overlap_size:]
                    
                    # Process the chunk
                    logger.info(f"Processing chunk of {len(processing_chunk)} samples")
                    transformed_chunk = self.process_audio_chunk(processing_chunk)
                    
                    if len(transformed_chunk) > 0:
                        # Add to continuous output buffer
                        with self.buffer_lock:
                            self.output_audio_buffer = np.concatenate([self.output_audio_buffer, transformed_chunk])
                        
                        logger.info(f"Added {len(transformed_chunk)} samples to output buffer (total: {len(self.output_audio_buffer)})")
                    else:
                        logger.warning("No transformed audio to add to output buffer")
                
                time.sleep(0.01)  # Small delay to prevent busy waiting
                
            except queue.Empty:
                time.sleep(0.01)
            except Exception as e:
                logger.error(f"Processing error: {e}")
                import traceback
                logger.error(traceback.format_exc())
                time.sleep(0.1)
    
    def start_real_time_processing(self, input_device=None, output_device=None):
        """
        Start real-time voice processing.
        
        Args:
            input_device: Input device ID (None for default)
            output_device: Output device ID (None for default)
        """
        if not Path(self.audio_prompt_path).exists():
            raise FileNotFoundError(f"Audio prompt file not found: {self.audio_prompt_path}")
        
        # Load models if not already loaded
        if self.whisper_model is None:
            self.load_models()
        
        logger.info("Starting real-time voice processing...")
        
        self.running = True
        
        # Start processing worker thread
        processing_thread = threading.Thread(target=self.processing_worker, daemon=True)
        processing_thread.start()
        
        # Audio stream parameters
        blocksize = 1024  # Small blocksize for low latency
        
        try:
            # Start input and output streams
            # Use TTS model's sample rate for output for better quality
            with sd.InputStream(
                device=input_device,
                channels=1,
                samplerate=self.sample_rate,  # Keep 16kHz for Whisper input
                blocksize=blocksize,
                callback=self.audio_input_callback
            ), sd.OutputStream(
                device=output_device,
                channels=1,
                samplerate=self.output_sample_rate,  # Use TTS model's native sample rate
                blocksize=blocksize,
                callback=self.audio_output_callback
            ):
                logger.info("🎤 Real-time voice processing started!")
                logger.info(f"Input: {self.sample_rate}Hz, Output: {self.output_sample_rate}Hz")
                logger.info("Speak into your microphone. The transformed audio will be output to the selected device.")
                logger.info("Press Ctrl+C to stop...")
                
                # Keep running until interrupted
                while self.running:
                    time.sleep(0.1)
                    
        except KeyboardInterrupt:
            logger.info("Stopping real-time processing...")
        except Exception as e:
            logger.error(f"Stream error: {e}")
        finally:
            self.stop_processing()
    
    def stop_processing(self):
        """Stop real-time processing."""
        self.running = False
        logger.info("Real-time processing stopped.")
    
    def list_audio_devices(self):
        """List available audio devices."""
        logger.info("Available audio devices:")
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
            print(f"  {idx}: {name} (channels: {channels})")
        
        print("\n📤 Output Devices (Speakers/Virtual Devices):")
        for idx, name, channels in output_devices:
            print(f"  {idx}: {name} (channels: {channels})")
        
        return input_devices, output_devices


class VirtualMicrophoneManager:
    """
    Manager for virtual microphone devices.
    
    This provides utilities for setting up virtual audio devices that other
    applications can use as microphone inputs.
    """
    
    @staticmethod
    def setup_virtual_device_instructions():
        """Print instructions for setting up virtual audio devices."""
        print("\n🎧 Setting up Virtual Microphone:")
        print("=" * 50)
        print("To use the transformed audio as a microphone in other apps:")
        print("")
        print("📋 WINDOWS:")
        print("1. Install VB-Cable or VoiceMeeter")
        print("   - VB-Cable: https://vb-audio.com/Cable/")
        print("   - VoiceMeeter: https://vb-audio.com/Voicemeeter/")
        print("2. Set output device to 'CABLE Input' or 'VoiceMeeter Input'")
        print("3. In your app (Discord, Zoom), select 'CABLE Output' or 'VoiceMeeter Output' as microphone")
        print("")
        print("📋 MACOS:")
        print("1. Install BlackHole or SoundFlower")
        print("   - BlackHole: https://github.com/ExistentialAudio/BlackHole")
        print("2. Set output device to 'BlackHole 2ch'")
        print("3. In your app, select 'BlackHole 2ch' as microphone")
        print("")
        print("📋 LINUX:")
        print("1. Use PulseAudio virtual sink:")
        print("   pactl load-module module-null-sink sink_name=virtual_mic")
        print("2. Set output device to the virtual sink")
        print("3. In your app, select the virtual sink as microphone")
        print("")
    
    @staticmethod
    def find_virtual_devices():
        """Find potential virtual audio devices."""
        devices = sd.query_devices()
        virtual_devices = []
        
        virtual_keywords = [
            'cable', 'voicemeeter', 'blackhole', 'soundflower', 
            'virtual', 'null', 'monitor', 'loopback'
        ]
        
        for i, device in enumerate(devices):
            device_name_lower = device['name'].lower()
            if any(keyword in device_name_lower for keyword in virtual_keywords):
                virtual_devices.append((i, device['name'], device))
        
        return virtual_devices


def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Real-time voice transformation with virtual microphone output"
    )
    parser.add_argument(
        "audio_prompt",
        help="Path to audio prompt file for voice cloning"
    )
    parser.add_argument(
        "--input-device", "-i",
        type=int,
        help="Input device ID (microphone)"
    )
    parser.add_argument(
        "--output-device", "-o", 
        type=int,
        help="Output device ID (speakers/virtual device)"
    )
    parser.add_argument(
        "--list-devices", "-l",
        action="store_true",
        help="List available audio devices"
    )
    parser.add_argument(
        "--chunk-duration", "-c",
        type=float,
        default=3.0,
        help="Audio chunk duration in seconds (default: 3.0)"
    )
    parser.add_argument(
        "--setup-help", "-s",
        action="store_true",
        help="Show virtual device setup instructions"
    )
    
    args = parser.parse_args()
    
    if args.setup_help:
        VirtualMicrophoneManager.setup_virtual_device_instructions()
        return
    
    # Create processor
    processor = RealTimeVoiceProcessor(
        audio_prompt_path=args.audio_prompt,
        chunk_duration=args.chunk_duration
    )
    
    if args.list_devices:
        processor.list_audio_devices()
        
        print("\n🔍 Detected Virtual Devices:")
        virtual_devices = VirtualMicrophoneManager.find_virtual_devices()
        if virtual_devices:
            for idx, name, device in virtual_devices:
                print(f"  {idx}: {name}")
        else:
            print("  No virtual devices detected.")
            print("  Run with --setup-help for setup instructions.")
        return
    
    # Validate audio prompt
    if not Path(args.audio_prompt).exists():
        print(f"❌ Error: Audio prompt file '{args.audio_prompt}' not found")
        return
    
    # Start processing
    try:
        processor.start_real_time_processing(
            input_device=args.input_device,
            output_device=args.output_device
        )
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main() 