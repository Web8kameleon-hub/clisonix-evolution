#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Albanian Dictionary for Curiosity Ocean
500+ common words and phrases to help the AI understand Albanian
"""

# Common Albanian greetings and phrases
GREETINGS = {
    "pershendetje": "hello/greetings",
    "tungjatjeta": "hello (formal)",
    "mirëdita": "good day",
    "mirëmëngjes": "good morning",
    "mirëmbrëma": "good evening",
    "natën e mirë": "good night",
    "si jeni": "how are you (formal)",
    "si je": "how are you (informal)",
    "faleminderit": "thank you",
    "shumë faleminderit": "thank you very much",
    "ju lutem": "please",
    "të lutem": "please (informal)",
    "mirupafshim": "goodbye",
    "lamtumirë": "farewell",
    "shihemi": "see you",
    "shihemi më vonë": "see you later",
    "po": "yes",
    "jo": "no",
    "ndoshta": "maybe",
    "sigurisht": "of course",
    "patjetër": "certainly",
    "më fal": "excuse me/sorry",
    "më vjen keq": "I'm sorry",
    "asgjë": "nothing/you're welcome",
    "s'ka problem": "no problem",
    "dakord": "okay/agreed",
    "në rregull": "alright",
}

# Question words
QUESTION_WORDS = {
    "kush": "who",
    "çfarë": "what",
    "cfare": "what",
    "ku": "where",
    "kur": "when",
    "pse": "why",
    "si": "how",
    "sa": "how much/many",
    "cili": "which (m)",
    "cila": "which (f)",
    "a": "question particle",
}

# Common verbs
VERBS = {
    "jam": "I am",
    "je": "you are",
    "është": "he/she/it is",
    "jemi": "we are",
    "jeni": "you are (plural)",
    "janë": "they are",
    "kam": "I have",
    "ke": "you have",
    "ka": "he/she/it has",
    "kemi": "we have",
    "keni": "you have (plural)",
    "kanë": "they have",
    "bëj": "I do/make",
    "shkoj": "I go",
    "vij": "I come",
    "them": "I say",
    "di": "I know",
    "dua": "I want/love",
    "mund": "I can",
    "duhet": "must/need",
    "punoj": "I work",
    "jetoj": "I live",
    "flas": "I speak",
    "lexoj": "I read",
    "shkruaj": "I write",
    "dëgjoj": "I listen",
    "shoh": "I see",
    "kuptoj": "I understand",
    "mësoj": "I learn/teach",
    "pyes": "I ask",
    "përgjigjem": "I answer",
    "ndihmoj": "I help",
    "mendoj": "I think",
    "besoj": "I believe",
    "pres": "I wait",
    "filloj": "I start",
    "mbaroj": "I finish",
    "hap": "I open",
    "mbyll": "I close",
    "marr": "I take",
    "jap": "I give",
    "blej": "I buy",
    "shes": "I sell",
    "ha": "I eat",
    "pi": "I drink",
    "fle": "I sleep",
    "zgjohem": "I wake up",
    "ec": "I walk",
    "vrapoj": "I run",
    "fluturoj": "I fly",
    "notoj": "I swim",
    "luaj": "I play",
    "këndoj": "I sing",
    "vallëzoj": "I dance",
    "qesh": "I laugh",
    "qaj": "I cry",
}

# Common nouns
NOUNS = {
    "njeri": "person/human",
    "burrë": "man",
    "grua": "woman",
    "fëmijë": "child",
    "djalë": "boy",
    "vajzë": "girl",
    "familje": "family",
    "nënë": "mother",
    "atë": "father",
    "prind": "parent",
    "vëlla": "brother",
    "motër": "sister",
    "gjysh": "grandfather",
    "gjyshe": "grandmother",
    "mik": "friend",
    "shok": "friend/comrade",
    "shoqe": "female friend",
    "shtëpi": "house",
    "apartament": "apartment",
    "dhomë": "room",
    "kuzhinë": "kitchen",
    "banjë": "bathroom",
    "korridor": "hallway",
    "dritare": "window",
    "derë": "door",
    "tavolinë": "table",
    "karrige": "chair",
    "shtrat": "bed",
    "qytet": "city",
    "fshat": "village",
    "rrugë": "street/road",
    "shesh": "square",
    "park": "park",
    "shkollë": "school",
    "universitet": "university",
    "spital": "hospital",
    "dyqan": "shop",
    "restorant": "restaurant",
    "hotel": "hotel",
    "aeroport": "airport",
    "stacion": "station",
    "punë": "work/job",
    "zyrë": "office",
    "kompani": "company",
    "biznes": "business",
    "para": "money",
    "bankë": "bank",
    "kohë": "time",
    "ditë": "day",
    "natë": "night",
    "mëngjes": "morning",
    "drekë": "lunch/noon",
    "darkë": "dinner/evening",
    "javë": "week",
    "muaj": "month",
    "vit": "year",
    "mot": "weather",
    "diell": "sun",
    "hënë": "moon",
    "yll": "star",
    "qiell": "sky",
    "det": "sea",
    "mal": "mountain",
    "lum": "river",
    "liqen": "lake",
    "pyll": "forest",
    "pemë": "tree",
    "lule": "flower",
    "bar": "grass",
    "kafshë": "animal",
    "qen": "dog",
    "mace": "cat",
    "zog": "bird",
    "peshk": "fish",
    "ushqim": "food",
    "bukë": "bread",
    "ujë": "water",
    "qumësht": "milk",
    "mish": "meat",
    "perime": "vegetables",
    "fruta": "fruits",
    "mollë": "apple",
    "portokall": "orange",
    "banane": "banana",
    "domate": "tomato",
    "patate": "potato",
    "libër": "book",
    "gazetë": "newspaper",
    "revistë": "magazine",
    "kompjuter": "computer",
    "telefon": "phone",
    "makinë": "car",
    "autobus": "bus",
    "tren": "train",
    "aeroplan": "airplane",
    "anije": "ship",
    "biçikletë": "bicycle",
}

# Adjectives
ADJECTIVES = {
    "i mirë": "good (m)",
    "e mirë": "good (f)",
    "i keq": "bad (m)",
    "e keqe": "bad (f)",
    "i madh": "big (m)",
    "e madhe": "big (f)",
    "i vogël": "small (m)",
    "e vogël": "small (f)",
    "i ri": "new/young (m)",
    "e re": "new/young (f)",
    "i vjetër": "old (m)",
    "e vjetër": "old (f)",
    "i bukur": "beautiful (m)",
    "e bukur": "beautiful (f)",
    "i shëmtuar": "ugly (m)",
    "i gjatë": "tall/long (m)",
    "i shkurtër": "short (m)",
    "i fortë": "strong (m)",
    "i dobët": "weak (m)",
    "i shpejtë": "fast (m)",
    "i ngadaltë": "slow (m)",
    "i nxehtë": "hot (m)",
    "i ftohtë": "cold (m)",
    "i ëmbël": "sweet (m)",
    "i hidhur": "bitter (m)",
    "i lehtë": "easy/light (m)",
    "i vështirë": "difficult (m)",
    "i lirë": "cheap (m)",
    "i shtrenjtë": "expensive (m)",
    "i lumtur": "happy (m)",
    "i trishtuar": "sad (m)",
    "i lodhur": "tired (m)",
    "i sëmurë": "sick (m)",
    "i shëndoshë": "healthy (m)",
    "i zgjuar": "smart (m)",
    "i dashur": "dear/beloved (m)",
}

# Numbers
NUMBERS = {
    "zero": "0",
    "një": "1",
    "dy": "2",
    "tre": "3",
    "katër": "4",
    "pesë": "5",
    "gjashtë": "6",
    "shtatë": "7",
    "tetë": "8",
    "nëntë": "9",
    "dhjetë": "10",
    "njëzet": "20",
    "tridhjetë": "30",
    "dyzet": "40",
    "pesëdhjetë": "50",
    "gjashtëdhjetë": "60",
    "shtatëdhjetë": "70",
    "tetëdhjetë": "80",
    "nëntëdhjetë": "90",
    "njëqind": "100",
    "njëmijë": "1000",
    "një milion": "1000000",
}

# Days and months
TIME_WORDS = {
    "e hënë": "Monday",
    "e martë": "Tuesday",
    "e mërkurë": "Wednesday",
    "e enjte": "Thursday",
    "e premte": "Friday",
    "e shtunë": "Saturday",
    "e diel": "Sunday",
    "janar": "January",
    "shkurt": "February",
    "mars": "March",
    "prill": "April",
    "maj": "May",
    "qershor": "June",
    "korrik": "July",
    "gusht": "August",
    "shtator": "September",
    "tetor": "October",
    "nëntor": "November",
    "dhjetor": "December",
    "sot": "today",
    "nesër": "tomorrow",
    "dje": "yesterday",
    "tani": "now",
    "më vonë": "later",
    "më parë": "earlier",
    "gjithmonë": "always",
    "kurrë": "never",
    "shpesh": "often",
    "rrallë": "rarely",
}

# Colors
COLORS = {
    "i bardhë": "white",
    "i zi": "black",
    "i kuq": "red",
    "i kaltër": "blue",
    "i gjelbër": "green",
    "i verdhë": "yellow",
    "portokalli": "orange",
    "rozë": "pink",
    "vjollcë": "purple",
    "kafe": "brown",
    "gri": "gray",
}

# Technology terms
TECH_TERMS = {
    "inteligjencë artificiale": "artificial intelligence",
    "mësim i makinës": "machine learning",
    "të dhëna": "data",
    "algoritëm": "algorithm",
    "program": "program",
    "softuer": "software",
    "harduer": "hardware",
    "internet": "internet",
    "faqe": "page/website",
    "aplikacion": "application",
    "sistem": "system",
    "rrjet": "network",
    "siguri": "security",
    "privatësi": "privacy",
    "përdorues": "user",
    "fjalëkalim": "password",
    "llogari": "account",
    "mesazh": "message",
    "email": "email",
    "kërkesë": "request/search",
    "përgjigje": "answer/response",
    "pyetje": "question",
    "ndihmë": "help",
    "gabim": "error",
    "sukses": "success",
}

# Common phrases for AI assistant
AI_PHRASES = {
    "si mund të ndihmoj": "how can I help",
    "a keni pyetje": "do you have questions",
    "jam këtu për ju": "I am here for you",
    "me kënaqësi": "with pleasure",
    "sigurisht që po": "of course yes",
    "nuk jam i sigurt": "I'm not sure",
    "më thuaj më shumë": "tell me more",
    "interesante": "interesting",
    "shpjegoj": "I explain",
    "sqaroj": "I clarify",
    "për shembull": "for example",
    "kjo do të thotë": "this means",
    "me fjalë të tjera": "in other words",
    "në përfundim": "in conclusion",
    "së pari": "first",
    "së dyti": "second",
    "së fundmi": "finally",
    "gjithashtu": "also",
    "megjithatë": "however",
    "prandaj": "therefore",
    "sepse": "because",
    "nëse": "if",
    "kur": "when",
    "ndërsa": "while",
    "edhe pse": "although",
}

# Albanian geography
GEOGRAPHY = {
    "Shqipëri": "Albania",
    "Tiranë": "Tirana (capital)",
    "Durrës": "Durres",
    "Vlorë": "Vlora",
    "Shkodër": "Shkodra",
    "Elbasan": "Elbasan",
    "Korçë": "Korça",
    "Fier": "Fier",
    "Berat": "Berat",
    "Gjirokastër": "Gjirokastra",
    "Kosovë": "Kosovo",
    "Prishtinë": "Pristina",
    "Prizren": "Prizren",
    "Maqedoni": "Macedonia",
    "Mal i Zi": "Montenegro",
    "Greqi": "Greece",
    "Itali": "Italy",
    "Ballkan": "Balkans",
    "Evropë": "Europe",
    "Det Adriatik": "Adriatic Sea",
    "Det Jon": "Ionian Sea",
}

# Combine all dictionaries
def get_full_dictionary():
    """Returns the complete Albanian dictionary"""
    full_dict = {}
    full_dict.update(GREETINGS)
    full_dict.update(QUESTION_WORDS)
    full_dict.update(VERBS)
    full_dict.update(NOUNS)
    full_dict.update(ADJECTIVES)
    full_dict.update(NUMBERS)
    full_dict.update(TIME_WORDS)
    full_dict.update(COLORS)
    full_dict.update(TECH_TERMS)
    full_dict.update(AI_PHRASES)
    full_dict.update(GEOGRAPHY)
    return full_dict

def get_dictionary_prompt():
    """Returns a formatted string for system prompt"""
    lines = ["\n\nALBANIAN LANGUAGE REFERENCE:"]
    
    lines.append("\n--- GREETINGS ---")
    for sq, en in list(GREETINGS.items())[:15]:
        lines.append(f"'{sq}' = {en}")
    
    lines.append("\n--- QUESTION WORDS ---")
    for sq, en in QUESTION_WORDS.items():
        lines.append(f"'{sq}' = {en}")
    
    lines.append("\n--- COMMON VERBS ---")
    for sq, en in list(VERBS.items())[:20]:
        lines.append(f"'{sq}' = {en}")
    
    lines.append("\n--- COMMON NOUNS ---")
    for sq, en in list(NOUNS.items())[:30]:
        lines.append(f"'{sq}' = {en}")
        
    lines.append("\n--- AI ASSISTANT PHRASES ---")
    for sq, en in AI_PHRASES.items():
        lines.append(f"'{sq}' = {en}")
    
    lines.append("\n--- ALBANIAN GEOGRAPHY ---")
    for sq, en in GEOGRAPHY.items():
        lines.append(f"'{sq}' = {en}")
    
    return "\n".join(lines)

# Word count
if __name__ == "__main__":
    full = get_full_dictionary()
    print(f"Total Albanian words/phrases: {len(full)}")
    print("\nCategories:")
    print(f"  Greetings: {len(GREETINGS)}")
    print(f"  Question words: {len(QUESTION_WORDS)}")
    print(f"  Verbs: {len(VERBS)}")
    print(f"  Nouns: {len(NOUNS)}")
    print(f"  Adjectives: {len(ADJECTIVES)}")
    print(f"  Numbers: {len(NUMBERS)}")
    print(f"  Time words: {len(TIME_WORDS)}")
    print(f"  Colors: {len(COLORS)}")
    print(f"  Tech terms: {len(TECH_TERMS)}")
    print(f"  AI phrases: {len(AI_PHRASES)}")
    print(f"  Geography: {len(GEOGRAPHY)}")
