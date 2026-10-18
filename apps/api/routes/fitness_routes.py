"""
Fitness Module API Routes
Comprehensive fitness training, biometric tracking, and AI coaching endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, Query, File, UploadFile
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session
import uuid
import json

# Import models
from apps.api.database.fitness_models import (
    FitnessUser, Workout, Exercise, BiometricData, CoachingSession, 
    UserAchievement, FitnessStats, FitnessLevel, FitnessGoal, ExerciseType,
    WorkoutIntensity, BiometricType
)

# Import modules
from apps.api.modules.biometric_tracker import BiometricTracker, EmotionalState
from apps.api.modules.coaching_engine import CoachingEngine

# ==================== PYDANTIC SCHEMAS ====================

class UserProfileCreate(BaseModel):
    """Create fitness user profile"""
    username: str
    email: str
    age: Optional[int] = None
    gender: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    fitness_level: FitnessLevel = FitnessLevel.BEGINNER
    primary_goal: Optional[FitnessGoal] = None
    secondary_goals: List[FitnessGoal] = []
    resting_heart_rate: Optional[float] = None
    workout_duration_minutes: int = 45
    workouts_per_week: int = 3


class UserProfileUpdate(BaseModel):
    """Update fitness user profile"""
    weight_kg: Optional[float] = None
    resting_heart_rate: Optional[float] = None
    fitness_level: Optional[FitnessLevel] = None
    primary_goal: Optional[FitnessGoal] = None
    preferred_intensity: Optional[WorkoutIntensity] = None


class BiometricReading(BaseModel):
    """Biometric data reading"""
    biometric_type: BiometricType
    value: float
    unit: str
    device_type: Optional[str] = "phone"
    context: Optional[str] = None


class WorkoutCreate(BaseModel):
    """Create workout session"""
    name: str
    workout_type: ExerciseType
    intensity: WorkoutIntensity = WorkoutIntensity.MODERATE
    description: Optional[str] = None


class WorkoutUpdate(BaseModel):
    """Update workout details"""
    mood_after: Optional[str] = None
    energy_after: Optional[int] = None
    pain_level: Optional[int] = None
    notes: Optional[str] = None
    ai_feedback: Optional[str] = None
    completed: bool = True


class ExerciseCreate(BaseModel):
    """Add exercise to workout"""
    name: str
    exercise_type: ExerciseType
    muscle_groups: List[str] = []
    sets: Optional[int] = None
    reps: Optional[int] = None
    weight_kg: Optional[float] = None
    duration_seconds: Optional[int] = None


class PoseAnalysisRequest(BaseModel):
    """Pose analysis request"""
    exercise_name: str
    pose_landmarks: Dict[str, Any]
    confidence_scores: Dict[str, float]


class EmotionalStateRequest(BaseModel):
    """Emotional state detection request"""
    pupil_size: float
    pupil_dilation_rate: float
    blink_rate: float
    eye_gaze_stability: float
    heart_rate: Optional[float] = None


class StressDetectionRequest(BaseModel):
    """Stress level detection request"""
    heart_rate: float
    heart_rate_variability: float
    pupil_dilation_rate: float
    respiratory_rate: Optional[float] = None


# ==================== ROUTER SETUP ====================

fitness_router = APIRouter(prefix="/fitness", tags=["fitness"])


def get_db() -> Session:
    """Get database session - adjust based on your setup"""
    from apps.api.database.connection import SessionLocal
    from apps.api.database.connection import engine
    if engine.dialect.name == "sqlite":
        from apps.api.database.fitness_models import Base
        Base.metadata.create_all(engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==================== USER PROFILE ENDPOINTS ====================

@fitness_router.post("/users/profile", response_model=Dict)
async def create_user_profile(
    profile: UserProfileCreate,
    db: Session = Depends(get_db)
):
    """Create new fitness user profile"""
    
    # Check if user already exists
    existing = db.query(FitnessUser).filter(FitnessUser.email == profile.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Create new user
    new_user = FitnessUser(
        id=str(uuid.uuid4()),
        user_id=f"user_{datetime.now(timezone.utc).timestamp()}",
        username=profile.username,
        email=profile.email,
        age=profile.age,
        gender=profile.gender,
        height_cm=profile.height_cm,
        weight_kg=profile.weight_kg,
        fitness_level=profile.fitness_level,
        primary_goal=profile.primary_goal,
        secondary_goals=profile.secondary_goals,
        resting_heart_rate=profile.resting_heart_rate or 60.0,
        workout_duration_minutes=profile.workout_duration_minutes,
        workouts_per_week=profile.workouts_per_week,
        max_heart_rate=220 - (profile.age or 30)  # Rough estimate
    )
    
    # Create fitness stats
    stats = FitnessStats(
        id=str(uuid.uuid4()),
        user_id=new_user.id
    )
    
    db.add(new_user)
    db.add(stats)
    db.commit()
    db.refresh(new_user)
    
    return {
        "success": True,
        "user_id": new_user.id,
        "username": new_user.username,
        "email": new_user.email,
        "fitness_level": new_user.fitness_level.value,
        "created_at": new_user.created_at.isoformat()
    }


@fitness_router.get("/users/{user_id}/profile")
async def get_user_profile(user_id: str, db: Session = Depends(get_db)):
    """Get user fitness profile"""
    
    user = db.query(FitnessUser).filter(FitnessUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "age": user.age,
        "height_cm": user.height_cm,
        "weight_kg": user.weight_kg,
        "fitness_level": user.fitness_level.value,
        "primary_goal": user.primary_goal.value if user.primary_goal else None,
        "resting_heart_rate": user.resting_heart_rate,
        "max_heart_rate": user.max_heart_rate,
        "workout_duration_minutes": user.workout_duration_minutes,
        "workouts_per_week": user.workouts_per_week,
        "created_at": user.created_at.isoformat()
    }


@fitness_router.put("/users/{user_id}/profile")
async def update_user_profile(
    user_id: str,
    profile_update: UserProfileUpdate,
    db: Session = Depends(get_db)
):
    """Update user fitness profile"""
    
    user = db.query(FitnessUser).filter(FitnessUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if profile_update.weight_kg:
        user.weight_kg = profile_update.weight_kg
    if profile_update.resting_heart_rate:
        user.resting_heart_rate = profile_update.resting_heart_rate
    if profile_update.fitness_level:
        user.fitness_level = profile_update.fitness_level
    if profile_update.primary_goal:
        user.primary_goal = profile_update.primary_goal
    if profile_update.preferred_intensity:
        user.preferred_intensity = profile_update.preferred_intensity
    
    user.updated_at = datetime.now(timezone.utc)
    db.commit()
    
    return {
        "success": True,
        "message": "Profile updated",
        "updated_at": user.updated_at.isoformat()
    }


# ==================== WORKOUT ENDPOINTS ====================

@fitness_router.post("/users/{user_id}/workouts", response_model=Dict)
async def start_workout(
    user_id: str,
    workout: WorkoutCreate,
    db: Session = Depends(get_db)
):
    """Start new workout session"""
    
    user = db.query(FitnessUser).filter(FitnessUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    new_workout = Workout(
        id=str(uuid.uuid4()),
        user_id=user_id,
        name=workout.name,
        workout_type=workout.workout_type,
        intensity=workout.intensity,
        description=workout.description,
        started_at=datetime.now(timezone.utc)
    )
    
    db.add(new_workout)
    db.commit()
    
    return {
        "success": True,
        "workout_id": new_workout.id,
        "name": new_workout.name,
        "type": new_workout.workout_type.value,
        "intensity": new_workout.intensity.value,
        "started_at": new_workout.started_at.isoformat()
    }


@fitness_router.get("/users/{user_id}/workouts")
async def get_user_workouts(
    user_id: str,
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get user's recent workouts"""
    
    workouts = db.query(Workout).filter(
        Workout.user_id == user_id
    ).order_by(Workout.started_at.desc()).limit(limit).all()
    
    return [
        {
            "id": w.id,
            "name": w.name,
            "type": w.workout_type.value,
            "intensity": w.intensity.value,
            "started_at": w.started_at.isoformat(),
            "ended_at": w.ended_at.isoformat() if w.ended_at else None,
            "duration_minutes": w.duration_minutes,
            "total_calories_burned": w.total_calories_burned,
            "average_heart_rate": w.average_heart_rate,
            "completed": w.completed
        }
        for w in workouts
    ]


