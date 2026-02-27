"""
System utilities for hardware detection and optimization
"""
import os
import platform
import subprocess
import sys
import os



def get_base_path() -> str:
    """Get base path - works in frozen and development"""
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    else:
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_gifs_path() -> str:
    """Get path to GIFs directory"""
    base = get_base_path()
    return os.path.join(base, "assets", "gifs")


class SystemOptimizer:
    """Detects hardware capabilities and optimizes settings"""

    def __init__(self):
        self.has_gpu = False
        self.gpu_name = None
        self.available_vram = 0
        self.cpu_cores = os.cpu_count() or 4
        self.detect_hardware()

    def detect_hardware(self):
        """Detect available hardware (GPU/VRAM)"""
        try:
            # Try to detect NVIDIA GPU
            if platform.system() == "Windows":
                self.detect_gpu_windows()
            elif platform.system() == "Linux":
                self.detect_gpu_linux()
            elif platform.system() == "Darwin":  # macOS
                self.detect_gpu_macos()

            print(f"\n{'=' * 50}")
            print(f"🖥️  HARDWARE DETECTION RESULTS")
            print(f"{'=' * 50}")
            print(f"✅ CPU Cores: {self.cpu_cores}")

            if self.has_gpu:
                print(f"✅ GPU Detected: {self.gpu_name}")
                print(f"✅ VRAM Available: {self.available_vram} MB")
                print(f"✅ Mode: GPU ACCELERATED 🚀")
            else:
                print(f"⚠️  No GPU detected")
                print(f"✅ Mode: CPU OPTIMIZED 💻")
            print(f"{'=' * 50}\n")

        except Exception as e:
            print(f"⚠️  Hardware detection error: {e}")
            self.has_gpu = False

    def detect_gpu_windows(self):
        """Detect GPU on Windows using nvidia-smi or wmic"""
        try:
            # Try nvidia-smi first (NVIDIA GPUs)
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=name,memory.free', '--format=csv,noheader'],
                capture_output=True,
                text=True,
                timeout=2
            )

            if result.returncode == 0 and result.stdout:
                gpu_info = result.stdout.strip().split(',')
                self.gpu_name = gpu_info[0].strip()
                self.available_vram = int(gpu_info[1].strip().split()[0])
                self.has_gpu = True
                return
        except:
            pass

        # Fallback: Try wmic (works for all GPUs on Windows)
        try:
            result = subprocess.run(
                ['wmic', 'path', 'win32_VideoController', 'get', 'name'],
                capture_output=True,
                text=True,
                timeout=2
            )

            if result.returncode == 0 and result.stdout:
                gpu_list = result.stdout.strip().split('\n')[1:]  # Skip header
                for gpu in gpu_list:
                    gpu = gpu.strip()
                    if gpu and 'Intel' not in gpu:  # Prefer dedicated GPU over integrated
                        self.gpu_name = gpu
                        self.has_gpu = True
                        self.available_vram = 2048  # Estimate (can't get exact VRAM from wmic)
                        return
        except:
            pass

    def detect_gpu_linux(self):
        """Detect GPU on Linux"""
        try:
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=name,memory.free', '--format=csv,noheader'],
                capture_output=True,
                text=True,
                timeout=2
            )

            if result.returncode == 0 and result.stdout:
                gpu_info = result.stdout.strip().split(',')
                self.gpu_name = gpu_info[0].strip()
                self.available_vram = int(gpu_info[1].strip().split()[0])
                self.has_gpu = True
        except:
            pass

    def detect_gpu_macos(self):
        """Detect GPU on macOS"""
        try:
            result = subprocess.run(
                ['system_profiler', 'SPDisplaysDataType'],
                capture_output=True,
                text=True,
                timeout=2
            )

            if result.returncode == 0 and 'Chipset Model' in result.stdout:
                # macOS has GPU, but MediaPipe CPU is often faster on Apple Silicon
                self.gpu_name = "Apple GPU"
                self.has_gpu = False  # Force CPU mode on macOS (better compatibility)
        except:
            pass

    def get_optimal_settings(self):
        """Get optimal MediaPipe settings based on hardware"""
        if self.has_gpu and self.available_vram >= 2048:
            # HIGH-END: GPU with 2GB+ VRAM
            return {
                "model_complexity": 2,
                "smooth_landmarks": True,
                "min_detection_confidence": 0.5,
                "min_tracking_confidence": 0.5,
                "camera_width": 640,
                "camera_height": 480,
                "camera_fps": 30,
                "process_every_n_frames": 1,  # Process every frame
                "description": "GPU Accelerated (High Quality)"
            }

        elif self.has_gpu and self.available_vram >= 1024:
            # MID-RANGE: GPU with 1GB+ VRAM
            return {
                "model_complexity": 1,
                "smooth_landmarks": True,
                "min_detection_confidence": 0.5,
                "min_tracking_confidence": 0.5,
                "camera_width": 640,
                "camera_height": 480,
                "camera_fps": 30,
                "process_every_n_frames": 2,  # Process every 2nd frame
                "description": "GPU Accelerated (Balanced)"
            }

        elif self.cpu_cores >= 8:
            # HIGH-END CPU: 8+ cores, no GPU
            return {
                "model_complexity": 1,
                "smooth_landmarks": True,
                "min_detection_confidence": 0.5,
                "min_tracking_confidence": 0.5,
                "camera_width": 640,
                "camera_height": 480,
                "camera_fps": 30,
                "process_every_n_frames": 2,  # Process every 2nd frame
                "description": "CPU Optimized (Multi-Core)"
            }

        elif self.cpu_cores >= 4:
            # MID-RANGE CPU: 4-7 cores, no GPU
            return {
                "model_complexity": 1,
                "smooth_landmarks": False,  # Disable smoothing
                "min_detection_confidence": 0.4,
                "min_tracking_confidence": 0.4,
                "camera_width": 480,
                "camera_height": 360,
                "camera_fps": 25,
                "process_every_n_frames": 3,  # Process every 3rd frame
                "description": "CPU Optimized (Balanced)"
            }

        else:
            # LOW-END: < 4 cores, no GPU
            return {
                "model_complexity": 0,  # Fastest, lowest quality
                "smooth_landmarks": False,
                "min_detection_confidence": 0.3,
                "min_tracking_confidence": 0.3,
                "camera_width": 320,
                "camera_height": 240,
                "camera_fps": 20,
                "process_every_n_frames": 4,  # Process every 4th frame
                "description": "CPU Optimized (Low-End Performance Mode)"
            }