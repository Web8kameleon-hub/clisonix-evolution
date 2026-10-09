# -*- coding: utf-8 -*-
"""
🌍 EASTERN EUROPE & BALKANS - COMPLETE DATA SOURCES
====================================================
300+ Free Open Data Sources from Eastern Europe & Balkans

Countries Covered:
- Russia 🇷🇺
- Ukraine 🇺🇦
- Belarus 🇧🇾
- Moldova 🇲🇩
- Romania 🇷🇴
- Bulgaria 🇧🇬
- Serbia 🇷🇸
- Croatia 🇭🇷
- Slovenia 🇸🇮
- Bosnia & Herzegovina 🇧🇦
- Montenegro 🇲🇪
- North Macedonia 🇲🇰
- Albania 🇦🇱
- Kosovo 🇽🇰
- Czech Republic 🇨🇿
- Slovakia 🇸🇰
- Hungary 🇭🇺
- Lithuania 🇱🇹
- Latvia 🇱🇻
- Estonia 🇪🇪
- Greece 🇬🇷
- Cyprus 🇨🇾
"""

from dataclasses import dataclass
from typing import List
from enum import Enum

class SourceCategory(Enum):
    GOVERNMENT = "government"
    UNIVERSITY = "university"
    HOSPITAL = "hospital"
    BANK = "bank"
    INDUSTRY = "industry"
    NEWS = "news"
    CULTURE = "culture"
    RESEARCH = "research"
    STATISTICS = "statistics"
    TRANSPORT = "transport"
    ENERGY = "energy"
    TELECOM = "telecom"
    TECHNOLOGY = "technology"
    SPORT = "sport"
    TOURISM = "tourism"

@dataclass
class DataSource:
    url: str
    name: str
    category: SourceCategory
    country: str
    description: str = ""
    api_available: bool = False
    license: str = "Public"

# ============================================================
# 🇷🇺 RUSSIA
# ============================================================

RUSSIA_SOURCES = [
    DataSource("https://www.gov.ru/", "Russia Government", SourceCategory.GOVERNMENT, "RU", "Government portal"),
    DataSource("https://www.duma.gov.ru/", "State Duma", SourceCategory.GOVERNMENT, "RU", "Parliament lower house"),
    DataSource("https://council.gov.ru/", "Federation Council", SourceCategory.GOVERNMENT, "RU", "Parliament upper house"),
    DataSource("https://rosstat.gov.ru/", "Rosstat", SourceCategory.STATISTICS, "RU", "Federal Statistics", True),
    DataSource("https://data.gov.ru/", "Open Data Russia", SourceCategory.STATISTICS, "RU", "Open data", True),
    DataSource("https://www.msu.ru/", "Moscow State University", SourceCategory.UNIVERSITY, "RU", "MGU"),
    DataSource("https://www.spbu.ru/", "Saint Petersburg State University", SourceCategory.UNIVERSITY, "RU", "SPbGU"),
    DataSource("https://mipt.ru/", "MIPT", SourceCategory.UNIVERSITY, "RU", "Physics & Tech"),
    DataSource("https://www.hse.ru/", "HSE University", SourceCategory.UNIVERSITY, "RU", "Higher School of Economics"),
    DataSource("https://www.bmstu.ru/", "Bauman Moscow State Tech", SourceCategory.UNIVERSITY, "RU", "BMSTU"),
    DataSource("https://www.itmo.ru/", "ITMO University", SourceCategory.UNIVERSITY, "RU", "IT & Optics"),
    DataSource("https://cbr.ru/", "Central Bank of Russia", SourceCategory.BANK, "RU", "Central bank", True),
    DataSource("https://www.moex.com/", "Moscow Exchange", SourceCategory.BANK, "RU", "Stock Exchange", True),
    DataSource("https://www.sberbank.ru/", "Sberbank", SourceCategory.BANK, "RU", "Major bank"),
    DataSource("https://www.vtb.ru/", "VTB", SourceCategory.BANK, "RU", "Major bank"),
    DataSource("https://www.gazprombank.ru/", "Gazprombank", SourceCategory.BANK, "RU", "Major bank"),
    DataSource("https://www.tinkoff.ru/", "Tinkoff", SourceCategory.BANK, "RU", "Digital bank"),
    DataSource("https://www.gazprom.ru/", "Gazprom", SourceCategory.ENERGY, "RU", "Gas company"),
    DataSource("https://www.rosneft.ru/", "Rosneft", SourceCategory.ENERGY, "RU", "Oil company"),
    DataSource("https://www.lukoil.ru/", "Lukoil", SourceCategory.ENERGY, "RU", "Oil company"),
    DataSource("https://www.aeroflot.ru/", "Aeroflot", SourceCategory.TRANSPORT, "RU", "National airline"),
    DataSource("https://www.s7.ru/", "S7 Airlines", SourceCategory.TRANSPORT, "RU", "Airline"),
    DataSource("https://pass.rzd.ru/", "RZD", SourceCategory.TRANSPORT, "RU", "Railways", True),
    DataSource("https://www.megafon.ru/", "MegaFon", SourceCategory.TELECOM, "RU", "Telecom"),
    DataSource("https://www.mts.ru/", "MTS", SourceCategory.TELECOM, "RU", "Telecom"),
    DataSource("https://www.beeline.ru/", "Beeline", SourceCategory.TELECOM, "RU", "Telecom"),
    DataSource("https://www.yandex.ru/", "Yandex", SourceCategory.TECHNOLOGY, "RU", "Tech giant"),
    DataSource("https://www.mail.ru/", "VK / Mail.ru", SourceCategory.TECHNOLOGY, "RU", "Tech/social"),
    DataSource("https://tass.ru/", "TASS", SourceCategory.NEWS, "RU", "News agency", True),
    DataSource("https://ria.ru/", "RIA Novosti", SourceCategory.NEWS, "RU", "News agency"),
    DataSource("https://www.interfax.ru/", "Interfax", SourceCategory.NEWS, "RU", "News agency"),
    DataSource("https://www.kommersant.ru/", "Kommersant", SourceCategory.NEWS, "RU", "Business newspaper"),
    DataSource("https://www.rbc.ru/", "RBC", SourceCategory.NEWS, "RU", "Business news"),
    DataSource("https://meduza.io/", "Meduza", SourceCategory.NEWS, "RU", "Independent news"),
    DataSource("https://www.hermitagemuseum.org/", "Hermitage Museum", SourceCategory.CULTURE, "RU", "Art museum"),
    DataSource("https://www.kreml.ru/", "Moscow Kremlin Museums", SourceCategory.CULTURE, "RU", "Museums"),
    DataSource("https://www.russia.travel/", "Russia Travel", SourceCategory.TOURISM, "RU", "Tourism", True),
    DataSource("https://www.rfs.ru/", "RFS", SourceCategory.SPORT, "RU", "Football federation"),
    DataSource("https://www.premierliga.ru/", "Russian Premier League", SourceCategory.SPORT, "RU", "Football league"),
    DataSource("https://www.khl.ru/", "KHL", SourceCategory.SPORT, "RU", "Hockey league", True),
]