@fitness_router.get("/workouts/{workout_id}")
async def get_workout_details(
    workout_id: str,
    db: Session = Depends(get_db)
):
    """Get detailed workout information"""
    
    workout = db.query(Workout).filter(Workout.id == workout_id).first()
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    
    exercises = db.query(Exercise).filter(Exercise.workout_id == workout_id).all()
    
    return {
        "id": workout.id,
        "name": workout.name,
        "type": workout.workout_type.value,
        "intensity": workout.intensity.value,
        "started_at": workout.started_at.isoformat(),
        "ended_at": workout.ended_at.isoformat() if workout.ended_at else None,
        "duration_minutes": workout.duration_minutes,
        "total_calories_burned": workout.total_calories_burned,
        "average_heart_rate": workout.average_heart_rate,
        "max_heart_rate": workout.max_heart_rate,
        "min_heart_rate": workout.min_heart_rate,
        "mood_before": workout.mood_before,
        "mood_after": workout.mood_after,
        "energy_before": workout.energy_before,
        "energy_after": workout.energy_after,
        "pain_level": workout.pain_level,
        "ai_feedback": workout.ai_feedback,
        "completed": workout.completed,
        "exercises_count": len(exercises),
        "exercises": [
            {
                "id": e.id,
                "name": e.name,
                "type": e.exercise_type.value,
                "sets": e.sets,
                "reps": e.reps,
                "weight_kg": e.weight_kg,
                "form_score": e.form_score,
                "form_issues": e.form_issues
            }
            for e in exercises
        ]
    }


