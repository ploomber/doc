import torchaudio as ta
import torch
from transformers import WhisperProcessor, WhisperForConditionalGeneration
from chatterbox.tts import ChatterboxTTS

def voice_to_text_to_voice_pipeline(input_audio_path, audio_prompt_path, output_path):
    """
    Complete pipeline: voice -> text -> voice (transformed)
    
    Args:
        input_audio_path: Path to input audio file to transcribe
        audio_prompt_path: Path to audio prompt for voice transformation
        output_path: Path to save the transformed output audio
    """
    
    # Step 1: Voice -> Text using Whisper from transformers
    print("Loading Whisper model...")
    processor = WhisperProcessor.from_pretrained("openai/whisper-base")
    model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-base")
    
    print(f"Transcribing audio from {input_audio_path}...")
    # Load audio file
    audio_input, sample_rate = ta.load(input_audio_path)
    
    # Resample to 16kHz if needed (Whisper expects 16kHz)
    if sample_rate != 16000:
        resampler = ta.transforms.Resample(sample_rate, 16000)
        audio_input = resampler(audio_input)
    
    # Convert to mono if stereo
    if audio_input.shape[0] > 1:
        audio_input = torch.mean(audio_input, dim=0, keepdim=True)
    
    # Process audio
    input_features = processor(audio_input.squeeze().numpy(), sampling_rate=16000, return_tensors="pt").input_features
    
    # Generate transcription
    with torch.no_grad():
        predicted_ids = model.generate(input_features)
    
    transcribed_text = processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
    print(f"Transcribed text: {transcribed_text}")
    
    # Step 2: Text -> Voice using ChatterboxTTS with audio prompt
    print("Loading ChatterboxTTS model...")
    assert torch.cuda.is_available(), "CUDA is not available. Please install CUDA and PyTorch with GPU support."
    tts_model = ChatterboxTTS.from_pretrained(device="cuda")
    
    print(f"Generating transformed voice using prompt from {audio_prompt_path}...")
    wav = tts_model.generate(transcribed_text, audio_prompt_path=audio_prompt_path)
    
    # Step 3: Save the transformed audio
    ta.save(output_path, wav, tts_model.sr)
    print(f"Transformed audio saved to {output_path}")
    
    return transcribed_text, output_path

# Example usage with your existing setup
if __name__ == "__main__":
    # Original text-to-speech example (keeping for reference)
    print("=== Original Text-to-Speech Example ===")
    text = "Ezreal and Jinx teamed up with Ahri, Yasuo, and Teemo to take down the enemy's Nexus in an epic late-game pentakill."
    model = ChatterboxTTS.from_pretrained(device="cuda" if torch.cuda.is_available() else "cpu")
    AUDIO_PROMPT_PATH = "male_petergriffin.wav"
    wav = model.generate(text, audio_prompt_path=AUDIO_PROMPT_PATH)
    ta.save("output_original.wav", wav, model.sr)
    print("Original output saved to output_original.wav")
    
    # New voice-to-text-to-voice pipeline with file input
    print("\n=== Voice-to-Text-to-Voice Pipeline (File Input) ===")
    # You'll need to provide an input audio file to transcribe
    # For demo purposes, let's use the audio prompt as input (you can change this)
    INPUT_AUDIO_PATH = "male_petergriffin.wav"  # Change this to your input audio file
    AUDIO_PROMPT_PATH = "male_petergriffin.wav"  # This transforms the voice style
    OUTPUT_PATH = "output_transformed.wav"
    
    try:
        transcribed_text, output_file = voice_to_text_to_voice_pipeline(
            INPUT_AUDIO_PATH, 
            AUDIO_PROMPT_PATH, 
            OUTPUT_PATH
        )
        print(f"\nFile pipeline completed successfully!")
        print(f"Transcribed: '{transcribed_text}'")
        print(f"Transformed audio saved to: {output_file}")
    except Exception as e:
        print(f"Error in file pipeline: {e}")
        print("Make sure you have an input audio file and the required models are available.")
    
    # Live microphone recording demo
    print("\n=== Live Microphone Recording Demo ===")
    try:
        from microphone_recorder import MicrophoneRecorder
        
        response = input("Would you like to try live microphone recording? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            recorder = MicrophoneRecorder()
            
            print("\n🎤 Available audio devices:")
            recorder.list_audio_devices()
            
            print(f"\n🔴 Ready to record! Speak into your microphone...")
            print("Press ENTER when you're done speaking.")
            
            temp_recording_path = "temp_recording.wav"
            success = recorder.record_and_save(temp_recording_path)
            
            if success:
                print(f"\n🎯 Processing your recorded audio...")
                transcribed_text, output_file = voice_to_text_to_voice_pipeline(
                    temp_recording_path,
                    AUDIO_PROMPT_PATH,
                    "output_live_recording.wav"
                )
                
                print(f"\n✅ Live recording pipeline completed!")
                print(f"📝 You said: '{transcribed_text}'")
                print(f"🔊 Your voice transformed and saved to: output_live_recording.wav")
                
                # Clean up temporary file
                import os
                os.remove(temp_recording_path)
                print("🗑️  Temporary recording file cleaned up.")
            else:
                print("❌ Recording failed.")
        else:
            print("Skipping live recording demo.")
            
    except ImportError:
        print("Microphone recording not available. Install sounddevice and soundfile packages.")
    except Exception as e:
        print(f"Error in live recording demo: {e}")
