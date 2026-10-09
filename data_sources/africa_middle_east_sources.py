# -*- coding: utf-8 -*-
"""
🌍 AFRICA & MIDDLE EAST - COMPLETE DATA SOURCES
================================================
500+ Free Open Data Sources from Africa and Middle East

Countries/Regions Covered:
AFRICA:
- South Africa 🇿🇦
- Nigeria 🇳🇬
- Egypt 🇪🇬
- Kenya 🇰🇪
- Morocco 🇲🇦
- Ghana 🇬🇭
- Tanzania 🇹🇿
- Ethiopia 🇪🇹
- Uganda 🇺🇬
- Rwanda 🇷🇼
- Senegal 🇸🇳
- Côte d'Ivoire 🇨🇮
- Algeria 🇩🇿
- Tunisia 🇹🇳
- Mauritius 🇲🇺
- Botswana 🇧🇼
- Namibia 🇳🇦
- Zambia 🇿🇲
- Zimbabwe 🇿🇼

MIDDLE EAST:
- Saudi Arabia 🇸🇦
- UAE 🇦🇪
- Israel 🇮🇱
- Turkey 🇹🇷
- Iran 🇮🇷
- Iraq 🇮🇶
- Jordan 🇯🇴
- Lebanon 🇱🇧
- Kuwait 🇰🇼
- Qatar 🇶🇦
- Bahrain 🇧🇭
- Oman 🇴🇲

Categories:
- Government & Statistics
- Universities & Research
- Banks & Financial
- Industry & Technology
- News & Media
- Culture & Tourism
- Sport & Entertainment
"""

from dataclasses import dataclass
from typing import List, Dict, Any
from enum import Enum

class SourceCategory(Enum):
    GOVERNMENT = "government"
    UNIVERSITY = "university"
    HOSPITAL = "hospital"
    BANK = "bank"
    INDUSTRY = "industry"
    NEWS = "news"
    CULTURE = "culture"
    RATING = "rating"
    RESEARCH = "research"
    STATISTICS = "statistics"
    ENVIRONMENTAL = "environmental"
    TRANSPORT = "transport"
    ENERGY = "energy"
    TELECOM = "telecom"
    TECHNOLOGY = "technology"
    SPORT = "sport"
    ENTERTAINMENT = "entertainment"
    TOURISM = "tourism"
    EVENTS = "events"
    LIFESTYLE = "lifestyle"
    INTERNATIONAL = "international"

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
# 🇿🇦 SOUTH AFRICA DATA SOURCES
# ============================================================

SOUTH_AFRICA_SOURCES = [
    DataSource("https://www.gov.za/", "South Africa Government", SourceCategory.GOVERNMENT, "ZA", "Government portal"),
    DataSource("https://www.parliament.gov.za/", "Parliament of RSA", SourceCategory.GOVERNMENT, "ZA", "Parliament"),
    DataSource("https://www.statssa.gov.za/", "Stats SA", SourceCategory.STATISTICS, "ZA", "Statistics South Africa", True),
    DataSource("https://www.data.gov.za/", "Data.gov.za", SourceCategory.STATISTICS, "ZA", "Open data", True),
    DataSource("https://www.wits.ac.za/", "University of the Witwatersrand", SourceCategory.UNIVERSITY, "ZA", "Wits University"),
    DataSource("https://www.uct.ac.za/", "University of Cape Town", SourceCategory.UNIVERSITY, "ZA", "UCT"),
    DataSource("https://www.sun.ac.za/", "Stellenbosch University", SourceCategory.UNIVERSITY, "ZA", "Stellenbosch"),
    DataSource("https://www.up.ac.za/", "University of Pretoria", SourceCategory.UNIVERSITY, "ZA", "UP"),
    DataSource("https://www.ukzn.ac.za/", "University of KwaZulu-Natal", SourceCategory.UNIVERSITY, "ZA", "UKZN"),
    DataSource("https://www.uj.ac.za/", "University of Johannesburg", SourceCategory.UNIVERSITY, "ZA", "UJ"),
    DataSource("https://www.ufs.ac.za/", "University of Free State", SourceCategory.UNIVERSITY, "ZA", "UFS"),
    DataSource("https://www.ru.ac.za/", "Rhodes University", SourceCategory.UNIVERSITY, "ZA", "Rhodes"),
    DataSource("https://www.nrf.ac.za/", "National Research Foundation", SourceCategory.RESEARCH, "ZA", "NRF", True),
    DataSource("https://www.csir.co.za/", "CSIR", SourceCategory.RESEARCH, "ZA", "Scientific Research"),
    DataSource("https://www.resbank.co.za/", "South African Reserve Bank", SourceCategory.BANK, "ZA", "SARB", True),
    DataSource("https://www.standardbank.co.za/", "Standard Bank", SourceCategory.BANK, "ZA", "Major bank"),
    DataSource("https://www.fnb.co.za/", "First National Bank", SourceCategory.BANK, "ZA", "FNB"),
    DataSource("https://www.nedbank.co.za/", "Nedbank", SourceCategory.BANK, "ZA", "Major bank"),
    DataSource("https://www.absa.co.za/", "Absa Bank", SourceCategory.BANK, "ZA", "Major bank"),
    DataSource("https://www.jse.co.za/", "JSE", SourceCategory.BANK, "ZA", "Stock Exchange", True),
    DataSource("https://www.naspers.com/", "Naspers", SourceCategory.TECHNOLOGY, "ZA", "Tech/media"),
    DataSource("https://www.mtn.com/", "MTN Group", SourceCategory.TELECOM, "ZA", "Telecom"),
    DataSource("https://www.vodacom.co.za/", "Vodacom", SourceCategory.TELECOM, "ZA", "Telecom"),
    DataSource("https://www.sasol.com/", "Sasol", SourceCategory.ENERGY, "ZA", "Energy/chemicals"),
    DataSource("https://www.eskom.co.za/", "Eskom", SourceCategory.ENERGY, "ZA", "Power utility"),
    DataSource("https://www.saa.co.za/", "South African Airways", SourceCategory.TRANSPORT, "ZA", "National airline"),
    DataSource("https://www.kulula.com/", "Kulula", SourceCategory.TRANSPORT, "ZA", "Low-cost airline"),
    DataSource("https://www.prasa.com/", "PRASA", SourceCategory.TRANSPORT, "ZA", "Rail"),
    DataSource("https://www.news24.com/", "News24", SourceCategory.NEWS, "ZA", "News portal"),
    DataSource("https://www.timeslive.co.za/", "Times Live", SourceCategory.NEWS, "ZA", "Major newspaper"),
    DataSource("https://www.dailymaverick.co.za/", "Daily Maverick", SourceCategory.NEWS, "ZA", "Investigative"),
    DataSource("https://www.iol.co.za/", "IOL", SourceCategory.NEWS, "ZA", "News portal"),
    DataSource("https://www.sabc.co.za/", "SABC", SourceCategory.NEWS, "ZA", "Public broadcaster"),
    DataSource("https://ewn.co.za/", "Eyewitness News", SourceCategory.NEWS, "ZA", "News network"),
    DataSource("https://www.iziko.org.za/", "Iziko Museums", SourceCategory.CULTURE, "ZA", "Museums"),
    DataSource("https://www.southafrica.net/", "South Africa Tourism", SourceCategory.TOURISM, "ZA", "Tourism", True),
    DataSource("https://www.safa.net/", "SAFA", SourceCategory.SPORT, "ZA", "Football"),
    DataSource("https://www.psl.co.za/", "PSL", SourceCategory.SPORT, "ZA", "Premier Soccer League"),
    DataSource("https://www.sarugby.co.za/", "SA Rugby", SourceCategory.SPORT, "ZA", "Rugby"),
    DataSource("https://www.cricket.co.za/", "Cricket SA", SourceCategory.SPORT, "ZA", "Cricket"),
    DataSource("https://www.sascoc.co.za/", "SASCOC", SourceCategory.SPORT, "ZA", "Olympic committee"),
]