# ============================================================
# 🇺🇦 UKRAINE
# ============================================================

UKRAINE_SOURCES = [
    DataSource("https://www.kmu.gov.ua/", "Ukraine Government", SourceCategory.GOVERNMENT, "UA", "Government"),
    DataSource("https://www.rada.gov.ua/", "Verkhovna Rada", SourceCategory.GOVERNMENT, "UA", "Parliament"),
    DataSource("https://ukrstat.gov.ua/", "State Statistics Service", SourceCategory.STATISTICS, "UA", "Statistics", True),
    DataSource("https://data.gov.ua/", "Open Data Ukraine", SourceCategory.STATISTICS, "UA", "Open data", True),
    DataSource("https://www.univ.kiev.ua/", "Taras Shevchenko National University", SourceCategory.UNIVERSITY, "UA", "Top university"),
    DataSource("https://kpi.ua/", "Igor Sikorsky KPI", SourceCategory.UNIVERSITY, "UA", "Tech university"),
    DataSource("https://www.lnu.edu.ua/", "Lviv National University", SourceCategory.UNIVERSITY, "UA", "LNU"),
    DataSource("https://bank.gov.ua/", "National Bank of Ukraine", SourceCategory.BANK, "UA", "Central bank", True),
    DataSource("https://pfts.ua/", "PFTS Stock Exchange", SourceCategory.BANK, "UA", "Stock Exchange"),
    DataSource("https://privatbank.ua/", "PrivatBank", SourceCategory.BANK, "UA", "Major bank"),
    DataSource("https://www.flyuia.com/", "Ukraine International Airlines", SourceCategory.TRANSPORT, "UA", "National airline"),
    DataSource("https://www.uz.gov.ua/", "Ukrzaliznytsia", SourceCategory.TRANSPORT, "UA", "Railways"),
    DataSource("https://www.ukrinform.ua/", "Ukrinform", SourceCategory.NEWS, "UA", "News agency"),
    DataSource("https://www.unian.ua/", "UNIAN", SourceCategory.NEWS, "UA", "News agency"),
    DataSource("https://www.pravda.com.ua/", "Ukrainska Pravda", SourceCategory.NEWS, "UA", "News portal"),
    DataSource("https://www.visitukraine.today/", "Visit Ukraine", SourceCategory.TOURISM, "UA", "Tourism", True),
    DataSource("https://uaf.ua/", "UAF", SourceCategory.SPORT, "UA", "Football federation"),
    DataSource("https://upl.ua/", "Ukrainian Premier League", SourceCategory.SPORT, "UA", "Football league"),
]

# ============================================================
# 🇧🇾 BELARUS
# ============================================================

BELARUS_SOURCES = [
    DataSource("https://www.gov.by/", "Belarus Government", SourceCategory.GOVERNMENT, "BY", "Government"),
    DataSource("https://house.gov.by/", "House of Representatives", SourceCategory.GOVERNMENT, "BY", "Parliament"),
    DataSource("https://www.belstat.gov.by/", "Belstat", SourceCategory.STATISTICS, "BY", "Statistics", True),
    DataSource("https://www.bsu.by/", "Belarusian State University", SourceCategory.UNIVERSITY, "BY", "BSU"),
    DataSource("https://www.bntu.by/", "BNTU", SourceCategory.UNIVERSITY, "BY", "Tech university"),
    DataSource("https://www.nbrb.by/", "National Bank of Belarus", SourceCategory.BANK, "BY", "Central bank", True),
    DataSource("https://www.belavia.by/", "Belavia", SourceCategory.TRANSPORT, "BY", "National airline"),
    DataSource("https://www.belta.by/", "BelTA", SourceCategory.NEWS, "BY", "News agency"),
    DataSource("https://www.abff.by/", "ABFF", SourceCategory.SPORT, "BY", "Football federation"),
]

# ============================================================
# 🇲🇩 MOLDOVA
# ============================================================

