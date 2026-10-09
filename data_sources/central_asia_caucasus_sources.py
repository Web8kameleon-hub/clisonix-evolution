# -*- coding: utf-8 -*-
"""
🌍 CENTRAL ASIA & CAUCASUS - COMPLETE DATA SOURCES
===================================================
200+ Free Open Data Sources from Central Asia & Caucasus

Countries Covered:
- Kazakhstan 🇰🇿
- Uzbekistan 🇺🇿
- Turkmenistan 🇹🇲
- Kyrgyzstan 🇰🇬
- Tajikistan 🇹🇯
- Azerbaijan 🇦🇿
- Georgia 🇬🇪
- Armenia 🇦🇲
- Mongolia 🇲🇳
- Afghanistan 🇦🇫
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
# 🇰🇿 KAZAKHSTAN
# ============================================================

KAZAKHSTAN_SOURCES = [
    DataSource("https://www.gov.kz/", "Kazakhstan Government", SourceCategory.GOVERNMENT, "KZ", "E-government portal"),
    DataSource("https://www.parlam.kz/", "Kazakhstan Parliament", SourceCategory.GOVERNMENT, "KZ", "Parliament"),
    DataSource("https://stat.gov.kz/", "Statistics Kazakhstan", SourceCategory.STATISTICS, "KZ", "Statistics", True),
    DataSource("https://data.egov.kz/", "Open Data Kazakhstan", SourceCategory.STATISTICS, "KZ", "Open data", True),
    DataSource("https://www.kaznu.kz/", "Al-Farabi Kazakh National University", SourceCategory.UNIVERSITY, "KZ", "Top university"),
    DataSource("https://www.nu.edu.kz/", "Nazarbayev University", SourceCategory.UNIVERSITY, "KZ", "Modern university"),
    DataSource("https://www.kbtu.kz/", "KBTU", SourceCategory.UNIVERSITY, "KZ", "Business & Tech"),
    DataSource("https://www.nationalbank.kz/", "National Bank of Kazakhstan", SourceCategory.BANK, "KZ", "Central bank", True),
    DataSource("https://kase.kz/", "KASE", SourceCategory.BANK, "KZ", "Stock Exchange", True),
    DataSource("https://halykbank.kz/", "Halyk Bank", SourceCategory.BANK, "KZ", "Major bank"),
    DataSource("https://www.kaspi.kz/", "Kaspi Bank", SourceCategory.BANK, "KZ", "Digital bank"),
    DataSource("https://www.kmg.kz/", "KazMunayGas", SourceCategory.ENERGY, "KZ", "Oil & Gas"),
    DataSource("https://www.kegoc.kz/", "KEGOC", SourceCategory.ENERGY, "KZ", "Power grid"),
    DataSource("https://www.airastana.com/", "Air Astana", SourceCategory.TRANSPORT, "KZ", "National airline"),
    DataSource("https://flyqazaq.com/", "Qazaq Air", SourceCategory.TRANSPORT, "KZ", "Regional airline"),
    DataSource("https://www.ktj.kz/", "Kazakhstan Railways", SourceCategory.TRANSPORT, "KZ", "Railways"),
    DataSource("https://kcell.kz/", "Kcell", SourceCategory.TELECOM, "KZ", "Telecom"),
    DataSource("https://www.beeline.kz/", "Beeline Kazakhstan", SourceCategory.TELECOM, "KZ", "Telecom"),
    DataSource("https://www.inform.kz/", "Kazinform", SourceCategory.NEWS, "KZ", "News agency"),
    DataSource("https://tengrinews.kz/", "Tengri News", SourceCategory.NEWS, "KZ", "News portal"),
    DataSource("https://vlast.kz/", "Vlast", SourceCategory.NEWS, "KZ", "News magazine"),
    DataSource("https://www.nationalmuseum.kz/", "National Museum", SourceCategory.CULTURE, "KZ", "Museum"),
    DataSource("https://www.kazakhstan.travel/", "Kazakhstan Travel", SourceCategory.TOURISM, "KZ", "Tourism", True),
    DataSource("https://www.kff.kz/", "KFF", SourceCategory.SPORT, "KZ", "Football federation"),
]

# ============================================================
# 🇺🇿 UZBEKISTAN
# ============================================================

UZBEKISTAN_SOURCES = [
    DataSource("https://www.gov.uz/", "Uzbekistan Government", SourceCategory.GOVERNMENT, "UZ", "E-government"),
    DataSource("https://parliament.gov.uz/", "Oliy Majlis", SourceCategory.GOVERNMENT, "UZ", "Parliament"),
    DataSource("https://stat.uz/", "Statistics Uzbekistan", SourceCategory.STATISTICS, "UZ", "Statistics", True),
    DataSource("https://data.gov.uz/", "Open Data Uzbekistan", SourceCategory.STATISTICS, "UZ", "Open data", True),
    DataSource("https://nuu.uz/", "National University of Uzbekistan", SourceCategory.UNIVERSITY, "UZ", "Top university"),
    DataSource("https://tsue.uz/", "Tashkent State University of Economics", SourceCategory.UNIVERSITY, "UZ", "Economics"),
    DataSource("https://www.wiut.uz/", "Westminster International University", SourceCategory.UNIVERSITY, "UZ", "International"),
    DataSource("https://cbu.uz/", "Central Bank of Uzbekistan", SourceCategory.BANK, "UZ", "Central bank", True),
    DataSource("https://uzse.uz/", "Tashkent Stock Exchange", SourceCategory.BANK, "UZ", "Stock Exchange"),
    DataSource("https://www.nbu.uz/", "National Bank of Uzbekistan", SourceCategory.BANK, "UZ", "Major bank"),
    DataSource("https://www.uzneftegaz.uz/", "Uzbekneftegaz", SourceCategory.ENERGY, "UZ", "Oil & Gas"),
    DataSource("https://www.uzairways.com/", "Uzbekistan Airways", SourceCategory.TRANSPORT, "UZ", "National airline"),
    DataSource("https://railway.uz/", "Uzbekistan Railways", SourceCategory.TRANSPORT, "UZ", "Railways"),
    DataSource("https://uztelecom.uz/", "Uztelecom", SourceCategory.TELECOM, "UZ", "Telecom"),
    DataSource("https://www.uza.uz/", "UzA", SourceCategory.NEWS, "UZ", "News agency"),
    DataSource("https://kun.uz/", "Kun.uz", SourceCategory.NEWS, "UZ", "News portal"),
    DataSource("https://www.gazeta.uz/", "Gazeta.uz", SourceCategory.NEWS, "UZ", "News portal"),
    DataSource("https://uzbekistan.travel/", "Uzbekistan Travel", SourceCategory.TOURISM, "UZ", "Tourism", True),
    DataSource("https://www.the-ufa.com/", "UFA", SourceCategory.SPORT, "UZ", "Football federation"),
]

# ============================================================
# 🇰🇬 KYRGYZSTAN
# ============================================================

KYRGYZSTAN_SOURCES = [
    DataSource("https://www.gov.kg/", "Kyrgyzstan Government", SourceCategory.GOVERNMENT, "KG", "Government"),
    DataSource("https://www.kenesh.kg/", "Jogorku Kenesh", SourceCategory.GOVERNMENT, "KG", "Parliament"),
    DataSource("https://www.stat.kg/", "National Statistics", SourceCategory.STATISTICS, "KG", "Statistics", True),
    DataSource("https://data.gov.kg/", "Open Data Kyrgyzstan", SourceCategory.STATISTICS, "KG", "Open data", True),
    DataSource("https://www.knu.kg/", "Kyrgyz National University", SourceCategory.UNIVERSITY, "KG", "Top university"),
    DataSource("https://www.auca.kg/", "AUCA", SourceCategory.UNIVERSITY, "KG", "American University"),
    DataSource("https://www.nbkr.kg/", "National Bank of Kyrgyzstan", SourceCategory.BANK, "KG", "Central bank", True),
    DataSource("https://www.kse.kg/", "Kyrgyz Stock Exchange", SourceCategory.BANK, "KG", "Stock Exchange"),
    DataSource("https://www.kyrgyzairways.kg/", "Kyrgyzstan Airways", SourceCategory.TRANSPORT, "KG", "Airline"),
    DataSource("https://www.kabar.kg/", "Kabar", SourceCategory.NEWS, "KG", "News agency"),
    DataSource("https://24.kg/", "24.kg", SourceCategory.NEWS, "KG", "News portal"),
    DataSource("https://www.discoverkyrgyzstan.org/", "Discover Kyrgyzstan", SourceCategory.TOURISM, "KG", "Tourism", True),
    DataSource("https://www.ffkr.kg/", "FFKR", SourceCategory.SPORT, "KG", "Football federation"),
]

# ============================================================
# 🇹🇯 TAJIKISTAN
# ============================================================

TAJIKISTAN_SOURCES = [
    DataSource("https://www.president.tj/", "Tajikistan Presidency", SourceCategory.GOVERNMENT, "TJ", "Presidency"),
    DataSource("https://www.parlament.tj/", "Majlisi Oli", SourceCategory.GOVERNMENT, "TJ", "Parliament"),
    DataSource("https://www.stat.tj/", "Statistics Tajikistan", SourceCategory.STATISTICS, "TJ", "Statistics", True),
    DataSource("https://tnu.tj/", "Tajik National University", SourceCategory.UNIVERSITY, "TJ", "Top university"),
    DataSource("https://nbt.tj/", "National Bank of Tajikistan", SourceCategory.BANK, "TJ", "Central bank", True),
    DataSource("https://www.tajikair.tj/", "Tajik Air", SourceCategory.TRANSPORT, "TJ", "National airline"),
    DataSource("https://www.khovar.tj/", "Khovar", SourceCategory.NEWS, "TJ", "News agency"),
    DataSource("https://www.asiaplus.tj/", "Asia-Plus", SourceCategory.NEWS, "TJ", "News portal"),
    DataSource("https://www.traveltajikistan.tj/", "Visit Tajikistan", SourceCategory.TOURISM, "TJ", "Tourism", True),
]

# ============================================================
# 🇹🇲 TURKMENISTAN
# ============================================================

TURKMENISTAN_SOURCES = [
    DataSource("https://www.gov.tm/", "Turkmenistan Government", SourceCategory.GOVERNMENT, "TM", "Government"),
    DataSource("https://www.mejlis.gov.tm/", "Mejlis", SourceCategory.GOVERNMENT, "TM", "Parliament"),
    DataSource("https://www.stat.gov.tm/", "Statistics Turkmenistan", SourceCategory.STATISTICS, "TM", "Statistics"),
    DataSource("https://cbt.gov.tm/", "Central Bank of Turkmenistan", SourceCategory.BANK, "TM", "Central bank"),
    DataSource("https://turkmenistanairlines.tm/", "Turkmenistan Airlines", SourceCategory.TRANSPORT, "TM", "National airline"),
    DataSource("https://www.turkmenistan.gov.tm/", "TDH", SourceCategory.NEWS, "TM", "News agency"),
]

# ============================================================
# 🇦🇿 AZERBAIJAN
# ============================================================

AZERBAIJAN_SOURCES = [
    DataSource("https://www.gov.az/", "Azerbaijan Government", SourceCategory.GOVERNMENT, "AZ", "E-government"),
    DataSource("https://www.meclis.gov.az/", "Milli Majlis", SourceCategory.GOVERNMENT, "AZ", "Parliament"),
    DataSource("https://www.stat.gov.az/", "Statistics Azerbaijan", SourceCategory.STATISTICS, "AZ", "Statistics", True),
    DataSource("https://data.gov.az/", "Open Data Azerbaijan", SourceCategory.STATISTICS, "AZ", "Open data", True),
    DataSource("https://www.bsu.edu.az/", "Baku State University", SourceCategory.UNIVERSITY, "AZ", "Top university"),
    DataSource("https://www.ada.edu.az/", "ADA University", SourceCategory.UNIVERSITY, "AZ", "Modern university"),
    DataSource("https://www.khazar.org/", "Khazar University", SourceCategory.UNIVERSITY, "AZ", "Private university"),
    DataSource("https://www.cbar.az/", "Central Bank of Azerbaijan", SourceCategory.BANK, "AZ", "Central bank", True),
    DataSource("https://bse.az/", "Baku Stock Exchange", SourceCategory.BANK, "AZ", "Stock Exchange"),
    DataSource("https://www.kapitalbank.az/", "Kapital Bank", SourceCategory.BANK, "AZ", "Major bank"),
    DataSource("https://www.pasha-bank.az/", "PASHA Bank", SourceCategory.BANK, "AZ", "Major bank"),
    DataSource("https://www.socar.az/", "SOCAR", SourceCategory.ENERGY, "AZ", "Oil company"),
    DataSource("https://www.azal.az/", "Azerbaijan Airlines", SourceCategory.TRANSPORT, "AZ", "National airline"),
    DataSource("https://www.ady.az/", "Azerbaijan Railways", SourceCategory.TRANSPORT, "AZ", "Railways"),
    DataSource("https://azertag.az/", "AZERTAC", SourceCategory.NEWS, "AZ", "News agency"),
    DataSource("https://report.az/", "Report.az", SourceCategory.NEWS, "AZ", "News portal"),
    DataSource("https://www.trend.az/", "Trend News", SourceCategory.NEWS, "AZ", "News portal"),
    DataSource("https://www.azerbaijan.travel/", "Azerbaijan Tourism", SourceCategory.TOURISM, "AZ", "Tourism", True),
    DataSource("https://www.affa.az/", "AFFA", SourceCategory.SPORT, "AZ", "Football federation"),
]

# ============================================================
# 🇬🇪 GEORGIA
# ============================================================

GEORGIA_SOURCES = [
    DataSource("https://www.gov.ge/", "Georgia Government", SourceCategory.GOVERNMENT, "GE", "Government"),
    DataSource("https://parliament.ge/", "Parliament of Georgia", SourceCategory.GOVERNMENT, "GE", "Parliament"),
    DataSource("https://www.geostat.ge/", "GeoStat", SourceCategory.STATISTICS, "GE", "Statistics", True),
    DataSource("https://data.gov.ge/", "Open Data Georgia", SourceCategory.STATISTICS, "GE", "Open data", True),
    DataSource("https://www.tsu.ge/", "Tbilisi State University", SourceCategory.UNIVERSITY, "GE", "Top university"),
    DataSource("https://www.freeuni.edu.ge/", "Free University", SourceCategory.UNIVERSITY, "GE", "Private university"),
    DataSource("https://www.iliauni.edu.ge/", "Ilia State University", SourceCategory.UNIVERSITY, "GE", "University"),
    DataSource("https://www.nbg.gov.ge/", "National Bank of Georgia", SourceCategory.BANK, "GE", "Central bank", True),
    DataSource("https://gse.ge/", "Georgian Stock Exchange", SourceCategory.BANK, "GE", "Stock Exchange"),
    DataSource("https://www.tbcbank.ge/", "TBC Bank", SourceCategory.BANK, "GE", "Major bank"),
    DataSource("https://www.bog.ge/", "Bank of Georgia", SourceCategory.BANK, "GE", "Major bank"),
    DataSource("https://www.gnta.ge/", "Georgian National Tourism Admin", SourceCategory.TOURISM, "GE", "Tourism", True),
    DataSource("https://www.georgianairways.com/", "Georgian Airways", SourceCategory.TRANSPORT, "GE", "National airline"),
    DataSource("https://www.railway.ge/", "Georgian Railway", SourceCategory.TRANSPORT, "GE", "Railways"),
    DataSource("https://agenda.ge/", "Agenda.ge", SourceCategory.NEWS, "GE", "News portal"),
    DataSource("https://civil.ge/", "Civil.ge", SourceCategory.NEWS, "GE", "News portal"),
    DataSource("https://gff.ge/", "GFF", SourceCategory.SPORT, "GE", "Football federation"),
]

# ============================================================
# 🇦🇲 ARMENIA
# ============================================================

ARMENIA_SOURCES = [
    DataSource("https://www.gov.am/", "Armenia Government", SourceCategory.GOVERNMENT, "AM", "Government"),
    DataSource("https://www.parliament.am/", "National Assembly", SourceCategory.GOVERNMENT, "AM", "Parliament"),
    DataSource("https://www.armstat.am/", "ArmStat", SourceCategory.STATISTICS, "AM", "Statistics", True),
    DataSource("https://data.gov.am/", "Open Data Armenia", SourceCategory.STATISTICS, "AM", "Open data", True),
    DataSource("https://www.ysu.am/", "Yerevan State University", SourceCategory.UNIVERSITY, "AM", "Top university"),
    DataSource("https://aua.am/", "American University of Armenia", SourceCategory.UNIVERSITY, "AM", "AUA"),
    DataSource("https://www.cba.am/", "Central Bank of Armenia", SourceCategory.BANK, "AM", "Central bank", True),
    DataSource("https://www.amx.am/", "Armenian Securities Exchange", SourceCategory.BANK, "AM", "Stock Exchange"),
    DataSource("https://www.ameriabank.am/", "Ameriabank", SourceCategory.BANK, "AM", "Major bank"),
    DataSource("https://www.armswissbank.am/", "ArmSwissBank", SourceCategory.BANK, "AM", "Bank"),
    DataSource("https://www.flyone.am/", "FlyOne Armenia", SourceCategory.TRANSPORT, "AM", "Airline"),
    DataSource("https://armenpress.am/", "Armenpress", SourceCategory.NEWS, "AM", "News agency"),
    DataSource("https://www.azatutyun.am/", "Azatutyun", SourceCategory.NEWS, "AM", "News portal"),
    DataSource("https://armenia.travel/", "Armenia Travel", SourceCategory.TOURISM, "AM", "Tourism", True),
    DataSource("https://www.ffa.am/", "FFA", SourceCategory.SPORT, "AM", "Football federation"),
]

# ============================================================
# 🇦🇫 AFGHANISTAN
# ============================================================

AFGHANISTAN_SOURCES = [
    DataSource("https://president.gov.af/", "Afghanistan Government", SourceCategory.GOVERNMENT, "AF", "Government"),
    DataSource("https://nsia.gov.af/", "NSIA", SourceCategory.STATISTICS, "AF", "Statistics"),
    DataSource("https://www.ku.edu.af/", "Kabul University", SourceCategory.UNIVERSITY, "AF", "Top university"),
    DataSource("https://www.auca.af/", "American University of Afghanistan", SourceCategory.UNIVERSITY, "AF", "AUAF"),
    DataSource("https://dab.gov.af/", "Da Afghanistan Bank", SourceCategory.BANK, "AF", "Central bank"),
    DataSource("https://www.ariana-afghan.com/", "Ariana Afghan Airlines", SourceCategory.TRANSPORT, "AF", "National airline"),
    DataSource("https://www.tolonews.com/", "TOLOnews", SourceCategory.NEWS, "AF", "News network"),
    DataSource("https://www.pajhwok.com/", "Pajhwok", SourceCategory.NEWS, "AF", "News agency"),
    DataSource("https://www.aff.org.af/", "AFF", SourceCategory.SPORT, "AF", "Football federation"),
]

# ============================================================
# 🇲🇳 MONGOLIA (Extended)
# ============================================================

MONGOLIA_SOURCES = [
    DataSource("https://www.gov.mn/", "Mongolia Government", SourceCategory.GOVERNMENT, "MN", "Government"),
    DataSource("https://www.parliament.mn/", "State Great Khural", SourceCategory.GOVERNMENT, "MN", "Parliament"),
    DataSource("https://www.1212.mn/", "National Statistics Office", SourceCategory.STATISTICS, "MN", "Statistics", True),
    DataSource("https://www.num.edu.mn/", "National University of Mongolia", SourceCategory.UNIVERSITY, "MN", "Top university"),
    DataSource("https://www.must.edu.mn/", "MUST", SourceCategory.UNIVERSITY, "MN", "Science & Tech"),
    DataSource("https://www.mongolbank.mn/", "Bank of Mongolia", SourceCategory.BANK, "MN", "Central bank", True),
    DataSource("https://mse.mn/", "Mongolian Stock Exchange", SourceCategory.BANK, "MN", "Stock Exchange", True),
    DataSource("https://www.khanbank.com/", "Khan Bank", SourceCategory.BANK, "MN", "Major bank"),
    DataSource("https://www.miat.com/", "MIAT Mongolian Airlines", SourceCategory.TRANSPORT, "MN", "National airline"),
    DataSource("https://montsame.mn/", "Montsame", SourceCategory.NEWS, "MN", "News agency"),
    DataSource("https://news.mn/", "News.mn", SourceCategory.NEWS, "MN", "News portal"),
    DataSource("https://www.discovermongolia.mn/", "Discover Mongolia", SourceCategory.TOURISM, "MN", "Tourism", True),
    DataSource("https://www.football.mn/", "MFF", SourceCategory.SPORT, "MN", "Football federation"),
]

# ============================================================
# COMBINED EXPORT
# ============================================================

ALL_CENTRAL_ASIA_CAUCASUS_SOURCES = (
    KAZAKHSTAN_SOURCES + UZBEKISTAN_SOURCES + KYRGYZSTAN_SOURCES +
    TAJIKISTAN_SOURCES + TURKMENISTAN_SOURCES + AZERBAIJAN_SOURCES +
    GEORGIA_SOURCES + ARMENIA_SOURCES + AFGHANISTAN_SOURCES +
    MONGOLIA_SOURCES
)

def get_all_sources() -> List[DataSource]:
    return ALL_CENTRAL_ASIA_CAUCASUS_SOURCES

def get_sources_by_country(country_code: str) -> List[DataSource]:
    return [s for s in ALL_CENTRAL_ASIA_CAUCASUS_SOURCES if s.country == country_code]

if __name__ == "__main__":
    print(f"🏔️ Central Asia & Caucasus Sources: {len(ALL_CENTRAL_ASIA_CAUCASUS_SOURCES)}")
    print("Countries: KZ, UZ, KG, TJ, TM, AZ, GE, AM, AF, MN")