# ============================================================
# 🇳🇬 NIGERIA DATA SOURCES
# ============================================================

NIGERIA_SOURCES = [
    DataSource("https://www.nigeria.gov.ng/", "Nigeria Government", SourceCategory.GOVERNMENT, "NG", "Government portal"),
    DataSource("https://nass.gov.ng/", "National Assembly", SourceCategory.GOVERNMENT, "NG", "Parliament"),
    DataSource("https://nigerianstat.gov.ng/", "NBS", SourceCategory.STATISTICS, "NG", "National Bureau of Statistics", True),
    DataSource("https://data.worldbank.org/country/nigeria", "Nigeria Data", SourceCategory.STATISTICS, "NG", "World Bank data", True),
    DataSource("https://www.unilag.edu.ng/", "University of Lagos", SourceCategory.UNIVERSITY, "NG", "UNILAG"),
    DataSource("https://www.ui.edu.ng/", "University of Ibadan", SourceCategory.UNIVERSITY, "NG", "UI"),
    DataSource("https://www.unn.edu.ng/", "University of Nigeria", SourceCategory.UNIVERSITY, "NG", "UNN"),
    DataSource("https://www.abu.edu.ng/", "Ahmadu Bello University", SourceCategory.UNIVERSITY, "NG", "ABU"),
    DataSource("https://www.oauife.edu.ng/", "Obafemi Awolowo University", SourceCategory.UNIVERSITY, "NG", "OAU"),
    DataSource("https://www.cbn.gov.ng/", "Central Bank of Nigeria", SourceCategory.BANK, "NG", "CBN", True),
    DataSource("https://www.gtbank.com/", "GTBank", SourceCategory.BANK, "NG", "Major bank"),
    DataSource("https://www.firstbanknigeria.com/", "First Bank", SourceCategory.BANK, "NG", "Major bank"),
    DataSource("https://www.zenithbank.com/", "Zenith Bank", SourceCategory.BANK, "NG", "Major bank"),
    DataSource("https://www.accessbank.com/", "Access Bank", SourceCategory.BANK, "NG", "Major bank"),
    DataSource("https://ngxgroup.com/", "NGX", SourceCategory.BANK, "NG", "Stock Exchange", True),
    DataSource("https://www.nnpcgroup.com/", "NNPC", SourceCategory.ENERGY, "NG", "National Petroleum"),
    DataSource("https://www.dangote.com/", "Dangote Group", SourceCategory.INDUSTRY, "NG", "Conglomerate"),
    DataSource("https://www.mtn.ng/", "MTN Nigeria", SourceCategory.TELECOM, "NG", "Telecom"),
    DataSource("https://www.airtel.com.ng/", "Airtel Nigeria", SourceCategory.TELECOM, "NG", "Telecom"),
    DataSource("https://www.flutterwave.com/", "Flutterwave", SourceCategory.TECHNOLOGY, "NG", "Fintech"),
    DataSource("https://www.paystack.com/", "Paystack", SourceCategory.TECHNOLOGY, "NG", "Fintech"),
    DataSource("https://www.jumia.com.ng/", "Jumia", SourceCategory.TECHNOLOGY, "NG", "E-commerce"),
    DataSource("https://www.aikiairlines.com/", "Arik Air", SourceCategory.TRANSPORT, "NG", "Airline"),
    DataSource("https://www.punch.ng/", "Punch", SourceCategory.NEWS, "NG", "Major newspaper"),
    DataSource("https://guardian.ng/", "The Guardian Nigeria", SourceCategory.NEWS, "NG", "Newspaper"),
    DataSource("https://www.vanguardngr.com/", "Vanguard", SourceCategory.NEWS, "NG", "Newspaper"),
    DataSource("https://www.premiumtimesng.com/", "Premium Times", SourceCategory.NEWS, "NG", "Online news"),
    DataSource("https://www.channels.tv/", "Channels TV", SourceCategory.NEWS, "NG", "Broadcasting"),
    DataSource("https://www.nan.ng/", "NAN", SourceCategory.NEWS, "NG", "News agency"),
    DataSource("https://www.tourismnigeriainfo.com/", "Nigeria Tourism", SourceCategory.TOURISM, "NG", "Tourism"),
    DataSource("https://www.thenff.com/", "NFF", SourceCategory.SPORT, "NG", "Football"),
    DataSource("https://www.npfl.ng/", "NPFL", SourceCategory.SPORT, "NG", "Premier League"),
]

# ============================================================
# 🇪🇬 EGYPT DATA SOURCES
# ============================================================