MOLDOVA_SOURCES = [
    DataSource("https://gov.md/", "Moldova Government", SourceCategory.GOVERNMENT, "MD", "Government"),
    DataSource("https://www.parlament.md/", "Parliament of Moldova", SourceCategory.GOVERNMENT, "MD", "Parliament"),
    DataSource("https://statistica.gov.md/", "National Bureau of Statistics", SourceCategory.STATISTICS, "MD", "Statistics", True),
    DataSource("https://www.usm.md/", "State University of Moldova", SourceCategory.UNIVERSITY, "MD", "Top university"),
    DataSource("https://www.bnm.md/", "National Bank of Moldova", SourceCategory.BANK, "MD", "Central bank", True),
    DataSource("https://www.airmoldova.md/", "Air Moldova", SourceCategory.TRANSPORT, "MD", "National airline"),
    DataSource("https://www.moldpres.md/", "Moldpres", SourceCategory.NEWS, "MD", "News agency"),
    DataSource("https://www.fmf.md/", "FMF", SourceCategory.SPORT, "MD", "Football federation"),
]

# ============================================================
# 🇷🇴 ROMANIA
# ============================================================

ROMANIA_SOURCES = [
    DataSource("https://www.gov.ro/", "Romania Government", SourceCategory.GOVERNMENT, "RO", "Government"),
    DataSource("https://www.cdep.ro/", "Chamber of Deputies", SourceCategory.GOVERNMENT, "RO", "Parliament"),
    DataSource("https://www.senat.ro/", "Senate", SourceCategory.GOVERNMENT, "RO", "Senate"),
    DataSource("https://insse.ro/", "INSSE", SourceCategory.STATISTICS, "RO", "Statistics", True),
    DataSource("https://data.gov.ro/", "Open Data Romania", SourceCategory.STATISTICS, "RO", "Open data", True),
    DataSource("https://unibuc.ro/", "University of Bucharest", SourceCategory.UNIVERSITY, "RO", "Top university"),
    DataSource("https://www.ubbcluj.ro/", "Babeș-Bolyai University", SourceCategory.UNIVERSITY, "RO", "UBB"),
    DataSource("https://www.upb.ro/", "Politehnica Bucharest", SourceCategory.UNIVERSITY, "RO", "Tech university"),
    DataSource("https://www.bnr.ro/", "National Bank of Romania", SourceCategory.BANK, "RO", "Central bank", True),
    DataSource("https://www.bvb.ro/", "Bucharest Stock Exchange", SourceCategory.BANK, "RO", "Stock Exchange", True),
    DataSource("https://www.bcr.ro/", "BCR", SourceCategory.BANK, "RO", "Major bank"),
    DataSource("https://www.tarom.ro/", "TAROM", SourceCategory.TRANSPORT, "RO", "National airline"),
    DataSource("https://www.cfr.ro/", "CFR", SourceCategory.TRANSPORT, "RO", "Railways"),
    DataSource("https://www.agerpres.ro/", "Agerpres", SourceCategory.NEWS, "RO", "News agency"),
    DataSource("https://www.digi24.ro/", "Digi24", SourceCategory.NEWS, "RO", "News network"),
    DataSource("https://www.hotnews.ro/", "HotNews", SourceCategory.NEWS, "RO", "News portal"),
    DataSource("https://www.romania.travel/", "Romania Travel", SourceCategory.TOURISM, "RO", "Tourism", True),
    DataSource("https://www.frf.ro/", "FRF", SourceCategory.SPORT, "RO", "Football federation"),
    DataSource("https://www.lpf.ro/", "Liga 1", SourceCategory.SPORT, "RO", "Football league"),
]

# ============================================================
# 🇧🇬 BULGARIA
# ============================================================

BULGARIA_SOURCES = [
    DataSource("https://www.gov.bg/", "Bulgaria Government", SourceCategory.GOVERNMENT, "BG", "Government"),
    DataSource("https://www.parliament.bg/", "National Assembly", SourceCategory.GOVERNMENT, "BG", "Parliament"),
    DataSource("https://www.nsi.bg/", "NSI Bulgaria", SourceCategory.STATISTICS, "BG", "Statistics", True),
    DataSource("https://data.egov.bg/", "Open Data Bulgaria", SourceCategory.STATISTICS, "BG", "Open data", True),
    DataSource("https://www.uni-sofia.bg/", "Sofia University", SourceCategory.UNIVERSITY, "BG", "Top university"),
    DataSource("https://www.tu-sofia.bg/", "Technical University Sofia", SourceCategory.UNIVERSITY, "BG", "Tech university"),
    DataSource("https://www.bnb.bg/", "Bulgarian National Bank", SourceCategory.BANK, "BG", "Central bank", True),
    DataSource("https://www.bse-sofia.bg/", "Bulgarian Stock Exchange", SourceCategory.BANK, "BG", "Stock Exchange", True),
    DataSource("https://www.air.bg/", "Bulgaria Air", SourceCategory.TRANSPORT, "BG", "National airline"),
    DataSource("https://www.bdz.bg/", "BDZ", SourceCategory.TRANSPORT, "BG", "Railways"),
    DataSource("https://www.bta.bg/", "BTA", SourceCategory.NEWS, "BG", "News agency"),
    DataSource("https://www.novinite.com/", "Novinite", SourceCategory.NEWS, "BG", "News portal"),
    DataSource("https://bulgariatravel.org/", "Bulgaria Travel", SourceCategory.TOURISM, "BG", "Tourism", True),
    DataSource("https://bfu.bg/", "BFU", SourceCategory.SPORT, "BG", "Football federation"),
]

# ============================================================
# 🇷🇸 SERBIA
# ============================================================

