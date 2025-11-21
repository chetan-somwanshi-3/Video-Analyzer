## 🩰 Dance Video Analyzer

### 🎯 Overview

**Dance Movement Analyzer** is a lightweight AI tool that analyzes dance videos using **MediaPipe Pose** and **OpenCV**.
It detects the **main dancer’s body keypoints**, overlays a **skeleton visualization**, and computes simple **movement metrics** like intensity and limb dominance.

The project includes:

* 🎥 Pose detection and skeleton overlay
* 📊 Movement metric analysis
* ⚙️ FastAPI backend for video uploads and processing
* 🧪 Unit tests for reliability
* 🐳 Docker-ready setup for cloud deployment

---

## Project Organization

```
├── LICENSE            <- Open-source license if one is chosen
├── Makefile           <- Makefile with convenience commands like `make data` or `make train`
├── README.md          <- The top-level README for developers using this project.
├── data
│   ├── external       <- Data from third party sources.
│   ├── interim        <- Intermediate data that has been transformed.
│   ├── processed      <- The final, canonical data sets for modeling.
│   └── raw            <- The original, immutable data dump.
│
├── docs               <- A default mkdocs project; see www.mkdocs.org for details
│
├── models             <- Trained and serialized models, model predictions, or model summaries
│
├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
│                         the creator's initials, and a short `-` delimited description, e.g.
│                         `1.0-jqp-initial-data-exploration`.
│
├── pyproject.toml     <- Project configuration file with package metadata for 
│                         src and configuration for tools like black
│
├── references         <- Data dictionaries, manuals, and all other explanatory materials.
│
├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
│   └── figures        <- Generated graphics and figures to be used in reporting
│
├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
│                         generated with `pip freeze > requirements.txt`
│
├── setup.cfg          <- Configuration file for flake8
│
└── src   <- Source code for use in this project.
    │
    ├── __init__.py             <- Makes src a Python module
    │
    ├── config.py               <- Store useful variables and configuration
    │
    ├── dataset.py              <- Scripts to download or generate data
    │
    ├── features.py             <- Code to create features for modeling
    │
    ├── modeling                
    │   ├── __init__.py 
    │   ├── predict.py          <- Code to run model inference with trained models          
    │   └── train.py            <- Code to train models
    │
    └── plots.py                <- Code to create visualizations
```
---

### ⚙️ Installation

#### 1. Clone the repository

```bash
git clone https://github.com/chetanns3/Dance-Video-Analyzer
cd Dance-Video-Analyzer
```

#### 2. Create and activate a Conda environment

```bash
conda create -n aiml-env python=3.11 -y
conda activate aiml-env
```

#### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 🚀 Running the App Locally

Start the FastAPI app:

```bash
uvicorn app.api:app --reload
```

The API will be available at:
👉 **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

#### Test the `/analyze` endpoint

Use **Postman** or **cURL** to upload a video:

```bash
curl -X POST "http://127.0.0.1:8000/analyze" \
  -F "file=@sample_dance.mp4" \
  -o processed_output.mp4
```

After processing, you’ll get:

* A **skeleton-overlayed video**
* Logged metrics like:

  * Total frames processed
  * Average movement intensity
  * Dominant limb (left/right)

---

### 🧪 Running Tests

```bash
pytest -v
```

This will:

* Create a small synthetic test video
* Run the processor
* Verify that output video and metrics are generated successfully

---

### 📊 Metrics Generated

| Metric                   | Description                                     |
| ------------------------ | ----------------------------------------------- |
| `frames_processed`       | Total frames analyzed                           |
| `frames_with_pose`       | Frames where pose was detected                  |
| `avg_movement_intensity` | Average per-joint displacement across frames    |
| `dominant_limb`          | Side (left/right) showing higher average motion |

---

### 🐳 Docker Usage

Build the image:

```bash
docker build -t dance-analyzer .
```

Run the container:

```bash
docker run -p 8000:8000 dance-analyzer
```

Access the API at
👉 `http://localhost:8000/analyze`

---

### ⚠️ Limitations

* Designed for **single-person dance videos** (MediaPipe Pose)
* May not handle multiple dancers simultaneously
* Accuracy depends on lighting, camera angle, and frame resolution

---

### 💡 Future Enhancements

* Integrate **multi-person detection** (YOLOv8-Pose or MMPose)
* Add **gesture classification** and rhythm analysis
* Real-time webcam-based dance tracking

---