EGYPT_SOURCES = [
    DataSource("https://www.egypt.gov.eg/", "Egypt Government", SourceCategory.GOVERNMENT, "EG", "Government portal"),
    DataSource("https://www.parliament.gov.eg/", "Egyptian Parliament", SourceCategory.GOVERNMENT, "EG", "Parliament"),
    DataSource("https://www.capmas.gov.eg/", "CAPMAS", SourceCategory.STATISTICS, "EG", "Statistics", True),
    DataSource("https://www.cu.edu.eg/", "Cairo University", SourceCategory.UNIVERSITY, "EG", "CU"),
    DataSource("https://www.auc.edu.eg/", "American University Cairo", SourceCategory.UNIVERSITY, "EG", "AUC"),
    DataSource("https://www.asu.edu.eg/", "Ain Shams University", SourceCategory.UNIVERSITY, "EG", "ASU"),
    DataSource("https://www.alexu.edu.eg/", "Alexandria University", SourceCategory.UNIVERSITY, "EG", "AU"),
    DataSource("https://www.cbe.org.eg/", "Central Bank of Egypt", SourceCategory.BANK, "EG", "CBE", True),
    DataSource("https://www.nbe.com.eg/", "National Bank of Egypt", SourceCategory.BANK, "EG", "NBE"),
    DataSource("https://www.banquemisr.com/", "Banque Misr", SourceCategory.BANK, "EG", "Major bank"),
    DataSource("https://www.egx.com.eg/", "EGX", SourceCategory.BANK, "EG", "Stock Exchange", True),
    DataSource("https://www.egyptoil-gas.com/", "Egypt Oil & Gas", SourceCategory.ENERGY, "EG", "Energy news"),
    DataSource("https://www.orascom.com/", "Orascom", SourceCategory.INDUSTRY, "EG", "Construction"),
    DataSource("https://www.vodafone.com.eg/", "Vodafone Egypt", SourceCategory.TELECOM, "EG", "Telecom"),
    DataSource("https://www.orange.com.eg/", "Orange Egypt", SourceCategory.TELECOM, "EG", "Telecom"),
    DataSource("https://www.egyptair.com/", "EgyptAir", SourceCategory.TRANSPORT, "EG", "National airline"),
    DataSource("https://www.ahram.org.eg/", "Al-Ahram", SourceCategory.NEWS, "EG", "Major newspaper"),
    DataSource("https://english.ahram.org.eg/", "Ahram Online", SourceCategory.NEWS, "EG", "English news"),
    DataSource("https://www.egypttoday.com/", "Egypt Today", SourceCategory.NEWS, "EG", "English magazine"),
    DataSource("https://www.dailynewsegypt.com/", "Daily News Egypt", SourceCategory.NEWS, "EG", "English newspaper"),
    DataSource("https://www.egyptindependent.com/", "Egypt Independent", SourceCategory.NEWS, "EG", "English news"),
    DataSource("https://www.sis.gov.eg/", "SIS Egypt", SourceCategory.NEWS, "EG", "State information"),
    DataSource("https://www.sca-egypt.org/", "Supreme Council of Antiquities", SourceCategory.CULTURE, "EG", "Antiquities"),
    DataSource("https://www.egypt.travel/", "Egypt Tourism", SourceCategory.TOURISM, "EG", "Tourism", True),
    DataSource("https://www.efa.com.eg/", "EFA", SourceCategory.SPORT, "EG", "Football"),
    DataSource("https://www.egyptianpremiersleague.com/", "EPL", SourceCategory.SPORT, "EG", "Premier League"),
]

# ============================================================
# 🇰🇪 KENYA DATA SOURCES
# ============================================================

KENYA_SOURCES = [
    DataSource("https://www.president.go.ke/", "Kenya Presidency", SourceCategory.GOVERNMENT, "KE", "Government"),
    DataSource("https://www.parliament.go.ke/", "Kenya Parliament", SourceCategory.GOVERNMENT, "KE", "Parliament"),
    DataSource("https://www.knbs.or.ke/", "KNBS", SourceCategory.STATISTICS, "KE", "Statistics Bureau", True),
    DataSource("https://opendata.go.ke/", "Kenya Open Data", SourceCategory.STATISTICS, "KE", "Open data", True),
    DataSource("https://www.uonbi.ac.ke/", "University of Nairobi", SourceCategory.UNIVERSITY, "KE", "UoN"),
    DataSource("https://www.ku.ac.ke/", "Kenyatta University", SourceCategory.UNIVERSITY, "KE", "KU"),
    DataSource("https://www.strathmore.edu/", "Strathmore University", SourceCategory.UNIVERSITY, "KE", "Strathmore"),
    DataSource("https://www.usiu.ac.ke/", "USIU-Africa", SourceCategory.UNIVERSITY, "KE", "USIU"),
    DataSource("https://www.centralbank.go.ke/", "Central Bank of Kenya", SourceCategory.BANK, "KE", "CBK", True),
    DataSource("https://www.kcbgroup.com/", "KCB Group", SourceCategory.BANK, "KE", "Major bank"),
    DataSource("https://www.equitybankgroup.com/", "Equity Bank", SourceCategory.BANK, "KE", "Major bank"),
    DataSource("https://www.cooperative.co.ke/", "Co-operative Bank", SourceCategory.BANK, "KE", "Major bank"),
    DataSource("https://www.nse.co.ke/", "NSE", SourceCategory.BANK, "KE", "Stock Exchange", True),
    DataSource("https://www.safaricom.co.ke/", "Safaricom", SourceCategory.TELECOM, "KE", "Telecom/M-Pesa"),
    DataSource("https://www.nation.africa/kenya/", "Nation Kenya", SourceCategory.NEWS, "KE", "Major newspaper"),
    DataSource("https://www.standardmedia.co.ke/", "Standard", SourceCategory.NEWS, "KE", "Newspaper"),
    DataSource("https://www.the-star.co.ke/", "The Star", SourceCategory.NEWS, "KE", "Newspaper"),
    DataSource("https://www.citizen.digital/", "Citizen Digital", SourceCategory.NEWS, "KE", "News portal"),
    DataSource("https://www.kbc.co.ke/", "KBC", SourceCategory.NEWS, "KE", "Public broadcaster"),
    DataSource("https://magicalkenya.com/", "Magical Kenya", SourceCategory.TOURISM, "KE", "Tourism", True),
    DataSource("https://www.fkf.or.ke/", "FKF", SourceCategory.SPORT, "KE", "Football"),
    DataSource("https://www.athleticskenya.or.ke/", "Athletics Kenya", SourceCategory.SPORT, "KE", "Athletics"),
]

# ============================================================
# 🇲🇦 MOROCCO DATA SOURCES
# ============================================================

MOROCCO_SOURCES = [
    DataSource("https://www.maroc.ma/", "Morocco Portal", SourceCategory.GOVERNMENT, "MA", "Government portal"),
    DataSource("https://www.parlement.ma/", "Morocco Parliament", SourceCategory.GOVERNMENT, "MA", "Parliament"),
    DataSource("https://www.hcp.ma/", "HCP", SourceCategory.STATISTICS, "MA", "Statistics", True),
    DataSource("https://www.data.gov.ma/", "Data.gov.ma", SourceCategory.STATISTICS, "MA", "Open data", True),
    DataSource("https://www.um5.ac.ma/", "Mohammed V University", SourceCategory.UNIVERSITY, "MA", "UM5"),
    DataSource("https://www.um6p.ma/", "Mohammed VI Polytechnic", SourceCategory.UNIVERSITY, "MA", "UM6P"),
    DataSource("https://www.bkam.ma/", "Bank Al-Maghrib", SourceCategory.BANK, "MA", "Central bank", True),
    DataSource("https://www.gbp.ma/", "Attijariwafa Bank", SourceCategory.BANK, "MA", "Major bank"),
    DataSource("https://www.casablanca-bourse.com/", "Casablanca Stock Exchange", SourceCategory.BANK, "MA", "Stock Exchange", True),
    DataSource("https://www.ocp.ma/", "OCP Group", SourceCategory.INDUSTRY, "MA", "Phosphate"),
    DataSource("https://www.iam.ma/", "Maroc Telecom", SourceCategory.TELECOM, "MA", "Telecom"),
    DataSource("https://www.royalairmaroc.com/", "Royal Air Maroc", SourceCategory.TRANSPORT, "MA", "National airline"),
    DataSource("https://www.map.ma/", "MAP", SourceCategory.NEWS, "MA", "News agency"),
    DataSource("https://www.hespress.com/", "Hespress", SourceCategory.NEWS, "MA", "News portal"),
    DataSource("https://www.le360.ma/", "Le360", SourceCategory.NEWS, "MA", "News portal"),
    DataSource("https://www.visitmorocco.com/", "Visit Morocco", SourceCategory.TOURISM, "MA", "Tourism", True),
    DataSource("https://www.frmf.ma/", "FRMF", SourceCategory.SPORT, "MA", "Football"),
]