SERBIA_SOURCES = [
    DataSource("https://www.srbija.gov.rs/", "Serbia Government", SourceCategory.GOVERNMENT, "RS", "Government"),
    DataSource("https://www.parlament.gov.rs/", "National Assembly", SourceCategory.GOVERNMENT, "RS", "Parliament"),
    DataSource("https://www.stat.gov.rs/", "Statistics Serbia", SourceCategory.STATISTICS, "RS", "Statistics", True),
    DataSource("https://data.gov.rs/", "Open Data Serbia", SourceCategory.STATISTICS, "RS", "Open data", True),
    DataSource("https://www.bg.ac.rs/", "University of Belgrade", SourceCategory.UNIVERSITY, "RS", "Top university"),
    DataSource("https://www.uns.ac.rs/", "University of Novi Sad", SourceCategory.UNIVERSITY, "RS", "UNS"),
    DataSource("https://www.nbs.rs/", "National Bank of Serbia", SourceCategory.BANK, "RS", "Central bank", True),
    DataSource("https://www.belex.rs/", "Belgrade Stock Exchange", SourceCategory.BANK, "RS", "Stock Exchange"),
    DataSource("https://www.airserbia.com/", "Air Serbia", SourceCategory.TRANSPORT, "RS", "National airline"),
    DataSource("https://www.srbvoz.rs/", "Srbija Voz", SourceCategory.TRANSPORT, "RS", "Railways"),
    DataSource("https://www.tanjug.rs/", "Tanjug", SourceCategory.NEWS, "RS", "News agency"),
    DataSource("https://www.b92.net/", "B92", SourceCategory.NEWS, "RS", "News portal"),
    DataSource("https://www.serbia.travel/", "Serbia Travel", SourceCategory.TOURISM, "RS", "Tourism", True),
    DataSource("https://www.fss.rs/", "FSS", SourceCategory.SPORT, "RS", "Football federation"),
]

# ============================================================
# 🇭🇷 CROATIA
# ============================================================

CROATIA_SOURCES = [
    DataSource("https://vlada.gov.hr/", "Croatia Government", SourceCategory.GOVERNMENT, "HR", "Government"),
    DataSource("https://www.sabor.hr/", "Croatian Parliament", SourceCategory.GOVERNMENT, "HR", "Parliament"),
    DataSource("https://www.dzs.hr/", "Croatian Bureau of Statistics", SourceCategory.STATISTICS, "HR", "Statistics", True),
    DataSource("https://data.gov.hr/", "Open Data Croatia", SourceCategory.STATISTICS, "HR", "Open data", True),
    DataSource("https://www.unizg.hr/", "University of Zagreb", SourceCategory.UNIVERSITY, "HR", "Top university"),
    DataSource("https://www.unist.hr/", "University of Split", SourceCategory.UNIVERSITY, "HR", "Split"),
    DataSource("https://www.hnb.hr/", "Croatian National Bank", SourceCategory.BANK, "HR", "Central bank", True),
    DataSource("https://www.zse.hr/", "Zagreb Stock Exchange", SourceCategory.BANK, "HR", "Stock Exchange", True),
    DataSource("https://www.croatiaairlines.com/", "Croatia Airlines", SourceCategory.TRANSPORT, "HR", "National airline"),
    DataSource("https://www.hzpp.hr/", "HŽPP", SourceCategory.TRANSPORT, "HR", "Railways"),
    DataSource("https://www.hina.hr/", "HINA", SourceCategory.NEWS, "HR", "News agency"),
    DataSource("https://www.jutarnji.hr/", "Jutarnji list", SourceCategory.NEWS, "HR", "Major newspaper"),
    DataSource("https://croatia.hr/", "Croatia.hr", SourceCategory.TOURISM, "HR", "Tourism", True),
    DataSource("https://hns-cff.hr/", "HNS", SourceCategory.SPORT, "HR", "Football federation"),
]

# ============================================================
# 🇸🇮 SLOVENIA
# ============================================================

SLOVENIA_SOURCES = [
    DataSource("https://www.gov.si/", "Slovenia Government", SourceCategory.GOVERNMENT, "SI", "Government"),
    DataSource("https://www.dz-rs.si/", "National Assembly", SourceCategory.GOVERNMENT, "SI", "Parliament"),
    DataSource("https://www.stat.si/", "Statistics Slovenia", SourceCategory.STATISTICS, "SI", "Statistics", True),
    DataSource("https://podatki.gov.si/", "Open Data Slovenia", SourceCategory.STATISTICS, "SI", "Open data", True),
    DataSource("https://www.uni-lj.si/", "University of Ljubljana", SourceCategory.UNIVERSITY, "SI", "Top university"),
    DataSource("https://www.um.si/", "University of Maribor", SourceCategory.UNIVERSITY, "SI", "Maribor"),
    DataSource("https://www.bsi.si/", "Bank of Slovenia", SourceCategory.BANK, "SI", "Central bank", True),
    DataSource("https://www.ljse.si/", "Ljubljana Stock Exchange", SourceCategory.BANK, "SI", "Stock Exchange"),
    DataSource("https://www.adria.si/", "Adria Airways", SourceCategory.TRANSPORT, "SI", "Airline"),
    DataSource("https://www.sta.si/", "STA", SourceCategory.NEWS, "SI", "News agency"),
    DataSource("https://www.slovenia.info/", "Slovenia.info", SourceCategory.TOURISM, "SI", "Tourism", True),
    DataSource("https://www.nzs.si/", "NZS", SourceCategory.SPORT, "SI", "Football federation"),
]

# ============================================================
# 🇧🇦 BOSNIA & HERZEGOVINA
# ============================================================

