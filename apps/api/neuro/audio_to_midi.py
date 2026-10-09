"""
Audio to MIDI Converter - REAL pitch detection and note extraction
NO MOCK - uses librosa onset/pitch detection
"""

import logging
from typing import Dict, Any
import numpy as np

try:
    import librosa
    HAS_LIBROSA = True
except ImportError:
    HAS_LIBROSA = False

try:
    from midiutil import MIDIFile
    HAS_MIDIUTIL = True
except ImportError:
    HAS_MIDIUTIL = False

logger = logging.getLogger(__name__)


class AudioToMidi:
    """Convert audio to MIDI using REAL pitch detection"""
    
    def __init__(self):
        self.sample_rate = 22050
    
    def convert(self, audio_path: str, midi_path: str) -> str:
        """
        Convert audio file to MIDI
        Returns: path to generated MIDI file
        """
        if not HAS_LIBROSA:
            raise ImportError("librosa not installed")
        if not HAS_MIDIUTIL:
            raise ImportError("midiutil not installed - pip install MIDIUtil")
        
        try:
            # 1. Load audio
            y, sr = librosa.load(audio_path, sr=self.sample_rate)
            
            # 2. REAL pitch detection using librosa
            pitches, magnitudes = librosa.piptrack(y=y, sr=sr, fmin=50, fmax=2000)
            
            # 3. Extract notes from pitches
            notes = []
            hop_length = 512
            time_step = hop_length / sr
            
            for t in range(pitches.shape[1]):
                # Get pitch with highest magnitude at this time
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                magnitude = magnitudes[index, t]
                
                if pitch > 0 and magnitude > 0.1:  # Threshold for note detection
                    midi_note = self._hz_to_midi(pitch)
                    velocity = int(min(127, magnitude * 127))
                    time = t * time_step
                    notes.append({
                        'midi_note': midi_note,
                        'time': time,
                        'velocity': velocity
                    })
            
            # 4. Group consecutive same notes into longer notes
            grouped_notes = self._group_notes(notes, time_step)
            
            # 5. REAL tempo detection
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            tempo = float(tempo)
            
            # 6. Create MIDI file
            midi = MIDIFile(1)  # 1 track
            track = 0
            channel = 0
            midi.addTempo(track, 0, tempo)
            midi.addTrackName(track, 0, "Converted Audio")
            
            # Add notes to MIDI
            for note in grouped_notes:
                midi.addNote(
                    track=track,
                    channel=channel,
                    pitch=note['midi_note'],
                    time=note['time'],
                    duration=note['duration'],
                    volume=note['velocity']
                )
            
            # 7. Write MIDI file
            with open(midi_path, 'wb') as f:
                midi.writeFile(f)
            
            logger.info(f"Converted {len(grouped_notes)} notes to MIDI at {tempo:.1f} BPM")
            
            return midi_path
            
        except Exception as e:
            logger.error(f"Audio to MIDI conversion error: {e}")
            raise
    
    def _hz_to_midi(self, frequency: float) -> int:
        """Convert frequency (Hz) to MIDI note number"""
        # MIDI note = 69 + 12 * log2(f / 440)
        # 69 = A4 (440 Hz)
        if frequency <= 0:
            return 0
        
        midi_note = 69 + 12 * np.log2(frequency / 440.0)
        return int(round(midi_note))
    
    def _group_notes(self, notes: list, time_step: float) -> list:
        """Group consecutive identical notes into longer notes"""
        if not notes:
            return []
        
        grouped = []
        current_note = notes[0].copy()
        current_note['duration'] = time_step
        
        for i in range(1, len(notes)):
            note = notes[i]
            
            # If same note and close in time, extend duration
            if (note['midi_note'] == current_note['midi_note'] and
                abs(note['time'] - (current_note['time'] + current_note['duration'])) < time_step * 2):
                current_note['duration'] += time_step
            else:
                # Save current note and start new one
                grouped.append(current_note)
                current_note = note.copy()
                current_note['duration'] = time_step
        
        # Add last note
        grouped.append(current_note)
        
        return grouped
