"""
api.py
FastAPI app exposing /analyze endpoint:
- POST /analyze : upload a video file (multipart/form-data)
- returns processed video file (skeleton overlay) + movement metrics
"""

import shutil
import uuid
import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
from .processor import process_video

app = FastAPI(title="Dance Movement Analyzer")

TMP_DIR = Path("/tmp/dance_analyzer")
TMP_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXT = {".mp4", ".mov", ".avi", ".mkv", ".webm"}


@app.post("/analyze")
async def analyze_video(file: UploadFile = File(...)):
    """Analyze uploaded dance video and return processed output + movement metrics."""
    fname = Path(file.filename)
    ext = fname.suffix.lower()
    if ext not in ALLOWED_EXT:
        raise HTTPException(status_code=415, detail=f"Unsupported file type: {ext}")

    unique = uuid.uuid4().hex
    in_path = TMP_DIR / f"{unique}_input{ext}"
    out_path = TMP_DIR / f"{unique}_output.mp4"

    try:
        # Save uploaded file to disk
        with open(in_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # Process video and collect metrics
        frames_written, fps, metrics = process_video(
            str(in_path),
            str(out_path),
            target_fps=None,
            max_frames=300,
            return_metrics=True
        )

        if frames_written == 0 or not out_path.exists():
            raise HTTPException(status_code=500, detail="Processing produced no output.")

        # Embed metrics into response headers for convenience
        headers = {
            "X-Frames-Processed": str(metrics["frames_processed"]),
            "X-Frames-With-Pose": str(metrics["frames_with_pose"]),
            "X-Avg-Movement-Intensity": str(metrics["avg_movement_intensity"]),
            "X-Dominant-Limb": str(metrics["dominant_limb"]),
        }

        # Return JSON + file URL if you’re hosting static files
        return JSONResponse(
            content={
                "message": "Processing complete.",
                "output_video": f"/download/{unique}",
                "metrics": metrics,
            },
            headers=headers
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal processing error: {e}")
    finally:
        # Cleanup uploaded input file
        try:
            file.file.close()
        except Exception:
            pass
        try:
            if in_path.exists():
                in_path.unlink()
        except Exception:
            pass


@app.get("/download/{file_id}")
async def download_video(file_id: str):
    """Download processed video by ID."""
    out_path = TMP_DIR / f"{file_id}_output.mp4"
    if not out_path.exists():
        raise HTTPException(status_code=404, detail="File not found.")
    return FileResponse(str(out_path), media_type="video/mp4", filename=f"{file_id}_skeleton.mp4")
