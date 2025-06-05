# Voice-to-Text-to-Voice Pipeline

This project implements a complete voice transformation pipeline that:

1. **Voice → Text**: Uses OpenAI's Whisper model (via Transformers) to transcribe speech to text
2. **Text → Voice**: Uses ChatterboxTTS to generate speech with voice cloning based on an audio prompt


This can be done from a file, or by using system audio like microphone & speaker

## Usage

Install the dependencies.
```sh
pip install -r requirements.txt
```

Make sure to uninstall & reinstall the right version of Torch, compatible with your Cuda version

Once ready, start the voice_pipeline.

```sh
python voice_pipeline.py
```

### Platform-specific Setup:

**Windows:**
1. Install [VB-Cable](https://vb-audio.com/Cable/) (free)
2. Set output device to "CABLE Input"
3. In Discord/Zoom, select "CABLE Output" as microphone

**macOS:**
1. Install [BlackHole](https://github.com/ExistentialAudio/BlackHole) (free)
2. Set output device to "BlackHole 2ch"
3. In Discord/Zoom, select "BlackHole 2ch" as microphone

**Linux:**
1. Create virtual device: `pactl load-module module-null-sink sink_name=virtual_mic`
2. Set output device to the virtual sink
3. In Discord/Zoom, select the virtual source as microphone

### Performance Tips

- **Lower latency**: Use shorter chunk durations (1-2 seconds)
- **Better quality**: Use longer chunk durations (3-5 seconds)
- **GPU acceleration**: Ensure CUDA is available for faster processing
- **Audio quality**: Use high-quality voice prompt files

## Files

- [`main.py`](./main.py) - Main pipeline implementation with demos
- [`voice_pipeline.py`](./voice_pipeline.py) - Command-line utility script  
- [`male_petergriffin.wav`](./male_petergriffin.wav) - Sample audio prompt for voice cloning
