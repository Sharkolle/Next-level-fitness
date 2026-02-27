# 🧠 Pose Detection Technical Documentation

## Overview
Next Level Fitness utilizes **Google MediaPipe Pose** for real-time body tracking. Our engine translates raw visual landmarks into meaningful physical data.

## 📐 How we count reps
We use a **State Machine** combined with **Angular Trigonometry**.

### 1. Vector Calculation
To determine the angle of a joint (e.g., the elbow), we calculate the angle between three points:
* $A = (x_1, y_1)$ [Shoulder]
* $B = (x_2, y_2)$ [Elbow]
* $C = (x_3, y_3)$ [Wrist]

We calculate the angle $\theta$ using:
$$\theta = \arccos\left(\frac{\vec{BA} \cdot \vec{BC}}{|\vec{BA}| |\vec{BC}|}\right)$$

### 2. State Logic
* **Stage NONE:** Waiting for the user to enter the frame.
* **Stage DOWN:** Triggered when the angle $\theta$ drops below a specific threshold (e.g., $90^\circ$ for a push-up).
* **Stage UP:** Triggered when the user returns to the starting position (e.g., $160^\circ$). A rep is only counted when the state cycles from `UP` -> `DOWN` -> `UP`.

## ⚡ Hardware-Aware Performance
The engine uses `SystemOptimizer` to choose between three modes:
1.  **High-End:** Model Complexity 2 (Heavy), 1080p capture, 60fps.
2.  **Standard:** Model Complexity 1 (Full), 720p capture, 30fps.
3.  **Performance:** Model Complexity 0 (Lite), 480p capture, frame-skipping enabled.
