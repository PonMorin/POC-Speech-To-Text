import os
import asyncio
from dotenv import load_dotenv
load_dotenv()
from node.funcs.wav_convertor import convert_to_wav_specific
from node.funcs.uploader import upload_wav_to_bucket
from config.GCP import initialize_gcs_client
import shutil

async def main(data_path: str, output_path: str):
    
    input_files: list[str] = os.listdir(data_path)
    # 1. Convertings all videos to wav
    convert_to_wav_specific(input_files=input_files, output_path=output_path)
    
    client = initialize_gcs_client()
    # 2. Uploading all wavs to a bucket
    for file in os.listdir(output_path):
        print(file)
        upload_wav_to_bucket(
            file_obj=f"{output_path}/{file}",
            gcs_client=client
        )
    
    # 3. Clear up the directory
    shutil.rmtree(output_path)
    
    for input in input_files:
        path: str = f"{data_path}/{input}"
        if os.path.exists(path):
            os.remove(path)

    print("\n\033[94mProcess is done!\033[00m")

if __name__ == "__main__":
    
    data_path: str = "data"
    output_path: str = "data/wav"
    
    asyncio.run(main(data_path=data_path, output_path=output_path))