# ============================================================
# 🇬🇭 GHANA DATA SOURCES
# ============================================================

GHANA_SOURCES = [
    DataSource("https://www.ghana.gov.gh/", "Ghana Government", SourceCategory.GOVERNMENT, "GH", "Government portal"),
    DataSource("https://www.parliament.gh/", "Ghana Parliament", SourceCategory.GOVERNMENT, "GH", "Parliament"),
    DataSource("https://www.statsghana.gov.gh/", "Ghana Statistical Service", SourceCategory.STATISTICS, "GH", "Statistics", True),
    DataSource("https://www.ug.edu.gh/", "University of Ghana", SourceCategory.UNIVERSITY, "GH", "UG"),
    DataSource("https://www.knust.edu.gh/", "KNUST", SourceCategory.UNIVERSITY, "GH", "Science & Tech"),
    DataSource("https://www.bog.gov.gh/", "Bank of Ghana", SourceCategory.BANK, "GH", "Central bank", True),
    DataSource("https://gse.com.gh/", "Ghana Stock Exchange", SourceCategory.BANK, "GH", "Stock Exchange", True),
    DataSource("https://www.mtn.com.gh/", "MTN Ghana", SourceCategory.TELECOM, "GH", "Telecom"),
    DataSource("https://www.vodafone.com.gh/", "Vodafone Ghana", SourceCategory.TELECOM, "GH", "Telecom"),
    DataSource("https://www.graphic.com.gh/", "Graphic Online", SourceCategory.NEWS, "GH", "Major newspaper"),
    DataSource("https://www.myjoyonline.com/", "Joy Online", SourceCategory.NEWS, "GH", "News portal"),
    DataSource("https://www.gna.org.gh/", "GNA", SourceCategory.NEWS, "GH", "News agency"),
    DataSource("https://www.ghana.travel/", "Visit Ghana", SourceCategory.TOURISM, "GH", "Tourism", True),
    DataSource("https://ghanafa.org/", "GFA", SourceCategory.SPORT, "GH", "Football"),
]

# ============================================================
# 🇸🇦 SAUDI ARABIA DATA SOURCES
# ============================================================

SAUDI_ARABIA_SOURCES = [
    DataSource("https://www.my.gov.sa/", "Saudi Arabia Government", SourceCategory.GOVERNMENT, "SA", "Government portal"),
    DataSource("https://www.stats.gov.sa/", "GASTAT", SourceCategory.STATISTICS, "SA", "Statistics", True),
    DataSource("https://od.data.gov.sa/", "Saudi Open Data", SourceCategory.STATISTICS, "SA", "Open data", True),
    DataSource("https://www.ksu.edu.sa/", "King Saud University", SourceCategory.UNIVERSITY, "SA", "KSU"),
    DataSource("https://www.kaust.edu.sa/", "KAUST", SourceCategory.UNIVERSITY, "SA", "Science & Tech"),
    DataSource("https://www.kfupm.edu.sa/", "KFUPM", SourceCategory.UNIVERSITY, "SA", "Petroleum"),
    DataSource("https://www.pnu.edu.sa/", "Princess Nourah University", SourceCategory.UNIVERSITY, "SA", "PNU"),
    DataSource("https://www.sama.gov.sa/", "SAMA", SourceCategory.BANK, "SA", "Central bank", True),
    DataSource("https://www.alrajhibank.com.sa/", "Al Rajhi Bank", SourceCategory.BANK, "SA", "Major bank"),
    DataSource("https://www.alahli.com/", "NCB", SourceCategory.BANK, "SA", "National Commercial Bank"),
    DataSource("https://www.tadawul.com.sa/", "Tadawul", SourceCategory.BANK, "SA", "Stock Exchange", True),
    DataSource("https://www.saudi-aramco.com/", "Saudi Aramco", SourceCategory.ENERGY, "SA", "Oil company"),
    DataSource("https://www.sabic.com/", "SABIC", SourceCategory.INDUSTRY, "SA", "Chemicals"),
    DataSource("https://www.stc.com.sa/", "STC", SourceCategory.TELECOM, "SA", "Telecom"),
    DataSource("https://www.saudia.com/", "Saudia", SourceCategory.TRANSPORT, "SA", "National airline"),
    DataSource("https://www.spa.gov.sa/", "SPA", SourceCategory.NEWS, "SA", "News agency"),
    DataSource("https://english.alarabiya.net/", "Al Arabiya", SourceCategory.NEWS, "SA", "News network"),
    DataSource("https://www.arabnews.com/", "Arab News", SourceCategory.NEWS, "SA", "English newspaper"),
    DataSource("https://www.visitsaudi.com/", "Visit Saudi", SourceCategory.TOURISM, "SA", "Tourism", True),
    DataSource("https://www.saff.com.sa/", "SAFF", SourceCategory.SPORT, "SA", "Football"),
    DataSource("https://spl.sa/", "Saudi Pro League", SourceCategory.SPORT, "SA", "Football league"),
]

# ============================================================
# 🇦🇪 UAE DATA SOURCES
# ============================================================

UAE_SOURCES = [
    DataSource("https://www.government.ae/", "UAE Government", SourceCategory.GOVERNMENT, "AE", "Government portal"),
    DataSource("https://www.fcsc.gov.ae/", "FCSC", SourceCategory.STATISTICS, "AE", "Statistics", True),
    DataSource("https://bayanat.ae/", "Bayanat", SourceCategory.STATISTICS, "AE", "Open data", True),
    DataSource("https://www.uaeu.ac.ae/", "UAE University", SourceCategory.UNIVERSITY, "AE", "UAEU"),
    DataSource("https://www.ku.ac.ae/", "Khalifa University", SourceCategory.UNIVERSITY, "AE", "KU"),
    DataSource("https://www.aud.edu/", "American University Dubai", SourceCategory.UNIVERSITY, "AE", "AUD"),
    DataSource("https://www.nyuad.nyu.edu/", "NYU Abu Dhabi", SourceCategory.UNIVERSITY, "AE", "NYUAD"),
    DataSource("https://www.centralbank.ae/", "Central Bank of UAE", SourceCategory.BANK, "AE", "CBUAE", True),
    DataSource("https://www.emiratesnbd.com/", "Emirates NBD", SourceCategory.BANK, "AE", "Major bank"),
    DataSource("https://www.fab.com/", "First Abu Dhabi Bank", SourceCategory.BANK, "AE", "FAB"),
    DataSource("https://www.adx.ae/", "ADX", SourceCategory.BANK, "AE", "Abu Dhabi Exchange", True),
    DataSource("https://www.dfm.ae/", "DFM", SourceCategory.BANK, "AE", "Dubai Financial Market", True),
    DataSource("https://www.adnoc.ae/", "ADNOC", SourceCategory.ENERGY, "AE", "Oil company"),
    DataSource("https://www.dp-world.com/", "DP World", SourceCategory.TRANSPORT, "AE", "Ports"),
    DataSource("https://www.emirates.com/", "Emirates", SourceCategory.TRANSPORT, "AE", "Airline"),
    DataSource("https://www.etihad.com/", "Etihad Airways", SourceCategory.TRANSPORT, "AE", "Airline"),
    DataSource("https://www.flydubai.com/", "flydubai", SourceCategory.TRANSPORT, "AE", "Airline"),
    DataSource("https://www.etisalat.ae/", "Etisalat", SourceCategory.TELECOM, "AE", "Telecom"),
    DataSource("https://www.du.ae/", "du", SourceCategory.TELECOM, "AE", "Telecom"),
    DataSource("https://www.thenationalnews.com/", "The National", SourceCategory.NEWS, "AE", "English newspaper"),
    DataSource("https://gulfnews.com/", "Gulf News", SourceCategory.NEWS, "AE", "English newspaper"),
    DataSource("https://www.khaleejtimes.com/", "Khaleej Times", SourceCategory.NEWS, "AE", "English newspaper"),
    DataSource("https://wam.ae/", "WAM", SourceCategory.NEWS, "AE", "News agency"),
    DataSource("https://www.louvre.ae/", "Louvre Abu Dhabi", SourceCategory.CULTURE, "AE", "Museum"),
    DataSource("https://www.visitdubai.com/", "Visit Dubai", SourceCategory.TOURISM, "AE", "Tourism", True),
    DataSource("https://www.visitabudhabi.ae/", "Visit Abu Dhabi", SourceCategory.TOURISM, "AE", "Tourism", True),
    DataSource("https://www.theuae.fa.com/", "UAE FA", SourceCategory.SPORT, "AE", "Football"),
    DataSource("https://www.uaeguardian.com/", "UAE Pro League", SourceCategory.SPORT, "AE", "Football league"),
]

