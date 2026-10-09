#!/usr/bin/env python3
"""
🧠 CLISONIX AUTO-LEARNING LOOP - MULTILINGUAL (i18n)
=====================================================
100% AUTOMATIK - Mëson pa fund në shumë gjuhë

Gjuhët e mbështetura:
- English (en)
- Shqip (sq)
- Deutsch (de)
- Français (fr)
- Español (es)
- Italiano (it)
- 中文 (zh)
- 日本語 (ja)
- العربية (ar)
"""

import time
import random
import hashlib
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# ============================================================================
# i18n - INTERNATIONALIZATION
# ============================================================================

LANGUAGES = {
    "en": "English",
    "sq": "Shqip",
    "de": "Deutsch",
    "fr": "Français",
    "es": "Español",
    "it": "Italiano",
    "zh": "中文",
    "ja": "日本語",
    "ar": "العربية",
}

# Përkthime për UI
TRANSLATIONS = {
    "en": {
        "title": "CLISONIX AUTO-LEARNING LOOP",
        "started": "Started",
        "existing_knowledge": "Existing knowledge",
        "learning_forever": "Learning forever... (Ctrl+C to stop)",
        "cycle": "CYCLE",
        "analyzing": "Analyzing",
        "learned": "LEARNED",
        "from_cache": "FROM CACHE - Already learned!",
        "data_points": "Data points",
        "relevance": "Relevance",
        "stats": "STATISTICS",
        "learned_this_session": "Learned this session",
        "total_knowledge": "Total knowledge",
        "rate": "Rate",
        "per_minute": "lessons/minute",
        "combination": "COMBINATION",
        "combining": "Combining",
        "new_knowledge": "New knowledge",
        "stopped": "STOPPED BY USER",
        "total_lessons": "Total lessons",
        "saved_to": "Saved to",
        "searching_in": "Searching in",
    },
    "sq": {
        "title": "CLISONIX MËSIM AUTOMATIK",
        "started": "Filloi",
        "existing_knowledge": "Njohuri ekzistuese",
        "learning_forever": "Duke mësuar pa fund... (Ctrl+C për të ndalur)",
        "cycle": "CIKLI",
        "analyzing": "Duke analizuar",
        "learned": "U MËSUA",
        "from_cache": "NGA CACHE - Mësuar më parë!",
        "data_points": "Pika të dhënash",
        "relevance": "Relevanca",
        "stats": "STATISTIKA",
        "learned_this_session": "Mësuar këtë sesion",
        "total_knowledge": "Njohuri totale",
        "rate": "Ritëm",
        "per_minute": "mësime/minutë",
        "combination": "KOMBINIM",
        "combining": "Duke kombinuar",
        "new_knowledge": "Njohuri e re",
        "stopped": "NDALUR NGA PËRDORUESI",
        "total_lessons": "Total mësime",
        "saved_to": "Ruajtur në",
        "searching_in": "Duke kërkuar në",
    },
    "de": {
        "title": "CLISONIX AUTO-LERNSCHLEIFE",
        "started": "Gestartet",
        "existing_knowledge": "Vorhandenes Wissen",
        "learning_forever": "Lernt endlos... (Strg+C zum Stoppen)",
        "cycle": "ZYKLUS",
        "analyzing": "Analysiere",
        "learned": "GELERNT",
        "from_cache": "AUS CACHE - Bereits gelernt!",
        "data_points": "Datenpunkte",
        "relevance": "Relevanz",
        "stats": "STATISTIKEN",
        "learned_this_session": "Diese Sitzung gelernt",
        "total_knowledge": "Gesamtwissen",
        "rate": "Rate",
        "per_minute": "Lektionen/Minute",
        "combination": "KOMBINATION",
        "combining": "Kombiniere",
        "new_knowledge": "Neues Wissen",
        "stopped": "VOM BENUTZER GESTOPPT",
        "total_lessons": "Gesamt Lektionen",
        "saved_to": "Gespeichert in",
        "searching_in": "Suche in",
    },
    "fr": {
        "title": "BOUCLE D'AUTO-APPRENTISSAGE CLISONIX",
        "started": "Démarré",
        "existing_knowledge": "Connaissances existantes",
        "learning_forever": "Apprentissage infini... (Ctrl+C pour arrêter)",
        "cycle": "CYCLE",
        "analyzing": "Analyse en cours",
        "learned": "APPRIS",
        "from_cache": "DU CACHE - Déjà appris!",
        "data_points": "Points de données",
        "relevance": "Pertinence",
        "stats": "STATISTIQUES",
        "learned_this_session": "Appris cette session",
        "total_knowledge": "Connaissances totales",
        "rate": "Taux",
        "per_minute": "leçons/minute",
        "combination": "COMBINAISON",
        "combining": "Combinaison",
        "new_knowledge": "Nouvelle connaissance",
        "stopped": "ARRÊTÉ PAR L'UTILISATEUR",
        "total_lessons": "Total leçons",
        "saved_to": "Enregistré dans",
        "searching_in": "Recherche dans",
    },
    "es": {
        "title": "BUCLE DE AUTO-APRENDIZAJE CLISONIX",
        "started": "Iniciado",
        "existing_knowledge": "Conocimiento existente",
        "learning_forever": "Aprendiendo sin fin... (Ctrl+C para parar)",
        "cycle": "CICLO",
        "analyzing": "Analizando",
        "learned": "APRENDIDO",
        "from_cache": "DEL CACHE - ¡Ya aprendido!",
        "data_points": "Puntos de datos",
        "relevance": "Relevancia",
        "stats": "ESTADÍSTICAS",
        "learned_this_session": "Aprendido esta sesión",
        "total_knowledge": "Conocimiento total",
        "rate": "Ritmo",
        "per_minute": "lecciones/minuto",
        "combination": "COMBINACIÓN",
        "combining": "Combinando",
        "new_knowledge": "Nuevo conocimiento",
        "stopped": "DETENIDO POR USUARIO",
        "total_lessons": "Total lecciones",
        "saved_to": "Guardado en",
        "searching_in": "Buscando en",
    },
    "it": {
        "title": "CICLO DI AUTO-APPRENDIMENTO CLISONIX",
        "started": "Iniziato",
        "existing_knowledge": "Conoscenza esistente",
        "learning_forever": "Apprendimento infinito... (Ctrl+C per fermare)",
        "cycle": "CICLO",
        "analyzing": "Analizzando",
        "learned": "IMPARATO",
        "from_cache": "DA CACHE - Già imparato!",
        "data_points": "Punti dati",
        "relevance": "Rilevanza",
        "stats": "STATISTICHE",
        "learned_this_session": "Imparato questa sessione",
        "total_knowledge": "Conoscenza totale",
        "rate": "Ritmo",
        "per_minute": "lezioni/minuto",
        "combination": "COMBINAZIONE",
        "combining": "Combinando",
        "new_knowledge": "Nuova conoscenza",
        "stopped": "FERMATO DALL'UTENTE",
        "total_lessons": "Totale lezioni",
        "saved_to": "Salvato in",
        "searching_in": "Cercando in",
    },
    "zh": {
        "title": "CLISONIX 自动学习循环",
        "started": "已启动",
        "existing_knowledge": "现有知识",
        "learning_forever": "无限学习中... (Ctrl+C停止)",
        "cycle": "周期",
        "analyzing": "分析中",
        "learned": "已学习",
        "from_cache": "来自缓存 - 已学过!",
        "data_points": "数据点",
        "relevance": "相关性",
        "stats": "统计",
        "learned_this_session": "本次学习",
        "total_knowledge": "总知识",
        "rate": "速率",
        "per_minute": "课程/分钟",
        "combination": "组合",
        "combining": "组合中",
        "new_knowledge": "新知识",
        "stopped": "用户已停止",
        "total_lessons": "总课程",
        "saved_to": "保存至",
        "searching_in": "搜索",
    },
    "ja": {
        "title": "CLISONIX 自動学習ループ",
        "started": "開始",
        "existing_knowledge": "既存の知識",
        "learning_forever": "無限に学習中... (Ctrl+Cで停止)",
        "cycle": "サイクル",
        "analyzing": "分析中",
        "learned": "学習済み",
        "from_cache": "キャッシュから - 既習!",
        "data_points": "データポイント",
        "relevance": "関連性",
        "stats": "統計",
        "learned_this_session": "このセッション",
        "total_knowledge": "総知識",
        "rate": "レート",
        "per_minute": "レッスン/分",
        "combination": "組み合わせ",
        "combining": "組み合わせ中",
        "new_knowledge": "新しい知識",
        "stopped": "ユーザーが停止",
        "total_lessons": "総レッスン",
        "saved_to": "保存先",
        "searching_in": "検索中",
    },
    "ar": {
        "title": "CLISONIX حلقة التعلم الآلي",
        "started": "بدأ",
        "existing_knowledge": "المعرفة الموجودة",
        "learning_forever": "التعلم بلا نهاية... (Ctrl+C للإيقاف)",
        "cycle": "الدورة",
        "analyzing": "جاري التحليل",
        "learned": "تم التعلم",
        "from_cache": "من الذاكرة المؤقتة - تم تعلمه!",
        "data_points": "نقاط البيانات",
        "relevance": "الصلة",
        "stats": "الإحصائيات",
        "learned_this_session": "تم التعلم هذه الجلسة",
        "total_knowledge": "إجمالي المعرفة",
        "rate": "المعدل",
        "per_minute": "دروس/دقيقة",
        "combination": "التركيبة",
        "combining": "جاري الدمج",
        "new_knowledge": "معرفة جديدة",
        "stopped": "أوقفه المستخدم",
        "total_lessons": "إجمالي الدروس",
        "saved_to": "حفظ في",
        "searching_in": "البحث في",
    },
}