@fitness_router.put("/workouts/{workout_id}/end", response_model=Dict)
async def end_workout(
    workout_id: str,
    update: WorkoutUpdate,
    db: Session = Depends(get_db)
):
    """End workout session"""
    
    workout = db.query(Workout).filter(Workout.id == workout_id).first()
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    
    workout.ended_at = datetime.now(timezone.utc)
    if workout.started_at:
        workout.duration_minutes = int((workout.ended_at - workout.started_at).total_seconds() / 60)
    
    if update.mood_after:
        workout.mood_after = update.mood_after
    if update.energy_after:
        workout.energy_after = update.energy_after
    if update.pain_level is not None:
        workout.pain_level = update.pain_level
    if update.notes:
        workout.notes = update.notes
    if update.ai_feedback:
        workout.ai_feedback = update.ai_feedback
    
    workout.completed = update.completed
    
    db.commit()
    
    return {
        "success": True,
        "message": "Workout ended",
        "workout_id": workout.id,
        "duration_minutes": workout.duration_minutes,
        "ended_at": workout.ended_at.isoformat()
    }


# ==================== EXERCISE ENDPOINTS ====================

@fitness_router.post("/workouts/{workout_id}/exercises")
async def add_exercise(
    workout_id: str,
    exercise: ExerciseCreate,
    db: Session = Depends(get_db)
):
    """Add exercise to workout"""
    
    workout = db.query(Workout).filter(Workout.id == workout_id).first()
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    
    new_exercise = Exercise(
        id=str(uuid.uuid4()),
        workout_id=workout_id,
        name=exercise.name,
        exercise_type=exercise.exercise_type,
        muscle_groups=exercise.muscle_groups,
        sets=exercise.sets,
        reps=exercise.reps,
        weight_kg=exercise.weight_kg,
        duration_seconds=exercise.duration_seconds,
        started_at=datetime.now(timezone.utc)
    )
    
    db.add(new_exercise)
    db.commit()
    
    return {
        "success": True,
        "exercise_id": new_exercise.id,
        "name": new_exercise.name,
        "type": new_exercise.exercise_type.value,
        "started_at": new_exercise.started_at.isoformat()
    }


# ==================== BIOMETRIC ENDPOINTS ====================