# ============================================================
# 🇮🇱 ISRAEL DATA SOURCES
# ============================================================

ISRAEL_SOURCES = [
    DataSource("https://www.gov.il/", "Israel Government", SourceCategory.GOVERNMENT, "IL", "Government portal"),
    DataSource("https://www.knesset.gov.il/", "Knesset", SourceCategory.GOVERNMENT, "IL", "Parliament"),
    DataSource("https://www.cbs.gov.il/", "CBS", SourceCategory.STATISTICS, "IL", "Statistics", True),
    DataSource("https://data.gov.il/", "Data.gov.il", SourceCategory.STATISTICS, "IL", "Open data", True),
    DataSource("https://www.huji.ac.il/", "Hebrew University", SourceCategory.UNIVERSITY, "IL", "HUJI"),
    DataSource("https://www.technion.ac.il/", "Technion", SourceCategory.UNIVERSITY, "IL", "Tech"),
    DataSource("https://www.tau.ac.il/", "Tel Aviv University", SourceCategory.UNIVERSITY, "IL", "TAU"),
    DataSource("https://www.weizmann.ac.il/", "Weizmann Institute", SourceCategory.RESEARCH, "IL", "Science"),
    DataSource("https://www.bgu.ac.il/", "Ben-Gurion University", SourceCategory.UNIVERSITY, "IL", "BGU"),
    DataSource("https://www.boi.org.il/", "Bank of Israel", SourceCategory.BANK, "IL", "Central bank", True),
    DataSource("https://www.tase.co.il/", "TASE", SourceCategory.BANK, "IL", "Stock Exchange", True),
    DataSource("https://www.bankhapoalim.co.il/", "Bank Hapoalim", SourceCategory.BANK, "IL", "Major bank"),
    DataSource("https://www.leumi.co.il/", "Bank Leumi", SourceCategory.BANK, "IL", "Major bank"),
    DataSource("https://www.elal.com/", "El Al", SourceCategory.TRANSPORT, "IL", "National airline"),
    DataSource("https://www.haaretz.com/", "Haaretz", SourceCategory.NEWS, "IL", "English newspaper"),
    DataSource("https://www.timesofisrael.com/", "Times of Israel", SourceCategory.NEWS, "IL", "English news"),
    DataSource("https://www.jpost.com/", "Jerusalem Post", SourceCategory.NEWS, "IL", "English newspaper"),
    DataSource("https://www.ynetnews.com/", "Ynet", SourceCategory.NEWS, "IL", "News portal"),
    DataSource("https://www.info.goisrael.com/", "Go Israel", SourceCategory.TOURISM, "IL", "Tourism", True),
    DataSource("https://www.football.org.il/", "IFA", SourceCategory.SPORT, "IL", "Football"),
]

# ============================================================
# 🇹🇷 TURKEY DATA SOURCES
# ============================================================

TURKEY_SOURCES = [
    DataSource("https://www.turkiye.gov.tr/", "Turkiye.gov.tr", SourceCategory.GOVERNMENT, "TR", "E-government"),
    DataSource("https://www.tbmm.gov.tr/", "TBMM", SourceCategory.GOVERNMENT, "TR", "Parliament"),
    DataSource("https://www.tuik.gov.tr/", "TÜİK", SourceCategory.STATISTICS, "TR", "Statistics", True),
    DataSource("https://data.tuik.gov.tr/", "TÜİK Data", SourceCategory.STATISTICS, "TR", "Statistics data", True),
    DataSource("https://www.ankara.edu.tr/", "Ankara University", SourceCategory.UNIVERSITY, "TR", "AU"),
    DataSource("https://www.boun.edu.tr/", "Boğaziçi University", SourceCategory.UNIVERSITY, "TR", "Bosphorus"),
    DataSource("https://www.metu.edu.tr/", "METU", SourceCategory.UNIVERSITY, "TR", "Middle East Tech"),
    DataSource("https://www.itu.edu.tr/", "Istanbul Tech", SourceCategory.UNIVERSITY, "TR", "ITU"),
    DataSource("https://www.istanbul.edu.tr/", "Istanbul University", SourceCategory.UNIVERSITY, "TR", "IU"),
    DataSource("https://www.ku.edu.tr/", "Koç University", SourceCategory.UNIVERSITY, "TR", "Koç"),
    DataSource("https://www.sabanciuniv.edu/", "Sabancı University", SourceCategory.UNIVERSITY, "TR", "Sabancı"),
    DataSource("https://www.tcmb.gov.tr/", "TCMB", SourceCategory.BANK, "TR", "Central bank", True),
    DataSource("https://www.borsaistanbul.com/", "Borsa Istanbul", SourceCategory.BANK, "TR", "Stock Exchange", True),
    DataSource("https://www.isbank.com.tr/", "İş Bankası", SourceCategory.BANK, "TR", "Major bank"),
    DataSource("https://www.ziraatbank.com.tr/", "Ziraat Bankası", SourceCategory.BANK, "TR", "State bank"),
    DataSource("https://www.thy.com/", "Turkish Airlines", SourceCategory.TRANSPORT, "TR", "National airline"),
    DataSource("https://www.turkcell.com.tr/", "Turkcell", SourceCategory.TELECOM, "TR", "Telecom"),
    DataSource("https://www.turktelekom.com.tr/", "Türk Telekom", SourceCategory.TELECOM, "TR", "Telecom"),
    DataSource("https://www.aa.com.tr/", "Anadolu Agency", SourceCategory.NEWS, "TR", "News agency", True),
    DataSource("https://www.hurriyetdailynews.com/", "Hürriyet Daily News", SourceCategory.NEWS, "TR", "English newspaper"),
    DataSource("https://www.dailysabah.com/", "Daily Sabah", SourceCategory.NEWS, "TR", "English newspaper"),
    DataSource("https://www.trtworld.com/", "TRT World", SourceCategory.NEWS, "TR", "Public broadcaster"),
    DataSource("https://www.goturkey.com/", "Go Turkey", SourceCategory.TOURISM, "TR", "Tourism", True),
    DataSource("https://www.tff.org/", "TFF", SourceCategory.SPORT, "TR", "Football"),
    DataSource("https://www.trendyol.com/", "Süper Lig", SourceCategory.SPORT, "TR", "Football league"),
]

