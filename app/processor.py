"""
processor.py
MediaPipe + OpenCV video processor:
- reads an input video
- runs MediaPipe Pose detection per-frame
- draws skeleton overlay and writes output mp4
- computes basic movement metrics
"""

import cv2
import numpy as np
import os
from typing import Tuple
import mediapipe as mp

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils


def process_video(
    input_path: str,
    output_path: str,
    target_fps: float = None,
    max_frames: int = None,
    return_metrics: bool = False
) -> Tuple[int, float, dict]:
    """
    Processes input video and writes an output video with skeleton overlay + metrics.

    Args:
        input_path: path to input video file
        output_path: path where result video will be saved
        target_fps: if set, force output FPS; otherwise uses input FPS
        max_frames: if set, process only up to max_frames frames (useful for tests)
        return_metrics: if True, also return movement metrics

    Returns:
        (frames_written, output_fps, metrics) or (frames_written, output_fps)
    """

    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise IOError(f"Cannot open video: {input_path}")

    in_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 640)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 480)
    input_frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    out_fps = float(target_fps) if target_fps else in_fps

    # Setup VideoWriter
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(output_path, fourcc, out_fps, (width, height))
    if not writer.isOpened():
        cap.release()
        raise IOError("Could not open VideoWriter - check codecs and container environment")

    # Initialize MediaPipe Pose
    pose = mp_pose.Pose(static_image_mode=False,
                        min_detection_confidence=0.5,
                        min_tracking_confidence=0.5)

    # --- Metrics ---
    metrics = {
        "frames_processed": 0,
        "frames_with_pose": 0,
        "avg_movement_intensity": 0.0,
        "dominant_limb": None,
    }
    prev_landmarks = None
    movement_accumulator = 0.0
    total_points = 0
    left_movement, right_movement = 0.0, 0.0

    frame_idx = 0
    written = 0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame_idx += 1
            if max_frames and frame_idx > max_frames:
                break

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(rgb)

            if results.pose_landmarks:
                metrics["frames_with_pose"] += 1
                mp_drawing.draw_landmarks(
                    frame,
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2),
                )

                landmarks = np.array([(lm.x, lm.y) for lm in results.pose_landmarks.landmark])

                if prev_landmarks is not None and landmarks.shape == prev_landmarks.shape:
                    diff = np.linalg.norm(landmarks - prev_landmarks, axis=1)
                    movement_accumulator += diff.sum()
                    total_points += len(diff)

                    left_idx = [11, 13, 15, 23, 25, 27]
                    right_idx = [12, 14, 16, 24, 26, 28]
                    left_movement += diff[left_idx].sum()
                    right_movement += diff[right_idx].sum()

                prev_landmarks = landmarks

            # Annotate frame number
            cv2.putText(frame, f"Frame: {frame_idx}/{input_frame_count}",
                        (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

            writer.write(frame)
            written += 1

    finally:
        pose.close()
        writer.release()
        cap.release()

    # Finalize metrics
    metrics["frames_processed"] = written
    if total_points > 0:
        metrics["avg_movement_intensity"] = round(movement_accumulator / total_points, 5)
        metrics["dominant_limb"] = "left" if left_movement > right_movement else "right"

    if return_metrics:
        return written, out_fps, metrics
    return written, out_fps
