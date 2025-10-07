import json
from datetime import timedelta
from typing import Tuple
import yaml

def parse_yaml(file_path: str) -> dict:
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def parse_transcript(json_content, output="plain") -> Tuple[str, int]:
    """
    Parse Google STT JSON result into different formats.
    
    Args:
        json_content (str | dict): JSON string or dict from Google STT output
        output (str): "plain" or "timestamp"
    
    Returns:
        str: formatted transcript
        int: total lines of transcript
    """
    if isinstance(json_content, str):
        data = json.loads(json_content)
    else:
        data = json_content

    results = data.get("results", [])
    lines = []

    def format_time(offset_str):
        # offset_str เช่น "59.940s" → timedelta
        seconds = float(offset_str.replace("s", ""))
        td = timedelta(seconds=seconds)
        return td

    if output == "plain":
        # แค่รวม transcript ทั้งหมด
        for r in results:
            if r.get("alternatives"):
                lines.append(r["alternatives"][0]["transcript"])
        return "\n".join(lines), len(results)

    elif output == "timestamp":
        # แสดง transcript พร้อมเวลา (mm:ss)
        for r in results:
            if r.get("alternatives"):
                text = r["alternatives"][0]["transcript"]
                end_time = format_time(r["resultEndOffset"])
                minutes, seconds = divmod(end_time.total_seconds(), 60)
                time_str = f"[{int(minutes):02}:{int(seconds):02}]"
                lines.append(f"{time_str} {text}")
        return "\n".join(lines), len(results)

    else:
        raise ValueError("Invalid output type. Choose from 'plain', 'timestamp', or 'srt'.")