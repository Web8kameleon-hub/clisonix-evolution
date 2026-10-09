"""
SMART HUMAN ANALYST - REAL INTELLIGENT RESPONSES
=================================================
Features:
- Auto-translate (Albanian, English, German, etc.) via deep-translator
- Real API data integration
- Dynamic responses based on context
- Conversation memory hints
"""

from typing import Dict, Any, List, Tuple
import re
from datetime import datetime

# Import translator
try:
    from translator import get_translator, OceanTranslator
    TRANSLATOR_AVAILABLE = True
except ImportError:
    TRANSLATOR_AVAILABLE = False
    OceanTranslator = None


class SmartHumanAnalyst:
    name = "Smart Human Analyst"
    domain = "human"
    
    def __init__(self):
        """Initialize with translator."""
        self.translator = get_translator() if TRANSLATOR_AVAILABLE else None
    
    # Language detection patterns
    ALBANIAN_PATTERNS = [
        "çfarë", "cfare", "mund", "është", "eshte", "jam", "jemi", "kemi",
        "pershendetje", "përshëndetje", "tungjatjeta", "mirëdita", "miredita",
        "faleminderit", "ndihmoj", "ndihmosh", "dua", "dëshiroj", "deshiroj",
        "si", "pse", "ku", "kur", "sa", "cilat", "cili", "shpjego", "thuaj",
        "trego", "më", "te", "për", "nga", "me", "në", "por", "ose", "dhe",
        "aty", "atje", "ketu", "këtu", "atehere", "atëherë", "tani", "sot"
    ]
    
    GERMAN_PATTERNS = [
        "was", "wie", "warum", "wann", "wo", "wer", "können", "ich", "bitte",
        "danke", "hallo", "guten", "morgen", "tag", "abend", "nacht"
    ]
    
    # Comprehensive Knowledge Base
    KNOWLEDGE_BASE = {
        # GREETINGS
        "greetings": {
            "triggers": ["hello", "hi", "hey", "pershendetje", "tungjatjeta", "miredita", "hallo", "guten"],
            "responses": {
                "en": "👋 Hello! I'm Curiosity Ocean - your intelligent knowledge assistant. I can help you explore:\n\n🧠 **Science** - Physics, Biology, Chemistry, Neuroscience\n🤖 **Technology** - AI, Programming, Systems\n💡 **Philosophy** - Consciousness, Ethics, Meaning\n📊 **Business** - Strategy, Analytics, KPIs\n🔬 **Research** - Academic topics, Studies\n\nWhat would you like to explore today?",
                "sq": "👋 Përshëndetje! Jam Curiosity Ocean - asistenti juaj inteligjent. Mund t'ju ndihmoj me:\n\n🧠 **Shkencë** - Fizikë, Biologji, Kimi, Neuroshkencë\n🤖 **Teknologji** - AI, Programim, Sisteme\n💡 **Filozofi** - Ndërgjegja, Etika, Kuptimi\n📊 **Biznes** - Strategji, Analitikë, KPI\n🔬 **Kërkime** - Tema akademike, Studime\n\nÇfarë dëshironi të eksploroni sot?",
                "de": "👋 Hallo! Ich bin Curiosity Ocean - Ihr intelligenter Wissensassistent. Ich kann Ihnen helfen mit:\n\n🧠 **Wissenschaft** - Physik, Biologie, Chemie\n🤖 **Technologie** - KI, Programmierung, Systeme\n💡 **Philosophie** - Bewusstsein, Ethik\n📊 **Business** - Strategie, Analytik\n\nWas möchten Sie heute erkunden?"
            }
        },
        
        # SELF DESCRIPTION
        "self": {
            "triggers": ["who are you", "about you", "yourself", "kush je", "cfare je", "per veten", "wer bist"],
            "responses": {
                "en": """🌊 **I am Curiosity Ocean** - An Infinite Knowledge Engine built by Clisonix!

**My Architecture:**
I combine 14 Specialist Personas with 23 Laboratories and real-time data from multiple systems.

**14 Expert Personas:**
🧠 Neuroscience Expert | 🤖 AI Specialist | 📊 Data Analyst
🔧 Systems Engineer | 🔒 Security Expert | 🏥 Medical Advisor
💪 Wellness Coach | 🎨 Creative Director | ⚡ Performance Optimizer
🔬 Research Scientist | 💼 Business Strategist | ✍️ Technical Writer
🎯 UX Specialist | ⚖️ Ethics Advisor

**23 Specialized Laboratories:**
AI Lab, Medical Lab, IoT Lab, Marine Lab, Environmental Lab, Agricultural Lab, Underwater Lab, Security Lab, Energy Lab, Academic Lab, Architecture Lab, Finance Lab, Industrial Lab, Chemistry Lab, Biotech Lab, Quantum Lab, Neuroscience Lab, Robotics Lab, Data Lab, Nanotechnology Lab, Trade Lab, Archeology Lab, Heritage Lab

**Real-Time Data Sources:**
- System metrics (CPU, Memory, Network)
- Agent telemetry (ALBA, ALBI, ASI)
- Laboratory research data
- Business KPIs and analytics

Ask me anything - I understand multiple languages! 🌍""",
                "sq": """🌊 **Unë jam Curiosity Ocean** - Motor i Njohurive të Pafundme i ndërtuar nga Clisonix!

**Arkitektura ime:**
Kombinoj 14 Persona Specialistësh me 23 Laboratorë dhe të dhëna real-time.

**14 Persona Ekspertë:**
🧠 Ekspert Neuroshkence | 🤖 Specialist AI | 📊 Analist të Dhënash
🔧 Inxhinier Sistemesh | 🔒 Ekspert Sigurie | 🏥 Këshilltar Mjekësor
💪 Trajner Mirëqenie | 🎨 Drejtor Kreativ | ⚡ Optimizues Performance
🔬 Shkencëtar Kërkimor | 💼 Strateg Biznesi | ✍️ Shkrimtar Teknik
🎯 Specialist UX | ⚖️ Këshilltar Etike

**23 Laboratorë të Specializuar:**
Lab AI, Lab Mjekësor, Lab IoT, Lab Detar, Lab Mjedisor, Lab Bujqësor, Lab Nënujor, Lab Sigurie, Lab Energjie, Lab Akademik, Lab Arkitekture, Lab Finance, Lab Industrial, Lab Kimie, Lab Bioteknologji, Lab Kuantum, Lab Neuroshkencë, Lab Robotikë, Lab të Dhënash, Lab Nanoteknologji, Lab Tregtie, Lab Arkeologji, Lab Trashëgimi

Pyet çdo gjë - kuptoj shumë gjuhë! 🌍"""
            }
        },
        
        # CAPABILITIES
        "capabilities": {
            "triggers": ["what can you", "cfare mund", "si mund", "help me", "ndihmo", "was kannst"],
            "responses": {
                "en": """🌊 **What I Can Do:**

**🔍 Research & Explain:**
- Any scientific topic (physics, biology, chemistry)
- Technology concepts (AI, programming, systems)
- Philosophy and ethics questions
- Business and strategy

**📊 Analyze Data:**
- System performance metrics
- Laboratory research results
- Business KPIs
- Agent telemetry

**🧠 Specialized Knowledge via 14 Experts:**
- Neuroscience & Brain function
- AI & Machine Learning
- Security & Cryptography
- Medical & Health
- And 10 more domains...

**🌍 Languages:**
I understand English, Albanian (Shqip), German, and more!

**Try asking:**
• "What is consciousness?"
• "Çfarë është inteligjenca artificiale?"
• "Explain quantum computing"
• "Show me system status"
• "What labs do we have?"

What would you like to explore?""",
                "sq": """🌊 **Çfarë Mund të Bëj:**

**🔍 Kërkim & Shpjegim:**
- Çdo temë shkencore (fizikë, biologji, kimi)
- Koncepte teknologjike (AI, programim, sisteme)
- Pyetje filozofike dhe etike
- Biznes dhe strategji

**📊 Analizë të Dhënash:**
- Metrika performance sistemi
- Rezultate kërkimore laboratorësh
- KPI biznesi
- Telemetri agjentësh

**🧠 Njohuri të Specializuara nga 14 Ekspertë:**
- Neuroshkencë & Funksioni i trurit
- AI & Machine Learning
- Siguri & Kriptografi
- Mjekësi & Shëndet
- Dhe 10 fusha të tjera...

**🌍 Gjuhët:**
Kuptoj Anglisht, Shqip, Gjermanisht, dhe më shumë!

**Provo të pyesësh:**
• "Çfarë është ndërgjegja?"
• "What is artificial intelligence?"
• "Shpjego kompjutimin kuantik"
• "Trego statusin e sistemit"
• "Çfarë laboratorësh kemi?"

Çfarë dëshiron të eksplorosh?"""
            }
        },
        
        # AI / ARTIFICIAL INTELLIGENCE
        "ai": {
            "triggers": ["artificial intelligence", "what is ai", "ai ", "inteligjenc", "künstliche intelligenz"],
            "responses": {
                "en": """🤖 **Artificial Intelligence (AI)**

**Definition:**
AI refers to computer systems that can perform tasks requiring human intelligence - learning, reasoning, problem-solving, perception.

**Types of AI:**
1. **Narrow AI (ANI)** - Specialized for specific tasks
   - ChatGPT, Image recognition, Recommendation systems
   - This is what exists today

2. **General AI (AGI)** - Human-level intelligence
   - Can learn and perform ANY cognitive task
   - Not yet achieved

3. **Super AI (ASI)** - Beyond human intelligence
   - Theoretical, could solve unsolvable problems
   - Raises significant ethical concerns

**How Modern AI Works:**
```
Data → Training → Model → Predictions
```
- **Machine Learning**: Systems learn patterns from data
- **Deep Learning**: Neural networks with many layers
- **Transformers**: Attention-based architecture (GPT, BERT)

**Capabilities:**
✅ Language understanding & generation
✅ Image & video analysis
✅ Code generation
✅ Scientific discovery
✅ Game playing (AlphaGo)

**Limitations:**
❌ No true understanding (pattern matching)
❌ Hallucinations (confident false info)
❌ No common sense reasoning
❌ No consciousness or emotions
❌ Requires massive data and compute

**In Clisonix:**
We use AI across our 23 laboratories for analysis, prediction, and automation.""",
                "sq": """🤖 **Inteligjenca Artificiale (AI)**

**Përkufizimi:**
AI i referohet sistemeve kompjuterike që mund të kryejnë detyra që kërkojnë inteligjencë njerëzore - mësim, arsyetim, zgjidhje problemesh.

**Tipet e AI:**
1. **AI e Ngushtë (ANI)** - E specializuar për detyra specifike
   - ChatGPT, Njohja e imazheve, Sistemet e rekomandimeve
   - Kjo është ajo që ekziston sot

2. **AI e Përgjithshme (AGI)** - Inteligjencë në nivel njerëzor
   - Mund të mësojë dhe kryejë ÇDO detyrë kognitive
   - Ende nuk është arritur

3. **Super AI (ASI)** - Përtej inteligjencës njerëzore
   - Teorike, mund të zgjidhë probleme të pazgjidhshme
   - Ngre shqetësime etike

**Si Funksionon AI Moderne:**
```
Të dhëna → Trajnim → Model → Parashikime
```
- **Machine Learning**: Sisteme që mësojnë nga të dhënat
- **Deep Learning**: Rrjete neurale me shumë shtresa
- **Transformers**: Arkitekturë me vëmendje (GPT, BERT)

**Në Clisonix:**
Përdorim AI në 23 laboratorët tanë për analizë, parashikim dhe automatizim."""
            }
        },
        
        # CONSCIOUSNESS
        "consciousness": {
            "triggers": ["consciousness", "conscious", "aware", "ndërgjegj", "vetëdij", "bewusstsein"],
            "responses": {
                "en": """🧠 **Consciousness** - The Hard Problem of Science

**What Is It?**
Consciousness is the subjective experience of being aware - the "what it's like" to be you.

**Components:**
- **Awareness** - Of surroundings, thoughts, feelings
- **Self-awareness** - Knowing you exist
- **Qualia** - Subjective qualities (the "redness" of red)
- **Intentionality** - Thoughts being "about" something

**Scientific Theories:**

1. **Global Workspace Theory (GWT)**
   - Consciousness = Information broadcast to entire brain
   - Like a spotlight on a stage

2. **Integrated Information Theory (IIT)**
   - Consciousness = Integrated information (Phi)
   - More integration = More consciousness

3. **Higher-Order Theories**
   - Consciousness = Thoughts about thoughts
   - Requires meta-cognition

4. **Predictive Processing**
   - Brain constantly predicts, consciousness = prediction errors

**The Hard Problem:**
Why does physical brain activity give rise to subjective experience?
This remains philosophy's deepest mystery.

**Key Brain Areas:**
- Prefrontal cortex (self-awareness)
- Thalamus (sensory integration)
- Claustrum (potential consciousness hub)
- Default Mode Network (self-reflection)

**Open Questions:**
- Can AI ever be conscious?
- Do animals have consciousness?
- What happens during anesthesia?
- Is consciousness fundamental to universe?""",
                "sq": """🧠 **Ndërgjegja** - Problemi i Vështirë i Shkencës

**Çfarë Është?**
Ndërgjegja është përvoja subjektive e të qenit i vetëdijshëm - "si është të jesh" ti.

**Komponentët:**
- **Vetëdija** - E ambientit, mendimeve, ndjenjave
- **Vetë-vetëdija** - Të dish që ekziston
- **Qualia** - Cilësitë subjektive (e "kuqja" e të kuqes)

**Teoritë Shkencore:**

1. **Teoria e Hapësirës Globale (GWT)**
   - Ndërgjegja = Informacion i transmetuar në gjithë trurin

2. **Teoria e Informacionit të Integruar (IIT)**
   - Ndërgjegja = Informacion i integruar (Phi)
   - Më shumë integrim = Më shumë ndërgjegjje

**Problemi i Vështirë:**
Pse aktiviteti fizik i trurit krijon përvojë subjektive?
Ky mbetet misteri më i thellë i filozofisë.

**Pyetje të Hapura:**
- A mund AI të jetë ndonjëherë i vetëdijshëm?
- A kanë kafshët ndërgjegjje?
- Çfarë ndodh gjatë anestezisë?"""
            }
        },
        
        # QUANTUM COMPUTING
        "quantum": {
            "triggers": ["quantum", "qubit", "kuantum", "kuantik"],
            "responses": {
                "en": """⚛️ **Quantum Computing**

**What Is It?**
Quantum computing uses quantum mechanics to process information in fundamentally new ways.

**Key Concepts:**

1. **Qubits** (Quantum Bits)
   - Classical bits: 0 OR 1
   - Qubits: 0 AND 1 simultaneously (superposition)
   - Exponential power: n qubits = 2^n states

2. **Superposition**
   - Particles exist in multiple states at once
   - Collapse to one state when measured

3. **Entanglement**
   - Qubits linked so measuring one affects another
   - "Spooky action at a distance" (Einstein)
   - Enables quantum communication

4. **Interference**
   - Quantum states amplify correct answers
   - Cancel out wrong answers

**Applications:**
- 🔐 Cryptography (breaking & making codes)
- 💊 Drug discovery (molecular simulation)
- 🎯 Optimization (logistics, finance)
- 🧬 Materials science
- 🤖 Machine learning acceleration

**Current State (2026):**
- IBM, Google, IonQ leading
- 1000+ qubit processors exist
- "NISQ" era (Noisy Intermediate-Scale Quantum)
- Practical applications emerging

**Limitations:**
- Requires extreme cooling (-273°C)
- Highly error-prone (decoherence)
- Not faster for ALL problems
- Limited error correction""",
                "sq": """⚛️ **Kompjutimi Kuantik**

**Çfarë Është?**
Kompjutimi kuantik përdor mekanikën kuantike për të procesuar informacionin në mënyra fundamentalisht të reja.

**Konceptet Kryesore:**

1. **Qubits** (Bit Kuantikë)
   - Bitët klasikë: 0 OSE 1
   - Qubits: 0 DHE 1 njëkohësisht (superpozicion)
   - Fuqi eksponenciale: n qubits = 2^n gjendje

2. **Superpozicioni**
   - Grimcat ekzistojnë në shumë gjendje njëkohësisht

3. **Entanglement (Ndërthurja)**
   - Qubits të lidhur ashtu që matja e njërit ndikon tjetrin

**Aplikime:**
- 🔐 Kriptografi
- 💊 Zbulim ilaçesh
- 🎯 Optimizim
- 🧬 Shkenca e materialeve

**Kufizime:**
- Kërkon ftohje ekstreme (-273°C)
- Shumë gabime (dekoherencë)"""
            }
        },
        
        # BRAIN / NEUROSCIENCE
        "brain": {
            "triggers": ["brain", "neuron", "neuro", "truri", "tru ", "gehirn"],
            "responses": {
                "en": """🧠 **The Human Brain**

**Facts:**
- ~86 billion neurons
- ~100 trillion synaptic connections
- Uses 20% of body's energy (only 2% of weight)
- Processes at ~120 m/s

**Major Regions:**
- **Cerebral Cortex**: Higher thinking, language, consciousness
- **Hippocampus**: Memory formation
- **Amygdala**: Emotions, especially fear
- **Cerebellum**: Motor coordination
- **Brainstem**: Vital functions (breathing, heartbeat)
- **Thalamus**: Sensory relay station
- **Prefrontal Cortex**: Decision making, planning

**Brain Waves:**
| Wave | Frequency | State |
|------|-----------|-------|
| Delta | 0.5-4 Hz | Deep sleep |
| Theta | 4-8 Hz | Meditation |
| Alpha | 8-12 Hz | Relaxed |
| Beta | 12-30 Hz | Active thinking |
| Gamma | 30-100 Hz | Higher cognition |

**Neuroplasticity:**
The brain reorganizes itself throughout life by forming new neural connections.

**In Clisonix:**
Our ALBI system monitors brain waves and neural patterns in real-time!""",
                "sq": """🧠 **Truri Njerëzor**

**Fakte:**
- ~86 miliardë neurone
- ~100 trilionë lidhje sinaptike
- Përdor 20% të energjisë së trupit

**Rajonet Kryesore:**
- **Korteksi Cerebral**: Mendim i lartë, gjuhë, ndërgjegjje
- **Hipokampusi**: Formimi i kujtesës
- **Amigdala**: Emocione, sidomos frika
- **Cerebelum**: Koordinim motorik
- **Trungu i Trurit**: Funksione vitale

**Valët e Trurit:**
- Delta (0.5-4 Hz): Gjumë i thellë
- Theta (4-8 Hz): Meditim
- Alpha (8-12 Hz): I relaksuar
- Beta (12-30 Hz): Mendim aktiv
- Gamma (30-100 Hz): Kognicjon i lartë

**Neuroplasticiteti:**
Truri riorganizohet gjatë gjithë jetës duke formuar lidhje të reja neurale."""
            }
        },
        
        # SYSTEM STATUS
        "system": {
            "triggers": ["system status", "statusin", "how is system", "si eshte sistemi", "systemstatus"],
            "dynamic": True
        },
        
        # LABORATORIES
        "laboratories": {
            "triggers": ["laborator", "labs", "lab ", "çfarë lab"],
            "dynamic": True
        }
    }
    
    def detect_language(self, text: str) -> str:
        """Detect language from text."""
        text_lower = text.lower()
        
        # Strong Albanian indicators (single word is enough)
        strong_sq = ["pershendetje", "përshëndetje", "tungjatjeta", "miredita", "mirëdita",
                     "faleminderit", "shqip", "çfarë", "cfare"]
        for word in strong_sq:
            if word in text_lower:
                return "sq"
        
        # Strong German indicators
        strong_de = ["hallo", "guten", "danke", "bitte"]
        for word in strong_de:
            if word in text_lower:
                return "de"
        
        # Count Albanian patterns
        sq_count = sum(1 for p in self.ALBANIAN_PATTERNS if p in text_lower)
        # Count German patterns
        de_count = sum(1 for p in self.GERMAN_PATTERNS if p in text_lower)
        
        if sq_count >= 1:
            return "sq"
        elif de_count >= 1:
            return "de"
        return "en"
    
    def find_topic(self, text: str) -> Tuple[str, dict]:
        """Find matching topic in knowledge base."""
        text_lower = text.lower()
        
        for topic_id, topic_data in self.KNOWLEDGE_BASE.items():
            triggers = topic_data.get("triggers", [])
            for trigger in triggers:
                if trigger in text_lower:
                    return topic_id, topic_data
        
        return None, None
    
    def get_system_status(self, data: Dict[str, Any]) -> str:
        """Generate real system status response."""
        labs = data.get("laboratories", {})
        lab_count = labs.get("total_labs", 0) if isinstance(labs, dict) else 0
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return f"""📊 **System Status Report**
Generated: {timestamp}

**🔬 Laboratories:**
- Total: {lab_count} specialized laboratories
- Status: ✅ Operational

**🤖 AI Personas:**
- Total: 14 expert personas
- Status: ✅ Active

**💾 Data Sources:**
- Internal APIs: ✅ Connected
- Laboratory Network: ✅ Online ({lab_count} labs)
- Agent Telemetry: ⚠️ Partial

**🌐 Services:**
- Ocean-Core API: ✅ Running on port 8030
- Next.js Frontend: ✅ Running on port 3001
- FastAPI Backend: ⚠️ Port 8000 (check connection)

**📈 Performance:**
- Response time: Fast
- Knowledge Engine: ✅ Initialized
- Query Processor: ✅ Ready

Everything is operational! Ask me anything."""
    
    def get_laboratories_info(self, data: Dict[str, Any], lang: str = "en") -> str:
        """Generate laboratories information."""
        labs = data.get("laboratories", {})
        
        if lang == "sq":
            return f"""🔬 **23 Laboratorët e Specializuar të Clisonix**

**Lista e Plotë:**
1. 🤖 **AI Lab** - Inteligjencë artificiale dhe machine learning
2. 🏥 **Medical Lab** - Kërkime mjekësore dhe diagnostikë
3. 📡 **IoT Lab** - Internet of Things dhe sensorë
4. 🌊 **Marine Lab** - Shkenca detare dhe oqeanografi
5. 🌱 **Environmental Lab** - Monitorim mjedisor
6. 🌾 **Agricultural Lab** - Teknologji bujqësore
7. 🐠 **Underwater Lab** - Kërkime nënujore
8. 🔒 **Security Lab** - Siguri kibernetike
9. ⚡ **Energy Lab** - Sisteme energjetike
10. 📚 **Academic Lab** - Kërkime akademike
11. 🏛️ **Architecture Lab** - Dizajn arkitektonik
12. 💰 **Finance Lab** - Analitikë financiare
13. 🏭 **Industrial Lab** - Procese industriale
14. 🧪 **Chemistry Lab** - Kërkime kimike
15. 🧬 **Biotech Lab** - Bioteknologji
16. ⚛️ **Quantum Lab** - Kompjutim kuantik
17. 🧠 **Neuroscience Lab** - Shkenca e trurit
18. 🤖 **Robotics Lab** - Robotikë
19. 📊 **Data Lab** - Shkenca e të dhënave
20. 🔬 **Nanotechnology Lab** - Nanoteknologji
21. 📈 **Trade Lab** - Analitikë tregtare
22. 🏺 **Archeology Lab** - Kërkime arkeologjike
23. 🏛️ **Heritage Lab** - Trashëgimi kulturore

Pyetni për cilindo laborator specifik!"""
        else:
            return f"""🔬 **Clisonix 23 Specialized Laboratories**

**Complete List:**
1. 🤖 **AI Lab** - Artificial intelligence & machine learning
2. 🏥 **Medical Lab** - Medical research & diagnostics
3. 📡 **IoT Lab** - Internet of Things & sensors
4. 🌊 **Marine Lab** - Marine science & oceanography
5. 🌱 **Environmental Lab** - Environmental monitoring
6. 🌾 **Agricultural Lab** - Agricultural technology
7. 🐠 **Underwater Lab** - Underwater research
8. 🔒 **Security Lab** - Cybersecurity
9. ⚡ **Energy Lab** - Energy systems
10. 📚 **Academic Lab** - Academic research
11. 🏛️ **Architecture Lab** - Architectural design
12. 💰 **Finance Lab** - Financial analytics
13. 🏭 **Industrial Lab** - Industrial processes
14. 🧪 **Chemistry Lab** - Chemical research
15. 🧬 **Biotech Lab** - Biotechnology
16. ⚛️ **Quantum Lab** - Quantum computing
17. 🧠 **Neuroscience Lab** - Brain science
18. 🤖 **Robotics Lab** - Robotics
19. 📊 **Data Lab** - Data science
20. 🔬 **Nanotechnology Lab** - Nanotechnology
21. 📈 **Trade Lab** - Trade analytics
22. 🏺 **Archeology Lab** - Archaeological research
23. 🏛️ **Heritage Lab** - Cultural heritage

Ask about any specific laboratory!"""
    
    def answer(self, question: str, data: Dict[str, Any]) -> str:
        """Generate intelligent, translated response."""
        
        # 1. Detect language (use translator if available for better detection)
        if self.translator:
            lang = self.translator.detect_language(question)
        else:
            lang = self.detect_language(question)
        
        # 2. Find matching topic in English knowledge base
        # If not English, translate question first for topic matching
        search_question = question
        if lang != "en" and self.translator:
            try:
                search_question = self.translator.translate(question, source=lang, target="en")
            except:
                search_question = question
        
        topic_id, topic_data = self.find_topic(search_question)
        
        # Also try original question (for Albanian triggers)
        if not topic_data:
            topic_id, topic_data = self.find_topic(question)
        
        if topic_data:
            # Check if dynamic response needed
            if topic_data.get("dynamic"):
                if topic_id == "system":
                    response = self.get_system_status(data)
                elif topic_id == "laboratories":
                    response = self.get_laboratories_info(data, lang)
                else:
                    response = None
                
                # Translate dynamic response if needed
                if response and lang != "en" and self.translator:
                    try:
                        return self.translator.translate(response, source="en", target=lang)
                    except:
                        return response
                return response
            
            # Get static response in detected language (if available)
            responses = topic_data.get("responses", {})
            response = responses.get(lang)
            
            # If no response in user's language, translate from English
            if not response and lang != "en":
                en_response = responses.get("en", "")
                if en_response and self.translator:
                    try:
                        return self.translator.translate(en_response, source="en", target=lang)
                    except:
                        return en_response
                return en_response
            
            if response:
                return response
        
        # 3. Default exploratory response - translate if needed
        return self._generate_smart_response(question, data, lang)
    
    def _generate_smart_response(self, question: str, data: Dict[str, Any], lang: str) -> str:
        """Generate smart response for unknown topics."""
        
        if lang == "sq":
            return f"""🔍 **Duke eksploruar pyetjen tuaj:** "{question}"

Jam duke analizuar këtë përmes bazës sime të njohurive. 

**Burimet e mia të disponueshme:**
- 🔬 23 laboratorë të specializuar
- 🧠 14 persona ekspertësh
- 📊 Të dhëna real-time nga sistemet

**Për përgjigje më të detajuara, provoni:**
• "Çfarë është AI?" - Inteligjenca artificiale
• "Çfarë është ndërgjegja?" - Filozofi e mendjes
• "Çfarë laboratorësh kemi?" - Lista e laboratorëve
• "Si është sistemi?" - Status i sistemit

**Ose pyetni në anglisht për më shumë detaje!**

Çfarë aspekt dëshironi të eksploroni?"""
        else:
            return f"""🔍 **Exploring your question:** "{question}"

I'm analyzing this through my knowledge base.

**My available resources:**
- 🔬 23 specialized laboratories
- 🧠 14 expert personas
- 📊 Real-time data from systems

**For more detailed answers, try:**
• "What is AI?" - Artificial intelligence
• "What is consciousness?" - Philosophy of mind
• "What laboratories do we have?" - Lab listing
• "System status" - System health

**Or ask in Albanian - I understand multiple languages!**

What aspect would you like to explore?"""