BOSNIA_SOURCES = [
    DataSource("https://www.vijeceministara.gov.ba/", "Council of Ministers", SourceCategory.GOVERNMENT, "BA", "Government"),
    DataSource("https://www.parlament.ba/", "Parliamentary Assembly", SourceCategory.GOVERNMENT, "BA", "Parliament"),
    DataSource("https://bhas.gov.ba/", "Agency for Statistics", SourceCategory.STATISTICS, "BA", "Statistics", True),
    DataSource("https://www.unsa.ba/", "University of Sarajevo", SourceCategory.UNIVERSITY, "BA", "Top university"),
    DataSource("https://www.cbbh.ba/", "Central Bank of BiH", SourceCategory.BANK, "BA", "Central bank", True),
    DataSource("https://www.sase.ba/", "Sarajevo Stock Exchange", SourceCategory.BANK, "BA", "Stock Exchange"),
    DataSource("https://www.flyvia.ba/", "FlyBosnia", SourceCategory.TRANSPORT, "BA", "Airline"),
    DataSource("https://www.fena.ba/", "FENA", SourceCategory.NEWS, "BA", "News agency"),
    DataSource("https://www.bhtourism.ba/", "BiH Tourism", SourceCategory.TOURISM, "BA", "Tourism", True),
    DataSource("https://www.nfsbih.ba/", "NFSBiH", SourceCategory.SPORT, "BA", "Football federation"),
]

# ============================================================
# 🇲🇪 MONTENEGRO
# ============================================================

MONTENEGRO_SOURCES = [
    DataSource("https://www.gov.me/", "Montenegro Government", SourceCategory.GOVERNMENT, "ME", "Government"),
    DataSource("https://www.skupstina.me/", "Parliament of Montenegro", SourceCategory.GOVERNMENT, "ME", "Parliament"),
    DataSource("https://www.monstat.org/", "MONSTAT", SourceCategory.STATISTICS, "ME", "Statistics", True),
    DataSource("https://www.ucg.ac.me/", "University of Montenegro", SourceCategory.UNIVERSITY, "ME", "Top university"),
    DataSource("https://www.cbcg.me/", "Central Bank of Montenegro", SourceCategory.BANK, "ME", "Central bank", True),
    DataSource("https://www.montenegroairlines.com/", "Air Montenegro", SourceCategory.TRANSPORT, "ME", "Airline"),
    DataSource("https://mina.news/", "MINA", SourceCategory.NEWS, "ME", "News agency"),
    DataSource("https://www.montenegro.travel/", "Montenegro Travel", SourceCategory.TOURISM, "ME", "Tourism", True),
    DataSource("https://www.fscg.me/", "FSCG", SourceCategory.SPORT, "ME", "Football federation"),
]

# ============================================================
# 🇲🇰 NORTH MACEDONIA
# ============================================================

NORTH_MACEDONIA_SOURCES = [
    DataSource("https://vlada.mk/", "North Macedonia Government", SourceCategory.GOVERNMENT, "MK", "Government"),
    DataSource("https://www.sobranie.mk/", "Assembly", SourceCategory.GOVERNMENT, "MK", "Parliament"),
    DataSource("https://www.stat.gov.mk/", "State Statistical Office", SourceCategory.STATISTICS, "MK", "Statistics", True),
    DataSource("https://www.ukim.edu.mk/", "Ss. Cyril and Methodius University", SourceCategory.UNIVERSITY, "MK", "Top university"),
    DataSource("https://www.nbrm.mk/", "National Bank", SourceCategory.BANK, "MK", "Central bank", True),
    DataSource("https://www.mse.mk/", "Macedonian Stock Exchange", SourceCategory.BANK, "MK", "Stock Exchange"),
    DataSource("https://www.mia.mk/", "MIA", SourceCategory.NEWS, "MK", "News agency"),
    DataSource("https://www.exploringmacedonia.com/", "Macedonia Tourism", SourceCategory.TOURISM, "MK", "Tourism", True),
    DataSource("https://www.ffm.mk/", "FFM", SourceCategory.SPORT, "MK", "Football federation"),
]

# ============================================================
# 🇦🇱 ALBANIA
# ============================================================

ALBANIA_SOURCES = [
    DataSource("https://www.kryeministria.al/", "Albania Government", SourceCategory.GOVERNMENT, "AL", "Prime Minister"),
    DataSource("https://www.parlament.al/", "Assembly of Albania", SourceCategory.GOVERNMENT, "AL", "Parliament"),
    DataSource("https://www.instat.gov.al/", "INSTAT", SourceCategory.STATISTICS, "AL", "Statistics", True),
    DataSource("https://opendata.gov.al/", "Open Data Albania", SourceCategory.STATISTICS, "AL", "Open data", True),
    DataSource("https://www.unitir.edu.al/", "University of Tirana", SourceCategory.UNIVERSITY, "AL", "Top university"),
    DataSource("https://upt.al/", "Polytechnic University of Tirana", SourceCategory.UNIVERSITY, "AL", "Tech university"),
    DataSource("https://www.bankofalbania.org/", "Bank of Albania", SourceCategory.BANK, "AL", "Central bank", True),
    DataSource("https://www.bfrsh.al/", "Albanian Securities Exchange", SourceCategory.BANK, "AL", "Stock Exchange"),
    DataSource("https://www.albcontrol.al/", "Albcontrol", SourceCategory.TRANSPORT, "AL", "Air control"),
    DataSource("https://www.ata.gov.al/", "ATA", SourceCategory.NEWS, "AL", "News agency"),
    DataSource("https://top-channel.tv/", "Top Channel", SourceCategory.NEWS, "AL", "TV news"),
    DataSource("https://albania.al/", "Albania.al", SourceCategory.TOURISM, "AL", "Tourism", True),
    DataSource("https://fshf.org/", "FSHF", SourceCategory.SPORT, "AL", "Football federation"),
    DataSource("https://www.abissnet.al/", "Superliga", SourceCategory.SPORT, "AL", "Football league"),
]

# ============================================================
# 🇽🇰 KOSOVO
# ============================================================