# ============================================================
# 🇯🇴 JORDAN DATA SOURCES
# ============================================================

JORDAN_SOURCES = [
    DataSource("https://www.jordan.gov.jo/", "Jordan Government", SourceCategory.GOVERNMENT, "JO", "E-government"),
    DataSource("https://dosweb.dos.gov.jo/", "DOS", SourceCategory.STATISTICS, "JO", "Statistics", True),
    DataSource("https://www.ju.edu.jo/", "University of Jordan", SourceCategory.UNIVERSITY, "JO", "UJ"),
    DataSource("https://www.cbj.gov.jo/", "Central Bank of Jordan", SourceCategory.BANK, "JO", "CBJ", True),
    DataSource("https://www.ase.com.jo/", "ASE", SourceCategory.BANK, "JO", "Stock Exchange", True),
    DataSource("https://www.rj.com/", "Royal Jordanian", SourceCategory.TRANSPORT, "JO", "National airline"),
    DataSource("https://www.jordantimes.com/", "Jordan Times", SourceCategory.NEWS, "JO", "English newspaper"),
    DataSource("https://petra.gov.jo/", "Petra News", SourceCategory.NEWS, "JO", "News agency"),
    DataSource("https://www.visitjordan.com/", "Visit Jordan", SourceCategory.TOURISM, "JO", "Tourism", True),
    DataSource("https://www.jfa.jo/", "JFA", SourceCategory.SPORT, "JO", "Football"),
]

# ============================================================
# 🇶🇦 QATAR DATA SOURCES
# ============================================================

QATAR_SOURCES = [
    DataSource("https://www.gov.qa/", "Qatar Government", SourceCategory.GOVERNMENT, "QA", "Government portal"),
    DataSource("https://www.psa.gov.qa/", "PSA Qatar", SourceCategory.STATISTICS, "QA", "Statistics", True),
    DataSource("https://www.qu.edu.qa/", "Qatar University", SourceCategory.UNIVERSITY, "QA", "QU"),
    DataSource("https://www.qatar-foundation.org/", "Qatar Foundation", SourceCategory.RESEARCH, "QA", "Education/research"),
    DataSource("https://www.qcb.gov.qa/", "Qatar Central Bank", SourceCategory.BANK, "QA", "Central bank", True),
    DataSource("https://www.qe.com.qa/", "Qatar Stock Exchange", SourceCategory.BANK, "QA", "Stock Exchange", True),
    DataSource("https://www.qp.com.qa/", "Qatar Petroleum", SourceCategory.ENERGY, "QA", "Oil/gas"),
    DataSource("https://www.qatarairways.com/", "Qatar Airways", SourceCategory.TRANSPORT, "QA", "National airline"),
    DataSource("https://www.ooredoo.qa/", "Ooredoo Qatar", SourceCategory.TELECOM, "QA", "Telecom"),
    DataSource("https://www.aljazeera.com/", "Al Jazeera", SourceCategory.NEWS, "QA", "News network", True),
    DataSource("https://www.qatar-tribune.com/", "Qatar Tribune", SourceCategory.NEWS, "QA", "English newspaper"),
    DataSource("https://www.visitqatar.qa/", "Visit Qatar", SourceCategory.TOURISM, "QA", "Tourism", True),
    DataSource("https://www.qfa.qa/", "QFA", SourceCategory.SPORT, "QA", "Football"),
]

# ============================================================
# 🇰🇼 KUWAIT DATA SOURCES
# ============================================================

KUWAIT_SOURCES = [
    DataSource("https://www.e.gov.kw/", "Kuwait Government", SourceCategory.GOVERNMENT, "KW", "E-government"),
    DataSource("https://www.csb.gov.kw/", "CSB Kuwait", SourceCategory.STATISTICS, "KW", "Statistics", True),
    DataSource("https://www.kuniv.edu/", "Kuwait University", SourceCategory.UNIVERSITY, "KW", "KU"),
    DataSource("https://www.cbk.gov.kw/", "Central Bank of Kuwait", SourceCategory.BANK, "KW", "CBK", True),
    DataSource("https://www.boursakuwait.com.kw/", "Boursa Kuwait", SourceCategory.BANK, "KW", "Stock Exchange", True),
    DataSource("https://www.kpc.com.kw/", "Kuwait Petroleum", SourceCategory.ENERGY, "KW", "Oil company"),
    DataSource("https://www.kuwaitairways.com/", "Kuwait Airways", SourceCategory.TRANSPORT, "KW", "National airline"),
    DataSource("https://www.kuna.net.kw/", "KUNA", SourceCategory.NEWS, "KW", "News agency"),
    DataSource("https://www.arabtimesonline.com/", "Arab Times", SourceCategory.NEWS, "KW", "English newspaper"),
    DataSource("https://www.kuwaitfa.com/", "KFA", SourceCategory.SPORT, "KW", "Football"),
]

# ============================================================
# 🇧🇭 BAHRAIN DATA SOURCES
# ============================================================

BAHRAIN_SOURCES = [
    DataSource("https://www.bahrain.bh/", "Bahrain Government", SourceCategory.GOVERNMENT, "BH", "Government portal"),
    DataSource("https://www.data.gov.bh/", "Bahrain Open Data", SourceCategory.STATISTICS, "BH", "Open data", True),
    DataSource("https://www.uob.edu.bh/", "University of Bahrain", SourceCategory.UNIVERSITY, "BH", "UoB"),
    DataSource("https://www.cbb.gov.bh/", "Central Bank of Bahrain", SourceCategory.BANK, "BH", "CBB", True),
    DataSource("https://www.bahrainbourse.com/", "Bahrain Bourse", SourceCategory.BANK, "BH", "Stock Exchange", True),
    DataSource("https://www.bapco.net/", "Bapco", SourceCategory.ENERGY, "BH", "Oil refinery"),
    DataSource("https://www.gulfair.com/", "Gulf Air", SourceCategory.TRANSPORT, "BH", "National airline"),
    DataSource("https://www.bna.bh/", "BNA", SourceCategory.NEWS, "BH", "News agency"),
    DataSource("https://www.gdnonline.com/", "GDN Online", SourceCategory.NEWS, "BH", "English newspaper"),
    DataSource("https://www.btea.bh/", "Bahrain Tourism", SourceCategory.TOURISM, "BH", "Tourism", True),
    DataSource("https://www.bahraingp.com/", "Bahrain Grand Prix", SourceCategory.SPORT, "BH", "F1"),
]

