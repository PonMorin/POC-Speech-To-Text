from state import EtlState
from pydub import AudioSegment
import os

def convert_to_wav_specific(state: EtlState) -> EtlState:
    """
    Converts an audio/video file to a .wav file with specific audio settings:
    - Codec: pcm_s16le (16-bit PCM)
    - Sampling rate: 16000 Hz
    - Channels: 1 (mono)

    Supports: .mov, .mp4, .m4a, .mp3, .wav, .flac, .ogg, etc.

    Args:
        input_file (str): Path to the input file.
        output_file (str): Path to save the output .wav file.

    Returns:
        str: Path to the converted .wav file.
    """
    print("\033[92m--- Converting to wav ---\033[00m")
    input_files: str = state.get("input_files", None)
    
    if input_files:
        for file in input_files:
            input_file: str = "data/" +  file
            filename = os.path.basename(file)
            absolute_filename = os.path.splitext(filename)[0]
            output_file: str = state["output_file"] + f"/{absolute_filename}.wav"
            
            if os.path.isdir(input_file):
                continue
            
            os.makedirs(state["output_file"], exist_ok=True)
            # Check file exists
            if not os.path.exists(input_file):
                raise FileNotFoundError(f"Input file not found: {input_file}")

            # Get the file extension (without dot)
            ext = os.path.splitext(input_file)[1].lower().replace(".", "")

            # Load the file with the detected format
            if ext != "wav":
                try:
                    audio = AudioSegment.from_file(input_file, format=ext)
                except Exception as e:
                    raise ValueError(f"Cannot load {input_file}. Unsupported format or missing codec.\nError: {e}")

                # Apply target settings
                audio = (
                    audio.set_channels(1)
                    .set_frame_rate(16000)
                    .set_sample_width(2)  # 16-bit PCM
                )

                # Export as WAV
                audio.export(output_file, format="wav")
                print(f"✅ Converted to WAV: {output_file}")
            else:
                print("This file is .wav already.")
    else:
        print("No input files")
        
    return state