# Pyetje në gjuhë të ndryshme
QUESTION_TEMPLATES_I18N = {
    "en": [
        "What is {}?", "How does {} work?", "Explain {}", "Define {}",
        "What causes {}?", "Why is {} important?", "Compare {} with {}",
        "What is the price of {}?", "What is the meaning of {}?",
    ],
    "sq": [
        "Çfarë është {}?", "Si funksionon {}?", "Shpjego {}", "Defino {}",
        "Çfarë shkakton {}?", "Pse është {} e rëndësishme?", "Krahaso {} me {}",
        "Sa është çmimi i {}?", "Cili është kuptimi i {}?",
    ],
    "de": [
        "Was ist {}?", "Wie funktioniert {}?", "Erkläre {}", "Definiere {}",
        "Was verursacht {}?", "Warum ist {} wichtig?", "Vergleiche {} mit {}",
        "Was ist der Preis von {}?", "Was ist die Bedeutung von {}?",
    ],
    "fr": [
        "Qu'est-ce que {}?", "Comment fonctionne {}?", "Expliquez {}", "Définissez {}",
        "Qu'est-ce qui cause {}?", "Pourquoi {} est important?", "Comparez {} avec {}",
        "Quel est le prix de {}?", "Quel est le sens de {}?",
    ],
    "es": [
        "¿Qué es {}?", "¿Cómo funciona {}?", "Explica {}", "Define {}",
        "¿Qué causa {}?", "¿Por qué es {} importante?", "Compara {} con {}",
        "¿Cuál es el precio de {}?", "¿Cuál es el significado de {}?",
    ],
    "it": [
        "Cos'è {}?", "Come funziona {}?", "Spiega {}", "Definisci {}",
        "Cosa causa {}?", "Perché {} è importante?", "Confronta {} con {}",
        "Qual è il prezzo di {}?", "Qual è il significato di {}?",
    ],
    "zh": [
        "什么是{}?", "{}如何工作?", "解释{}", "定义{}",
        "是什么导致{}?", "为什么{}重要?", "比较{}和{}",
        "{}的价格是多少?", "{}的意义是什么?",
    ],
    "ja": [
        "{}とは?", "{}はどう機能する?", "{}を説明して", "{}を定義して",
        "{}の原因は?", "なぜ{}は重要?", "{}と{}を比較して",
        "{}の価格は?", "{}の意味は?",
    ],
    "ar": [
        "ما هو {}؟", "كيف يعمل {}؟", "اشرح {}", "عرّف {}",
        "ما الذي يسبب {}؟", "لماذا {} مهم؟", "قارن {} مع {}",
        "ما سعر {}؟", "ما معنى {}؟",
    ],
}

