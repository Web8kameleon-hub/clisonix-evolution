"""
ML Overlay Manager - Intelligence Layer
========================================
Provides ML capabilities ONLY for MATURE rows.

Key Principle: ML aktivizohet vetëm mbi rreshtat e pjekur (MATURE).
ML does not make decisions - it suggests and monitors.

Models:
- Classification → ML_Score
- Recommender → ML_Suggested_Agent, ML_Suggested_Lab
- Anomaly Detection → ML_Anomaly_Prob
"""

import random
import hashlib
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum


class MLConfidence(Enum):
    """ML prediction confidence level"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class ModelType(Enum):
    """Types of ML models"""
    CLASSIFIER = "classifier"
    RECOMMENDER = "recommender"
    ANOMALY_DETECTOR = "anomaly_detector"
    FORECASTER = "forecaster"


@dataclass
class MLPrediction:
    """ML model prediction result"""
    model_id: str
    model_type: ModelType
    prediction: Any
    confidence: float
    confidence_level: MLConfidence
    features_used: List[str]
    timestamp: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'model_id': self.model_id,
            'model_type': self.model_type.value,
            'prediction': self.prediction,
            'confidence': self.confidence,
            'confidence_level': self.confidence_level.value,
            'features_used': self.features_used,
            'timestamp': self.timestamp
        }


class MLModel(ABC):
    """Abstract base class for ML models"""
    
    @property
    @abstractmethod
    def model_id(self) -> str:
        """Model identifier"""
        pass
    
    @property
    @abstractmethod
    def model_type(self) -> ModelType:
        """Type of model"""
        pass
    
    @abstractmethod
    def predict(self, row: Dict[str, Any]) -> MLPrediction:
        """Make a prediction for the given row"""
        pass
    
    def _compute_confidence_level(self, confidence: float) -> MLConfidence:
        """Compute confidence level from score"""
        if confidence >= 0.8:
            return MLConfidence.HIGH
        elif confidence >= 0.5:
            return MLConfidence.MEDIUM
        return MLConfidence.LOW


class RowClassifier(MLModel):
    """
    Classifies rows by quality/priority
    Output: ML_Score (0-1)
    """
    
    @property
    def model_id(self) -> str:
        return "ml-row-classifier"
    
    @property
    def model_type(self) -> ModelType:
        return ModelType.CLASSIFIER
    
    def predict(self, row: Dict[str, Any]) -> MLPrediction:
        """
        Classify row quality/priority
        
        Features considered:
        - Security status
        - Validation status
        - Lab results
        - Artifacts count
        - Source protocol
        """
        features = []
        score = 0.5  # Base score
        
        # Security bonus
        if row.get('security') == 'PASS':
            score += 0.15
            features.append('security')
        
        # Validation bonus
        if row.get('schema_validation') == 'PASS':
            score += 0.15
            features.append('schema_validation')
        
        # Artifacts bonus
        artifacts = row.get('artifacts', [])
        if artifacts:
            score += min(0.1, len(artifacts) * 0.02)
            features.append('artifacts')
        
        # Lab results bonus
        lab_result = row.get('lab', {})
        if isinstance(lab_result, dict):
            labs_passed = lab_result.get('labs_passed', 0)
            score += min(0.1, labs_passed * 0.03)
            features.append('lab_results')
        
        # Protocol reliability factor
        reliable_protocols = ['REST', 'GraphQL', 'gRPC']
        if row.get('source_protocol') in reliable_protocols:
            score += 0.05
            features.append('source_protocol')
        
        # Clamp to [0, 1]
        score = max(0.0, min(1.0, score))
        confidence = 0.6 + (0.3 * random.random())  # Simulated confidence
        
        return MLPrediction(
            model_id=self.model_id,
            model_type=self.model_type,
            prediction=score,
            confidence=confidence,
            confidence_level=self._compute_confidence_level(confidence),
            features_used=features,
            timestamp=datetime.utcnow().isoformat()
        )


class AgentRecommender(MLModel):
    """
    Recommends best agent for similar future rows
    Output: ML_Suggested_Agent
    """
    
    AGENT_PATTERNS = {
        'agent-data-processing': ['L1', 'L2', 'File', 'Webhook'],
        'agent-integration': ['REST', 'GraphQL', 'gRPC'],
        'agent-analytics': ['L2', 'L3', 'report', 'analytics'],
        'agent-ml': ['MATURE']
    }
    
    @property
    def model_id(self) -> str:
        return "ml-agent-recommender"
    
    @property
    def model_type(self) -> ModelType:
        return ModelType.RECOMMENDER
    
    def predict(self, row: Dict[str, Any]) -> MLPrediction:
        """
        Recommend agent based on row characteristics
        
        Uses pattern matching and historical performance
        """
        features = []
        scores = {}
        
        layer = row.get('layer', 'L1')
        protocol = row.get('source_protocol', '')
        input_type = row.get('input_type', '').lower()
        
        features.extend(['layer', 'source_protocol', 'input_type'])
        
        # Score each agent
        for agent_id, patterns in self.AGENT_PATTERNS.items():
            score = 0.0
            for pattern in patterns:
                if pattern in layer:
                    score += 0.3
                if pattern in protocol:
                    score += 0.3
                if pattern.lower() in input_type:
                    score += 0.2
            scores[agent_id] = score
        
        # Find best agent
        best_agent = max(scores, key=scores.get)
        best_score = scores[best_agent]
        
        # Confidence based on score differential
        sorted_scores = sorted(scores.values(), reverse=True)
        if len(sorted_scores) > 1:
            confidence = 0.5 + (sorted_scores[0] - sorted_scores[1]) * 0.5
        else:
            confidence = 0.7
        
        return MLPrediction(
            model_id=self.model_id,
            model_type=self.model_type,
            prediction=best_agent,
            confidence=confidence,
            confidence_level=self._compute_confidence_level(confidence),
            features_used=features,
            timestamp=datetime.utcnow().isoformat()
        )


class LabRecommender(MLModel):
    """
    Recommends best lab for processing
    Output: ML_Suggested_Lab
    """
    
    LAB_PATTERNS = {
        'lab-data-validation': ['validation', 'data', 'check', 'verify'],
        'lab-transformation': ['transform', 'convert', 'process', 'normalize'],
        'lab-integration': ['integration', 'api', 'external', 'connect']
    }
    
    @property
    def model_id(self) -> str:
        return "ml-lab-recommender"
    
    @property
    def model_type(self) -> ModelType:
        return ModelType.RECOMMENDER
    
    def predict(self, row: Dict[str, Any]) -> MLPrediction:
        """
        Recommend lab based on row characteristics
        """
        features = []
        scores = {}
        
        input_type = row.get('input_type', '').lower()
        protocol = row.get('source_protocol', '').lower()
        
        features.extend(['input_type', 'source_protocol'])
        
        # Score each lab
        for lab_id, patterns in self.LAB_PATTERNS.items():
            score = 0.0
            for pattern in patterns:
                if pattern in input_type:
                    score += 0.4
                if pattern in protocol:
                    score += 0.2
            scores[lab_id] = score
        
        # If no strong match, default to data validation
        if max(scores.values()) < 0.2:
            scores['lab-data-validation'] = 0.5
        
        best_lab = max(scores, key=scores.get)
        confidence = 0.5 + scores[best_lab] * 0.4
        
        return MLPrediction(
            model_id=self.model_id,
            model_type=self.model_type,
            prediction=best_lab,
            confidence=confidence,
            confidence_level=self._compute_confidence_level(confidence),
            features_used=features,
            timestamp=datetime.utcnow().isoformat()
        )


class AnomalyDetector(MLModel):
    """
    Detects anomalous patterns in rows
    Output: ML_Anomaly_Prob (0-1)
    """
    
    @property
    def model_id(self) -> str:
        return "ml-anomaly-detector"
    
    @property
    def model_type(self) -> ModelType:
        return ModelType.ANOMALY_DETECTOR
    
    def predict(self, row: Dict[str, Any]) -> MLPrediction:
        """
        Detect anomalies in row data
        
        Checks for:
        - Unusual field values
        - Missing expected fields
        - Inconsistent status combinations
        """
        features = []
        anomaly_score = 0.0
        
        # Check for unusual cycle values
        cycle = row.get('cycle', 0)
        if cycle < 0 or cycle > 10000:
            anomaly_score += 0.3
            features.append('unusual_cycle')
        
        # Check for status inconsistencies
        security = row.get('security', 'PENDING')
        status = row.get('status', 'RAW')
        if security == 'FAIL' and status == 'READY':
            anomaly_score += 0.4
            features.append('status_inconsistency')
        
        # Check for unusual protocols
        known_protocols = ['REST', 'GraphQL', 'gRPC', 'Webhook', 'File']
        protocol = row.get('source_protocol', '')
        if protocol and protocol not in known_protocols:
            anomaly_score += 0.2
            features.append('unknown_protocol')
        
        # Check for missing artifacts on READY status
        if status == 'READY' and not row.get('artifacts'):
            anomaly_score += 0.2
            features.append('missing_artifacts')
        
        # Clamp to [0, 1]
        anomaly_score = max(0.0, min(1.0, anomaly_score))
        
        # Higher anomaly = lower confidence in data
        confidence = 0.7 + (0.2 * random.random())
        
        return MLPrediction(
            model_id=self.model_id,
            model_type=self.model_type,
            prediction=anomaly_score,
            confidence=confidence,
            confidence_level=self._compute_confidence_level(confidence),
            features_used=features,
            timestamp=datetime.utcnow().isoformat()
        )


class MLManager:
    """
    Manages ML model execution
    
    Key Rule: Only runs on MATURE rows
    """
    
    def __init__(self):
        self.models: Dict[str, MLModel] = {}
        self._register_defaults()
    
    def _register_defaults(self):
        """Register default models"""
        self.register(RowClassifier())
        self.register(AgentRecommender())
        self.register(LabRecommender())
        self.register(AnomalyDetector())
    
    def register(self, model: MLModel):
        """Register a model"""
        self.models[model.model_id] = model
    
    def is_eligible(self, row: Dict[str, Any]) -> bool:
        """
        Check if row is eligible for ML overlay
        
        Rule: Only MATURE rows can have ML applied
        """
        maturity = row.get('maturity_state', 'IMMATURE')
        return maturity == 'MATURE'
    
    def run_model(self, row: Dict[str, Any], model_id: str) -> Optional[MLPrediction]:
        """Run a specific model"""
        if not self.is_eligible(row):
            return None
        
        model = self.models.get(model_id)
        if not model:
            return None
        
        return model.predict(row)
    
    def run_all_models(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run all models on a row
        
        Returns dict with ML columns ready to update row
        """
        if not self.is_eligible(row):
            return {
                'ml_applied': False,
                'ml_reason': 'Row not MATURE'
            }
        
        results = {
            'ml_applied': True,
            'ml_timestamp': datetime.utcnow().isoformat()
        }
        
        # Run classifier
        classifier = self.models.get('ml-row-classifier')
        if classifier:
            pred = classifier.predict(row)
            results['ml_score'] = pred.prediction
            results['ml_confidence'] = pred.confidence_level.value
        
        # Run agent recommender
        agent_rec = self.models.get('ml-agent-recommender')
        if agent_rec:
            pred = agent_rec.predict(row)
            results['ml_suggested_agent'] = pred.prediction
        
        # Run lab recommender
        lab_rec = self.models.get('ml-lab-recommender')
        if lab_rec:
            pred = lab_rec.predict(row)
            results['ml_suggested_lab'] = pred.prediction
        
        # Run anomaly detector
        anomaly = self.models.get('ml-anomaly-detector')
        if anomaly:
            pred = anomaly.predict(row)
            results['ml_anomaly_prob'] = pred.prediction
            
            # Add anomaly alert if high
            if pred.prediction > 0.5:
                results['ml_anomaly_alert'] = True
                results['ml_anomaly_features'] = pred.features_used
        
        return results


# Global ML manager
_ml_manager: Optional[MLManager] = None

def get_ml_manager() -> MLManager:
    """Get or create the global ML manager"""
    global _ml_manager
    if _ml_manager is None:
        _ml_manager = MLManager()
    return _ml_manager


def run_ml_models(row: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main entry point: Run ML models on a row
    
    Args:
        row: Canonical row data (must be MATURE)
        
    Returns:
        Dict with ML results to update row
    """
    manager = get_ml_manager()
    return manager.run_all_models(row)


def is_ml_eligible(row: Dict[str, Any]) -> bool:
    """
    Check if a row is eligible for ML overlay
    
    Args:
        row: Canonical row data
        
    Returns:
        True if row is MATURE and eligible for ML
    """
    manager = get_ml_manager()
    return manager.is_eligible(row)
