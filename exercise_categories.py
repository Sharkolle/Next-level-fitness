"""
Exercise Categories System
Organizes exercises by category with level-based unlocking
"""

EXERCISE_CATEGORIES = {
    "💪 UPPER BODY": {
        "color": "#FF6B6B",
        "exercises": [
            {
                "id": "push-up",
                "display_name": "Push-ups",
                "required_level": 1,
                "description": "Classic upper body strength",
                "muscle_groups": ["Chest", "Triceps", "Shoulders"],
                "difficulty": "Medium",
                "camera_position": "SIDE VIEW",
                "how_to": [
                    "Start in a high plank — hands shoulder-width apart, body in a straight line from head to heels.",
                    "Lower your chest toward the floor by bending both elbows evenly.",
                    "Stop when your chest is about 2-3 cm from the floor (or as low as you can).",
                    "Push through your palms to straighten your arms back to the start.",
                    "Keep your core tight and hips level throughout — no sagging or piking."
                ],
                "tips": [
                    "Squeeze your glutes to keep your hips from dropping.",
                    "Elbows should flare about 45° from your body — not straight out.",
                    "Look slightly forward, not straight down, to keep your neck neutral.",
                    "If full push-ups are too hard, drop to your knees to build strength first."
                ]
            },
            {
                "id": "tricep-dip",
                "display_name": "Tricep Dips",
                "required_level": 8,
                "description": "Isolated tricep strength",
                "muscle_groups": ["Triceps", "Shoulders"],
                "difficulty": "Medium",
                "camera_position": "SIDE VIEW",
                "how_to": [
                    "Sit on the edge of a sturdy chair or bench, hands gripping the edge beside your hips.",
                    "Slide your hips off the seat and walk your feet forward until your arms are supporting your weight.",
                    "Lower your body by bending your elbows straight back — not out to the sides.",
                    "Stop when your upper arms are roughly parallel to the floor (90° elbow bend).",
                    "Push through your palms to straighten your arms and return to start."
                ],
                "tips": [
                    "Keep your back close to the chair — don't let your hips drift far forward.",
                    "The further your feet are from the chair, the harder the exercise.",
                    "Keep your shoulders down and away from your ears throughout.",
                    "Control the descent — don't just drop and bounce back up."
                ]
            },
        ]
    },

    "🔥 CORE / ABS": {
        "color": "#FFD700",
        "exercises": [
            {
                "id": "sit-up",
                "display_name": "Sit-ups",
                "required_level": 1,
                "description": "Core strength fundamental",
                "muscle_groups": ["Abs", "Hip Flexors"],
                "difficulty": "Medium",
                "camera_position": "SIDE VIEW",
                "how_to": [
                    "Lie on your back with knees bent at roughly 90° and feet flat on the floor.",
                    "Cross your arms over your chest or place your hands lightly behind your head.",
                    "Engage your core and curl your torso up toward your knees.",
                    "Rise until your elbows (or chest) touch or pass your knees.",
                    "Slowly lower back down until your shoulder blades touch the floor."
                ],
                "tips": [
                    "Don't pull on your neck — let your abs do the work.",
                    "Exhale as you rise, inhale as you lower.",
                    "Keep your feet planted; anchor them under a sofa if needed.",
                    "Full range of motion = full shoulder blade contact on the way down."
                ]
            },
            {
                "id": "plank",
                "display_name": "Plank",
                "required_level": 1,
                "description": "Total core stability",
                "muscle_groups": ["Core", "Shoulders", "Glutes"],
                "difficulty": "Hard",
                "camera_position": "SIDE VIEW",
                "how_to": [
                    "Place your forearms on the floor, elbows directly below your shoulders.",
                    "Extend your legs behind you, balancing on your toes.",
                    "Create a straight line from your head through your heels — no sagging or piking.",
                    "Brace your core as if you're about to take a punch to the stomach.",
                    "Hold the position and breathe steadily. The AI tracks your hold time."
                ],
                "tips": [
                    "Squeeze your glutes hard — it locks your hips in place.",
                    "Push your forearms into the floor to engage your lats and keep shoulders stable.",
                    "Look at a spot on the floor slightly in front of your hands to keep your neck neutral.",
                    "If your hips drop, reset — a 20-second perfect plank beats a 60-second sloppy one."
                ]
            },
            {
                "id": "leg-raise",
                "display_name": "Leg Raises",
                "required_level": 5,
                "description": "Lower ab strength builder",
                "muscle_groups": ["Lower Abs", "Hip Flexors"],
                "difficulty": "Medium",
                "camera_position": "SIDE VIEW",
                "how_to": [
                    "Lie flat on your back, legs straight, hands under your glutes for lower back support.",
                    "Keep your legs together and raise them slowly until they are vertical (L-shape at 90°).",
                    "Pause briefly at the top, then lower your legs slowly back toward the floor.",
                    "Stop just above the floor — don't let your heels touch — and repeat.",
                    "Keep your lower back pressed into the floor throughout the movement."
                ],
                "tips": [
                    "The slower the descent, the harder your lower abs work.",
                    "If your lower back arches, you're going too low — hover heels higher.",
                    "Keep your legs fully straight — bending at the knee is cheating.",
                    "Breathe out as you raise, breathe in as you lower."
                ]
            },
        ]
    },

    "🦵 LOWER BODY": {
        "color": "#4ECDC4",
        "exercises": [
            {
                "id": "squat",
                "display_name": "Squats",
                "required_level": 1,
                "description": "Leg strength powerhouse",
                "muscle_groups": ["Quads", "Glutes", "Hamstrings"],
                "difficulty": "Medium",
                "camera_position": "FRONT or SIDE VIEW",
                "how_to": [
                    "Stand with feet shoulder-width apart, toes pointing slightly outward.",
                    "Keep your chest tall and core braced.",
                    "Bend your knees and push your hips back as if sitting into a chair.",
                    "Lower until your thighs are at least parallel to the floor (or as low as comfortable).",
                    "Drive through your heels to stand back up to the starting position."
                ],
                "tips": [
                    "Keep your knees tracking over your toes — don't let them cave inward.",
                    "Your weight should be in your heels, not your toes.",
                    "Keep your chest upright — don't let your torso collapse forward.",
                    "Full depth builds more muscle — aim to break parallel with your thighs."
                ]
            },
            {
                "id": "lunge",
                "display_name": "Lunges",
                "required_level": 1,
                "description": "Unilateral leg developer",
                "muscle_groups": ["Quads", "Glutes", "Balance"],
                "difficulty": "Medium",
                "camera_position": "FRONT VIEW",
                "how_to": [
                    "Stand tall with feet together, hands on hips or by your sides.",
                    "Step one foot forward about 60–90 cm, landing heel first.",
                    "Lower your back knee toward the floor until both knees are at roughly 90°.",
                    "Your front knee should stay directly above your front ankle — not past your toes.",
                    "Push off your front heel to step back to the start, then alternate legs."
                ],
                "tips": [
                    "Keep your torso upright — don't lean forward over your front leg.",
                    "The longer your step, the more glute activation. Shorter = more quad.",
                    "Control the drop — don't let your back knee crash into the floor.",
                    "Focus on a point in front of you to help with balance."
                ]
            },
            {
                "id": "wall-sit",
                "display_name": "Wall Sit",
                "required_level": 10,
                "description": "Isometric leg endurance",
                "muscle_groups": ["Quads", "Glutes"],
                "difficulty": "Hard",
                "camera_position": "SIDE VIEW",
                "how_to": [
                    "Stand with your back flat against a smooth wall.",
                    "Walk your feet out until they are about 60 cm from the wall.",
                    "Slide your back down the wall until your thighs are parallel to the floor.",
                    "Your knees should be directly above your ankles — at a 90° angle.",
                    "Hold the position and breathe steadily. The AI tracks your hold time."
                ],
                "tips": [
                    "Keep your entire back flat against the wall — no arching.",
                    "Don't rest your hands on your thighs — keep them by your sides or crossed.",
                    "If it gets too easy, hold a water bottle or add a small weight.",
                    "Look straight ahead and breathe — don't hold your breath."
                ]
            },
        ]
    },

    "⚡ CARDIO / FULL BODY": {
        "color": "#45B7D1",
        "exercises": [
            {
                "id": "jumping-jack",
                "display_name": "Jumping Jacks",
                "required_level": 1,
                "description": "Full body warmup & cardio",
                "muscle_groups": ["Full Body", "Cardiovascular"],
                "difficulty": "Easy",
                "camera_position": "FRONT VIEW",
                "how_to": [
                    "Stand tall with feet together and arms by your sides.",
                    "Jump and simultaneously spread your feet wider than shoulder-width.",
                    "As your feet spread, raise both arms overhead until your hands nearly meet.",
                    "Jump again to bring your feet back together and lower your arms to your sides.",
                    "That's one rep. Keep a steady rhythm and maintain a soft bend in the knees."
                ],
                "tips": [
                    "Land softly on the balls of your feet to protect your knees.",
                    "Keep your core engaged so your back doesn't arch as arms go up.",
                    "Use a consistent pace — quality rhythm beats sloppy speed.",
                    "Great as a warm-up: 2–3 minutes gets your heart rate up fast."
                ]
            },
            {
                "id": "high-knees",
                "display_name": "High Knees",
                "required_level": 5,
                "description": "Dynamic cardio and leg power",
                "muscle_groups": ["Legs", "Core", "Cardio"],
                "difficulty": "Medium",
                "camera_position": "SIDE VIEW ← REQUIRED",
                "how_to": [
                    "Stand sideways to the camera so your full body profile is visible.",
                    "Run in place, driving your knees up as high as possible with each step.",
                    "Aim to bring each knee up to at least hip height — the higher the better.",
                    "Pump your arms in rhythm with your legs for full-body engagement.",
                    "The AI tracks alternating knee raises — left + right = counted reps."
                ],
                "tips": [
                    "IMPORTANT: Face sideways to the camera for accurate tracking.",
                    "Drive your knee up fast and slam it back down — power and speed matter.",
                    "Keep your core tight and stand tall — don't hunch forward.",
                    "Breathe rhythmically — don't hold your breath during fast reps."
                ]
            },
            {
                "id": "burpee",
                "display_name": "Burpees",
                "required_level": 12,
                "description": "Ultimate full body challenge",
                "muscle_groups": ["Full Body", "Cardiovascular"],
                "difficulty": "Very Hard",
                "camera_position": "SIDE VIEW",
                "how_to": [
                    "Start standing upright with feet shoulder-width apart.",
                    "Drop into a squat, place your hands on the floor in front of your feet.",
                    "Jump or step both feet back to land in a high plank position.",
                    "Optionally do a push-up at the bottom (for extra difficulty).",
                    "Jump or step feet back to your hands, then explosively jump up with arms overhead. That's 1 rep."
                ],
                "tips": [
                    "Start slow and nail the form before adding speed.",
                    "Keep your plank tight — don't let hips sag when you jump out.",
                    "Breathe out during the jump, breathe in on the way down.",
                    "Burpees are brutal — 5 quality reps beats 20 sloppy ones."
                ]
            },
        ]
    }
}


def get_available_exercises(user_level: int) -> dict:
    """Get exercises available at the user's current level"""
    available = {}

    for category_name, category_data in EXERCISE_CATEGORIES.items():
        category_exercises = []

        for exercise in category_data["exercises"]:
            if user_level >= exercise["required_level"]:
                category_exercises.append({
                    **exercise,
                    "locked": False
                })
            else:
                category_exercises.append({
                    **exercise,
                    "locked": True
                })

        available[category_name] = {
            "color": category_data["color"],
            "exercises": category_exercises
        }

    return available


def get_exercise_info(exercise_id: str) -> dict:
    """Get detailed info about a specific exercise"""
    for category_name, category_data in EXERCISE_CATEGORIES.items():
        for exercise in category_data["exercises"]:
            if exercise["id"] == exercise_id:
                return {
                    **exercise,
                    "category": category_name
                }
    return None


def get_all_exercise_ids() -> list:
    """Get list of all exercise IDs"""
    all_ids = []
    for category_data in EXERCISE_CATEGORIES.values():
        for exercise in category_data["exercises"]:
            all_ids.append(exercise["id"])
    return all_ids