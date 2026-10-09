"""
🧠 ALBI Neural Processing Architecture
=====================================
Specializimi i ALBI në procesimin e sinjaleve neurale dhe analizën e frekuencave të trurit.
Zemra e sistemit për EEG processing dhe brain signal analysis.
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import scipy.signal


class BrainwaveType(Enum):
    """Llojet e valëve të trurit"""
    DELTA = "delta"      # 0.5-4 Hz - Gjumë i thellë
    THETA = "theta"      # 4-8 Hz - Meditim i thellë
    ALPHA = "alpha"      # 8-12 Hz - Relaksim aktiv
    BETA = "beta"        # 12-30 Hz - Vëmendje aktive
    GAMMA = "gamma"      # 30+ Hz - Përqendrim i lartë


class ProcessingQuality(Enum):
    """Cilësia e procesimit"""
    EXCELLENT = "excellent"
    GOOD = "good"
    MODERATE = "moderate"
    POOR = "poor"
    ARTIFACT = "artifact"


@dataclass
class EEGChannel:
    """Kanali i EEG me pozicionin e elektrodës"""
    name: str  # p.sh. "Fp1", "C3", "O1"
    position: Tuple[float, float, float]  # Koordinatat 3D
    impedance: float = 5.0  # kOhm
    quality: ProcessingQuality = ProcessingQuality.GOOD
    data: List[float] = field(default_factory=list)


@dataclass
class BrainwaveAnalysis:
    """Rezultati i analizës së valëve të trurit"""
    dominant_frequency: float
    dominant_power: float
    brainwave_type: BrainwaveType
    frequency_bands: Dict[str, float]
    coherence_score: float
    artifact_level: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class NeuralPattern:
    """Pattern neuronal i identifikuar"""
    pattern_id: str
    pattern_type: str
    confidence: float
    frequency_signature: List[float]
    temporal_evolution: List[Dict]
    metadata: Dict[str, Any] = field(default_factory=dict)


class ALBINeuralProcessor:
    """
    🧠 Procesori neural i ALBI - specializimi në EEG dhe brain signals
    Përpunon sinjalet neurale dhe identifikon pattern-et e trurit
    """

    def __init__(self):
        self.sampling_rate = 256  # Hz - frekuenca e sampling
        self.channels = self._initialize_eeg_channels()
        self.processing_history = []
        self.learned_patterns = {}
        self.frequency_bands = {
            'delta': (0.5, 4.0),
            'theta': (4.0, 8.0),
            'alpha': (8.0, 12.0),
            'beta': (12.0, 30.0),
            'gamma': (30.0, 100.0)
        }

    def _initialize_eeg_channels(self) -> Dict[str, EEGChannel]:
        """Inicializon kanalet e EEG me pozicionet standarde"""
        # Pozicionet e elektrodave sipas sistemit 10-20
        channel_positions = {
            'Fp1': (-0.3, 0.7, 0.1),    # Frontal pole left
            'Fp2': (0.3, 0.7, 0.1),     # Frontal pole right
            'F3': (-0.5, 0.5, 0.3),     # Frontal left
            'F4': (0.5, 0.5, 0.3),      # Frontal right
            'C3': (-0.5, 0.0, 0.6),     # Central left
            'C4': (0.5, 0.0, 0.6),      # Central right
            'P3': (-0.5, -0.5, 0.3),    # Parietal left
            'P4': (0.5, -0.5, 0.3),     # Parietal right
            'O1': (-0.3, -0.7, 0.1),    # Occipital left
            'O2': (0.3, -0.7, 0.1),     # Occipital right
            'T3': (-0.7, 0.0, 0.0),     # Temporal left
            'T4': (0.7, 0.0, 0.0),      # Temporal right
        }

        channels = {}
        for name, position in channel_positions.items():
            channels[name] = EEGChannel(
                name=name,
                position=position,
                impedance=np.random.uniform(2.0, 8.0),  # Simulim i impedancës
                quality=ProcessingQuality.GOOD
            )

        return channels

    async def process_eeg_signal(self, raw_data: np.ndarray, channel_names: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        🔬 Procesimi kryesor i sinjaleve EEG

        Args:
            raw_data: Të dhënat e papërpunuara EEG (samples x channels)
            channel_names: Emrat e kanaleve (opsionale)

        Returns:
            Dict me rezultatet e analizës
        """
        processing_start = datetime.now()

        if channel_names is None:
            channel_names = list(self.channels.keys())[:raw_data.shape[1]]

        # HAPI 1: Pastrimi i sinjalit
        cleaned_data = await self._preprocess_signal(raw_data)

        # HAPI 2: Analiza e frekuencave
        frequency_analysis = await self._frequency_analysis(cleaned_data, channel_names)

        # HAPI 3: Identifikimi i pattern-eve
        pattern_detection = await self._detect_neural_patterns(cleaned_data, channel_names)

        # HAPI 4: Analiza e coherence-s
        coherence_analysis = await self._coherence_analysis(cleaned_data, channel_names)

        # HAPI 5: Interpretimi i gjendjes së trurit
        brain_state = await self._interpret_brain_state(frequency_analysis, pattern_detection)

        processing_duration = (datetime.now() - processing_start).total_seconds()

        # Ruaj në histori
        processing_record = {
            'timestamp': processing_start,
            'duration_ms': processing_duration * 1000,
            'channels_processed': len(channel_names),
            'samples_processed': raw_data.shape[0],
            'dominant_frequency': frequency_analysis.get('dominant_frequency', 0),
            'brain_state': brain_state.get('state_name', 'unknown')
        }
        self.processing_history.append(processing_record)

        quality_metrics = await self._calculate_quality_metrics(cleaned_data)
        synthesis_ready = await self._prepare_for_synthesis(frequency_analysis, brain_state)
        albi_insights = await self._generate_neural_insights(brain_state, pattern_detection)

        # Stable API keys (emoji-free) + legacy aliases for backward compatibility
        return {
            'brain_state': brain_state,
            'frequency_analysis': frequency_analysis,
            'pattern_detection': pattern_detection,
            'coherence_analysis': coherence_analysis,
            'processing_time_ms': processing_duration * 1000,
            'quality_metrics': quality_metrics,
            'synthesis_ready': synthesis_ready,
            'albi_insights': albi_insights,
            '🧠 brain_state': brain_state,
            '📊 frequency_analysis': frequency_analysis,
            '🔍 pattern_detection': pattern_detection,
            '🌊 coherence_analysis': coherence_analysis,
            '⏱️ processing_time_ms': processing_duration * 1000,
            '📈 quality_metrics': quality_metrics,
            '🎵 synthesis_ready': synthesis_ready,
            '✨ albi_insights': albi_insights
        }

    async def _preprocess_signal(self, raw_data: np.ndarray) -> np.ndarray:
        """🧹 Pastrimi dhe preprocessing i sinjalit"""
        # Filter band-pass 0.5-50 Hz
        nyquist = self.sampling_rate / 2
        low = 0.5 / nyquist
        high = 50.0 / nyquist

        # Dizajno filtrin
        sos = scipy.signal.butter(4, [low, high], btype='band', output='sos')

        # Apliko filtrin në secilin kanal
        filtered_data = np.zeros_like(raw_data)
        for i in range(raw_data.shape[1]):
            filtered_data[:, i] = scipy.signal.sosfiltfilt(sos, raw_data[:, i])

        # Hiq artifacts (outliers)
        cleaned_data = self._remove_artifacts(filtered_data)

        return cleaned_data

    def _remove_artifacts(self, data: np.ndarray) -> np.ndarray:
        """🚫 Heq artifacts dhe outliers"""
        cleaned = data.copy()

        for i in range(data.shape[1]):
            channel_data = data[:, i]

            # Identifiko outliers (> 3 standard deviations)
            mean_val = np.mean(channel_data)
            std_val = np.std(channel_data)
            outlier_threshold = 3 * std_val

            # Zëvendëso outliers me median
            outlier_mask = np.abs(channel_data - mean_val) > outlier_threshold
            if np.any(outlier_mask):
                median_val = np.median(channel_data)
                cleaned[outlier_mask, i] = median_val

        return cleaned

    async def _frequency_analysis(self, data: np.ndarray, channel_names: List[str]) -> Dict[str, Any]:
        """📊 Analiza e spektrit të frekuencave"""
        # FFT për secilin kanal
        fft_results: Dict[str, Dict[str, List[float]]] = {}
        power_spectra: Dict[str, np.ndarray] = {}
        channel_freqs: Dict[str, np.ndarray] = {}

        for i, channel in enumerate(channel_names):
            if i >= data.shape[1]:
                continue

            # FFT
            fft_result = np.fft.fft(data[:, i])
            freqs = np.fft.fftfreq(len(data[:, i]), 1/self.sampling_rate)

            # Power spectral density
            power_spectrum = np.abs(fft_result) ** 2

            # Merr vetëm frekuencat pozitive
            positive_freqs = freqs[:len(freqs)//2]
            positive_power = power_spectrum[:len(power_spectrum)//2]

            fft_results[channel] = {
                'frequencies': positive_freqs.tolist(),
                'power': positive_power.tolist()
            }
            power_spectra[channel] = positive_power
            channel_freqs[channel] = positive_freqs

        if not power_spectra:
            empty_band = {
                band_name: {
                    'frequency_range': f"{low_freq}-{high_freq} Hz",
                    'channel_power': {},
                    'average_power': 0.0
                }
                for band_name, (low_freq, high_freq) in self.frequency_bands.items()
            }
            return {
                'dominant_frequency': 0.0,
                'dominant_power': 0.0,
                'brainwave_type': BrainwaveType.DELTA.value,
                'frequency_bands': empty_band,
                'channel_spectra': fft_results,
                'spectral_centroid': 0.0
            }

        # Analizo brezat e frekuencave
        band_analysis = {}
        for band_name, (low_freq, high_freq) in self.frequency_bands.items():
            band_power = {}
            for channel in channel_names:
                if channel in power_spectra:
                    power = power_spectra[channel]
                    freqs_for_channel = channel_freqs[channel]
                    freq_mask = (freqs_for_channel >= low_freq) & (freqs_for_channel <= high_freq)
                    band_power[channel] = np.sum(power[freq_mask])

            band_analysis[band_name] = {
                'frequency_range': f"{low_freq}-{high_freq} Hz",
                'channel_power': band_power,
                'average_power': np.mean(list(band_power.values())) if band_power else 0
            }

        # Gjej frekuencën dominante
        all_power = np.concatenate([power_spectra[ch] for ch in power_spectra.keys()])
        all_freqs = np.concatenate([channel_freqs[ch] for ch in power_spectra.keys()])

        dominant_idx = np.argmax(all_power)
        dominant_frequency = all_freqs[dominant_idx] if len(all_freqs) > dominant_idx else 0

        # Klasifiko llojin e valës së trurit
        brainwave_type = self._classify_brainwave(dominant_frequency)

        mean_power = np.mean([power_spectra[ch] for ch in power_spectra.keys()], axis=0)
        ref_freqs = next(iter(channel_freqs.values()))
        centroid_denominator = float(np.sum(mean_power))
        spectral_centroid = float(np.average(ref_freqs, weights=mean_power)) if centroid_denominator > 0 else 0.0

        return {
            'dominant_frequency': float(dominant_frequency),
            'dominant_power': float(np.max(all_power)) if len(all_power) > 0 else 0,
            'brainwave_type': brainwave_type.value,
            'frequency_bands': band_analysis,
            'channel_spectra': fft_results,
            'spectral_centroid': spectral_centroid
        }

    def _classify_brainwave(self, frequency: float) -> BrainwaveType:
        """🧠 Klasifikon llojin e valës së trurit"""
        if frequency < 4:
            return BrainwaveType.DELTA
        elif frequency < 8:
            return BrainwaveType.THETA
        elif frequency < 12:
            return BrainwaveType.ALPHA
        elif frequency < 30:
            return BrainwaveType.BETA
        else:
            return BrainwaveType.GAMMA

    async def _detect_neural_patterns(self, data: np.ndarray, channel_names: List[str]) -> Dict[str, Any]:
        """🔍 Identifikon pattern-et neurale"""
        detected_patterns = []

        # Pattern 1: Synchronized oscillations
        sync_pattern = await self._detect_synchronization(data, channel_names)
        if sync_pattern['confidence'] > 0.7:
            detected_patterns.append(sync_pattern)

        # Pattern 2: Event-related potentials
        erp_pattern = await self._detect_erp(data, channel_names)
        if erp_pattern['confidence'] > 0.6:
            detected_patterns.append(erp_pattern)

        # Pattern 3: Cross-frequency coupling
        coupling_pattern = await self._detect_cross_frequency_coupling(data, channel_names)
        if coupling_pattern['confidence'] > 0.5:
            detected_patterns.append(coupling_pattern)

        # Ruaj pattern-et e mësuar
        for pattern in detected_patterns:
            pattern_id = pattern['pattern_id']
            if pattern_id not in self.learned_patterns:
                self.learned_patterns[pattern_id] = []
            self.learned_patterns[pattern_id].append({
                'timestamp': datetime.now(),
                'confidence': pattern['confidence'],
                'metadata': pattern.get('metadata', {})
            })

        return {
            'detected_patterns': detected_patterns,
            'pattern_count': len(detected_patterns),
            'learned_patterns_total': len(self.learned_patterns),
            'pattern_learning_progress': len(self.processing_history)
        }

    async def _detect_synchronization(self, data: np.ndarray, channels: List[str]) -> Dict[str, Any]:
        """🔄 Detekton sinkronizimin midis kanaleve"""
        if data.shape[1] < 2:
            return {'pattern_id': 'sync_001', 'confidence': 0.0, 'pattern_type': 'synchronization'}

        # Llogarit korrelacionin midis kanaleve
        correlations = []
        for i in range(data.shape[1]):
            for j in range(i+1, data.shape[1]):
                corr = np.corrcoef(data[:, i], data[:, j])[0, 1]
                if not np.isnan(corr):
                    correlations.append(abs(corr))

        avg_correlation = np.mean(correlations) if correlations else 0

        return {
            'pattern_id': f'sync_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'pattern_type': 'synchronization',
            'confidence': float(avg_correlation),
            'average_correlation': float(avg_correlation),
            'channel_pairs': len(correlations),
            'metadata': {
                'sync_strength': 'high' if avg_correlation > 0.7 else 'moderate' if avg_correlation > 0.4 else 'low'
            }
        }

    async def _detect_erp(self, data: np.ndarray, channels: List[str]) -> Dict[str, Any]:
        """⚡ Detekton Event-Related Potentials"""
        # Simulim i detection të ERP
        # Në implementim real do kërkonte trigger events

        # Kërko peaks të mëdha në signal
        peaks_per_channel = []
        for i in range(data.shape[1]):
            channel_data = data[:, i]
            peaks, _ = scipy.signal.find_peaks(np.abs(channel_data),
                                             height=np.std(channel_data) * 2,
                                             distance=int(self.sampling_rate * 0.1))  # Min 100ms apart
            peaks_per_channel.append(len(peaks))

        avg_peaks = np.mean(peaks_per_channel)
        confidence = float(np.clip(avg_peaks / 10.0, 0.0, 1.0))  # Normalize

        return {
            'pattern_id': f'erp_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'pattern_type': 'event_related_potential',
            'confidence': float(confidence),
            'average_peaks': float(avg_peaks),
            'total_channels': len(channels),
            'metadata': {
                'erp_strength': 'strong' if confidence > 0.7 else 'moderate' if confidence > 0.4 else 'weak'
            }
        }

    async def _detect_cross_frequency_coupling(self, data: np.ndarray, channels: List[str]) -> Dict[str, Any]:
        """🌊 Detekton Cross-Frequency Coupling"""
        # Simplified cross-frequency coupling detection

        coupling_scores = []
        for i in range(data.shape[1]):
            channel_data = data[:, i]

            # Nxjerr fuqinë e frekuencave të ndryshme
            freqs = np.fft.fftfreq(len(channel_data), 1/self.sampling_rate)
            fft_result = np.fft.fft(channel_data)
            power_spectrum = np.abs(fft_result) ** 2

            # Kontrollo coupling midis brezave të ndryshëm
            alpha_power = np.sum(power_spectrum[(freqs >= 8) & (freqs <= 12)])
            gamma_power = np.sum(power_spectrum[(freqs >= 30) & (freqs <= 50)])

            if alpha_power > 0:
                coupling_ratio = gamma_power / alpha_power
                coupling_scores.append(coupling_ratio)

        avg_coupling = np.mean(coupling_scores) if coupling_scores else 0
        confidence = min(avg_coupling / 0.5, 1.0)  # Normalize

        return {
            'pattern_id': f'coupling_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'pattern_type': 'cross_frequency_coupling',
            'confidence': float(confidence),
            'coupling_score': float(avg_coupling),
            'channels_analyzed': len(channels),
            'metadata': {
                'coupling_type': 'alpha_gamma',
                'coupling_strength': 'strong' if confidence > 0.6 else 'moderate' if confidence > 0.3 else 'weak'
            }
        }

    async def _coherence_analysis(self, data: np.ndarray, channels: List[str]) -> Dict[str, Any]:
        """🌊 Analiza e coherence-s midis kanaleve"""
        coherence_matrix = np.zeros((len(channels), len(channels)))

        for i in range(len(channels)):
            for j in range(len(channels)):
                if i < data.shape[1] and j < data.shape[1]:
                    # Llogarit coherence midis kanaleve
                    segment_length = min(256, len(data[:, i]), len(data[:, j]))
                    if segment_length < 8:
                        coherence_matrix[i, j] = 0.0
                        continue

                    f, Cxy = scipy.signal.coherence(
                        data[:, i],
                        data[:, j],
                        fs=self.sampling_rate,
                        nperseg=segment_length
                    )
                    # Merr coherence mesataren në brezin 1-50 Hz
                    freq_mask = (f >= 1) & (f <= 50)
                    coherence_matrix[i, j] = np.mean(Cxy[freq_mask]) if np.any(freq_mask) else 0.0

        # Statistika të coherence
        upper_triangle = coherence_matrix[np.triu_indices_from(coherence_matrix, k=1)]
        avg_coherence = np.mean(upper_triangle) if upper_triangle.size > 0 else 0.0
        max_coherence = np.max(coherence_matrix)

        return {
            'coherence_matrix': coherence_matrix.tolist(),
            'average_coherence': float(avg_coherence),
            'max_coherence': float(max_coherence),
            'coherence_quality': 'excellent' if avg_coherence > 0.8 else 'good' if avg_coherence > 0.6 else 'moderate',
            'channel_names': channels
        }

    async def _interpret_brain_state(self, freq_analysis: Dict, pattern_detection: Dict) -> Dict[str, Any]:
        """🧠 Interpreton gjendjen e trurit"""
        brainwave_type = freq_analysis.get('brainwave_type', 'unknown')
        dominant_freq = freq_analysis.get('dominant_frequency', 0)
        pattern_count = pattern_detection.get('pattern_count', 0)

        # Përcakto gjendjen bazuar në frekuencën dominante
        if brainwave_type == 'delta':
            state_name = "Deep Sleep"
            state_description = "Gjumë i thellë, riparimi neural aktiv"
            consciousness_level = 0.1
        elif brainwave_type == 'theta':
            state_name = "Deep Meditation"
            state_description = "Meditim i thellë, kreativitet, ëndrra"
            consciousness_level = 0.3
        elif brainwave_type == 'alpha':
            state_name = "Relaxed Awareness"
            state_description = "Relaksim aktiv, reflektim, qetësi"
            consciousness_level = 0.6
        elif brainwave_type == 'beta':
            state_name = "Active Focus"
            state_description = "Vëmendje aktive, procesim kognitiv"
            consciousness_level = 0.8
        elif brainwave_type == 'gamma':
            state_name = "Peak Consciousness"
            state_description = "Përqendrim maksimal, vetëdijtligi i lartë"
            consciousness_level = 1.0
        else:
            state_name = "Unknown State"
            state_description = "Gjendje e paqartë e trurit"
            consciousness_level = 0.5

        # Modifiko bazuar në pattern-et
        if pattern_count > 2:
            consciousness_level = min(consciousness_level + 0.1, 1.0)
            state_description += " (pattern-e komplekse të dukshëm)"

        return {
            'state_name': state_name,
            'state_description': state_description,
            'consciousness_level': consciousness_level,
            'dominant_brainwave': brainwave_type,
            'dominant_frequency_hz': dominant_freq,
            'neural_complexity': pattern_count,
            'interpretation_confidence': 0.85 if pattern_count > 0 else 0.7,
            'recommended_audio_synthesis': await self._recommend_audio_parameters(brainwave_type, consciousness_level)
        }

    async def _recommend_audio_parameters(self, brainwave_type: str, consciousness_level: float) -> Dict[str, Any]:
        """🎵 Rekomandon parametrat për sintezën audio"""
        base_frequencies = {
            'delta': 2.0,
            'theta': 6.0,
            'alpha': 10.0,
            'beta': 20.0,
            'gamma': 40.0
        }

        base_freq = base_frequencies.get(brainwave_type, 10.0)

        return {
            'base_frequency': base_freq,
            'amplitude': consciousness_level * 0.8,
            'harmonics': [base_freq * 2, base_freq * 3, base_freq * 4],
            'modulation_rate': consciousness_level * 2.0,
            'reverb_level': (1.0 - consciousness_level) * 0.5,
            'synthesis_mode': 'binaural' if consciousness_level > 0.7 else 'monaural'
        }

    async def _calculate_quality_metrics(self, data: np.ndarray) -> Dict[str, Any]:
        """📈 Llogarit metrikat e cilësisë së procesimit"""
        signal_to_noise = []

        for i in range(data.shape[1]):
            channel_data = data[:, i]

            # Simpel SNR calculation
            signal_power = np.var(channel_data)
            # Noise estimation nga frekuencat e larta
            high_freq_noise = np.var(np.diff(channel_data))

            if high_freq_noise > 0:
                snr = 10 * np.log10(signal_power / high_freq_noise)
                signal_to_noise.append(snr)

        avg_snr = np.mean(signal_to_noise) if signal_to_noise else 0

        # Cilësia e përgjithshme
        if avg_snr > 20:
            quality = ProcessingQuality.EXCELLENT
        elif avg_snr > 15:
            quality = ProcessingQuality.GOOD
        elif avg_snr > 10:
            quality = ProcessingQuality.MODERATE
        else:
            quality = ProcessingQuality.POOR

        channel_variances = np.var(data, axis=0)
        mean_channel_variance = np.mean(channel_variances)
        channel_balance = 1.0 - np.std(channel_variances) / mean_channel_variance if mean_channel_variance > 0 else 0.0

        return {
            'signal_to_noise_db': float(avg_snr),
            'processing_quality': quality.value,
            'data_integrity': 1.0 - (np.sum(np.isnan(data)) / data.size),
            'temporal_stability': float(1.0 / (1.0 + np.std(np.diff(np.mean(data, axis=1))))),
            'channel_balance': float(channel_balance)
        }

    async def _prepare_for_synthesis(self, freq_analysis: Dict, brain_state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """🎼 Përgatit të dhënat për sintezën audio nga JONA"""
        if brain_state is None:
            brain_state = {}

        return {
            'synthesis_ready': True,
            'recommended_synthesis_params': brain_state.get('recommended_audio_synthesis', {}),
            'dominant_frequency': freq_analysis.get('dominant_frequency', 10.0),
            'brainwave_type': freq_analysis.get('brainwave_type', 'alpha'),
            'spectral_features': {
                'centroid': freq_analysis.get('spectral_centroid', 10.0),
                'bandwidth': freq_analysis.get('dominant_power', 1.0),
                'rolloff': freq_analysis.get('dominant_frequency', 10.0) * 1.5
            }
        }

    async def _generate_neural_insights(self, brain_state: Dict, pattern_detection: Dict) -> List[str]:
        """✨ Gjeneron insights nga analiza neurale - ALBI wisdom"""
        insights = []

        state_name = brain_state.get('state_name', 'Unknown')
        consciousness_level = brain_state.get('consciousness_level', 0.5)
        pattern_count = pattern_detection.get('pattern_count', 0)

        # Insight për gjendjen
        if consciousness_level > 0.8:
            insights.append(f"🌟 Excellent neural activity detected! {state_name} indicates peak cognitive performance.")
        elif consciousness_level > 0.6:
            insights.append(f"😊 Good mental state: {state_name} suggests balanced cognitive function.")
        else:
            insights.append(f"🧘 Relaxed state: {state_name} indicates rest or meditative condition.")

        # Insight për pattern-et
        if pattern_count > 3:
            insights.append("🧠 Rich neural patterns detected - complex cognitive processing is active!")
        elif pattern_count > 1:
            insights.append("🔍 Moderate neural complexity - focused mental activity present.")
        else:
            insights.append("🌊 Simple neural patterns - calm, unified brain activity.")

        # Insight për rritjen e ALBI
        total_patterns = len(self.learned_patterns)
        if total_patterns > 100:
            insights.append(f"🚀 ALBI has learned {total_patterns} neural patterns! Intelligence rapidly expanding!")
        elif total_patterns > 10:
            insights.append(f"📈 ALBI growing steadily with {total_patterns} learned patterns.")

        # Rekomandim
        brainwave = brain_state.get('dominant_brainwave', 'alpha')
        if brainwave == 'gamma':
            insights.append("💫 Recommendation: This is perfect for learning and creativity!")
        elif brainwave == 'alpha':
            insights.append("🎯 Recommendation: Ideal state for meditation and reflection.")
        elif brainwave == 'beta':
            insights.append("⚡ Recommendation: Great for problem-solving and focused work.")

        return insights

    def get_processing_statistics(self) -> Dict[str, Any]:
        """📊 Kthen statistikat e procesimit"""
        if not self.processing_history:
            return {'status': 'No processing history available'}

        # Analizo historinë e procesimit
        processing_times = [record['duration_ms'] for record in self.processing_history]
        frequencies = [record['dominant_frequency'] for record in self.processing_history]
        states = [record['brain_state'] for record in self.processing_history]

        avg_time_ms = float(np.mean(processing_times)) if processing_times else 0.0
        avg_time_s = avg_time_ms / 1000.0
        throughput_sessions_per_second = (1.0 / avg_time_s) if avg_time_s > 0 else 0.0

        return {
            'total_sessions_processed': len(self.processing_history),
            'average_processing_time_ms': avg_time_ms,
            'fastest_processing_ms': float(np.min(processing_times)),
            'slowest_processing_ms': float(np.max(processing_times)),
            'average_frequency_hz': float(np.mean(frequencies)),
            'most_common_brain_state': max(set(states), key=states.count) if states else 'unknown',
            'learned_patterns': len(self.learned_patterns),
            'channels_configured': len(self.channels),
            'processing_efficiency_sessions_per_second': throughput_sessions_per_second,
            'processing_efficiency': throughput_sessions_per_second
        }


# Factory function
def get_neural_processor() -> ALBINeuralProcessor:
    """Factory për neural processor"""
    return ALBINeuralProcessor()


if __name__ == "__main__":
    # Test i shpejtë
    async def test_neural_processor():
        print("🧠 Testing ALBI Neural Processor...")

        processor = get_neural_processor()

        # Gjenero të dhëna EEG test
        duration = 2.0  # 2 sekonda
        samples = int(duration * processor.sampling_rate)
        channels = 4

        # Simulim i sinjalit EEG
        t = np.linspace(0, duration, samples)
        eeg_data = np.zeros((samples, channels))

        for i in range(channels):
            # Kombinim i disa frekuencave
            alpha_wave = np.sin(2 * np.pi * 10 * t) * 0.5  # 10 Hz alpha
            beta_wave = np.sin(2 * np.pi * 20 * t) * 0.3   # 20 Hz beta
            noise = np.random.normal(0, 0.1, samples)

            eeg_data[:, i] = alpha_wave + beta_wave + noise

        # Processo sinjalet
        result = await processor.process_eeg_signal(eeg_data, ['Fp1', 'Fp2', 'C3', 'C4'])

        # Shfaq rezultatet
        print(f"Brain State: {result['brain_state']['state_name']}")
        print(f"Dominant Frequency: {result['frequency_analysis']['dominant_frequency']:.1f} Hz")
        print(f"Patterns Detected: {result['pattern_detection']['pattern_count']}")
        print(f"Processing Time: {result['processing_time_ms']:.1f} ms")
        print(f"Insights: {result['albi_insights']}")

        # Statistikat
        stats = processor.get_processing_statistics()
        print(f"\nStatistics: {stats}")

    asyncio.run(test_neural_processor())