KOSOVO_SOURCES = [
    DataSource("https://kryeministri.rks-gov.net/", "Kosovo Government", SourceCategory.GOVERNMENT, "XK", "Prime Minister"),
    DataSource("https://www.kuvendikosoves.org/", "Assembly of Kosovo", SourceCategory.GOVERNMENT, "XK", "Parliament"),
    DataSource("https://ask.rks-gov.net/", "Kosovo Agency of Statistics", SourceCategory.STATISTICS, "XK", "Statistics", True),
    DataSource("https://www.uni-pr.edu/", "University of Pristina", SourceCategory.UNIVERSITY, "XK", "Top university"),
    DataSource("https://bqk-kos.org/", "Central Bank of Kosovo", SourceCategory.BANK, "XK", "Central bank", True),
    DataSource("https://koha.net/", "Koha", SourceCategory.NEWS, "XK", "News portal"),
    DataSource("https://www.visitkosovo.com/", "Visit Kosovo", SourceCategory.TOURISM, "XK", "Tourism", True),
    DataSource("https://www.ffk-kosova.com/", "FFK", SourceCategory.SPORT, "XK", "Football federation"),
]

# ============================================================
# 🇨🇿 CZECH REPUBLIC
# ============================================================

CZECH_SOURCES = [
    DataSource("https://www.vlada.cz/", "Czech Government", SourceCategory.GOVERNMENT, "CZ", "Government"),
    DataSource("https://www.psp.cz/", "Chamber of Deputies", SourceCategory.GOVERNMENT, "CZ", "Parliament"),
    DataSource("https://www.senat.cz/", "Senate", SourceCategory.GOVERNMENT, "CZ", "Senate"),
    DataSource("https://www.czso.cz/", "Czech Statistical Office", SourceCategory.STATISTICS, "CZ", "Statistics", True),
    DataSource("https://data.gov.cz/", "Open Data Czech", SourceCategory.STATISTICS, "CZ", "Open data", True),
    DataSource("https://cuni.cz/", "Charles University", SourceCategory.UNIVERSITY, "CZ", "Top university"),
    DataSource("https://www.cvut.cz/", "Czech Technical University", SourceCategory.UNIVERSITY, "CZ", "Tech university"),
    DataSource("https://www.muni.cz/", "Masaryk University", SourceCategory.UNIVERSITY, "CZ", "Brno"),
    DataSource("https://www.cnb.cz/", "Czech National Bank", SourceCategory.BANK, "CZ", "Central bank", True),
    DataSource("https://www.pse.cz/", "Prague Stock Exchange", SourceCategory.BANK, "CZ", "Stock Exchange", True),
    DataSource("https://www.csob.cz/", "ČSOB", SourceCategory.BANK, "CZ", "Major bank"),
    DataSource("https://www.csa.cz/", "Czech Airlines", SourceCategory.TRANSPORT, "CZ", "National airline"),
    DataSource("https://www.cd.cz/", "České dráhy", SourceCategory.TRANSPORT, "CZ", "Railways"),
    DataSource("https://www.ctk.cz/", "ČTK", SourceCategory.NEWS, "CZ", "News agency"),
    DataSource("https://www.irozhlas.cz/", "iROZHLAS", SourceCategory.NEWS, "CZ", "Public radio"),
    DataSource("https://www.czechtourism.com/", "CzechTourism", SourceCategory.TOURISM, "CZ", "Tourism", True),
    DataSource("https://facr.cz/", "FAČR", SourceCategory.SPORT, "CZ", "Football federation"),
]

# ============================================================
# 🇸🇰 SLOVAKIA
# ============================================================

SLOVAKIA_SOURCES = [
    DataSource("https://www.vlada.gov.sk/", "Slovakia Government", SourceCategory.GOVERNMENT, "SK", "Government"),
    DataSource("https://www.nrsr.sk/", "National Council", SourceCategory.GOVERNMENT, "SK", "Parliament"),
    DataSource("https://slovak.statistics.sk/", "Statistical Office", SourceCategory.STATISTICS, "SK", "Statistics", True),
    DataSource("https://data.gov.sk/", "Open Data Slovakia", SourceCategory.STATISTICS, "SK", "Open data", True),
    DataSource("https://uniba.sk/", "Comenius University", SourceCategory.UNIVERSITY, "SK", "Top university"),
    DataSource("https://www.stuba.sk/", "Slovak University of Technology", SourceCategory.UNIVERSITY, "SK", "Tech university"),
    DataSource("https://www.nbs.sk/", "National Bank of Slovakia", SourceCategory.BANK, "SK", "Central bank", True),
    DataSource("https://www.bsse.sk/", "Bratislava Stock Exchange", SourceCategory.BANK, "SK", "Stock Exchange"),
    DataSource("https://www.tasr.sk/", "TASR", SourceCategory.NEWS, "SK", "News agency"),
    DataSource("https://www.sme.sk/", "SME", SourceCategory.NEWS, "SK", "Major newspaper"),
    DataSource("https://slovakia.travel/", "Slovakia Travel", SourceCategory.TOURISM, "SK", "Tourism", True),
    DataSource("https://www.futbalsfz.sk/", "SFZ", SourceCategory.SPORT, "SK", "Football federation"),
]

# ============================================================
# 🇭🇺 HUNGARY
# ============================================================

