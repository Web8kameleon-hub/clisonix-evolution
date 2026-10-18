from enum import Enum


class FitnessLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    ELITE = "elite"


class FitnessGoal(str, Enum):
    WEIGHT_LOSS = "weight_loss"
    MUSCLE_GAIN = "muscle_gain"
    ENDURANCE = "endurance"
    STRENGTH = "strength"
    FLEXIBILITY = "flexibility"
    GENERAL_HEALTH = "general_health"
    SPORTS_PERFORMANCE = "sports_performance"


class ExerciseType(str, Enum):
    CARDIO = "cardio"
    STRENGTH = "strength"
    FLEXIBILITY = "flexibility"
    BALANCE = "balance"
    SPORTS = "sports"
    RECOVERY = "recovery"


class WorkoutIntensity(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    HIIT = "hiit"


class BiometricType(str, Enum):
    HEART_RATE = "heart_rate"
    CALORIES_BURNED = "calories_burned"
    STEPS = "steps"
    DISTANCE = "distance"
    ELEVATION = "elevation"
    RESPIRATION_RATE = "respiration_rate"
    BLOOD_PRESSURE_SYSTOLIC = "blood_pressure_systolic"
    BLOOD_PRESSURE_DIASTOLIC = "blood_pressure_diastolic"
    OXYGEN_SATURATION = "oxygen_saturation"
    BODY_TEMPERATURE = "body_temperature"
    EMOTIONAL_STATE = "emotional_state"
    STRESS_LEVEL = "stress_level"
    SLEEP_QUALITY = "sleep_quality"
    FATIGUE = "fatigue"
