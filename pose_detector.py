import cv2
import mediapipe as mp
import numpy as np
import time
from typing import Optional, Tuple, Dict

from src.system_utils import SystemOptimizer


class PoseDetector:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils

        # DETECT HARDWARE AND GET OPTIMAL SETTINGS
        optimizer = SystemOptimizer()
        settings = optimizer.get_optimal_settings()

        print(f"🎯 Pose Detection Mode: {settings['description']}")

        # Initialize MediaPipe with optimal settings
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=settings['model_complexity'],
            enable_segmentation=False,
            min_detection_confidence=settings['min_detection_confidence'],
            min_tracking_confidence=settings['min_tracking_confidence'],
            smooth_landmarks=settings['smooth_landmarks'],
        )

        # Store settings for camera optimization
        self.camera_settings = {
            'width': settings['camera_width'],
            'height': settings['camera_height'],
            'fps': settings['camera_fps'],
        }

        self.frame_skip = settings['process_every_n_frames']

        self.current_exercise = None
        self.rep_count = 0
        self.stage = None
        self.form_feedback = ""

        # Plank-specific attributes
        self.plank_start_time = None
        self.plank_duration = 0
        self.plank_hold_active = False

        print(f"✅ Pose detector initialized")
        print(f"   └─ Model Complexity: {settings['model_complexity']}")
        print(f"   └─ Camera: {settings['camera_width']}x{settings['camera_height']}@{settings['camera_fps']}fps")
        print(f"   └─ Frame Processing: Every {settings['process_every_n_frames']} frames")

    def get_interpolation_method(self):
        """Get OpenCV interpolation method based on quality preset"""
        methods = {
            "LANCZOS": cv2.INTER_LANCZOS4,  # Best quality
            "CUBIC": cv2.INTER_CUBIC,  # Good quality
            "LINEAR": cv2.INTER_LINEAR,  # Balanced
            "AREA": cv2.INTER_AREA,  # Good for downscaling
            "NEAREST": cv2.INTER_NEAREST  # Fastest
        }
        return methods.get(self.interpolation, cv2.INTER_LINEAR)

    def calculate_angle(self, a, b, c):
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)

        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)

        if angle > 180.0:
            angle = 360 - angle

        return angle

    def detect_pushup(self, landmarks) -> Tuple[bool, str]:
        # Get all necessary landmarks
        left_shoulder = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                         landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        right_shoulder = [landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                          landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
        left_elbow = [landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                      landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
        right_elbow = [landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                       landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
        left_wrist = [landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                      landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].y]
        right_wrist = [landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                       landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
        left_hip = [landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x,
                    landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y]
        right_hip = [landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                     landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].y]
        left_ankle = [landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                      landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
        right_ankle = [landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,
                       landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]

        # Calculate angles
        left_arm_angle = self.calculate_angle(left_shoulder, left_elbow, left_wrist)
        right_arm_angle = self.calculate_angle(right_shoulder, right_elbow, right_wrist)
        avg_arm_angle = (left_arm_angle + right_arm_angle) / 2

        # NEW: Calculate body horizontal alignment (shoulder-hip-ankle)
        body_angle = self.calculate_angle(left_shoulder, left_hip, left_ankle)

        # NEW: Check if body is properly horizontal (plank position)
        is_horizontal = 160 < body_angle < 200  # The Body should be straight
        shoulders_hips_aligned = abs(left_shoulder[1] - left_hip[1]) < 0.15  # Shoulders and hips at the same height

        # NEW: Check if wrists are below shoulders (proper push-up position)
        wrists_below_shoulders = (left_wrist[1] > left_shoulder[1] and
                                  right_wrist[1] > right_shoulder[1])

        is_plank_position = is_horizontal and shoulders_hips_aligned and wrists_below_shoulders

        feedback = "GET IN PLANK POSITION"
        rep_complete = False

        if not is_plank_position:
            return False, "Get in proper plank position - body straight, hands below shoulders"

        # Only count reps if in proper plank position
        if avg_arm_angle > 160:
            if self.stage == "down":
                self.rep_count += 1
                rep_complete = True
            self.stage = "up"
            feedback = "START PUSH UP"
        elif avg_arm_angle < 90:
            self.stage = "down"
            if avg_arm_angle < 70:
                feedback = "GO LOWER - CHEST TO GROUND"
            else:
                feedback = "GOOD DEPTH"

        # Check arm symmetry
        arm_symmetry = abs(left_arm_angle - right_arm_angle)
        if arm_symmetry > 20:
            feedback = "KEEP ARMS EVEN"

        return rep_complete, feedback

    def detect_squat(self, landmarks) -> Tuple[bool, str]:
        left_hip = [landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x,
                    landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y]
        right_hip = [landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                     landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].y]
        left_knee = [landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                     landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].y]
        right_knee = [landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE.value].x,
                      landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
        left_ankle = [landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                      landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
        right_ankle = [landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,
                       landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]

        # Calculate angles for BOTH legs
        left_angle = self.calculate_angle(left_hip, left_knee, left_ankle)
        right_angle = self.calculate_angle(right_hip, right_knee, right_ankle)

        # NEW: Use average of both legs and ensure they move together
        avg_angle = (left_angle + right_angle) / 2
        leg_symmetry = abs(left_angle - right_angle)

        feedback = "GOOD FORM"
        rep_complete = False

        # Check if legs are moving symmetrically
        if leg_symmetry > 30:
            feedback = "KEEP LEGS EVEN - BOTH KNEES SHOULD BEND TOGETHER"
            return False, feedback

        if avg_angle > 160:
            if self.stage == "down":
                self.rep_count += 1
                rep_complete = True
            self.stage = "up"
            feedback = "YOU ARE STANDING, SQUAD DOWN⬇️"
        elif avg_angle < 100:
            self.stage = "down"
            if avg_angle < 80:
                feedback = "PERFECT DEPTH🔥! NOW GET BACK UP "
            else:
                feedback = "GOOD SQUAT"

        return rep_complete, feedback

    def detect_jumping_jack(self, landmarks) -> Tuple[bool, str]:
        """Fixed jumping jack detection with debug logging"""
        left_shoulder = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                         landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        right_shoulder = [landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                          landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
        left_wrist = [landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                      landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].y]
        right_wrist = [landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                       landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
        left_ankle = [landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                      landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
        right_ankle = [landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,
                       landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]

        # Calculate position indicators
        left_arm_raised = left_wrist[1] < left_shoulder[1]
        right_arm_raised = right_wrist[1] < right_shoulder[1]
        arms_raised = left_arm_raised and right_arm_raised

        shoulder_width = abs(left_shoulder[0] - right_shoulder[0])
        leg_spread = abs(left_ankle[0] - right_ankle[0])
        legs_spread = leg_spread > shoulder_width * 1.5

        arm_spread = abs(left_wrist[0] - right_wrist[0])
        arms_spread = arm_spread > shoulder_width * 1.8

        # Check neutral position
        is_neutral = not arms_raised and not legs_spread

        feedback = "START IN NEUTRAL POSITION"
        rep_complete = False

        # Initialize state machine
        if self.stage is None:
            self.stage = "init"
            return False, "Get ready - arms down, legs together"

        # State machine logic
        if self.stage == "init":
            if is_neutral:
                self.stage = "together"
                feedback = "READY - JUMP AND SPREAD!"
            else:
                feedback = "START WITH ARMS DOWN & LEGS TOGETHER"

        elif self.stage == "together":
            if arms_raised and arms_spread and legs_spread:
                self.stage = "apart"
                feedback = "GOOD SPREAD! NOW RETURN ✨"
            elif is_neutral:
                feedback = "JUMP! SPREAD ARMS & LEGS WIDER"
            else:
                feedback = "SPREAD ARMS & LEGS WIDER"

        elif self.stage == "apart":
            if is_neutral:
                # COUNT THE REP - Full cycle completed
                self.rep_count += 1
                rep_complete = True
                self.stage = "together"  # Reset for next rep
                feedback = "REP COMPLETE! 🔥"
            elif not arms_raised:
                feedback = "BRING LEGS TOGETHER"
            elif not legs_spread:
                feedback = "BRING ARMS DOWN"
            else:
                feedback = "RETURN TO START POSITION"

        return rep_complete, feedback

    def detect_situp(self, landmarks) -> Tuple[bool, str]:
        left_shoulder = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                         landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        right_shoulder = [landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                          landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
        left_hip = [landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x,
                    landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y]
        right_hip = [landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                     landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].y]
        left_knee = [landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                     landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].y]
        right_knee = [landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE.value].x,
                      landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
        left_ankle = [landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                      landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
        right_ankle = [landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,
                       landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]

        # Calculate leg angles to ensure proper sit-up position
        left_leg_angle = self.calculate_angle(left_hip, left_knee, left_ankle)
        right_leg_angle = self.calculate_angle(right_hip, right_knee, right_ankle)
        avg_leg_angle = (left_leg_angle + right_leg_angle) / 2

        # Calculate torso angle
        torso_angle = self.calculate_angle(left_shoulder, left_hip, left_knee)

        feedback = "GET IN SIT-UP POSITION"
        rep_complete = False

        # FIXED: Adjust pyramid position to <95° for better user experience
        legs_bent = avg_leg_angle < 95  # CHANGED: More user-friendly pyramid detection

        if not legs_bent:
            return False, "Bend knees to pyramid position 🔺 (knees at <95°)"

        # Sit-up state machine - only works with proper leg position
        if torso_angle < 60:  # Sitting up position
            if self.stage == "down":
                self.rep_count += 1
                rep_complete = True
            self.stage = "up"
            feedback = "SIT UP COMPLETE! 💪"
        elif torso_angle > 100:  # Lying down position
            self.stage = "down"
            if torso_angle > 140:
                feedback = "FULL RANGE - EXCELLENT! 🔥"
            else:
                feedback = "GOOD RANGE OF MOTION"

        return rep_complete, feedback

    def detect_lunge(self, landmarks) -> Tuple[bool, str]:
        """Enhanced lunge detection with proper stance validation"""
        left_hip = [landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x,
                    landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y]
        right_hip = [landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                     landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].y]
        left_knee = [landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                     landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].y]
        right_knee = [landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE.value].x,
                      landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
        left_ankle = [landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                      landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
        right_ankle = [landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,
                       landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]
        left_shoulder = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                         landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        right_shoulder = [landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                          landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]

        # Calculate knee angles for both legs
        left_knee_angle = self.calculate_angle(left_hip, left_knee, left_ankle)
        right_knee_angle = self.calculate_angle(right_hip, right_knee, right_ankle)

        # Check for proper lunge stance (legs split front/back)
        # Calculate horizontal distance between ankles
        ankle_distance = abs(left_ankle[0] - right_ankle[0])

        # Calculate shoulder width as reference
        shoulder_width = abs(left_shoulder[0] - right_shoulder[0])

        # CRITICAL: Legs must be split apart (front/back stance)
        # In a lunge, ankles should be wider apart than shoulders
        is_split_stance = ankle_distance > shoulder_width * 1.5

        # Check if one leg is in front of the other
        # (not just standing with knees bent)
        front_leg_forward = abs(left_ankle[0] - right_ankle[0]) > shoulder_width * 1.2

        feedback = "Step into a lunge - one leg forward, one back"
        rep_complete = False

        # Only count reps if in proper split stance
        if not is_split_stance or not front_leg_forward:
            return False, "Get into lunge position - step one leg forward 🦿"

        # Now check knee bending (only if in proper stance)
        both_knees_bent = left_knee_angle < 120 and right_knee_angle < 120
        both_knees_straight = left_knee_angle > 160 and right_knee_angle > 160

        # State machine (only works with proper stance)
        if self.stage is None:
            self.stage = "standing"
            feedback = "Good stance! Now lower into lunge"

        if self.stage == "standing" and both_knees_bent:
            # Entered lunge position
            self.stage = "lunge"
            feedback = "Good lunge! Hold it for a moment"

        elif self.stage == "lunge" and both_knees_straight:
            # Returned to standing - COUNT THE REP
            self.rep_count += 1
            rep_complete = True
            self.stage = "standing"
            feedback = "REP COMPLETE! 💪 Great work!"

        elif self.stage == "lunge" and not both_knees_bent:
            feedback = "Hold the lunge position"

        elif self.stage == "standing" and not both_knees_straight:
            feedback = "Stand up fully between reps"

        # Additional form guidance
        if both_knees_bent and is_split_stance:
            if left_knee_angle < 90 or right_knee_angle < 90:
                feedback = "Perfect depth! 🔥"
            else:
                feedback = "Good! Lower a bit more for full depth"

        return rep_complete, feedback

    # plank detection
    def detect_plank(self, landmarks) -> Tuple[bool, str]:
        """Detect plank exercise with 20-second rest timer"""
        left_shoulder = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                         landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        right_shoulder = [landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                          landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
        left_elbow = [landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                      landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
        right_elbow = [landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                       landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
        left_wrist = [landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                      landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].y]
        right_wrist = [landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                       landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
        left_hip = [landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x,
                    landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y]
        right_hip = [landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                     landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].y]
        left_ankle = [landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                      landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
        right_ankle = [landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,
                       landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]

        # Calculate body alignment angles
        body_angle = self.calculate_angle(left_shoulder, left_hip, left_ankle)

        # Calculate arm angles for L-shape detection
        left_arm_angle = self.calculate_angle(left_shoulder, left_elbow, left_wrist)
        right_arm_angle = self.calculate_angle(right_shoulder, right_elbow, right_wrist)
        avg_arm_angle = (left_arm_angle + right_arm_angle) / 2

        feedback = "GET IN PLANK POSITION"
        rep_complete = False

        # Comprehensive plank position check
        is_body_straight = 160 < body_angle < 200  # Body straight
        is_body_horizontal = abs(left_shoulder[1] - left_hip[1]) < 0.15  # Shoulders/hips aligned
        is_facing_down = left_shoulder[1] < left_ankle[1]  # Shoulders above ankles
        has_proper_arms = 80 < avg_arm_angle < 100  # Arms at ~90 degrees (L-shape)
        wrists_below_shoulders = (left_wrist[1] > left_shoulder[1] and
                                  right_wrist[1] > right_shoulder[1])

        is_plank_position = (is_body_straight and is_body_horizontal and
                             is_facing_down and has_proper_arms and wrists_below_shoulders)

        current_time = time.time()

        if is_plank_position:
            # USER IS IN PLANK POSITION
            if not self.plank_hold_active:
                # Just entered plank position - check if we were paused
                if hasattr(self, 'plank_pause_time'):
                    pause_duration = current_time - self.plank_pause_time

                    if pause_duration <= 20:  # Within 20-second rest limit
                        # Resume the timer by adjusting start time
                        self.plank_start_time += pause_duration
                        feedback = "WELCOME BACK! PLANK RESUMED 💪"
                        # Clear the pause time
                        delattr(self, 'plank_pause_time')
                    else:
                        # Rest limit exceeded - reset plank completely
                        self.plank_start_time = current_time
                        self.plank_duration = 0
                        self.rep_count = 0
                        feedback = "REST TIME EXCEEDED - PLANK RESET! 🔄"
                        # Clear the pause time
                        delattr(self, 'plank_pause_time')
                else:
                    # Starting fresh plank (no previous pause)
                    if self.plank_start_time is None:
                        self.plank_start_time = current_time
                        self.plank_duration = 0
                    feedback = "PLANK STARTED! HOLD IT! 💪"

                self.plank_hold_active = True

            # Calculate current hold duration
            self.plank_duration = current_time - self.plank_start_time
            self.rep_count = int(self.plank_duration)

            # Time-based feedback
            if self.plank_duration < 10:
                feedback = f"PLANK: {int(self.plank_duration)}s - KEEP GOING!"
            elif self.plank_duration < 30:
                feedback = f"PLANK: {int(self.plank_duration)}s - GREAT HOLD!"
            elif self.plank_duration < 60:
                feedback = f"PLANK: {int(self.plank_duration)}s - AMAZING ENDURANCE! 🔥"
            else:
                feedback = f"PLANK: {int(self.plank_duration)}s - LEGENDARY! ⚡"

        else:
            # USER IS NOT IN PLANK POSITION
            if self.plank_hold_active:
                # Just left plank position - start rest timer
                self.plank_hold_active = False
                self.plank_pause_time = current_time
                feedback = "PLANK PAUSED - GET BACK IN 20s! ⏰"
            else:
                # Already paused - show countdown
                if hasattr(self, 'plank_pause_time'):
                    rest_time = current_time - self.plank_pause_time
                    time_remaining = 20 - rest_time

                    if time_remaining > 0:
                        feedback = f"RETURN TO PLANK IN {int(time_remaining)}s! ⏳"
                    else:
                        # Rest time exceeded - reset everything
                        self.plank_start_time = None
                        self.plank_duration = 0
                        self.rep_count = 0
                        feedback = "REST TIME EXCEEDED - PLANK RESET! 🔄"
                        # Clear pause time
                        delattr(self, 'plank_pause_time')
                else:
                    # First time getting into position or specific form feedback
                    if not is_body_straight:
                        feedback = "KEEP BODY STRAIGHT - DON'T SAG OR ARCH"
                    elif not is_body_horizontal:
                        feedback = "ALIGN SHOULDERS WITH HIPS"
                    elif not has_proper_arms:
                        feedback = "FORM 90-DEGREE ANGLES WITH ARMS"
                    elif not is_facing_down:
                        feedback = "FACE DOWN - HEAD IN NEUTRAL POSITION"
                    else:
                        feedback = "GET IN PLANK POSITION - ARMS BENT, BODY STRAIGHT"

        return rep_complete, feedback

    def detect_arm_circles(self, landmarks) -> Tuple[bool, str]:
        """
        REFINED: Arm circles detection - much more lenient and reliable
        Counts based on vertical wrist movement (up → down → up = 1 rep)
        """
        # Get key landmarks
        left_shoulder = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                         landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        right_shoulder = [landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                          landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
        left_elbow = [landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                      landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
        right_elbow = [landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                       landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
        left_wrist = [landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                      landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].y]
        right_wrist = [landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                       landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].y]

        # Calculate arm angles
        left_arm_angle = self.calculate_angle(left_shoulder, left_elbow, left_wrist)
        right_arm_angle = self.calculate_angle(right_shoulder, right_elbow, right_wrist)

        # Check if arms are reasonably extended (more lenient)
        arms_extended = left_arm_angle > 140 and right_arm_angle > 140

        feedback = "EXTEND YOUR ARMS OUT"
        rep_complete = False

        # Initialize tracking variables
        if not hasattr(self, 'arm_circle_stage'):
            self.arm_circle_stage = None
            print("🔄 Arm circles tracking initialized")

        if not arms_extended:
            self.arm_circle_stage = None
            return False, "EXTEND ARMS STRAIGHT OUT (like airplane wings)"

        # ✅ SIMPLIFIED APPROACH: Track vertical position of wrists
        # Use average of both wrists for more reliable detection
        shoulder_height = (left_shoulder[1] + right_shoulder[1]) / 2
        avg_wrist_height = (left_wrist[1] + right_wrist[1]) / 2

        # Determine position: above or below shoulder
        wrists_above_shoulder = avg_wrist_height < (shoulder_height - 0.05)
        wrists_below_shoulder = avg_wrist_height > (shoulder_height + 0.05)
        wrists_at_shoulder = not wrists_above_shoulder and not wrists_below_shoulder

        # Simple state machine: up → down → up = 1 circle
        if self.arm_circle_stage is None:
            # Initialize based on current position
            if wrists_at_shoulder:
                self.arm_circle_stage = "middle"
                feedback = "GOOD! START ROTATING - MAKE BIG CIRCLES!"
            elif wrists_above_shoulder:
                self.arm_circle_stage = "up"
                feedback = "START FROM HERE - ROTATE ARMS!"
            elif wrists_below_shoulder:
                self.arm_circle_stage = "down"
                feedback = "START FROM HERE - ROTATE ARMS!"

        elif self.arm_circle_stage == "middle":
            if wrists_above_shoulder:
                self.arm_circle_stage = "up"
                feedback = "ARMS UP! KEEP GOING!"
            elif wrists_below_shoulder:
                self.arm_circle_stage = "down"
                feedback = "ARMS DOWN! KEEP GOING!"

        elif self.arm_circle_stage == "up":
            if wrists_below_shoulder:
                # Went from up to down - half circle
                self.arm_circle_stage = "down"
                feedback = "HALFWAY! KEEP ROTATING!"
            elif wrists_at_shoulder:
                self.arm_circle_stage = "middle"

        elif self.arm_circle_stage == "down":
            if wrists_above_shoulder:
                # Went from down to up
                self.rep_count += 1
                rep_complete = True
                self.arm_circle_stage = "up"
                feedback = f"CIRCLE {self.rep_count} COMPLETE! 🔥"
                print(f"✅ Arm circle rep counted: {self.rep_count}")
            elif wrists_at_shoulder:
                self.arm_circle_stage = "middle"

        return rep_complete, feedback

    def detect_high_knees(self, landmarks) -> Tuple[bool, str]:
        """
        High knees: SIDEWAYS PROFILE detection.

        User stands SIDEWAYS to the camera (either side is fine).
        We pick whichever hip/knee/ankle pair is more visible (higher landmark
        visibility score) and track it as the "near" leg.

        SIDE-PROFILE THEORY:
        - From the side, a raised knee shows as the thigh rotating forward/up.
        - We measure the Hip → Knee → Ankle angle on the near (more visible) leg.
          * Leg DOWN  : angle > 150°  (leg hanging straight down)
          * Leg UP    : angle < 90°   (thigh lifted, shin tucked)
        - One full DOWN → UP → DOWN cycle on EITHER leg = 1 rep.
        - We also check that the knee Y-coordinate is above the hip Y-coordinate
          as a secondary guard against counting squats.
        """
        left_hip   = [landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x,
                      landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y]
        right_hip  = [landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                      landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].y]
        left_knee  = [landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                      landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].y]
        right_knee = [landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE.value].x,
                      landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
        left_ankle = [landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                      landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
        right_ankle= [landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,
                      landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]

        # Pick the more-visible hip as the "tracking" leg
        left_hip_vis  = landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].visibility
        right_hip_vis = landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].visibility

        if left_hip_vis >= right_hip_vis:
            hip, knee, ankle = left_hip, left_knee, left_ankle
        else:
            hip, knee, ankle = right_hip, right_knee, right_ankle

        feedback = "STAND SIDEWAYS - DRIVE KNEES UP!"
        rep_complete = False

        # Hip-Knee-Ankle angle on the near (more visible) leg
        knee_angle = self.calculate_angle(hip, knee, ankle)

        # Knee physically above hip? (Y decreases going up in image coords)
        knee_above_hip = knee[1] < hip[1]

        # Define states using angle thresholds
        leg_is_up   = (knee_angle < 90) and knee_above_hip   # Thigh driven up
        leg_is_down = knee_angle > 150                         # Leg hanging down

        # === STATE MACHINE ===
        if self.stage is None:
            self.stage = "down"
            return False, "STAND SIDEWAYS - KNEES UP! 🔥"

        if self.stage == "down":
            if leg_is_up:
                self.stage = "up"
                feedback = "KNEE UP! 💪 NOW SWITCH!"
            else:
                feedback = "DRIVE THAT KNEE HIGHER! ⬆️"

        elif self.stage == "up":
            if leg_is_down:
                # Full cycle complete — count the rep
                self.rep_count += 1
                rep_complete = True
                self.stage = "down"
                feedback = f"REP {self.rep_count}! 🔥 KEEP RUNNING!"
            elif not leg_is_up:
                # Mid-transition, just keep going
                feedback = "SWITCH LEGS FAST!"

        return rep_complete, feedback

    # ------------------
    # 2. TRICEP DIPS
    # ------------------
    def detect_tricep_dip(self, landmarks) -> Tuple[bool, str]:
        """
        Tricep dips: Arms behind back, lower and raise body
        """
        left_shoulder = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                         landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        right_shoulder = [landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                          landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
        left_elbow = [landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                      landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
        right_elbow = [landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                       landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
        left_wrist = [landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                      landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].y]
        right_wrist = [landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                       landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
        left_hip = [landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x,
                    landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y]

        # Calculate arm angles
        left_arm_angle = self.calculate_angle(left_shoulder, left_elbow, left_wrist)
        right_arm_angle = self.calculate_angle(right_shoulder, right_elbow, right_wrist)
        avg_arm_angle = (left_arm_angle + right_arm_angle) / 2

        # Check if elbows are behind body (wrists behind hips)
        avg_wrist_x = (left_wrist[0] + right_wrist[0]) / 2
        avg_hip_x = left_hip[0]

        elbows_behind = avg_wrist_x > avg_hip_x + 0.05

        feedback = "SIT ON EDGE, HANDS BEHIND"
        rep_complete = False

        if not elbows_behind:
            self.stage = None
            return False, "Place hands behind you on chair/bench"

        # Arms straight = up position
        # Arms bent = down position
        if avg_arm_angle > 160:
            if self.stage == "down":
                self.rep_count += 1
                rep_complete = True
            self.stage = "up"
            feedback = "LOWER DOWN"

        elif avg_arm_angle < 100:
            self.stage = "down"
            if avg_arm_angle < 80:
                feedback = "PERFECT DEPTH! Push up!"
            else:
                feedback = "GOOD! Now push up!"

        return rep_complete, feedback

    # ------------------
    # 3. HIGH KNEES (Already exists, but let's refine it)
    # ------------------
    # Use the existing detect_high_knees() - it's already good!

    # ------------------
    # 4. BURPEES
    # ------------------
    def detect_burpee(self, landmarks) -> Tuple[bool, str]:
        """
        Burpee detection: Stand → Plank → Jump = 1 rep
        """
        left_shoulder = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                         landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        left_hip = [landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x,
                    landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y]
        left_knee = [landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                     landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].y]
        left_ankle = [landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                      landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].y]

        # Determine body position
        body_angle = self.calculate_angle(left_shoulder, left_hip, left_ankle)

        is_standing = body_angle > 160  # Upright
        is_plank = 160 < body_angle < 200 and left_shoulder[1] < left_ankle[1]  # Horizontal

        feedback = "START STANDING"
        rep_complete = False

        if self.stage is None:
            self.stage = "standing"

        if self.stage == "standing":
            if is_plank:
                self.stage = "plank"
                feedback = "IN PLANK! Now jump up!"
            else:
                feedback = "Drop to plank position!"

        elif self.stage == "plank":
            if is_standing:
                self.rep_count += 1
                rep_complete = True
                self.stage = "standing"
                feedback = f"BURPEE {self.rep_count}! 🔥"
            else:
                feedback = "Jump back up to standing!"

        return rep_complete, feedback

    def detect_leg_raise(self, landmarks) -> Tuple[bool, str]:
        """
        Leg raises: Lying on back, raise straight legs to 90° (L-shape), then lower slowly.

        THEORY IMPLEMENTATION:
        - Leg Straightness Angle (hip→knee→ankle): Must stay > 150° (no knee tucks)
        - Hip Flexion Angle (shoulder→hip→ankle):
          * DOWN: > 150° (legs near floor)
          * UP: < 105° (L-shape at 90°)
        - Form feedback: Block cheating (knee tucks, floor resting)
        """
        # Extract landmarks (average both sides for robustness)
        left_shoulder = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                         landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        right_shoulder = [landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                          landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
        left_hip = [landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x,
                    landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y]
        right_hip = [landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                     landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].y]
        left_knee = [landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                     landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].y]
        right_knee = [landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE.value].x,
                      landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
        left_ankle = [landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                      landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
        right_ankle = [landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,
                       landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]

        # Average both sides for stable tracking
        avg_shoulder = [(left_shoulder[0] + right_shoulder[0]) / 2,
                        (left_shoulder[1] + right_shoulder[1]) / 2]
        avg_hip = [(left_hip[0] + right_hip[0]) / 2,
                   (left_hip[1] + right_hip[1]) / 2]
        avg_ankle = [(left_ankle[0] + right_ankle[0]) / 2,
                     (left_ankle[1] + right_ankle[1]) / 2]

        # === ANGLE 1: Leg Straightness (Hip → Knee → Ankle) ===
        # Must stay > 150° to prevent knee tuck cheating
        left_leg_straightness = self.calculate_angle(left_hip, left_knee, left_ankle)
        right_leg_straightness = self.calculate_angle(right_hip, right_knee, right_ankle)
        avg_leg_straightness = (left_leg_straightness + right_leg_straightness) / 2

        legs_straight = avg_leg_straightness > 150  # Allow micro-bend for hamstring tightness

        # === ANGLE 2: Hip Flexion (Shoulder → Hip → Ankle) ===
        # Tracks actual range of motion
        hip_flexion_angle = self.calculate_angle(avg_shoulder, avg_hip, avg_ankle)

        feedback = "LIE FLAT - LEGS STRAIGHT"
        rep_complete = False

        # === FORM CHECK 1: Are legs straight? ===
        if not legs_straight:
            self.stage = None
            return False, "STRAIGHTEN LEGS - NO KNEE TUCKS! 🚫"

        # === FORM CHECK 2: Basic lying down position ===
        # Check if shoulders and hips are roughly aligned (lying flat)
        is_lying = abs(avg_shoulder[1] - avg_hip[1]) < 0.35
        if not is_lying:
            self.stage = None
            return False, "LIE FLAT ON YOUR BACK"

        # === STATE MACHINE ===
        # Initialize stage
        if self.stage is None:
            if hip_flexion_angle > 150:
                self.stage = "down"
                feedback = "LEGS DOWN - READY TO RAISE!"
            else:
                self.stage = "unknown"
                feedback = "Lower legs to start position"

        # DOWN STATE: Legs near floor (hip flexion > 150°)
        if self.stage == "down":
            # FORM CHECK 3: Floor resting detection
            if hip_flexion_angle > 175:
                feedback = "DON'T REST - HOVER HEELS! 🔥"

            # Transition to UP when legs reach L-shape (< 105°)
            if hip_flexion_angle < 105:
                self.stage = "up"
                feedback = "PERFECT L-SHAPE! 🔥 NOW LOWER SLOWLY"
            else:
                feedback = "RAISE LEGS TO 90° (L-SHAPE)"

        # UP STATE: Legs at L-shape (hip flexion < 105°)
        elif self.stage == "up":
            # Rep completes when returning to down position (> 150°)
            if hip_flexion_angle > 150:
                self.rep_count += 1
                rep_complete = True
                self.stage = "down"
                feedback = f"REP {self.rep_count} COMPLETE! 💪 GREAT CONTROL!"
            else:
                feedback = "LOWER SLOWLY - CONTROL THE ECCENTRIC"

        # UNKNOWN STATE: Help user get into position
        elif self.stage == "unknown":
            if hip_flexion_angle > 150:
                self.stage = "down"
                feedback = "GOOD START - NOW RAISE LEGS!"
            else:
                feedback = "Lower legs to floor to begin"

        return rep_complete, feedback

    # ------------------
    # 6. WALL SIT
    # ------------------
    def detect_wall_sit(self, landmarks) -> Tuple[bool, str]:
        """
        Wall sit: Isometric hold with back against wall, thighs parallel
        """
        left_hip = [landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x,
                    landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y]
        left_knee = [landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                     landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].y]
        left_ankle = [landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                      landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
        left_shoulder = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                         landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]

        # Calculate leg angle
        leg_angle = self.calculate_angle(left_hip, left_knee, left_ankle)

        # Check if in sitting position (90 degree angle)
        is_sitting = 80 < leg_angle < 110

        # Check if back is vertical (against wall)
        is_upright = abs(left_shoulder[0] - left_hip[0]) < 0.1

        feedback = "GET INTO WALL SIT POSITION"
        rep_complete = False

        is_wall_sit = is_sitting and is_upright

        if not is_wall_sit:
            if not is_upright:
                feedback = "LEAN BACK AGAINST WALL"
            elif not is_sitting:
                if leg_angle > 110:
                    feedback = "SLIDE DOWN - KNEES AT 90°"
                else:
                    feedback = "LIFT UP SLIGHTLY - 90° ANGLE"

            # Reset timer if not in position
            if hasattr(self, 'wall_sit_start_time'):
                self.wall_sit_start_time = None
            return False, feedback

        # Track hold duration (like plank)
        current_time = time.time()

        if not hasattr(self, 'wall_sit_start_time') or self.wall_sit_start_time is None:
            self.wall_sit_start_time = current_time
            self.wall_sit_duration = 0

        self.wall_sit_duration = current_time - self.wall_sit_start_time
        self.rep_count = int(self.wall_sit_duration)

        if self.wall_sit_duration < 10:
            feedback = f"HOLD IT! {int(self.wall_sit_duration)}s"
        elif self.wall_sit_duration < 30:
            feedback = f"STRONG! {int(self.wall_sit_duration)}s 🔥"
        else:
            feedback = f"AMAZING! {int(self.wall_sit_duration)}s 💪"

        return rep_complete, feedback

    def process_frame(self, frame, exercise_type: str) -> Tuple[np.ndarray, bool, str, int]:
        try:
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = self.pose.process(image)
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            rep_complete = False
            feedback = ""

            if results.pose_landmarks:
                self.mp_drawing.draw_landmarks(
                    image,
                    results.pose_landmarks,
                    self.mp_pose.POSE_CONNECTIONS,
                    self.mp_drawing.DrawingSpec(color=(0, 212, 255), thickness=2, circle_radius=2),
                    self.mp_drawing.DrawingSpec(color=(0, 191, 255), thickness=2, circle_radius=2)
                )

                landmarks = results.pose_landmarks.landmark

                if exercise_type == "push-up":
                    rep_complete, feedback = self.detect_pushup(landmarks)
                elif exercise_type == "squat":
                    rep_complete, feedback = self.detect_squat(landmarks)
                elif exercise_type == "jumping-jack":
                    rep_complete, feedback = self.detect_jumping_jack(landmarks)
                elif exercise_type == "sit-up":
                    rep_complete, feedback = self.detect_situp(landmarks)
                elif exercise_type == "lunge":
                    rep_complete, feedback = self.detect_lunge(landmarks)
                elif exercise_type == "plank":
                    rep_complete, feedback = self.detect_plank(landmarks)
                elif exercise_type == "arm-circles":
                    rep_complete, feedback = self.detect_arm_circles(landmarks)
                elif exercise_type == "wall-sit":
                    rep_complete, feedback = self.detect_wall_sit(landmarks)
                elif exercise_type == "tricep-dip":
                    rep_complete, feedback = self.detect_tricep_dip(landmarks)
                elif exercise_type == "burpee":
                    rep_complete, feedback = self.detect_burpee(landmarks)
                elif exercise_type == "high-knees":
                    rep_complete, feedback = self.detect_high_knees(landmarks)
                elif exercise_type == "leg-raise":
                    rep_complete, feedback = self.detect_leg_raise(landmarks)

            return image, rep_complete, feedback, self.rep_count

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"❌ Pose detection error: {e}")
            print(f"📋 Full traceback:\n{error_details}")
            return frame, False, f"Error: {str(e)[:50]}", self.rep_count

    def reset(self):
        """Reset detector state for new workout session"""
        self.rep_count = 0
        self.stage = None  # Always start with None
        self.form_feedback = ""
        self.plank_start_time = None
        self.plank_duration = 0
        self.plank_hold_active = False

        # Clear any pause time on reset
        if hasattr(self, 'plank_pause_time'):
            delattr(self, 'plank_pause_time')

        # Initialize exercises properly based on type
        if hasattr(self, 'current_exercise'):
            if self.current_exercise == "jumping-jack":
                self.stage = "init"  # Start in init stage for jumping jacks
            elif self.current_exercise == "plank":
                self.stage = None  # Plank handles its own initialization
            else:
                self.stage = None  # All other exercises start fresh

    def release(self):
        self.pose.close()