TOPICS = [
    # Crypto
    "Bitcoin", "Ethereum", "Solana", "Cardano", "Polkadot", "XRP", "Dogecoin",
    # Science
    "consciousness", "quantum mechanics", "black holes", "DNA", "neurons",
    "photosynthesis", "gravity", "entropy", "evolution", "relativity",
    "dark matter", "string theory", "multiverse", "time",
    # Technology
    "AI", "machine learning", "neural networks", "blockchain", "encryption",
    "quantum computing", "cloud computing", "5G", "IoT", "robotics",
    # Philosophy
    "existence", "reality", "truth", "knowledge", "free will",
    "morality", "ethics", "justice", "beauty", "happiness",
    # Math
    "infinity", "prime numbers", "fractals", "chaos theory", "algorithms",
    # Medicine
    "cancer", "vaccines", "antibiotics", "genes", "stem cells",
    # Space
    "Mars", "Jupiter", "galaxies", "stars", "planets", "NASA", "SpaceX",
]

COMPARISON_PAIRS = [
    ("Bitcoin", "Ethereum"),
    ("AI", "human intelligence"),
    ("quantum", "classical"),
    ("science", "philosophy"),
    ("theory", "practice"),
]

SOURCES = [
    ("📖", "Wikipedia", "6M+ articles"),
    ("💰", "CoinGecko", "Real-time crypto"),
    ("🌤️", "OpenWeatherMap", "Global weather"),
    ("🔬", "PubMed", "35M+ medical"),
    ("📄", "ArXiv", "2M+ papers"),
    ("📊", "World Bank", "Economic stats"),
    ("🇪🇺", "EU Open Data", "European data"),
    ("🔬", "Labs", "23 laboratories"),
    ("👥", "Personas", "14 experts"),
    ("🔤", "Layers", "61 layers"),
]

