"""
Next Level Fitness - Standalone Pose Detection Test
This script allows you to test the open-source detection engine directly.
"""

import cv2
import time
from src.pose_detector import PoseDetector

def run_test():
    # Initialize the detector
    # Note: This will automatically use SystemOptimizer to profile your hardware
    detector = PoseDetector()
    
    # Initialize Camera
    cap = cv2.VideoCapture(0)
    
    print("--- Pose Engine Test Started ---")
    print("Press 'q' to quit")
    print("Current Exercise: Push-up (Hardcoded for test)")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Flip the frame for a mirror effect
        frame = cv2.flip(frame, 1)

        # Process the frame
        # Returns: annotated_image, is_rep_complete, feedback_text, current_count
        image, rep_complete, feedback, count = detector.process_frame(frame, "push-up")

        # Overlay simple UI for testing
        cv2.putText(image, f"Reps: {count}", (10, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 212, 255), 2)
        cv2.putText(image, f"Feedback: {feedback}", (10, 100), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        # Show the result
        cv2.imshow('NextLevel Pose Engine - Standalone Test', image)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    detector.release()

if __name__ == "__main__":
    run_test()
