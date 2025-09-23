from pydub import AudioSegment

def convert_mov_to_wav_specific(input_file: str, output_file: str) -> str:
    """
    Converts a .mov file to a .wav file with specific audio settings:
    - Codec: pcm_s16le (16-bit PCM)
    - Sampling rate: 16000 Hz
    - Channels: 1 (mono)

    Args:
        input_file (str): Path to the input .mov file.
        output_file (str): Path to save the output .wav file.

    Returns:
        str: Path to the converted .wav file.
    """
    # Load the audio from the input file
    audio = AudioSegment.from_file(input_file, format="mov")

    audio = audio.set_channels(1)
    
    audio = audio.set_frame_rate(16000)
    
    audio = audio.set_sample_width(2)

    # Export the audio to the output file in wav format
    audio.export(output_file, format="wav")

    return output_file