HUNGARY_SOURCES = [
    DataSource("https://www.kormany.hu/", "Hungary Government", SourceCategory.GOVERNMENT, "HU", "Government"),
    DataSource("https://www.parlament.hu/", "National Assembly", SourceCategory.GOVERNMENT, "HU", "Parliament"),
    DataSource("https://www.ksh.hu/", "Hungarian Central Statistics", SourceCategory.STATISTICS, "HU", "Statistics", True),
    DataSource("https://opendata.hu/", "Open Data Hungary", SourceCategory.STATISTICS, "HU", "Open data", True),
    DataSource("https://www.elte.hu/", "ELTE", SourceCategory.UNIVERSITY, "HU", "Top university"),
    DataSource("https://www.bme.hu/", "BME", SourceCategory.UNIVERSITY, "HU", "Tech university"),
    DataSource("https://www.szte.hu/", "University of Szeged", SourceCategory.UNIVERSITY, "HU", "Szeged"),
    DataSource("https://www.mnb.hu/", "Magyar Nemzeti Bank", SourceCategory.BANK, "HU", "Central bank", True),
    DataSource("https://www.bet.hu/", "Budapest Stock Exchange", SourceCategory.BANK, "HU", "Stock Exchange", True),
    DataSource("https://www.otp.hu/", "OTP Bank", SourceCategory.BANK, "HU", "Major bank"),
    DataSource("https://www.wizzair.com/", "Wizz Air", SourceCategory.TRANSPORT, "HU", "Airline"),
    DataSource("https://www.mavcsoport.hu/", "MÁV", SourceCategory.TRANSPORT, "HU", "Railways"),
    DataSource("https://www.mti.hu/", "MTI", SourceCategory.NEWS, "HU", "News agency"),
    DataSource("https://index.hu/", "Index", SourceCategory.NEWS, "HU", "News portal"),
    DataSource("https://gotohungary.com/", "Go To Hungary", SourceCategory.TOURISM, "HU", "Tourism", True),
    DataSource("https://www.mlsz.hu/", "MLSZ", SourceCategory.SPORT, "HU", "Football federation"),
]

# ============================================================
# 🇱🇹 LITHUANIA
# ============================================================

LITHUANIA_SOURCES = [
    DataSource("https://lrv.lt/", "Lithuania Government", SourceCategory.GOVERNMENT, "LT", "Government"),
    DataSource("https://www.lrs.lt/", "Seimas", SourceCategory.GOVERNMENT, "LT", "Parliament"),
    DataSource("https://www.stat.gov.lt/", "Statistics Lithuania", SourceCategory.STATISTICS, "LT", "Statistics", True),
    DataSource("https://www.vu.lt/", "Vilnius University", SourceCategory.UNIVERSITY, "LT", "Top university"),
    DataSource("https://www.ktu.edu/", "Kaunas University of Technology", SourceCategory.UNIVERSITY, "LT", "KTU"),
    DataSource("https://www.lb.lt/", "Bank of Lithuania", SourceCategory.BANK, "LT", "Central bank", True),
    DataSource("https://www.nasdaqbaltic.com/", "Nasdaq Baltic", SourceCategory.BANK, "LT", "Stock Exchange", True),
    DataSource("https://www.elta.lt/", "ELTA", SourceCategory.NEWS, "LT", "News agency"),
    DataSource("https://www.delfi.lt/", "Delfi", SourceCategory.NEWS, "LT", "News portal"),
    DataSource("https://www.lithuania.travel/", "Lithuania Travel", SourceCategory.TOURISM, "LT", "Tourism", True),
    DataSource("https://www.lff.lt/", "LFF", SourceCategory.SPORT, "LT", "Football federation"),
]

# ============================================================
# 🇱🇻 LATVIA
# ============================================================

LATVIA_SOURCES = [
    DataSource("https://www.mk.gov.lv/", "Latvia Government", SourceCategory.GOVERNMENT, "LV", "Government"),
    DataSource("https://www.saeima.lv/", "Saeima", SourceCategory.GOVERNMENT, "LV", "Parliament"),
    DataSource("https://www.csp.gov.lv/", "Central Statistics Bureau", SourceCategory.STATISTICS, "LV", "Statistics", True),
    DataSource("https://data.gov.lv/", "Open Data Latvia", SourceCategory.STATISTICS, "LV", "Open data", True),
    DataSource("https://www.lu.lv/", "University of Latvia", SourceCategory.UNIVERSITY, "LV", "Top university"),
    DataSource("https://www.rtu.lv/", "Riga Technical University", SourceCategory.UNIVERSITY, "LV", "RTU"),
    DataSource("https://www.bank.lv/", "Bank of Latvia", SourceCategory.BANK, "LV", "Central bank", True),
    DataSource("https://www.leta.lv/", "LETA", SourceCategory.NEWS, "LV", "News agency"),
    DataSource("https://www.latvia.travel/", "Latvia Travel", SourceCategory.TOURISM, "LV", "Tourism", True),
    DataSource("https://www.lff.lv/", "LFF", SourceCategory.SPORT, "LV", "Football federation"),
]

# ============================================================
# 🇪🇪 ESTONIA
# ============================================================

ESTONIA_SOURCES = [
    DataSource("https://www.valitsus.ee/", "Estonia Government", SourceCategory.GOVERNMENT, "EE", "Government"),
    DataSource("https://www.riigikogu.ee/", "Riigikogu", SourceCategory.GOVERNMENT, "EE", "Parliament"),
    DataSource("https://www.stat.ee/", "Statistics Estonia", SourceCategory.STATISTICS, "EE", "Statistics", True),
    DataSource("https://avaandmed.eesti.ee/", "Open Data Estonia", SourceCategory.STATISTICS, "EE", "Open data", True),
    DataSource("https://www.ut.ee/", "University of Tartu", SourceCategory.UNIVERSITY, "EE", "Top university"),
    DataSource("https://taltech.ee/", "Tallinn University of Technology", SourceCategory.UNIVERSITY, "EE", "TalTech"),
    DataSource("https://www.eestipank.ee/", "Bank of Estonia", SourceCategory.BANK, "EE", "Central bank", True),
    DataSource("https://www.err.ee/", "ERR", SourceCategory.NEWS, "EE", "Public broadcaster"),
    DataSource("https://www.postimees.ee/", "Postimees", SourceCategory.NEWS, "EE", "Major newspaper"),
    DataSource("https://www.visitestonia.com/", "Visit Estonia", SourceCategory.TOURISM, "EE", "Tourism", True),
    DataSource("https://www.jalgpall.ee/", "EJL", SourceCategory.SPORT, "EE", "Football federation"),
]