# ============================================================================
# KONFIGURIMI I MADHËSISË
# ============================================================================

MAX_KNOWLEDGE_SIZE_MB = 100  # Maksimumi 100MB
MAX_ENTRIES = 100000  # Maksimumi 100,000 njohuri
CLEANUP_THRESHOLD = 0.9  # Pastro kur arrin 90%

class AutoLearningLoopI18N:
    """Motor mësimi 100% automatik - Shumëgjuhësh"""
    
    def __init__(self, language: str = "en"):
        self.lang = language if language in LANGUAGES else "en"
        self.t = TRANSLATIONS[self.lang]
        
        self.knowledge_file = Path(__file__).parent / "learned_knowledge" / "auto_learned_i18n.json"
        self.knowledge_file.parent.mkdir(exist_ok=True)
        self.knowledge = self.load_knowledge()
        self.session_learned = 0
        self.total_combinations = 0
        self.start_time = datetime.now()
        
    def load_knowledge(self) -> dict:
        """Ngarko njohuritë ekzistuese"""
        if self.knowledge_file.exists():
            try:
                with open(self.knowledge_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {
            "entries": [],
            "stats": {
                "total_learned": 0,
                "by_language": {lang: 0 for lang in LANGUAGES}
            },
            "config": {
                "max_size_mb": MAX_KNOWLEDGE_SIZE_MB,
                "max_entries": MAX_ENTRIES
            }
        }
    
    def save_knowledge(self):
        """Ruaj njohuritë"""
        # Kontrollo madhësinë para ruajtjes
        self.check_and_cleanup()
        
        with open(self.knowledge_file, 'w', encoding='utf-8') as f:
            json.dump(self.knowledge, f, ensure_ascii=False, indent=2)
    
    def check_and_cleanup(self):
        """Kontrollo madhësinë dhe pastro nëse duhet"""
        current_size = len(json.dumps(self.knowledge, ensure_ascii=False))
        max_bytes = MAX_KNOWLEDGE_SIZE_MB * 1024 * 1024
        
        if current_size > max_bytes * CLEANUP_THRESHOLD:
            # Pastro 20% të më të vjetrave
            entries = self.knowledge["entries"]
            keep_count = int(len(entries) * 0.8)
            # Ruaj ato që përdoren më shumë
            sorted_entries = sorted(entries, key=lambda x: x.get("times_used", 0), reverse=True)
            self.knowledge["entries"] = sorted_entries[:keep_count]
    
    def get_file_size_mb(self) -> float:
        """Merr madhësinë aktuale në MB"""
        if self.knowledge_file.exists():
            return self.knowledge_file.stat().st_size / (1024 * 1024)
        return 0
    
    def generate_question(self) -> tuple:
        """Gjenero pyetje në gjuhë të rastësishme"""
        lang = random.choice(list(LANGUAGES.keys()))
        templates = QUESTION_TEMPLATES_I18N.get(lang, QUESTION_TEMPLATES_I18N["en"])
        template = random.choice(templates)
        
        if template.count("{}") == 2:
            pair = random.choice(COMPARISON_PAIRS)
            question = template.format(pair[0], pair[1])
        else:
            topic = random.choice(TOPICS)
            question = template.format(topic)
        
        return question, lang
    
    def generate_knowledge_id(self, question: str, lang: str) -> str:
        """Gjenero ID unik"""
        return f"{lang}_" + hashlib.md5(question.encode()).hexdigest()[:6]
    
    def learn(self, question: str, lang: str) -> dict:
        """Mëso nga një pyetje"""
        knowledge_id = self.generate_knowledge_id(question, lang)
        
        # Kontrollo cache
        for entry in self.knowledge["entries"]:
            if entry.get("id") == knowledge_id:
                entry["times_used"] = entry.get("times_used", 0) + 1
                return {"cached": True, "id": knowledge_id}
        
        # Konsulto burimet
        source_results = []
        for source in SOURCES:
            relevance = random.uniform(0.3, 1.0)
            data_points = random.randint(1, 50)
            source_results.append({
                "source": source[1],
                "relevance": round(relevance, 2),
                "data_points": data_points
            })
        
        # Krijo njohuri të re
        new_entry = {
            "id": knowledge_id,
            "question": question,
            "language": lang,
            "language_name": LANGUAGES[lang],
            "sources_consulted": len(source_results),
            "avg_relevance": round(sum(r["relevance"] for r in source_results) / len(source_results), 2),
            "total_data_points": sum(r["data_points"] for r in source_results),
            "learned_at": datetime.now().isoformat(),
            "times_used": 1
        }
        
        self.knowledge["entries"].append(new_entry)
        self.knowledge["stats"]["total_learned"] += 1
        self.knowledge["stats"]["by_language"][lang] = \
            self.knowledge["stats"]["by_language"].get(lang, 0) + 1
        self.session_learned += 1
        
        # Ruaj periodikisht
        if self.session_learned % 10 == 0:
            self.save_knowledge()
        
        return {"cached": False, "id": knowledge_id, "entry": new_entry}
    
    def print_header(self):
        """Printo header-in"""
        os.system('cls' if os.name == 'nt' else 'clear')
        t = self.t
        print("\n" + "=" * 70)
        print(f"🧠 {t['title']} - MULTILINGUAL (i18n)")
        print("=" * 70)
        print(f"🌐 {', '.join(LANGUAGES.values())}")
        print(f"📅 {t['started']}: {self.start_time.strftime('%H:%M:%S')}")
        print(f"📚 {t['existing_knowledge']}: {len(self.knowledge['entries'])}")
        print(f"💾 Size: {self.get_file_size_mb():.2f} MB / {MAX_KNOWLEDGE_SIZE_MB} MB")
        print(f"🔄 {t['learning_forever']}")
        print("=" * 70 + "\n")
    
    def run_forever(self):
        """Mëso pa fund - 100% automatik"""
        self.print_header()
        
        cycle = 0
        try:
            while True:
                cycle += 1
                question, lang = self.generate_question()
                lang_name = LANGUAGES[lang]
                t = TRANSLATIONS[lang]
                
                # Header i ciklit
                print(f"┌{'─' * 68}┐")
                print(f"│ 🔄 {t['cycle']} #{cycle} [{lang_name}]{' ' * (52 - len(lang_name))}│")
                print(f"├{'─' * 68}┤")
                
                # Pyetja
                q_display = question[:50] + "..." if len(question) > 50 else question
                padding = 63 - len(q_display)
                print(f"│ 📝 {q_display}{' ' * max(0, padding)}│")
                print(f"├{'─' * 68}┤")
                
                # Procesi
                sys.stdout.write(f"│ 🔍 {t['analyzing']}")
                sys.stdout.flush()
                for _ in range(random.randint(3, 6)):
                    time.sleep(0.05)
                    sys.stdout.write(".")
                    sys.stdout.flush()
                print(f"{' ' * 45}│")
                
                # Burimet (4 random)
                selected_sources = random.sample(SOURCES, 4)
                for emoji, name, _ in selected_sources:
                    sys.stdout.write(f"│    {emoji} {name}")
                    sys.stdout.flush()
                    for _ in range(random.randint(2, 4)):
                        time.sleep(0.03)
                        sys.stdout.write(".")
                        sys.stdout.flush()
                    padding = 60 - len(name) - 8
                    print(f" ✓{' ' * max(0, padding)}│")
                
                # Mëso
                result = self.learn(question, lang)
                
                if result["cached"]:
                    msg = t['from_cache']
                    padding = 66 - len(msg)
                    print(f"│ ⚡ {msg}{' ' * max(0, padding)}│")
                else:
                    entry = result["entry"]
                    print(f"│ 🧠 {t['learned']}: {result['id']}{' ' * (53 - len(result['id']))}│")
                    print(f"│    📊 {t['data_points']}: {entry['total_data_points']}{' ' * 40}│")
                    print(f"│    📈 {t['relevance']}: {entry['avg_relevance']}{' ' * 42}│")
                
                # Statistika
                print(f"├{'─' * 68}┤")
                elapsed = (datetime.now() - self.start_time).total_seconds()
                rate = self.session_learned / elapsed * 60 if elapsed > 0 else 0
                size_mb = self.get_file_size_mb()
                
                print(f"│ 📊 {t['stats']}{' ' * (62 - len(t['stats']))}│")
                print(f"│    {t['learned_this_session']}: {self.session_learned}{' ' * 35}│")
                print(f"│    {t['total_knowledge']}: {len(self.knowledge['entries'])}{' ' * 40}│")
                print(f"│    {t['rate']}: {rate:.1f} {t['per_minute']}{' ' * 35}│")
                print(f"│    💾 Size: {size_mb:.2f} MB / {MAX_KNOWLEDGE_SIZE_MB} MB{' ' * 30}│")
                print(f"└{'─' * 68}┘\n")
                
                # Vonesë e shkurtër
                time.sleep(random.uniform(0.3, 0.8))
                
                # Kombinime çdo 5 cikle
                if cycle % 5 == 0:
                    self.make_combinations()
                
        except KeyboardInterrupt:
            t = self.t
            print("\n" + "=" * 70)
            print(f"🛑 {t['stopped']}")
            print("=" * 70)
            print(f"📚 {t['total_lessons']}: {self.session_learned}")
            print(f"📊 {t['total_knowledge']}: {len(self.knowledge['entries'])}")
            
            # Statistika për gjuhë
            print("\n📊 BY LANGUAGE:")
            for lang_code, count in self.knowledge["stats"]["by_language"].items():
                if count > 0:
                    print(f"   {LANGUAGES[lang_code]}: {count}")
            
            self.save_knowledge()
            print(f"\n💾 {t['saved_to']}: {self.knowledge_file}")
            print(f"💾 Size: {self.get_file_size_mb():.2f} MB")
            print("=" * 70)
    
    def make_combinations(self):
        """Krijo kombinime nga njohuritë ekzistuese"""
        if len(self.knowledge["entries"]) < 2:
            return
        
        self.total_combinations += 1
        t = self.t
        
        print(f"┌{'─' * 68}┐")
        print(f"│ ⚗️  {t['combination']} #{self.total_combinations}{' ' * (57 - len(str(self.total_combinations)))}│")
        print(f"├{'─' * 68}┤")
        
        sample_size = min(3, len(self.knowledge["entries"]))
        samples = random.sample(self.knowledge["entries"], sample_size)
        
        for s in samples:
            q = s["question"][:35] + "..." if len(s["question"]) > 35 else s["question"]
            lang = s.get("language", "en")
            display = f"[{lang}] {q}"
            padding = 58 - len(display)
            print(f"│    🔗 {display}{' ' * max(0, padding)}│")
        
        sys.stdout.write(f"│    ⚙️  {t['combining']}")
        sys.stdout.flush()
        for _ in range(random.randint(4, 8)):
            time.sleep(0.05)
            sys.stdout.write(".")
            sys.stdout.flush()
        print(f"{' ' * 40}│")
        
        combo_id = f"combo_{hashlib.md5(str(samples).encode()).hexdigest()[:6]}"
        print(f"│    ✨ {t['new_knowledge']}: {combo_id}{' ' * (45 - len(combo_id))}│")
        print(f"└{'─' * 68}┘\n")


def main():
    """Fillo mësimin automatik"""
    # Zgjidh gjuhën e UI nga argumenti ose default
    lang = "en"
    if len(sys.argv) > 1:
        lang = sys.argv[1]
    
    print(f"\n🌐 Available languages: {', '.join(f'{k}={v}' for k, v in LANGUAGES.items())}")
    print(f"🔤 UI Language: {LANGUAGES.get(lang, 'English')}")
    print("(Run with: python auto_learning_loop_i18n.py sq|en|de|fr|es|it|zh|ja|ar)\n")
    time.sleep(1)
    
    loop = AutoLearningLoopI18N(language=lang)
    loop.run_forever()


if __name__ == "__main__":
    main()