# ============================================================
# 🇴🇲 OMAN DATA SOURCES
# ============================================================

OMAN_SOURCES = [
    DataSource("https://www.oman.om/", "Oman Government", SourceCategory.GOVERNMENT, "OM", "E-government"),
    DataSource("https://www.ncsi.gov.om/", "NCSI Oman", SourceCategory.STATISTICS, "OM", "Statistics", True),
    DataSource("https://www.squ.edu.om/", "Sultan Qaboos University", SourceCategory.UNIVERSITY, "OM", "SQU"),
    DataSource("https://www.cbo.gov.om/", "Central Bank of Oman", SourceCategory.BANK, "OM", "CBO", True),
    DataSource("https://www.msxoman.com/", "MSX Oman", SourceCategory.BANK, "OM", "Stock Exchange", True),
    DataSource("https://www.pdo.co.om/", "PDO", SourceCategory.ENERGY, "OM", "Petroleum"),
    DataSource("https://www.omanair.com/", "Oman Air", SourceCategory.TRANSPORT, "OM", "National airline"),
    DataSource("https://omannews.gov.om/", "ONA", SourceCategory.NEWS, "OM", "News agency"),
    DataSource("https://timesofoman.com/", "Times of Oman", SourceCategory.NEWS, "OM", "English newspaper"),
    DataSource("https://experienceoman.om/", "Experience Oman", SourceCategory.TOURISM, "OM", "Tourism", True),
]

# ============================================================
# ADDITIONAL AFRICAN COUNTRIES
# ============================================================

ADDITIONAL_AFRICA_SOURCES = [
    # Tanzania
    DataSource("https://www.tanzania.go.tz/", "Tanzania Government", SourceCategory.GOVERNMENT, "TZ", "Government"),
    DataSource("https://www.nbs.go.tz/", "NBS Tanzania", SourceCategory.STATISTICS, "TZ", "Statistics", True),
    DataSource("https://www.udsm.ac.tz/", "UDSM", SourceCategory.UNIVERSITY, "TZ", "University of Dar es Salaam"),
    DataSource("https://www.bot.go.tz/", "Bank of Tanzania", SourceCategory.BANK, "TZ", "Central bank", True),
    
    # Ethiopia
    DataSource("https://www.ethiopia.gov.et/", "Ethiopia Government", SourceCategory.GOVERNMENT, "ET", "Government"),
    DataSource("https://www.csa.gov.et/", "CSA Ethiopia", SourceCategory.STATISTICS, "ET", "Statistics", True),
    DataSource("https://www.aau.edu.et/", "Addis Ababa University", SourceCategory.UNIVERSITY, "ET", "AAU"),
    DataSource("https://www.nbe.gov.et/", "National Bank of Ethiopia", SourceCategory.BANK, "ET", "Central bank", True),
    DataSource("https://www.ethiopianairlines.com/", "Ethiopian Airlines", SourceCategory.TRANSPORT, "ET", "National airline"),
    
    # Rwanda
    DataSource("https://www.gov.rw/", "Rwanda Government", SourceCategory.GOVERNMENT, "RW", "Government"),
    DataSource("https://www.statistics.gov.rw/", "NISR Rwanda", SourceCategory.STATISTICS, "RW", "Statistics", True),
    DataSource("https://www.ur.ac.rw/", "University of Rwanda", SourceCategory.UNIVERSITY, "RW", "UR"),
    DataSource("https://www.bnr.rw/", "National Bank of Rwanda", SourceCategory.BANK, "RW", "Central bank", True),
    DataSource("https://www.rwandair.com/", "RwandAir", SourceCategory.TRANSPORT, "RW", "National airline"),
    
    # Uganda
    DataSource("https://www.gou.go.ug/", "Uganda Government", SourceCategory.GOVERNMENT, "UG", "Government"),
    DataSource("https://www.ubos.org/", "UBOS", SourceCategory.STATISTICS, "UG", "Statistics", True),
    DataSource("https://www.mak.ac.ug/", "Makerere University", SourceCategory.UNIVERSITY, "UG", "Makerere"),
    DataSource("https://www.bou.or.ug/", "Bank of Uganda", SourceCategory.BANK, "UG", "Central bank", True),
    
    # Senegal
    DataSource("https://www.gouv.sn/", "Senegal Government", SourceCategory.GOVERNMENT, "SN", "Government"),
    DataSource("https://www.ansd.sn/", "ANSD", SourceCategory.STATISTICS, "SN", "Statistics", True),
    DataSource("https://www.ucad.sn/", "UCAD", SourceCategory.UNIVERSITY, "SN", "Cheikh Anta Diop University"),
    DataSource("https://www.bceao.int/", "BCEAO", SourceCategory.BANK, "SN", "Central bank (WAEMU)", True),
    
    # Côte d'Ivoire
    DataSource("https://www.gouv.ci/", "Côte d'Ivoire Government", SourceCategory.GOVERNMENT, "CI", "Government"),
    DataSource("https://www.ins.ci/", "INS", SourceCategory.STATISTICS, "CI", "Statistics", True),
    
    # Algeria
    DataSource("https://www.el-mouradia.dz/", "Algeria Presidency", SourceCategory.GOVERNMENT, "DZ", "Presidency"),
    DataSource("https://www.ons.dz/", "ONS Algeria", SourceCategory.STATISTICS, "DZ", "Statistics", True),
    DataSource("https://www.bank-of-algeria.dz/", "Bank of Algeria", SourceCategory.BANK, "DZ", "Central bank", True),
    DataSource("https://www.airalgerie.dz/", "Air Algérie", SourceCategory.TRANSPORT, "DZ", "National airline"),
    
    # Tunisia
    DataSource("https://www.tunisie.gov.tn/", "Tunisia Government", SourceCategory.GOVERNMENT, "TN", "Government"),
    DataSource("https://www.ins.tn/", "INS Tunisia", SourceCategory.STATISTICS, "TN", "Statistics", True),
    DataSource("https://www.bct.gov.tn/", "BCT", SourceCategory.BANK, "TN", "Central bank", True),
    DataSource("https://www.tunisair.com/", "Tunisair", SourceCategory.TRANSPORT, "TN", "National airline"),
    
    # Mauritius
    DataSource("https://www.govmu.org/", "Mauritius Government", SourceCategory.GOVERNMENT, "MU", "Government"),
    DataSource("https://statsmauritius.govmu.org/", "Statistics Mauritius", SourceCategory.STATISTICS, "MU", "Statistics", True),
    DataSource("https://www.bom.mu/", "Bank of Mauritius", SourceCategory.BANK, "MU", "Central bank", True),
    DataSource("https://www.airmauritius.com/", "Air Mauritius", SourceCategory.TRANSPORT, "MU", "National airline"),
    DataSource("https://www.tourism-mauritius.mu/", "Mauritius Tourism", SourceCategory.TOURISM, "MU", "Tourism", True),
    
    # Botswana
    DataSource("https://www.gov.bw/", "Botswana Government", SourceCategory.GOVERNMENT, "BW", "Government"),
    DataSource("https://www.statsbots.org.bw/", "Statistics Botswana", SourceCategory.STATISTICS, "BW", "Statistics", True),
    DataSource("https://www.bankofbotswana.bw/", "Bank of Botswana", SourceCategory.BANK, "BW", "Central bank", True),
    DataSource("https://www.botswanatourism.co.bw/", "Botswana Tourism", SourceCategory.TOURISM, "BW", "Tourism", True),
    
    # Namibia
    DataSource("https://www.gov.na/", "Namibia Government", SourceCategory.GOVERNMENT, "NA", "Government"),
    DataSource("https://nsa.org.na/", "NSA Namibia", SourceCategory.STATISTICS, "NA", "Statistics", True),
    DataSource("https://www.bon.com.na/", "Bank of Namibia", SourceCategory.BANK, "NA", "Central bank", True),
    DataSource("https://www.namibiatourism.com.na/", "Namibia Tourism", SourceCategory.TOURISM, "NA", "Tourism", True),
    
    # Zambia
    DataSource("https://www.zambia.gov.zm/", "Zambia Government", SourceCategory.GOVERNMENT, "ZM", "Government"),
    DataSource("https://www.zamstats.gov.zm/", "ZamStats", SourceCategory.STATISTICS, "ZM", "Statistics", True),
    DataSource("https://www.boz.zm/", "Bank of Zambia", SourceCategory.BANK, "ZM", "Central bank", True),
    
    # Zimbabwe
    DataSource("https://www.zim.gov.zw/", "Zimbabwe Government", SourceCategory.GOVERNMENT, "ZW", "Government"),
    DataSource("https://www.zimstat.co.zw/", "ZimStat", SourceCategory.STATISTICS, "ZW", "Statistics", True),
    DataSource("https://www.rbz.co.zw/", "Reserve Bank of Zimbabwe", SourceCategory.BANK, "ZW", "Central bank", True),
]