# ============================================================
# 🇬🇷 GREECE
# ============================================================

GREECE_SOURCES = [
    DataSource("https://www.government.gov.gr/", "Greece Government", SourceCategory.GOVERNMENT, "GR", "Government"),
    DataSource("https://www.hellenicparliament.gr/", "Hellenic Parliament", SourceCategory.GOVERNMENT, "GR", "Parliament"),
    DataSource("https://www.statistics.gr/", "Hellenic Statistical Authority", SourceCategory.STATISTICS, "GR", "Statistics", True),
    DataSource("https://data.gov.gr/", "Open Data Greece", SourceCategory.STATISTICS, "GR", "Open data", True),
    DataSource("https://www.uoa.gr/", "National and Kapodistrian University", SourceCategory.UNIVERSITY, "GR", "Athens"),
    DataSource("https://www.auth.gr/", "Aristotle University", SourceCategory.UNIVERSITY, "GR", "Thessaloniki"),
    DataSource("https://www.ntua.gr/", "National Technical University", SourceCategory.UNIVERSITY, "GR", "NTUA"),
    DataSource("https://www.bankofgreece.gr/", "Bank of Greece", SourceCategory.BANK, "GR", "Central bank", True),
    DataSource("https://www.athexgroup.gr/", "Athens Stock Exchange", SourceCategory.BANK, "GR", "Stock Exchange", True),
    DataSource("https://www.nbg.gr/", "National Bank of Greece", SourceCategory.BANK, "GR", "Major bank"),
    DataSource("https://www.aegeanair.com/", "Aegean Airlines", SourceCategory.TRANSPORT, "GR", "Major airline"),
    DataSource("https://www.amna.gr/", "AMNA", SourceCategory.NEWS, "GR", "News agency"),
    DataSource("https://www.kathimerini.gr/", "Kathimerini", SourceCategory.NEWS, "GR", "Major newspaper"),
    DataSource("https://www.visitgreece.gr/", "Visit Greece", SourceCategory.TOURISM, "GR", "Tourism", True),
    DataSource("https://www.epo.gr/", "EPO", SourceCategory.SPORT, "GR", "Football federation"),
    DataSource("https://www.superleaguegreece.net/", "Super League", SourceCategory.SPORT, "GR", "Football league"),
]

# ============================================================
# 🇨🇾 CYPRUS
# ============================================================

CYPRUS_SOURCES = [
    DataSource("https://www.pio.gov.cy/", "Cyprus Government", SourceCategory.GOVERNMENT, "CY", "Government"),
    DataSource("https://www.parliament.cy/", "House of Representatives", SourceCategory.GOVERNMENT, "CY", "Parliament"),
    DataSource("https://www.mof.gov.cy/cystat/", "CyStat", SourceCategory.STATISTICS, "CY", "Statistics", True),
    DataSource("https://www.ucy.ac.cy/", "University of Cyprus", SourceCategory.UNIVERSITY, "CY", "Top university"),
    DataSource("https://www.centralbank.cy/", "Central Bank of Cyprus", SourceCategory.BANK, "CY", "Central bank", True),
    DataSource("https://www.cse.com.cy/", "Cyprus Stock Exchange", SourceCategory.BANK, "CY", "Stock Exchange"),
    DataSource("https://www.bankofcyprus.com/", "Bank of Cyprus", SourceCategory.BANK, "CY", "Major bank"),
    DataSource("https://www.cyprusairways.com/", "Cyprus Airways", SourceCategory.TRANSPORT, "CY", "Airline"),
    DataSource("https://www.cna.org.cy/", "CNA", SourceCategory.NEWS, "CY", "News agency"),
    DataSource("https://www.visitcyprus.com/", "Visit Cyprus", SourceCategory.TOURISM, "CY", "Tourism", True),
    DataSource("https://www.cfa.com.cy/", "CFA", SourceCategory.SPORT, "CY", "Football federation"),
]

# ============================================================
# COMBINED EXPORT
# ============================================================

ALL_EASTERN_EUROPE_BALKANS_SOURCES = (
    RUSSIA_SOURCES + UKRAINE_SOURCES + BELARUS_SOURCES + MOLDOVA_SOURCES +
    ROMANIA_SOURCES + BULGARIA_SOURCES + SERBIA_SOURCES + CROATIA_SOURCES +
    SLOVENIA_SOURCES + BOSNIA_SOURCES + MONTENEGRO_SOURCES + NORTH_MACEDONIA_SOURCES +
    ALBANIA_SOURCES + KOSOVO_SOURCES + CZECH_SOURCES + SLOVAKIA_SOURCES +
    HUNGARY_SOURCES + LITHUANIA_SOURCES + LATVIA_SOURCES + ESTONIA_SOURCES +
    GREECE_SOURCES + CYPRUS_SOURCES
)

def get_all_sources():
    return ALL_EASTERN_EUROPE_BALKANS_SOURCES

def get_sources_by_country(country_code: str):
    return [s for s in ALL_EASTERN_EUROPE_BALKANS_SOURCES if s.country == country_code]

if __name__ == "__main__":
    print(f"🏰 Eastern Europe & Balkans Sources: {len(ALL_EASTERN_EUROPE_BALKANS_SOURCES)}")
    print("Countries: RU, UA, BY, MD, RO, BG, RS, HR, SI, BA, ME, MK, AL, XK, CZ, SK, HU, LT, LV, EE, GR, CY")
