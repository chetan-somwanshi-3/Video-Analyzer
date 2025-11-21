"""
Unit tests for the processor.
We create a tiny synthetic video (a moving dot), run process_video, and assert:
- output video is created
- frame count and FPS are correct
- metrics dictionary has valid values
"""

import os
import cv2
import numpy as np
import pytest
from app.processor import process_video


def create_synthetic_video(path, width=160, height=120, fps=10, frames=15):
    """Generate a simple video with a green circle moving horizontally."""
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(path, fourcc, fps, (width, height))
    for i in range(frames):
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        x = int((i / frames) * (width - 20)) + 10
        y = height // 2
        cv2.circle(frame, (x, y), 8, (0, 255, 0), -1)
        writer.write(frame)
    writer.release()


def test_process_creates_output(tmp_path):
    """Ensure that process_video() creates an output file and returns metrics."""
    in_v = tmp_path / "in.mp4"
    out_v = tmp_path / "out.mp4"
    create_synthetic_video(str(in_v), width=160, height=120, fps=10, frames=15)

    frames_written, fps, metrics = process_video(
        str(in_v),
        str(out_v),
        target_fps=10,
        return_metrics=True
    )

    # File existence
    assert out_v.exists(), "Output video not created."

    # Frame & FPS sanity checks
    assert frames_written >= 10, "Too few frames written."
    assert abs(fps - 10.0) < 1e-3, f"Unexpected FPS: {fps}"

    # Metrics sanity checks
    assert isinstance(metrics, dict)
    assert "frames_processed" in metrics
    assert "avg_movement_intensity" in metrics
    assert metrics["frames_processed"] == frames_written
    assert 0 <= metrics["avg_movement_intensity"] < 1


if __name__ == "__main__":
    pytest.main([__file__])
