# POC-Speech-To-Text

## How to use GCP Function 

`path config/GCP.py`

### 1. Upload file
```python
initialize_gcs_client()
BUCKET_NAME = "Bucket name"
wav_file = "test.wav"
folder_name = f"km-video/test_upload/{wav_file}"

with open(wav_file, 'rb') as file_obj:
    upload_to_gcs(BUCKET_NAME, file_obj, folder_name)
```

### 2. List file in folder
```python
initialize_gcs_client()
BUCKET_NAME = "Bucket name"

folder_name = f"km-video/test_upload/"
list_file = list_blobs_in_folder(BUCKET_NAME, folder_name)

for i in list_file:
    print(i)
```

### 3. Move file A to B folder
```python
initialize_gcs_client()
BUCKET_NAME = "Bucket name"
SOURCE_FILE = "km-video/test_upload/Day2.wav"
DEST_FOLDER = "km-video/test_movefile/"

move_successful = move_blob_in_same_bucket(BUCKET_NAME, SOURCE_FILE, DEST_FOLDER)

if move_successful:
    print("Move operation completed.")
else:
    print("Move operation failed or source file was not found.")
```