@fitness_router.post("/users/{user_id}/biometrics")
async def record_biometric(
    user_id: str,
    reading: BiometricReading,
    db: Session = Depends(get_db)
):
    """Record biometric measurement"""
    
    user = db.query(FitnessUser).filter(FitnessUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    biometric = BiometricData(
        id=str(uuid.uuid4()),
        user_id=user_id,
        biometric_type=reading.biometric_type,
        value=reading.value,
        unit=reading.unit,
        device_type=reading.device_type,
        context=reading.context,
        measurement_time=datetime.now(timezone.utc)
    )
    
    db.add(biometric)
    db.commit()
    
    return {
        "success": True,
        "biometric_id": biometric.id,
        "type": reading.biometric_type.value,
        "value": reading.value,
        "unit": reading.unit,
        "recorded_at": biometric.measurement_time.isoformat()
    }


@fitness_router.get("/users/{user_id}/biometrics")
async def get_user_biometrics(
    user_id: str,
    biometric_type: Optional[BiometricType] = None,
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get user's biometric data"""
    
    query = db.query(BiometricData).filter(BiometricData.user_id == user_id)
    
    if biometric_type:
        query = query.filter(BiometricData.biometric_type == biometric_type)
    
    readings = query.order_by(BiometricData.measurement_time.desc()).limit(limit).all()
    
    return [
        {
            "id": r.id,
            "type": r.biometric_type.value,
            "value": r.value,
            "unit": r.unit,
            "device_type": r.device_type,
            "context": r.context,
            "measured_at": r.measurement_time.isoformat()
        }
        for r in readings
    ]


# ==================== COACHING ENDPOINTS ====================

@fitness_router.post("/analyze/pose")
async def analyze_exercise_form(request: PoseAnalysisRequest):
    """Analyze exercise form using pose estimation"""
    
    coach = CoachingEngine()
    analysis = coach.analyze_pose(
        exercise_name=request.exercise_name,
        pose_landmarks=request.pose_landmarks,
        confidence_scores=request.confidence_scores
    )
    
    return {
        "exercise": analysis.exercise_name,
        "form_score": analysis.form_score,
        "issues": analysis.issues,
        "recommendations": analysis.recommendations,
        "timestamp": analysis.timestamp.isoformat()
    }


@fitness_router.post("/analyze/emotional-state")
async def detect_emotional_state(request: EmotionalStateRequest):
    """Detect emotional state from pupil tracking"""
    
    tracker = BiometricTracker("temp_user", {"age": 30, "weight_kg": 75, "fitness_level": "intermediate"})
    state, confidence = tracker.detect_emotional_state(
        pupil_size=request.pupil_size,
        pupil_dilation_rate=request.pupil_dilation_rate,
        blink_rate=request.blink_rate,
        eye_gaze_stability=request.eye_gaze_stability,
        heart_rate=request.heart_rate
    )
    
    return {
        "emotional_state": state.value,
        "confidence": confidence,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@fitness_router.post("/analyze/stress-level")
async def detect_stress_level(request: StressDetectionRequest):
    """Detect stress level from biometric data"""
    
    tracker = BiometricTracker("temp_user", {"age": 30, "weight_kg": 75, "fitness_level": "intermediate"})
    stress_score, interpretation = tracker.detect_stress_level(
        heart_rate=request.heart_rate,
        heart_rate_variability=request.heart_rate_variability,
        pupil_dilation_rate=request.pupil_dilation_rate,
        respiratory_rate=request.respiratory_rate
    )
    
    return {
        "stress_level": stress_score,
        "interpretation": interpretation,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


# ==================== STATISTICS ENDPOINTS ====================

@fitness_router.get("/users/{user_id}/stats")
async def get_user_stats(user_id: str, db: Session = Depends(get_db)):
    """Get aggregated fitness statistics"""
    
    stats = db.query(FitnessStats).filter(FitnessStats.user_id == user_id).first()
    if not stats:
        raise HTTPException(status_code=404, detail="Stats not found")
    
    return {
        "total_workouts": stats.total_workouts,
        "total_workout_hours": stats.total_workout_hours,
        "total_calories_burned": stats.total_calories_burned,
        "total_distance_km": stats.total_distance_km,
        "total_steps": stats.total_steps,
        "current_workout_streak": stats.current_workout_streak,
        "longest_workout_streak": stats.longest_workout_streak,
        "avg_workout_duration_minutes": stats.avg_workout_duration_minutes,
        "avg_heart_rate": stats.avg_heart_rate,
        "avg_calories_per_workout": stats.avg_calories_per_workout,
        "max_heart_rate_recorded": stats.max_heart_rate_recorded,
        "longest_workout_minutes": stats.longest_workout_minutes,
        "weekly_improvement_percent": stats.weekly_improvement_percent,
        "monthly_improvement_percent": stats.monthly_improvement_percent,
        "form_accuracy_trend": stats.form_accuracy_trend,
        "updated_at": stats.updated_at.isoformat()
    }


@fitness_router.get("/health")
async def fitness_module_health():
    """Fitness module health check"""
    return {
        "status": "healthy",
        "module": "fitness_training",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


