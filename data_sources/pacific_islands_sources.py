# -*- coding: utf-8 -*-
"""
🏝️ PACIFIC ISLANDS - COMPLETE DATA SOURCES
===========================================
100+ Free Open Data Sources from Pacific Island Nations

Countries & Territories Covered:

MELANESIA:
- Fiji 🇫🇯
- Papua New Guinea 🇵🇬
- Solomon Islands 🇸🇧
- Vanuatu 🇻🇺
- New Caledonia 🇳🇨

MICRONESIA:
- Guam 🇬🇺
- Palau 🇵🇼
- Federated States of Micronesia 🇫🇲
- Marshall Islands 🇲🇭
- Kiribati 🇰🇮
- Nauru 🇳🇷
- Northern Mariana Islands 🇲🇵

POLYNESIA:
- Samoa 🇼🇸
- American Samoa 🇦🇸
- Tonga 🇹🇴
- French Polynesia 🇵🇫
- Cook Islands 🇨🇰
- Niue 🇳🇺
- Tokelau 🇹🇰
- Tuvalu 🇹🇻
- Wallis and Futuna 🇼🇫
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
    ENVIRONMENTAL = "environmental"

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
# MELANESIA
# ============================================================

# 🇫🇯 FIJI
FIJI_SOURCES = [
    DataSource("https://www.fiji.gov.fj/", "Fiji Government", SourceCategory.GOVERNMENT, "FJ", "Government"),
    DataSource("https://www.parliament.gov.fj/", "Parliament of Fiji", SourceCategory.GOVERNMENT, "FJ", "Parliament"),
    DataSource("https://www.statsfiji.gov.fj/", "Fiji Bureau of Statistics", SourceCategory.STATISTICS, "FJ", "Statistics", True),
    DataSource("https://www.usp.ac.fj/", "University of the South Pacific", SourceCategory.UNIVERSITY, "FJ", "Regional university"),
    DataSource("https://www.fnu.ac.fj/", "Fiji National University", SourceCategory.UNIVERSITY, "FJ", "National university"),
    DataSource("https://www.rbf.gov.fj/", "Reserve Bank of Fiji", SourceCategory.BANK, "FJ", "Central bank", True),
    DataSource("https://www.spse.com.fj/", "South Pacific Stock Exchange", SourceCategory.BANK, "FJ", "Stock Exchange"),
    DataSource("https://www.fijiairways.com/", "Fiji Airways", SourceCategory.TRANSPORT, "FJ", "National airline"),
    DataSource("https://www.fijitimes.com/", "Fiji Times", SourceCategory.NEWS, "FJ", "Major newspaper"),
    DataSource("https://www.fiji.travel/", "Tourism Fiji", SourceCategory.TOURISM, "FJ", "Tourism", True),
    DataSource("https://www.fijifa.com.fj/", "Fiji Football", SourceCategory.SPORT, "FJ", "Football federation"),
    DataSource("https://www.fijirugby.com/", "Fiji Rugby", SourceCategory.SPORT, "FJ", "Rugby union"),
]

# 🇵🇬 PAPUA NEW GUINEA
PNG_SOURCES = [
    DataSource("https://www.pm.gov.pg/", "PNG Government", SourceCategory.GOVERNMENT, "PG", "Prime Minister"),
    DataSource("https://www.parliament.gov.pg/", "National Parliament", SourceCategory.GOVERNMENT, "PG", "Parliament"),
    DataSource("https://www.nso.gov.pg/", "National Statistical Office", SourceCategory.STATISTICS, "PG", "Statistics", True),
    DataSource("https://www.upng.ac.pg/", "University of PNG", SourceCategory.UNIVERSITY, "PG", "Top university"),
    DataSource("https://www.unitech.ac.pg/", "PNG University of Technology", SourceCategory.UNIVERSITY, "PG", "Tech university"),
    DataSource("https://www.bankpng.gov.pg/", "Bank of PNG", SourceCategory.BANK, "PG", "Central bank", True),
    DataSource("https://www.pngx.com.pg/", "PNGX", SourceCategory.BANK, "PG", "Stock Exchange"),
    DataSource("https://www.airniugini.com.pg/", "Air Niugini", SourceCategory.TRANSPORT, "PG", "National airline"),
    DataSource("https://www.postcourier.com.pg/", "Post-Courier", SourceCategory.NEWS, "PG", "Major newspaper"),
    DataSource("https://www.papuanewguinea.travel/", "PNG Tourism", SourceCategory.TOURISM, "PG", "Tourism", True),
    DataSource("https://www.pngfa.com/", "PNG Football", SourceCategory.SPORT, "PG", "Football federation"),
]

# 🇸🇧 SOLOMON ISLANDS
SOLOMON_SOURCES = [
    DataSource("https://www.gov.sb/", "Solomon Islands Government", SourceCategory.GOVERNMENT, "SB", "Government"),
    DataSource("https://www.parliament.gov.sb/", "National Parliament", SourceCategory.GOVERNMENT, "SB", "Parliament"),
    DataSource("https://www.statistics.gov.sb/", "Statistics Office", SourceCategory.STATISTICS, "SB", "Statistics"),
    DataSource("https://www.sinu.edu.sb/", "Solomon Islands National University", SourceCategory.UNIVERSITY, "SB", "University"),
    DataSource("https://www.cbsi.com.sb/", "Central Bank", SourceCategory.BANK, "SB", "Central bank", True),
    DataSource("https://www.flysolomons.com/", "Solomon Airlines", SourceCategory.TRANSPORT, "SB", "National airline"),
    DataSource("https://www.visitsolomons.com.sb/", "Visit Solomons", SourceCategory.TOURISM, "SB", "Tourism", True),
    DataSource("https://www.siff.com.sb/", "SIFF", SourceCategory.SPORT, "SB", "Football federation"),
]

# 🇻🇺 VANUATU
VANUATU_SOURCES = [
    DataSource("https://www.gov.vu/", "Vanuatu Government", SourceCategory.GOVERNMENT, "VU", "Government"),
    DataSource("https://www.parliament.gov.vu/", "Parliament of Vanuatu", SourceCategory.GOVERNMENT, "VU", "Parliament"),
    DataSource("https://vnso.gov.vu/", "VNSO", SourceCategory.STATISTICS, "VU", "Statistics", True),
    DataSource("https://www.rbv.gov.vu/", "Reserve Bank of Vanuatu", SourceCategory.BANK, "VU", "Central bank", True),
    DataSource("https://www.airvanuatu.com/", "Air Vanuatu", SourceCategory.TRANSPORT, "VU", "National airline"),
    DataSource("https://www.vanuatu.travel/", "Vanuatu Tourism", SourceCategory.TOURISM, "VU", "Tourism", True),
    DataSource("https://www.vff.com.vu/", "VFF", SourceCategory.SPORT, "VU", "Football federation"),
]

# 🇳🇨 NEW CALEDONIA
NEW_CALEDONIA_SOURCES = [
    DataSource("https://www.gouv.nc/", "New Caledonia Government", SourceCategory.GOVERNMENT, "NC", "Government"),
    DataSource("https://www.isee.nc/", "ISEE", SourceCategory.STATISTICS, "NC", "Statistics", True),
    DataSource("https://www.unc.nc/", "University of New Caledonia", SourceCategory.UNIVERSITY, "NC", "University"),
    DataSource("https://www.aircalin.com/", "Aircalin", SourceCategory.TRANSPORT, "NC", "Airline"),
    DataSource("https://www.newcaledonia.travel/", "New Caledonia Tourism", SourceCategory.TOURISM, "NC", "Tourism", True),
    DataSource("https://www.fcfnc.nc/", "FCF", SourceCategory.SPORT, "NC", "Football federation"),
]

# ============================================================
# MICRONESIA
# ============================================================

# 🇬🇺 GUAM
GUAM_SOURCES = [
    DataSource("https://www.guam.gov/", "Guam Government", SourceCategory.GOVERNMENT, "GU", "Government"),
    DataSource("https://www.bsp.guam.gov/", "Bureau of Statistics & Plans", SourceCategory.STATISTICS, "GU", "Statistics"),
    DataSource("https://www.uog.edu/", "University of Guam", SourceCategory.UNIVERSITY, "GU", "University"),
    DataSource("https://www.visitguam.com/", "Visit Guam", SourceCategory.TOURISM, "GU", "Tourism", True),
    DataSource("https://guamfa.com/", "Guam FA", SourceCategory.SPORT, "GU", "Football federation"),
]

# 🇵🇼 PALAU
PALAU_SOURCES = [
    DataSource("https://www.palaugov.pw/", "Palau Government", SourceCategory.GOVERNMENT, "PW", "Government"),
    DataSource("https://www.palaugov.pw/statistics/", "Statistics Bureau", SourceCategory.STATISTICS, "PW", "Statistics"),
    DataSource("https://www.palau.edu/", "Palau Community College", SourceCategory.UNIVERSITY, "PW", "College"),
    DataSource("https://www.pristineparadisepalau.com/", "Visit Palau", SourceCategory.TOURISM, "PW", "Tourism", True),
    DataSource("https://www.palauff.com/", "Palau Football", SourceCategory.SPORT, "PW", "Football federation"),
]

# 🇫🇲 FEDERATED STATES OF MICRONESIA
FSM_SOURCES = [
    DataSource("https://www.fsmgov.org/", "FSM Government", SourceCategory.GOVERNMENT, "FM", "Government"),
    DataSource("https://www.sboc.fm/", "Statistics Office", SourceCategory.STATISTICS, "FM", "Statistics"),
    DataSource("https://www.comfsm.fm/", "College of Micronesia", SourceCategory.UNIVERSITY, "FM", "College"),
    DataSource("https://www.visit-micronesia.fm/", "Visit Micronesia", SourceCategory.TOURISM, "FM", "Tourism", True),
    DataSource("https://www.fsmfa.com/", "FSM Football", SourceCategory.SPORT, "FM", "Football federation"),
]

# 🇲🇭 MARSHALL ISLANDS
MARSHALL_SOURCES = [
    DataSource("https://www.rmigovernment.org/", "RMI Government", SourceCategory.GOVERNMENT, "MH", "Government"),
    DataSource("https://www.rmi-eppso.org/", "EPPSO", SourceCategory.STATISTICS, "MH", "Statistics"),
    DataSource("https://www.cmi.edu/", "College of Marshall Islands", SourceCategory.UNIVERSITY, "MH", "College"),
    DataSource("https://www.visitmarshallislands.com/", "Visit Marshall Islands", SourceCategory.TOURISM, "MH", "Tourism", True),
    DataSource("https://www.mifa.com.mh/", "MIFA", SourceCategory.SPORT, "MH", "Football federation"),
]

# 🇰🇮 KIRIBATI
KIRIBATI_SOURCES = [
    DataSource("https://www.president.gov.ki/", "Kiribati Government", SourceCategory.GOVERNMENT, "KI", "President"),
    DataSource("https://www.knso.gov.ki/", "Statistics Office", SourceCategory.STATISTICS, "KI", "Statistics"),
    DataSource("https://www.visitkiribati.travel/", "Visit Kiribati", SourceCategory.TOURISM, "KI", "Tourism", True),
    DataSource("https://www.kfa.ki/", "KFA", SourceCategory.SPORT, "KI", "Football federation"),
]

# 🇳🇷 NAURU
NAURU_SOURCES = [
    DataSource("https://www.naurugov.nr/", "Nauru Government", SourceCategory.GOVERNMENT, "NR", "Government"),
    DataSource("https://www.spc.int/", "SPC Statistics", SourceCategory.STATISTICS, "NR", "Statistics"),
    DataSource("https://www.naurufa.com/", "Nauru Football", SourceCategory.SPORT, "NR", "Football federation"),
]

# ============================================================
# POLYNESIA
# ============================================================

# 🇼🇸 SAMOA
SAMOA_SOURCES = [
    DataSource("https://www.samoagovt.ws/", "Samoa Government", SourceCategory.GOVERNMENT, "WS", "Government"),
    DataSource("https://www.sbs.gov.ws/", "Samoa Bureau of Statistics", SourceCategory.STATISTICS, "WS", "Statistics", True),
    DataSource("https://www.nus.edu.ws/", "National University of Samoa", SourceCategory.UNIVERSITY, "WS", "University"),
    DataSource("https://www.cbs.gov.ws/", "Central Bank of Samoa", SourceCategory.BANK, "WS", "Central bank", True),
    DataSource("https://www.samoaairways.com/", "Samoa Airways", SourceCategory.TRANSPORT, "WS", "National airline"),
    DataSource("https://www.samoa.travel/", "Samoa Tourism", SourceCategory.TOURISM, "WS", "Tourism", True),
    DataSource("https://www.samoanfootball.ws/", "Samoa Football", SourceCategory.SPORT, "WS", "Football federation"),
    DataSource("https://www.manusamoa.ws/", "Manu Samoa", SourceCategory.SPORT, "WS", "Rugby union"),
]

# 🇹🇴 TONGA
TONGA_SOURCES = [
    DataSource("https://www.gov.to/", "Tonga Government", SourceCategory.GOVERNMENT, "TO", "Government"),
    DataSource("https://www.tongastats.gov.to/", "Statistics Department", SourceCategory.STATISTICS, "TO", "Statistics", True),
    DataSource("https://www.nrbt.to/", "National Reserve Bank", SourceCategory.BANK, "TO", "Central bank", True),
    DataSource("https://www.tongatapu.net/", "Tonga News", SourceCategory.NEWS, "TO", "News"),
    DataSource("https://www.thekingdomoftonga.com/", "Kingdom of Tonga", SourceCategory.TOURISM, "TO", "Tourism", True),
    DataSource("https://www.tongafootball.to/", "Tonga Football", SourceCategory.SPORT, "TO", "Football federation"),
    DataSource("https://www.tongarugby.com/", "Tonga Rugby", SourceCategory.SPORT, "TO", "Rugby union"),
]

# 🇵🇫 FRENCH POLYNESIA
FRENCH_POLYNESIA_SOURCES = [
    DataSource("https://www.presidence.pf/", "French Polynesia Government", SourceCategory.GOVERNMENT, "PF", "Presidency"),
    DataSource("https://www.ispf.pf/", "ISPF Statistics", SourceCategory.STATISTICS, "PF", "Statistics", True),
    DataSource("https://www.upf.pf/", "University of French Polynesia", SourceCategory.UNIVERSITY, "PF", "University"),
    DataSource("https://www.airtahitinui.com/", "Air Tahiti Nui", SourceCategory.TRANSPORT, "PF", "Airline"),
    DataSource("https://www.tahititourisme.com/", "Tahiti Tourisme", SourceCategory.TOURISM, "PF", "Tourism", True),
    DataSource("https://www.ftf.pf/", "FTF", SourceCategory.SPORT, "PF", "Football federation"),
]

# 🇨🇰 COOK ISLANDS
COOK_ISLANDS_SOURCES = [
    DataSource("https://www.pmoffice.gov.ck/", "Cook Islands Government", SourceCategory.GOVERNMENT, "CK", "Prime Minister"),
    DataSource("https://www.mfem.gov.ck/statistics/", "Statistics Office", SourceCategory.STATISTICS, "CK", "Statistics"),
    DataSource("https://www.cookislands.travel/", "Cook Islands Tourism", SourceCategory.TOURISM, "CK", "Tourism", True),
    DataSource("https://www.cifa.ck/", "CIFA", SourceCategory.SPORT, "CK", "Football federation"),
]

# 🇹🇻 TUVALU
TUVALU_SOURCES = [
    DataSource("https://www.gov.tv/", "Tuvalu Government", SourceCategory.GOVERNMENT, "TV", "Government"),
    DataSource("https://www.nbt.tv/", "National Bank of Tuvalu", SourceCategory.BANK, "TV", "Bank"),
    DataSource("https://www.timelesstuvalu.com/", "Timeless Tuvalu", SourceCategory.TOURISM, "TV", "Tourism", True),
    DataSource("https://www.tnfa.tv/", "Tuvalu Football", SourceCategory.SPORT, "TV", "Football federation"),
]

# 🇳🇺 NIUE
NIUE_SOURCES = [
    DataSource("https://www.gov.nu/", "Niue Government", SourceCategory.GOVERNMENT, "NU", "Government"),
    DataSource("https://www.niueisland.com/", "Niue Tourism", SourceCategory.TOURISM, "NU", "Tourism", True),
    DataSource("https://www.niuefa.nu/", "Niue Football", SourceCategory.SPORT, "NU", "Football"),
]

# 🇦🇸 AMERICAN SAMOA
AMERICAN_SAMOA_SOURCES = [
    DataSource("https://www.americansamoa.gov/", "American Samoa Government", SourceCategory.GOVERNMENT, "AS", "Government"),
    DataSource("https://doc.as.gov/", "Statistics Division", SourceCategory.STATISTICS, "AS", "Statistics"),
    DataSource("https://www.ascc.edu/", "American Samoa Community College", SourceCategory.UNIVERSITY, "AS", "College"),
    DataSource("https://www.ffas.as/", "FFAS", SourceCategory.SPORT, "AS", "Football federation"),
]

# ============================================================
# REGIONAL & INTERNATIONAL PACIFIC ORGANIZATIONS
# ============================================================

PACIFIC_REGIONAL_SOURCES = [
    DataSource("https://www.spc.int/", "Pacific Community (SPC)", SourceCategory.RESEARCH, "PACIFIC", "Regional org", True),
    DataSource("https://www.forumsec.org/", "Pacific Islands Forum", SourceCategory.GOVERNMENT, "PACIFIC", "Regional forum"),
    DataSource("https://www.sprep.org/", "SPREP", SourceCategory.ENVIRONMENTAL, "PACIFIC", "Environment program"),
    DataSource("https://www.ffa.int/", "FFA", SourceCategory.INDUSTRY, "PACIFIC", "Fisheries agency"),
    DataSource("https://www.pina.com.fj/", "PINA", SourceCategory.NEWS, "PACIFIC", "Pacific news"),
    DataSource("https://www.oceaniafootball.com/", "OFC", SourceCategory.SPORT, "PACIFIC", "Oceania Football"),
    DataSource("https://www.oceaniarugby.com/", "Oceania Rugby", SourceCategory.SPORT, "PACIFIC", "Oceania Rugby"),
    DataSource("https://www.prif.org/", "PRIF", SourceCategory.BANK, "PACIFIC", "Regional finance"),
    DataSource("https://www.spto.org/", "SPTO", SourceCategory.TOURISM, "PACIFIC", "South Pacific Tourism"),
]

# ============================================================
# COMBINED EXPORT
# ============================================================

ALL_PACIFIC_SOURCES = (
    # Melanesia
    FIJI_SOURCES + PNG_SOURCES + SOLOMON_SOURCES + VANUATU_SOURCES + NEW_CALEDONIA_SOURCES +
    # Micronesia
    GUAM_SOURCES + PALAU_SOURCES + FSM_SOURCES + MARSHALL_SOURCES + KIRIBATI_SOURCES + NAURU_SOURCES +
    # Polynesia
    SAMOA_SOURCES + TONGA_SOURCES + FRENCH_POLYNESIA_SOURCES + COOK_ISLANDS_SOURCES + 
    TUVALU_SOURCES + NIUE_SOURCES + AMERICAN_SAMOA_SOURCES +
    # Regional
    PACIFIC_REGIONAL_SOURCES
)

def get_all_sources():
    return ALL_PACIFIC_SOURCES

def get_sources_by_country(country_code: str):
    return [s for s in ALL_PACIFIC_SOURCES if s.country == country_code]

def get_sources_by_region(region: str):
    """Get sources by Pacific region: melanesia, micronesia, polynesia"""
    region_map = {
        "melanesia": FIJI_SOURCES + PNG_SOURCES + SOLOMON_SOURCES + VANUATU_SOURCES + NEW_CALEDONIA_SOURCES,
        "micronesia": GUAM_SOURCES + PALAU_SOURCES + FSM_SOURCES + MARSHALL_SOURCES + KIRIBATI_SOURCES + NAURU_SOURCES,
        "polynesia": SAMOA_SOURCES + TONGA_SOURCES + FRENCH_POLYNESIA_SOURCES + COOK_ISLANDS_SOURCES + TUVALU_SOURCES + NIUE_SOURCES + AMERICAN_SAMOA_SOURCES
    }
    return region_map.get(region.lower(), [])

if __name__ == "__main__":
    print(f"🏝️ Pacific Islands Sources: {len(ALL_PACIFIC_SOURCES)}")
    print("Melanesia: FJ, PG, SB, VU, NC")
    print("Micronesia: GU, PW, FM, MH, KI, NR")
    print("Polynesia: WS, TO, PF, CK, TV, NU, AS")
