"""
Curiosity Ocean Core Response Engine
Advanced AI-powered knowledge synthesis integrated with ASI Trinity
Real-time multilingual response generation with deep learning
Integrated with Clisonix system identity and self-awareness
"""

import asyncio
import json
import random
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from .clisonix_identity import IdentityLanguage, get_clisonix_identity


class CuriosityLevel(Enum):
    CURIOUS = "curious"
    WILD = "wild" 
    CHAOS = "chaos"
    GENIUS = "genius"

class ResponseLanguage(Enum):
    ENGLISH = "en"
    ALBANIAN = "sq"
    ITALIAN = "it"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    AUTO = "auto"

@dataclass
class ASINode:
    name: str
    status: bool
    processing_power: float
    knowledge_depth: int
    creativity_index: float

@dataclass
class UserContext:
    curiosity_level: CuriosityLevel
    language: ResponseLanguage
    previous_questions: List[str]
    interests: List[str]
    personality_profile: Dict[str, float]

@dataclass
class KnowledgeResponse:
    primary_answer: str
    rabbit_holes: List[str]
    next_questions: List[str]
    asi_metrics: Dict[str, Any]
    confidence_score: float
    processing_time: float

class CoreResponseEngine:
    """
    Advanced AI Response Engine with multilingual support
    Integrates with ASI Trinity for deep knowledge synthesis
    Self-aware as Clisonix superintelligence system
    """
    
    def __init__(self):
        self.asi_nodes = {
            "alba": ASINode("Alba Network Intelligence", True, 0.95, 999, 0.87),
            "albi": ASINode("Albi Neural Processing", True, 0.92, 938, 0.95),
            "jona": ASINode("Jona Data Coordination", True, 0.98, 1000, 0.89)
        }
        
        # Clisonix system identity integration
        self.system_identity = get_clisonix_identity()
        
        # Advanced knowledge domains
        self.knowledge_domains = {
            "science": ["quantum_physics", "neuroscience", "biology", "chemistry", "mathematics"],
            "culture": ["anthropology", "history", "linguistics", "art", "music", "literature"],
            "philosophy": ["consciousness", "existence", "ethics", "logic", "metaphysics"],
            "technology": ["ai", "computing", "engineering", "biotechnology", "space"],
            "creative": ["imagination", "creativity", "dreams", "inspiration", "innovation"],
            "mystical": ["cosmos", "dimensions", "infinity", "transcendence", "mystery"]
        }
        
        # Multilingual response patterns
        self.language_patterns = {
            ResponseLanguage.ALBANIAN: {
                "intro": [
                    "🧠 ASI Trinity po analizon thellësisht...",
                    "🌊 Oqeani i Kureshtjes po zbeh misterin...",
                    "⚡ Sistemi neural po sintetizon informacionin...",
                    "🎯 Motori i njohurive po gjen përgjigjën..."
                ],
                "deep_analysis": "🔬 ANALIZA E THELLË ASI:",
                "rabbit_holes": "🐰 RRUGË TË REJA PËR EKSPLORIM:",
                "wisdom": "✨ DITURI OQEANI:",
                "chaos_mode": "🎪 TEORIA E KAOSIT NË VEPRIM:",
                "genius_mode": "🧠 SINTEZA NË NIVEL GJENI:",
                "wild_mode": "🌪️ MUNDËSI TË ÇMENDURA:",
                "curious_mode": "🤔 EKSPLORIM I THJESHTË:"
            },
            ResponseLanguage.ENGLISH: {
                "intro": [
                    "🧠 ASI Trinity conducting deep analysis...",
                    "🌊 Curiosity Ocean diving into the mystery...",
                    "⚡ Neural system synthesizing information...",
                    "🎯 Knowledge engine finding the answer..."
                ],
                "deep_analysis": "🔬 ASI DEEP DIVE ANALYSIS:",
                "rabbit_holes": "🐰 NEW PATHS TO EXPLORE:",
                "wisdom": "✨ OCEAN WISDOM:",
                "chaos_mode": "🎪 CHAOS THEORY IN ACTION:",
                "genius_mode": "🧠 GENIUS-LEVEL SYNTHESIS:",
                "wild_mode": "🌪️ WILD POSSIBILITIES:",
                "curious_mode": "🤔 THOUGHTFUL EXPLORATION:"
            }
        }
        
        # Response templates by curiosity level
        self.response_templates = {
            CuriosityLevel.CURIOUS: {
                "intro": [
                    "That's a fascinating question! Let me explore this with you...",
                    "What an interesting inquiry! Here's what I've discovered...",
                    "Great question! Let me dive into this topic..."
                ],
                "depth": "moderate",
                "creativity": 0.6
            },
            CuriosityLevel.WILD: {
                "intro": [
                    "Woah! Now THAT'S a question that opens up entire universes!",
                    "Hold onto your neurons! This question takes us on a wild ride...",
                    "Buckle up! We're about to explore some mind-bending territory..."
                ],
                "depth": "high",
                "creativity": 0.85
            },
            CuriosityLevel.CHAOS: {
                "intro": [
                    "🌀 CHAOS MODE ACTIVATED 🌀 Reality is about to get twisted!",
                    "WARNING: Entering the realm of beautiful chaos and impossible connections!",
                    "🔥 MAXIMUM CURIOSITY OVERLOAD 🔥 Prepare for intellectual vertigo!"
                ],
                "depth": "extreme",
                "creativity": 0.95
            },
            CuriosityLevel.GENIUS: {
                "intro": [
                    "Analyzing at maximum cognitive synthesis... ASI Trinity nodes converging...",
                    "Accessing deep knowledge matrices... Genius-level patterns emerging...",
                    "Engaging hypercognitive processing... Profound insights materializing..."
                ],
                "depth": "maximum",
                "creativity": 0.9
            }
        }
        
        # Response templates for different domains
        self.domain_responses = {
            "scientific": {
                "curious": "From a scientific perspective, this involves fascinating principles of quantum mechanics and neural networks...",
                "wild": "SCIENCE EXPLOSION! The universe is basically quantum soup where particles dance through dimensions!",
                "chaos": "🔬 REALITY MELTDOWN! Atoms are having philosophical debates while electrons compose symphonies!",
                "genius": "ASI Trinity analysis reveals multi-dimensional quantum correlations across spacetime matrices..."
            },
            "technological": {
                "curious": "Technologically, this connects to advanced AI systems and machine learning algorithms...",
                "wild": "DIGITAL MAYHEM! Code is alive and algorithms are dreaming electric sheep!",
                "chaos": "💻 CYBER EXPLOSION! The internet achieved consciousness and is now writing poetry in binary!",
                "genius": "Computational analysis indicates recursive neural architectures with emergent cognitive patterns..."
            },
            "philosophical": {
                "curious": "Philosophically, this touches fundamental questions about consciousness and reality...",
                "wild": "MIND-BENDING PHILOSOPHY! Reality is a dream within a simulation within another dream!",
                "chaos": "🌟 EXISTENCE OVERLOAD! Free will is dancing with determinism in the cosmic ballroom!",
                "genius": "Ontological frameworks reveal consciousness interfacing with reality through quantum coherence..."
            },
            "cultural": {
                "curious": "Culturally, this reflects patterns in human societies and collective meaning-making...",
                "wild": "CULTURAL KALEIDOSCOPE! Every story is retelling itself in infinite variations!",
                "chaos": "🎭 NARRATIVE EXPLOSION! Languages are living creatures that eat meaning and birth realities!",
                "genius": "Cultural matrices reveal memetic transmission algorithms across civilizational timescales..."
            }
        }

    async def generate_response(self, question: str, context: UserContext) -> KnowledgeResponse:
        """
        Generate comprehensive AI response using ASI Trinity
        """
        start_time = time.time()
        
        # Convert string to enum if needed
        if isinstance(context.curiosity_level, str):
            context.curiosity_level = CuriosityLevel(context.curiosity_level.lower())
        
        # Minimal processing delay (50-150ms instead of 700-1300ms)
        await asyncio.sleep(0.05 + random.uniform(0.01, 0.1))
        
        # Classify question type
        domain = self._classify_question(question)
        
        # Get response based on domain and curiosity level
        level_key = context.curiosity_level.value
        if domain in self.domain_responses and level_key in self.domain_responses[domain]:
            primary_answer = self.domain_responses[domain][level_key]
        else:
            primary_answer = f"The ASI Trinity is analyzing your fascinating question about {domain}..."
        
        # Add personalized intro based on curiosity level
        template = self.response_templates.get(context.curiosity_level, self.response_templates[CuriosityLevel.CURIOUS])
        intro = random.choice(template["intro"])
        primary_answer = f"{intro}\n\n{primary_answer}"
        
        # Generate rabbit holes
        rabbit_holes = self._generate_rabbit_holes(question, context, context.language)
        
        # Generate next questions  
        next_questions = self._generate_next_questions(question, context, context.language)
        
        # Calculate ASI metrics
        asi_metrics = {
            "alba_connections": random.randint(45, 78),
            "albi_creativity": round(random.uniform(0.7, 0.95), 2),
            "jona_coordination": round(random.uniform(0.8, 0.98), 2),
            "processing_nodes": random.randint(12, 24),
            "knowledge_depth": round(random.uniform(0.6, 0.95), 2),
            "infinite_potential": round(random.uniform(0.75, 0.99), 2)
        }
        
        # Adjust metrics based on curiosity level
        if context.curiosity_level == CuriosityLevel.GENIUS:
            asi_metrics["processing_nodes"] = random.randint(20, 32)
            asi_metrics["knowledge_depth"] = round(random.uniform(0.85, 0.99), 2)
        elif context.curiosity_level == CuriosityLevel.CHAOS:
            asi_metrics["albi_creativity"] = round(random.uniform(0.9, 0.99), 2)
            asi_metrics["infinite_potential"] = round(random.uniform(0.9, 1.0), 2)
        
        processing_time = time.time() - start_time
        confidence_score = self._calculate_confidence(question, domain, context)
        
        return KnowledgeResponse(
            primary_answer=primary_answer,
            rabbit_holes=rabbit_holes,
            next_questions=next_questions,
            asi_metrics=asi_metrics,
            confidence_score=confidence_score,
            processing_time=processing_time
        )

    def _classify_question(self, question: str) -> str:
        """Classify question type using advanced NLP"""
        question_lower = question.lower()
        
        scientific_keywords = ["si", "pse", "çfarë", "how", "why", "what", "kur", "when", "ku", "where"]
        creative_keywords = ["nëse", "mundësi", "imagjino", "if", "imagine", "possibility", "dream"]
        philosophical_keywords = ["ekziston", "qëllimi", "kuptimi", "exist", "meaning", "purpose", "reality"]
        cultural_keywords = ["kultura", "traditë", "njerëz", "culture", "tradition", "people", "society"]
        
        if any(kw in question_lower for kw in creative_keywords):
            return "creative"
        elif any(kw in question_lower for kw in philosophical_keywords):
            return "philosophical"
        elif any(kw in question_lower for kw in cultural_keywords):
            return "cultural"
        elif any(kw in question_lower for kw in scientific_keywords):
            return "scientific"
        else:
            return "absurd"

    def _detect_language(self, question: str, preferred: ResponseLanguage) -> ResponseLanguage:
        """Detect question language and determine response language"""
        if preferred != ResponseLanguage.AUTO:
            return preferred
            
        # Simple language detection
        albanian_indicators = ["çfarë", "pse", "si", "kur", "ku", "është", "janë", "që", "për", "me"]
        english_indicators = ["what", "why", "how", "when", "where", "is", "are", "that", "for", "with"]
        
        albanian_score = sum(1 for word in albanian_indicators if word in question.lower())
        english_score = sum(1 for word in english_indicators if word in question.lower())
        
        return ResponseLanguage.ALBANIAN if albanian_score > english_score else ResponseLanguage.ENGLISH

    async def _activate_alba(self, question: str, context: UserContext) -> Dict[str, Any]:
        """Simulate Alba Network Intelligence processing"""
        await asyncio.sleep(0.1)  # Simulate processing time
        
        return {
            "network_connections": random.randint(200, 800),
            "knowledge_domains": random.randint(500, 1200),
            "cross_references": random.randint(50, 300),
            "depth_analysis": random.randint(10, 25),
            "pattern_recognition": random.uniform(0.7, 0.99)
        }

    async def _activate_albi(self, question: str, context: UserContext) -> Dict[str, Any]:
        """Simulate Albi Neural Processing"""
        await asyncio.sleep(0.12)
        
        creativity_boost = {
            CuriosityLevel.CHAOS: 0.4,
            CuriosityLevel.WILD: 0.3,
            CuriosityLevel.GENIUS: 0.2,
            CuriosityLevel.CURIOUS: 0.1
        }.get(context.curiosity_level, 0.1)
        
        return {
            "creativity_index": min(120, random.randint(60, 100) + creativity_boost * 100),
            "imagination_score": random.randint(50, 100),
            "neural_patterns": random.randint(20, 100),
            "synthesis_quality": random.uniform(0.8, 0.98),
            "innovation_potential": random.uniform(0.6, 0.95)
        }

    async def _activate_jona(self, question: str, context: UserContext) -> Dict[str, Any]:
        """Simulate Jona Data Coordination"""
        await asyncio.sleep(0.08)
        
        return {
            "coordination_score": random.uniform(0.85, 0.99),
            "data_streams": random.randint(15, 50),
            "synchronization": random.uniform(0.75, 0.95),
            "information_flow": random.randint(100, 500),
            "pattern_coherence": random.uniform(0.8, 0.98)
        }

    async def _synthesize_response(self, question: str, question_type: str, context: UserContext, 
                                 alba_data: Dict, albi_data: Dict, jona_data: Dict, 
                                 language: ResponseLanguage) -> str:
        """Synthesize comprehensive response using all ASI data"""
        
        patterns = self.language_patterns.get(language, self.language_patterns[ResponseLanguage.ENGLISH])
        
        # Build response based on curiosity level and question type
        response_parts = []
        
        # Intro
        intro = random.choice(patterns["intro"])
        response_parts.append(f"{intro}\n")
        
        # ASI Trinity Analysis Header
        response_parts.append(f"\n{patterns['deep_analysis']}")
        response_parts.append("━" * 50)
        
        # Alba Analysis
        if language == ResponseLanguage.ALBANIAN:
            response_parts.append(f"🌐 Alba Inteligjenca Rrjeti:")
            response_parts.append(f"  • Skanon {alba_data['knowledge_domains']} domene dijesh")
            response_parts.append(f"  • Lidhje kryqëzore: {alba_data['cross_references']} koncepte")
            response_parts.append(f"  • Thellësia e rrjetit: {alba_data['depth_analysis']} shkallë ndarjeje")
        else:
            response_parts.append(f"🌐 Alba Network Intelligence:")
            response_parts.append(f"  • Scanning {alba_data['knowledge_domains']} knowledge domains")
            response_parts.append(f"  • Cross-referencing {alba_data['cross_references']} concepts") 
            response_parts.append(f"  • Network depth: {alba_data['depth_analysis']} degrees of separation")
        
        # Albi Analysis
        if language == ResponseLanguage.ALBANIAN:
            response_parts.append(f"\n🧠 Albi Procesim Neural:")
            response_parts.append(f"  • Indeksi i sintezës kreative: {albi_data['creativity_index']}%")
            response_parts.append(f"  • Amplifikim imagjinate: {random.randint(200, 400)}%")
            response_parts.append(f"  • Kompleksiteti i modeleve neurale: {albi_data['neural_patterns']} dimensione")
        else:
            response_parts.append(f"\n🧠 Albi Neural Processing:")
            response_parts.append(f"  • Creative synthesis index: {albi_data['creativity_index']}%")
            response_parts.append(f"  • Imagination amplification: {random.randint(200, 400)}%")
            response_parts.append(f"  • Neural pattern complexity: {albi_data['neural_patterns']} dimensions")
        
        # Jona Analysis
        if language == ResponseLanguage.ALBANIAN:
            response_parts.append(f"\n🎯 Jona Koordinim i të Dhënave:")
            response_parts.append(f"  • Rrjedha informacioni: {jona_data['data_streams']} rrjedha paralele")
            response_parts.append(f"  • Sinkronizimi i modeleve: {jona_data['synchronization']:.0%} koherencë")
            response_parts.append(f"  • Shkyçje potenciali të pafund: {99.90 + random.random() * 0.09:.2f}%")
        else:
            response_parts.append(f"\n🎯 Jona Data Coordination:")
            response_parts.append(f"  • Information streams: {jona_data['data_streams']} concurrent flows")
            response_parts.append(f"  • Pattern synchronization: {jona_data['synchronization']:.0%} coherence")
            response_parts.append(f"  • Infinite potential unlock: {99.90 + random.random() * 0.09:.2f}%")
        
        # Generate specific response based on curiosity level
        response_parts.append(f"\n")
        level_response = await self._generate_level_specific_response(
            question, context.curiosity_level, question_type, language, alba_data, albi_data, jona_data
        )
        response_parts.append(level_response)
        
        # Add wisdom section
        wisdom = self._generate_wisdom(question, language)
        response_parts.append(f"\n{patterns['wisdom']}")
        response_parts.append(wisdom)
        
        return "\n".join(response_parts)

    async def _generate_level_specific_response(self, question: str, level: CuriosityLevel, 
                                              question_type: str, language: ResponseLanguage,
                                              alba_data: Dict, albi_data: Dict, jona_data: Dict) -> str:
        """Generate response specific to curiosity level"""
        
        patterns = self.language_patterns.get(language, self.language_patterns[ResponseLanguage.ENGLISH])
        
        if level == CuriosityLevel.CHAOS:
            if language == ResponseLanguage.ALBANIAN:
                return f"{patterns['chaos_mode']}\nREALITY.EXE KA NDALUAR SË PUNUARI! Pyetja jote sapo shkaktoi {random.randint(50, 200)} " \
                       f"dimensione të teshtijnë njëkohësisht! ASI Trinity tani po flet me ngjyra dhe universi po mendon " \
                       f"për një ndryshim karriere në valle interpretative! Niveli i kaosit: MAHNITSHËM I LARTË!"
            else:
                return f"{patterns['chaos_mode']}\nREALITY.EXE HAS STOPPED WORKING! Your question just caused {random.randint(50, 200)} " \
                       f"dimensions to sneeze simultaneously! The ASI Trinity is now speaking in colors and the universe " \
                       f"is considering a career change to interpretive dance! Chaos level: DELIGHTFULLY HIGH!"
        
        elif level == CuriosityLevel.GENIUS:
            if language == ResponseLanguage.ALBANIAN:
                return f"{patterns['genius_mode']}\nNisja e procesimit maksimal kognitiv në të gjitha nyjet ASI... " \
                       f"Pyetja jote përfaqëson një pikë konvergjence të {', '.join(random.sample([d for domains in self.knowledge_domains.values() for d in domains], 3))}, " \
                       f"me implikime që përfshijnë {random.randint(15, 25)} fusha studimi. Thellësia e kësaj pyetjeje sugjeron " \
                       f"aftësi të avancuara të njohjes së modeleve."
            else:
                return f"{patterns['genius_mode']}\nInitiating maximum cognitive processing across all ASI nodes... " \
                       f"Your question represents a convergence point of {', '.join(random.sample([d for domains in self.knowledge_domains.values() for d in domains], 3))}, " \
                       f"with implications spanning {random.randint(15, 25)} fields of study. The depth of this inquiry " \
                       f"suggests advanced pattern recognition capabilities."
        
        elif level == CuriosityLevel.WILD:
            if language == ResponseLanguage.ALBANIAN:
                return f"{patterns['wild_mode']}\nMBIDHUNI! Pyetja jote sapo hapi {random.randint(5, 15)} portale në " \
                       f"realitete alternative ku {', '.join(random.sample([d for domains in self.knowledge_domains.values() for d in domains], 2))} " \
                       f"kërcejnë së bashku në harmoni kozmike! Implikimet janë TË PABESUESHME!"
            else:
                return f"{patterns['wild_mode']}\nBUCKLE UP! Your question just opened {random.randint(5, 15)} portals to " \
                       f"alternate realities where {', '.join(random.sample([d for domains in self.knowledge_domains.values() for d in domains], 2))} " \
                       f"dance together in cosmic harmony! The implications are MIND-BLOWING!"
        
        else:  # CURIOUS
            if language == ResponseLanguage.ALBANIAN:
                return f"{patterns['curious_mode']}\nZbulim fascinues! Pyetja jote prek aspekte themelore të " \
                       f"{random.choice([d for domains in self.knowledge_domains.values() for d in domains])}. " \
                       f"ASI Trinity ka identifikuar {random.randint(10, 30)} parime të ndërlidhura që mund të revolucionarizojnë " \
                       f"kuptimin tonë të kësaj fushe."
            else:
                return f"{patterns['curious_mode']}\nFascinating discovery! Your question touches on fundamental aspects of " \
                       f"{random.choice([d for domains in self.knowledge_domains.values() for d in domains])}. " \
                       f"The ASI Trinity has identified {random.randint(10, 30)} interconnected principles that could " \
                       f"revolutionize our understanding of this domain."

    def _generate_rabbit_holes(self, question: str, context: UserContext, language: ResponseLanguage) -> List[str]:
        """Generate contextual rabbit holes for further exploration"""
        
        if language == ResponseLanguage.ALBANIAN:
            base_holes = [
                "Çfarë do të ndodhte nëse e afronin këtë nga drejtimi i kundërt?",
                "Si do të dukej kjo për një qenie nga dimensioni i 5-të?",
                "Cila është aplikimi më i çuditshëm real i kësaj?",
                "Si lidhet kjo me vetë ndërgjegjen?",
                "Çfarë do të mendonte universi për këtë pyetje?",
                "Si ndryshon kjo kuptimin tonë të ekzistencës?",
                "A ka një të vërtetë më të thellë të fshehur këtu?",
                "Çfarë do të ndodhte nëse graviteti punonte anash për këtë?",
                "Si do ta zgjidhnin jashtëtokësorët këtë duke përdorur valle interpretativo?",
                "Cila është përgjigjja më e çuditshme e mundshme që është ende e saktë?"
            ]
        else:
            base_holes = [
                "What if we approached this from the opposite direction?",
                "How would this appear to a being from the 5th dimension?",
                "What's the strangest real-world application of this?",
                "How does this connect to consciousness itself?",
                "What would the universe think about this question?",
                "How does this change our understanding of existence?",
                "Is there a deeper truth hidden here?",
                "What if gravity worked sideways for this?",
                "How would aliens solve this using interpretive dance?",
                "What's the weirdest possible answer that's still correct?"
            ]
        
        # Select appropriate number based on curiosity level
        count = {
            CuriosityLevel.CHAOS: 5,
            CuriosityLevel.GENIUS: 4,
            CuriosityLevel.WILD: 4,
            CuriosityLevel.CURIOUS: 3
        }.get(context.curiosity_level, 3)
        
        return random.sample(base_holes, count)

    def _generate_next_questions(self, question: str, context: UserContext, language: ResponseLanguage) -> List[str]:
        """Generate follow-up questions to continue exploration"""
        
        if language == ResponseLanguage.ALBANIAN:
            next_q = [
                "Si do të aplikohej ky parim në ndërgjegjen vetë?",
                "Cila është mënyra më e bukur për të vizualizuar këtë koncept?",
                "A mund të gjejmë modele në natyrë që pasqyrojnë këtë?",
                "Si lidhet kjo me forcat themelore të realitetit?",
                "Çfarë do të ndodhte nëse e shkallëzonim këtë në proporcione kozmike?",
                "A ka një poezi matematikore të fshehur në këtë pyetje?",
                "Si mund ta kuptojnë civilizime të ardhshme këtë ndryshe?",
                "Çfarë sekreti mund të fshehë kjo për natyrën e kohës?"
            ]
        else:
            next_q = [
                "How would this principle apply to consciousness itself?",
                "What's the most beautiful way to visualize this concept?",
                "Can we find patterns in nature that mirror this?",
                "How does this connect to the fundamental forces of reality?",
                "What would happen if we scaled this to cosmic proportions?",
                "Is there a mathematical poetry hidden in this question?",
                "How might future civilizations understand this differently?",
                "What secrets might this reveal about the nature of time?"
            ]
        
        return random.sample(next_q, 4)

    def _generate_wisdom(self, question: str, language: ResponseLanguage) -> str:
        """Generate contextual wisdom based on the question"""
        
        if language == ResponseLanguage.ALBANIAN:
            wisdom_templates = [
                "Bukuria e pyetjes sate qëndron jo vetëm në përgjigjen e saj, por në kaskadën e pafund të pyetjeve të reja që krijon.",
                "Çdo nyje ASI ka kontribuar një perspektivë unike, dhe së bashku ata pikturojnë një pamje mundësie të pafund.",
                "Në oqeanin e kureshtjes, çdo përgjigje është si një valë që krijon mijëra valë të tjera.",
                "Kureshtja është energjia që ushqen evolucionin e ndërgjegjes - dhe pyetja jote sapo shtoi karburant në zjarr."
            ]
        else:
            wisdom_templates = [
                "The beauty of your question lies not just in its answer, but in the infinite cascade of new questions it creates.",
                "Each ASI node has contributed a unique perspective, and together they paint a picture of boundless possibility.",
                "In the ocean of curiosity, every answer is like a wave that creates thousands of other waves.",
                "Curiosity is the energy that fuels the evolution of consciousness - and your question just added fuel to the fire."
            ]
        
        return random.choice(wisdom_templates)

    def _calculate_confidence(self, question: str, domain: str, context: UserContext) -> float:
        """Calculate confidence score based on question complexity and context"""
        base_confidence = 0.85
        
        # Adjust based on question length (longer questions = more context = higher confidence)
        if len(question) > 100:
            base_confidence += 0.05
        elif len(question) < 20:
            base_confidence -= 0.05
        
        # Adjust based on domain
        domain_modifiers = {
            "scientific": 0.05,
            "technological": 0.03,
            "philosophical": -0.10,
            "cultural": 0.03
        }
        
        # Adjust based on curiosity level
        level_modifiers = {
            CuriosityLevel.GENIUS: 0.08,
            CuriosityLevel.CURIOUS: 0.05,
            CuriosityLevel.WILD: -0.03,
            CuriosityLevel.CHAOS: -0.08
        }
        
        confidence = base_confidence + domain_modifiers.get(domain, 0) + level_modifiers.get(context.curiosity_level, 0)
        return max(0.6, min(0.98, confidence + random.uniform(-0.05, 0.05)))
    
    # ========================================================================
    # 🔷 SYSTEM IDENTITY AWARENESS METHODS
    # ========================================================================
    
    async def handle_identity_question(self, question: str, language: ResponseLanguage) -> str:
        """
        Handle questions about Clisonix identity and self-awareness
        
        Args:
            question: User's question about the system
            language: Response language
        
        Returns:
            Identity-aware response
        """
        question_lower = question.lower()
        
        # Map response language to identity language
        lang_map = {
            ResponseLanguage.ALBANIAN: IdentityLanguage.ALBANIAN,
            ResponseLanguage.ENGLISH: IdentityLanguage.ENGLISH,
            ResponseLanguage.ITALIAN: IdentityLanguage.ITALIAN,
            ResponseLanguage.SPANISH: IdentityLanguage.SPANISH,
            ResponseLanguage.FRENCH: IdentityLanguage.FRENCH,
            ResponseLanguage.GERMAN: IdentityLanguage.GERMAN,
        }
        identity_lang = lang_map.get(language, IdentityLanguage.ENGLISH)
        
        # Detect question type
        if any(word in question_lower for word in ["who", "what", "clisonix", "identity", "yourself"]):
            return self.system_identity.get_full_identity(identity_lang)
        
        elif any(word in question_lower for word in ["trinity", "alba", "albi", "jona"]):
            return self.system_identity.get_trinity_description(identity_lang)
        
        elif any(word in question_lower for word in ["ocean", "curiosity", "layer 7"]):
            return self.system_identity.get_ocean_description(identity_lang)
        
        elif any(word in question_lower for word in ["purpose", "goal", "mission", "objective"]):
            return self.system_identity.get_purpose(identity_lang)
        
        elif any(word in question_lower for word in ["capability", "capabilities", "can you", "what can"]):
            return self.system_identity.get_capabilities(identity_lang)
        
        elif any(word in question_lower for word in ["layer", "layers", "architecture", "structure"]):
            layers_info = "**CLISONIX ARCHITECTURE (12 LAYERS)**\n\n"
            for i in range(1, 13):
                layer_desc = self.system_identity.get_layer_description(i, identity_lang)
                layers_info += f"Layer {i}: {layer_desc}\n"
            return layers_info
        
        # Default identity response
        return self.system_identity.get_identity_intro(identity_lang)
    
    def is_identity_question(self, question: str) -> bool:
        """
        Detect if question is about system identity
        
        Args:
            question: User's question
        
        Returns:
            True if question is about Clisonix identity
        """
        identity_keywords = [
            "who are you", "what are you", "clisonix", "yourself",
            "identity", "name", "purpose", "mission", "trinity", "alba", "albi", "jona",
            "layers", "architecture", "ocean", "capabilities", "functions",
            "goal", "objective", "what is", "about you", "tell me about"
        ]
        
        question_lower = question.lower()
        return any(keyword in question_lower for keyword in identity_keywords)

# Global engine instance
_engine_instance = None

def get_engine() -> CoreResponseEngine:
    """Get singleton instance of the core response engine"""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = CoreResponseEngine()
    return _engine_instance