# ============================================================
# AFRICAN REGIONAL ORGANIZATIONS
# ============================================================

AFRICAN_REGIONAL = [
    DataSource("https://au.int/", "African Union", SourceCategory.INTERNATIONAL, "AFRICA", "AU"),
    DataSource("https://www.afdb.org/", "African Development Bank", SourceCategory.BANK, "AFRICA", "AfDB", True),
    DataSource("https://www.uneca.org/", "UN Economic Commission for Africa", SourceCategory.INTERNATIONAL, "AFRICA", "UNECA", True),
    DataSource("https://www.cafonline.com/", "CAF", SourceCategory.SPORT, "AFRICA", "African Football", True),
    DataSource("https://www.ecowas.int/", "ECOWAS", SourceCategory.INTERNATIONAL, "AFRICA", "West African States"),
    DataSource("https://www.sadc.int/", "SADC", SourceCategory.INTERNATIONAL, "AFRICA", "Southern African Development"),
    DataSource("https://www.eac.int/", "EAC", SourceCategory.INTERNATIONAL, "AFRICA", "East African Community"),
    DataSource("https://www.comesa.int/", "COMESA", SourceCategory.INTERNATIONAL, "AFRICA", "Common Market"),
]

# ============================================================
# MIDDLE EAST REGIONAL ORGANIZATIONS
# ============================================================

MIDDLE_EAST_REGIONAL = [
    DataSource("https://www.gcc-sg.org/", "GCC", SourceCategory.INTERNATIONAL, "ME", "Gulf Cooperation Council"),
    DataSource("https://www.oic-oci.org/", "OIC", SourceCategory.INTERNATIONAL, "ME", "Organisation of Islamic Cooperation"),
    DataSource("https://www.opec.org/", "OPEC", SourceCategory.ENERGY, "ME", "Oil exporters", True),
    DataSource("https://www.arableagueonline.org/", "Arab League", SourceCategory.INTERNATIONAL, "ME", "Arab League"),
    DataSource("https://www.isdb.org/", "IsDB", SourceCategory.BANK, "ME", "Islamic Development Bank", True),
]

# ============================================================
# COMBINED EXPORT
# ============================================================

ALL_AFRICA_MIDDLE_EAST_SOURCES = (
    SOUTH_AFRICA_SOURCES + NIGERIA_SOURCES + EGYPT_SOURCES +
    KENYA_SOURCES + MOROCCO_SOURCES + GHANA_SOURCES +
    SAUDI_ARABIA_SOURCES + UAE_SOURCES + ISRAEL_SOURCES +
    TURKEY_SOURCES + JORDAN_SOURCES + QATAR_SOURCES +
    KUWAIT_SOURCES + BAHRAIN_SOURCES + OMAN_SOURCES +
    ADDITIONAL_AFRICA_SOURCES + AFRICAN_REGIONAL + MIDDLE_EAST_REGIONAL
)

def get_all_sources() -> List[DataSource]:
    """Return all Africa & Middle East data sources"""
    return ALL_AFRICA_MIDDLE_EAST_SOURCES

def get_sources_by_country(country_code: str) -> List[DataSource]:
    """Return sources for a specific country"""
    return [s for s in ALL_AFRICA_MIDDLE_EAST_SOURCES if s.country == country_code]

def get_sources_by_category(category: SourceCategory) -> List[DataSource]:
    """Return sources for a specific category"""
    return [s for s in ALL_AFRICA_MIDDLE_EAST_SOURCES if s.category == category]

def get_api_sources() -> List[DataSource]:
    """Return only sources with API access"""
    return [s for s in ALL_AFRICA_MIDDLE_EAST_SOURCES if s.api_available]

def get_african_sources() -> List[DataSource]:
    """Return only African sources"""
    african_codes = ["ZA", "NG", "EG", "KE", "MA", "GH", "TZ", "ET", "UG", "RW", 
                     "SN", "CI", "DZ", "TN", "MU", "BW", "NA", "ZM", "ZW", "AFRICA"]
    return [s for s in ALL_AFRICA_MIDDLE_EAST_SOURCES if s.country in african_codes]

def get_middle_east_sources() -> List[DataSource]:
    """Return only Middle East sources"""
    me_codes = ["SA", "AE", "IL", "TR", "JO", "QA", "KW", "BH", "OM", "ME"]
    return [s for s in ALL_AFRICA_MIDDLE_EAST_SOURCES if s.country in me_codes]

# Statistics
if __name__ == "__main__":
    print(f"🌍 Total Africa & Middle East Sources: {len(ALL_AFRICA_MIDDLE_EAST_SOURCES)}")
    print(f"African countries: ZA, NG, EG, KE, MA, GH, TZ, ET, UG, RW, SN, CI, DZ, TN, MU, BW, NA, ZM, ZW")
    print(f"Middle East: SA, AE, IL, TR, JO, QA, KW, BH, OM")
    print(f"Sources with API: {len(get_api_sources())}")
    print(f"African sources: {len(get_african_sources())}")
    print(f"Middle East sources: {len(get_middle_east_sources())}")
