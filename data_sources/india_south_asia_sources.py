# -*- coding: utf-8 -*-
"""
🇮🇳 INDIA & SOUTH ASIA - COMPLETE DATA SOURCES
=================================================
800+ Free Open Data Sources from India, Pakistan, Bangladesh, Sri Lanka, Nepal, Bhutan

Categories:
- Government & Statistics
- Universities & Research (IITs, IIMs, IISc, etc.)
- Hospitals & Healthcare
- Banks & Financial (RBI, SEBI, etc.)
- Factories & Industrial
- News & Media
- Culture & Museums
- Rating Agencies
- Research Centers
"""

from dataclasses import dataclass
from typing import List, Dict, Any
from enum import Enum

class SourceCategory(Enum):
    GOVERNMENT = "government"
    UNIVERSITY = "university"
    HOSPITAL = "hospital"
    BANK = "bank"
    FACTORY = "factory"
    NEWS = "news"
    CULTURE = "culture"
    RATING = "rating"
    RESEARCH = "research"
    STATISTICS = "statistics"
    ENVIRONMENTAL = "environmental"
    TRANSPORT = "transport"
    ENERGY = "energy"
    TELECOM = "telecom"
    AGRICULTURE = "agriculture"
    SPORT = "sport"
    HOBBY = "hobby"
    ENTERTAINMENT = "entertainment"
    TOURISM = "tourism"
    EVENTS = "events"
    LIFESTYLE = "lifestyle"

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
# 🇮🇳 INDIA - REPUBLIC OF INDIA
# ============================================================

INDIA_GOVERNMENT = [
    DataSource("https://data.gov.in/", "Data.gov.in", SourceCategory.GOVERNMENT, "IN", "Open data portal", True),
    DataSource("https://www.india.gov.in/", "National Portal of India", SourceCategory.GOVERNMENT, "IN", "Government portal"),
    DataSource("https://mospi.gov.in/", "Ministry of Statistics India", SourceCategory.STATISTICS, "IN", "Statistics", True),
    DataSource("https://www.niti.gov.in/", "NITI Aayog", SourceCategory.GOVERNMENT, "IN", "Policy think tank"),
    DataSource("https://www.mha.gov.in/", "Ministry of Home Affairs", SourceCategory.GOVERNMENT, "IN", "Home ministry"),
    DataSource("https://www.mea.gov.in/", "Ministry of External Affairs", SourceCategory.GOVERNMENT, "IN", "Foreign affairs"),
    DataSource("https://www.finmin.nic.in/", "Ministry of Finance India", SourceCategory.GOVERNMENT, "IN", "Financial data"),
    DataSource("https://www.education.gov.in/", "Ministry of Education India", SourceCategory.GOVERNMENT, "IN", "Education data"),
    DataSource("https://www.mohfw.gov.in/", "Ministry of Health Family Welfare", SourceCategory.GOVERNMENT, "IN", "Health data"),
    DataSource("https://www.commerce.gov.in/", "Ministry of Commerce Industry", SourceCategory.GOVERNMENT, "IN", "Trade data"),
    DataSource("https://www.agricoop.nic.in/", "Ministry of Agriculture India", SourceCategory.AGRICULTURE, "IN", "Agriculture data"),
    DataSource("https://www.moef.gov.in/", "Ministry of Environment Forests", SourceCategory.ENVIRONMENTAL, "IN", "Environmental data"),
    DataSource("https://www.morth.nic.in/", "Ministry of Road Transport", SourceCategory.TRANSPORT, "IN", "Transport data"),
    DataSource("https://www.pib.gov.in/", "Press Information Bureau", SourceCategory.NEWS, "IN", "Government news"),
    DataSource("https://www.meity.gov.in/", "Ministry of Electronics IT", SourceCategory.GOVERNMENT, "IN", "IT policy"),
    DataSource("https://www.dst.gov.in/", "Dept of Science Technology", SourceCategory.RESEARCH, "IN", "Science data"),
    DataSource("https://www.dbtindia.gov.in/", "Dept of Biotechnology", SourceCategory.RESEARCH, "IN", "Biotech data"),
    DataSource("https://www.isro.gov.in/", "ISRO", SourceCategory.RESEARCH, "IN", "Space data", True),
    DataSource("https://www.drdo.gov.in/", "DRDO", SourceCategory.RESEARCH, "IN", "Defense research"),
    DataSource("https://www.imd.gov.in/", "India Meteorological Dept", SourceCategory.ENVIRONMENTAL, "IN", "Weather data", True),
    DataSource("https://censusindia.gov.in/", "Census of India", SourceCategory.STATISTICS, "IN", "Population data", True),
    DataSource("https://www.cbic.gov.in/", "Central Board Indirect Taxes", SourceCategory.GOVERNMENT, "IN", "Tax data"),
    DataSource("https://www.incometax.gov.in/", "Income Tax India", SourceCategory.GOVERNMENT, "IN", "Tax data"),
    DataSource("https://dgft.gov.in/", "Directorate General Foreign Trade", SourceCategory.GOVERNMENT, "IN", "Trade data", True),
    DataSource("https://www.trai.gov.in/", "TRAI", SourceCategory.TELECOM, "IN", "Telecom regulator", True),
    DataSource("https://www.cea.nic.in/", "Central Electricity Authority", SourceCategory.ENERGY, "IN", "Power data", True),
    DataSource("https://ppac.gov.in/", "Petroleum Planning Analysis Cell", SourceCategory.ENERGY, "IN", "Oil gas data", True),
    DataSource("https://labour.gov.in/", "Ministry of Labour India", SourceCategory.GOVERNMENT, "IN", "Labour data"),
    DataSource("https://www.msme.gov.in/", "Ministry of MSME", SourceCategory.GOVERNMENT, "IN", "SME data"),
    DataSource("https://www.indianrailways.gov.in/", "Indian Railways", SourceCategory.TRANSPORT, "IN", "Railway data", True),
    
    # State Open Data Portals
    DataSource("https://opendata.maharashtra.gov.in/", "Maharashtra Open Data", SourceCategory.GOVERNMENT, "IN", "State data", True),
    DataSource("https://data.karnataka.gov.in/", "Karnataka Open Data", SourceCategory.GOVERNMENT, "IN", "State data", True),
    DataSource("https://data.tamil.gov.in/", "Tamil Nadu Data", SourceCategory.GOVERNMENT, "IN", "State data", True),
    DataSource("https://data.kerala.gov.in/", "Kerala Open Data", SourceCategory.GOVERNMENT, "IN", "State data", True),
    DataSource("https://opendata.telangana.gov.in/", "Telangana Open Data", SourceCategory.GOVERNMENT, "IN", "State data", True),
    DataSource("https://data.rajasthan.gov.in/", "Rajasthan Data", SourceCategory.GOVERNMENT, "IN", "State data", True),
    DataSource("https://data.gujaratindia.gov.in/", "Gujarat Open Data", SourceCategory.GOVERNMENT, "IN", "State data", True),
    DataSource("https://www.wbgov.in/", "West Bengal Government", SourceCategory.GOVERNMENT, "IN", "State portal"),
    DataSource("https://up.gov.in/", "Uttar Pradesh Government", SourceCategory.GOVERNMENT, "IN", "State portal"),
    DataSource("https://www.delhi.gov.in/", "Delhi Government", SourceCategory.GOVERNMENT, "IN", "Capital territory"),
]

INDIA_UNIVERSITIES_IIT = [
    DataSource("https://www.iitb.ac.in/", "IIT Bombay", SourceCategory.UNIVERSITY, "IN", "Top IIT"),
    DataSource("https://www.iitd.ac.in/", "IIT Delhi", SourceCategory.UNIVERSITY, "IN", "Top IIT"),
    DataSource("https://www.iitm.ac.in/", "IIT Madras", SourceCategory.UNIVERSITY, "IN", "Top IIT"),
    DataSource("https://www.iitk.ac.in/", "IIT Kanpur", SourceCategory.UNIVERSITY, "IN", "Top IIT"),
    DataSource("https://www.iitkgp.ac.in/", "IIT Kharagpur", SourceCategory.UNIVERSITY, "IN", "First IIT"),
    DataSource("https://www.iitr.ac.in/", "IIT Roorkee", SourceCategory.UNIVERSITY, "IN", "Historic IIT"),
    DataSource("https://www.iitg.ac.in/", "IIT Guwahati", SourceCategory.UNIVERSITY, "IN", "Northeast IIT"),
    DataSource("https://www.iith.ac.in/", "IIT Hyderabad", SourceCategory.UNIVERSITY, "IN", "New IIT"),
    DataSource("https://www.iitbhu.ac.in/", "IIT BHU Varanasi", SourceCategory.UNIVERSITY, "IN", "Historic"),
    DataSource("https://www.iiti.ac.in/", "IIT Indore", SourceCategory.UNIVERSITY, "IN", "New IIT"),
    DataSource("https://www.iitgoa.ac.in/", "IIT Goa", SourceCategory.UNIVERSITY, "IN", "New IIT"),
    DataSource("https://www.iitbbs.ac.in/", "IIT Bhubaneswar", SourceCategory.UNIVERSITY, "IN", "New IIT"),
    DataSource("https://www.iitj.ac.in/", "IIT Jodhpur", SourceCategory.UNIVERSITY, "IN", "New IIT"),
    DataSource("https://www.iitp.ac.in/", "IIT Patna", SourceCategory.UNIVERSITY, "IN", "New IIT"),
    DataSource("https://www.iitgn.ac.in/", "IIT Gandhinagar", SourceCategory.UNIVERSITY, "IN", "New IIT"),
    DataSource("https://www.iitrpr.ac.in/", "IIT Ropar", SourceCategory.UNIVERSITY, "IN", "New IIT"),
    DataSource("https://www.iitmandi.ac.in/", "IIT Mandi", SourceCategory.UNIVERSITY, "IN", "Himalayan IIT"),
    DataSource("https://www.iitpkd.ac.in/", "IIT Palakkad", SourceCategory.UNIVERSITY, "IN", "Kerala IIT"),
    DataSource("https://www.iitdh.ac.in/", "IIT Dharwad", SourceCategory.UNIVERSITY, "IN", "Karnataka IIT"),
    DataSource("https://www.iitbhilai.ac.in/", "IIT Bhilai", SourceCategory.UNIVERSITY, "IN", "Chhattisgarh IIT"),
    DataSource("https://www.iitjammu.ac.in/", "IIT Jammu", SourceCategory.UNIVERSITY, "IN", "J&K IIT"),
    DataSource("https://www.iittirupa.ac.in/", "IIT Tirupati", SourceCategory.UNIVERSITY, "IN", "AP IIT"),
]

INDIA_UNIVERSITIES_IIM = [
    DataSource("https://www.iima.ac.in/", "IIM Ahmedabad", SourceCategory.UNIVERSITY, "IN", "Top B-school"),
    DataSource("https://www.iimb.ac.in/", "IIM Bangalore", SourceCategory.UNIVERSITY, "IN", "Top B-school"),
    DataSource("https://www.iimc.ac.in/", "IIM Calcutta", SourceCategory.UNIVERSITY, "IN", "Historic IIM"),
    DataSource("https://www.iimk.ac.in/", "IIM Kozhikode", SourceCategory.UNIVERSITY, "IN", "Kerala IIM"),
    DataSource("https://www.iiml.ac.in/", "IIM Lucknow", SourceCategory.UNIVERSITY, "IN", "North IIM"),
    DataSource("https://www.iimi.ac.in/", "IIM Indore", SourceCategory.UNIVERSITY, "IN", "Central IIM"),
    DataSource("https://www.iimshillong.ac.in/", "IIM Shillong", SourceCategory.UNIVERSITY, "IN", "Northeast IIM"),
    DataSource("https://www.iimrohtak.ac.in/", "IIM Rohtak", SourceCategory.UNIVERSITY, "IN", "Haryana IIM"),
    DataSource("https://www.iimranchi.ac.in/", "IIM Ranchi", SourceCategory.UNIVERSITY, "IN", "Jharkhand IIM"),
    DataSource("https://www.iimraipur.ac.in/", "IIM Raipur", SourceCategory.UNIVERSITY, "IN", "Chhattisgarh IIM"),
    DataSource("https://www.iimkashipur.ac.in/", "IIM Kashipur", SourceCategory.UNIVERSITY, "IN", "Uttarakhand IIM"),
    DataSource("https://www.iimtrichy.ac.in/", "IIM Tiruchirappalli", SourceCategory.UNIVERSITY, "IN", "Tamil Nadu IIM"),
    DataSource("https://www.iimudaipur.ac.in/", "IIM Udaipur", SourceCategory.UNIVERSITY, "IN", "Rajasthan IIM"),
    DataSource("https://www.iimamritsar.ac.in/", "IIM Amritsar", SourceCategory.UNIVERSITY, "IN", "Punjab IIM"),
    DataSource("https://www.iimbg.ac.in/", "IIM Bodh Gaya", SourceCategory.UNIVERSITY, "IN", "Bihar IIM"),
    DataSource("https://www.iimnagpur.ac.in/", "IIM Nagpur", SourceCategory.UNIVERSITY, "IN", "Maharashtra IIM"),
    DataSource("https://www.iimv.ac.in/", "IIM Visakhapatnam", SourceCategory.UNIVERSITY, "IN", "AP IIM"),
    DataSource("https://www.iimsambalpur.ac.in/", "IIM Sambalpur", SourceCategory.UNIVERSITY, "IN", "Odisha IIM"),
    DataSource("https://www.iimj.ac.in/", "IIM Jammu", SourceCategory.UNIVERSITY, "IN", "J&K IIM"),
    DataSource("https://www.iimsindia.com/", "IIM Mumbai", SourceCategory.UNIVERSITY, "IN", "Mumbai IIM"),
]

INDIA_UNIVERSITIES_OTHER = [
    DataSource("https://www.iisc.ac.in/", "IISc Bangalore", SourceCategory.UNIVERSITY, "IN", "Top research", True),
    DataSource("https://www.jnu.ac.in/", "Jawaharlal Nehru University", SourceCategory.UNIVERSITY, "IN", "Social sciences"),
    DataSource("https://www.du.ac.in/", "University of Delhi", SourceCategory.UNIVERSITY, "IN", "Central university"),
    DataSource("https://www.bhu.ac.in/", "Banaras Hindu University", SourceCategory.UNIVERSITY, "IN", "Historic"),
    DataSource("https://www.amu.ac.in/", "Aligarh Muslim University", SourceCategory.UNIVERSITY, "IN", "Historic"),
    DataSource("https://www.hyderabad.ac.in/", "University of Hyderabad", SourceCategory.UNIVERSITY, "IN", "Central university"),
    DataSource("https://www.iiserpune.ac.in/", "IISER Pune", SourceCategory.UNIVERSITY, "IN", "Science research"),
    DataSource("https://www.iiserb.ac.in/", "IISER Bhopal", SourceCategory.UNIVERSITY, "IN", "Science research"),
    DataSource("https://www.iiserkol.ac.in/", "IISER Kolkata", SourceCategory.UNIVERSITY, "IN", "Science research"),
    DataSource("https://www.iisermohali.ac.in/", "IISER Mohali", SourceCategory.UNIVERSITY, "IN", "Science research"),
    DataSource("https://www.iisertvm.ac.in/", "IISER Thiruvananthapuram", SourceCategory.UNIVERSITY, "IN", "Science research"),
    DataSource("https://www.niser.ac.in/", "NISER Bhubaneswar", SourceCategory.UNIVERSITY, "IN", "Science research"),
    DataSource("https://www.bits-pilani.ac.in/", "BITS Pilani", SourceCategory.UNIVERSITY, "IN", "Private tech"),
    DataSource("https://www.iiitd.ac.in/", "IIIT Delhi", SourceCategory.UNIVERSITY, "IN", "IT institute"),
    DataSource("https://www.iiit.ac.in/", "IIIT Hyderabad", SourceCategory.UNIVERSITY, "IN", "IT institute"),
    DataSource("https://www.nitw.ac.in/", "NIT Warangal", SourceCategory.UNIVERSITY, "IN", "Top NIT"),
    DataSource("https://www.nitt.edu/", "NIT Trichy", SourceCategory.UNIVERSITY, "IN", "Top NIT"),
    DataSource("https://www.nitrkl.ac.in/", "NIT Rourkela", SourceCategory.UNIVERSITY, "IN", "Top NIT"),
    DataSource("https://www.nitk.ac.in/", "NIT Surathkal", SourceCategory.UNIVERSITY, "IN", "Top NIT"),
    DataSource("https://www.nits.ac.in/", "NIT Silchar", SourceCategory.UNIVERSITY, "IN", "Northeast NIT"),
    DataSource("https://www.isb.edu/", "Indian School of Business", SourceCategory.UNIVERSITY, "IN", "Business school"),
    DataSource("https://www.xlri.ac.in/", "XLRI Jamshedpur", SourceCategory.UNIVERSITY, "IN", "HR B-school"),
    DataSource("https://www.spjimr.org/", "SPJIMR Mumbai", SourceCategory.UNIVERSITY, "IN", "Business school"),
    DataSource("https://www.iift.ac.in/", "IIFT Delhi", SourceCategory.UNIVERSITY, "IN", "Trade institute"),
    DataSource("https://www.nift.ac.in/", "NIFT", SourceCategory.UNIVERSITY, "IN", "Fashion institute"),
    DataSource("https://www.nid.edu/", "NID Ahmedabad", SourceCategory.UNIVERSITY, "IN", "Design institute"),
    DataSource("https://ftii.ac.in/", "FTII Pune", SourceCategory.UNIVERSITY, "IN", "Film institute"),
    DataSource("https://www.tiss.edu/", "TISS Mumbai", SourceCategory.UNIVERSITY, "IN", "Social sciences"),
    DataSource("https://www.aiims.edu/", "AIIMS Delhi", SourceCategory.UNIVERSITY, "IN", "Medical institute"),
]

INDIA_HOSPITALS = [
    DataSource("https://www.aiims.edu/", "AIIMS Delhi", SourceCategory.HOSPITAL, "IN", "Premier hospital"),
    DataSource("https://aiimsjodhpur.edu.in/", "AIIMS Jodhpur", SourceCategory.HOSPITAL, "IN", "AIIMS branch"),
    DataSource("https://aiimsbhubaneswar.nic.in/", "AIIMS Bhubaneswar", SourceCategory.HOSPITAL, "IN", "AIIMS branch"),
    DataSource("https://aiimsbhopal.edu.in/", "AIIMS Bhopal", SourceCategory.HOSPITAL, "IN", "AIIMS branch"),
    DataSource("https://www.aiimspatna.org/", "AIIMS Patna", SourceCategory.HOSPITAL, "IN", "AIIMS branch"),
    DataSource("https://aiimsrishikesh.edu.in/", "AIIMS Rishikesh", SourceCategory.HOSPITAL, "IN", "AIIMS branch"),
    DataSource("https://www.aiimsraipur.edu.in/", "AIIMS Raipur", SourceCategory.HOSPITAL, "IN", "AIIMS branch"),
    DataSource("https://www.apollohospitals.com/", "Apollo Hospitals", SourceCategory.HOSPITAL, "IN", "Private chain"),
    DataSource("https://www.fortishealthcare.com/", "Fortis Healthcare", SourceCategory.HOSPITAL, "IN", "Private chain"),
    DataSource("https://www.maxhealthcare.in/", "Max Healthcare", SourceCategory.HOSPITAL, "IN", "Private chain"),
    DataSource("https://www.medanta.org/", "Medanta Gurgaon", SourceCategory.HOSPITAL, "IN", "Super specialty"),
    DataSource("https://www.kokilabenhospital.com/", "Kokilaben Mumbai", SourceCategory.HOSPITAL, "IN", "Super specialty"),
    DataSource("https://www.tatamemorialcentre.com/", "Tata Memorial Hospital", SourceCategory.HOSPITAL, "IN", "Cancer center"),
    DataSource("https://www.cmcvellore.ac.in/", "CMC Vellore", SourceCategory.HOSPITAL, "IN", "Teaching hospital"),
    DataSource("https://www.narayanahealth.org/", "Narayana Health", SourceCategory.HOSPITAL, "IN", "Heart specialty"),
    DataSource("https://www.manipalhospitals.com/", "Manipal Hospitals", SourceCategory.HOSPITAL, "IN", "Private chain"),
    DataSource("https://www.nfrht.gov.in/", "NIMHANS Bangalore", SourceCategory.HOSPITAL, "IN", "Mental health"),
    DataSource("https://www.sancheti.com/", "Sancheti Hospital Pune", SourceCategory.HOSPITAL, "IN", "Orthopedic"),
    DataSource("https://www.sreechitrahealth.org/", "Sree Chitra Trivandrum", SourceCategory.HOSPITAL, "IN", "Heart specialty"),
    DataSource("https://www.lilavatihosp.com/", "Lilavati Hospital Mumbai", SourceCategory.HOSPITAL, "IN", "Multi specialty"),
    DataSource("https://www.hindujahospital.com/", "Hinduja Hospital Mumbai", SourceCategory.HOSPITAL, "IN", "Multi specialty"),
    DataSource("https://www.cloudnine.care/", "Cloudnine Hospitals", SourceCategory.HOSPITAL, "IN", "Maternity"),
    DataSource("https://www.pgimer.edu.in/", "PGIMER Chandigarh", SourceCategory.HOSPITAL, "IN", "Medical research"),
    DataSource("https://www.jipmer.edu.in/", "JIPMER Puducherry", SourceCategory.HOSPITAL, "IN", "Medical institute"),
    DataSource("https://www.sgpgi.ac.in/", "SGPGI Lucknow", SourceCategory.HOSPITAL, "IN", "Graduate medical"),
    DataSource("https://www.kemhospital.org/", "KEM Hospital Mumbai", SourceCategory.HOSPITAL, "IN", "Government hospital"),
]

INDIA_BANKS = [
    DataSource("https://www.rbi.org.in/", "Reserve Bank of India", SourceCategory.BANK, "IN", "Central Bank", True),
    DataSource("https://www.sbi.co.in/", "State Bank of India", SourceCategory.BANK, "IN", "Largest bank", True),
    DataSource("https://www.hdfcbank.com/", "HDFC Bank", SourceCategory.BANK, "IN", "Private bank"),
    DataSource("https://www.icicibank.com/", "ICICI Bank", SourceCategory.BANK, "IN", "Private bank", True),
    DataSource("https://www.axisbank.com/", "Axis Bank", SourceCategory.BANK, "IN", "Private bank"),
    DataSource("https://www.kotak.com/", "Kotak Mahindra Bank", SourceCategory.BANK, "IN", "Private bank"),
    DataSource("https://www.pnbindia.in/", "Punjab National Bank", SourceCategory.BANK, "IN", "PSU bank"),
    DataSource("https://www.bankofindia.co.in/", "Bank of India", SourceCategory.BANK, "IN", "PSU bank"),
    DataSource("https://www.bankofbaroda.in/", "Bank of Baroda", SourceCategory.BANK, "IN", "PSU bank"),
    DataSource("https://www.canarabank.com/", "Canara Bank", SourceCategory.BANK, "IN", "PSU bank"),
    DataSource("https://www.unionbankofindia.co.in/", "Union Bank of India", SourceCategory.BANK, "IN", "PSU bank"),
    DataSource("https://www.indianbank.in/", "Indian Bank", SourceCategory.BANK, "IN", "PSU bank"),
    DataSource("https://www.iobnet.co.in/", "Indian Overseas Bank", SourceCategory.BANK, "IN", "PSU bank"),
    DataSource("https://www.centralbankofindia.co.in/", "Central Bank of India", SourceCategory.BANK, "IN", "PSU bank"),
    DataSource("https://www.idbibank.in/", "IDBI Bank", SourceCategory.BANK, "IN", "Development bank"),
    DataSource("https://www.yesbank.in/", "Yes Bank", SourceCategory.BANK, "IN", "Private bank"),
    DataSource("https://www.indusind.com/", "IndusInd Bank", SourceCategory.BANK, "IN", "Private bank"),
    DataSource("https://www.federalbank.co.in/", "Federal Bank", SourceCategory.BANK, "IN", "Private bank"),
    DataSource("https://www.bandhanbank.com/", "Bandhan Bank", SourceCategory.BANK, "IN", "Microfinance bank"),
    DataSource("https://www.nabard.org/", "NABARD", SourceCategory.BANK, "IN", "Agricultural bank", True),
    DataSource("https://www.sidbi.in/", "SIDBI", SourceCategory.BANK, "IN", "SME bank"),
    DataSource("https://www.eximbankfindia.in/", "Exim Bank India", SourceCategory.BANK, "IN", "Export bank"),
    DataSource("https://www.sebi.gov.in/", "SEBI", SourceCategory.RATING, "IN", "Securities regulator", True),
    DataSource("https://www.nseindia.com/", "NSE India", SourceCategory.BANK, "IN", "Stock exchange", True),
    DataSource("https://www.bseindia.com/", "BSE India", SourceCategory.BANK, "IN", "Stock exchange", True),
    DataSource("https://www.irdai.gov.in/", "IRDAI", SourceCategory.RATING, "IN", "Insurance regulator"),
    DataSource("https://www.pfrda.org.in/", "PFRDA", SourceCategory.RATING, "IN", "Pension regulator"),
    DataSource("https://www.icra.in/", "ICRA", SourceCategory.RATING, "IN", "Credit rating"),
    DataSource("https://www.crisil.com/", "CRISIL", SourceCategory.RATING, "IN", "Credit rating"),
    DataSource("https://www.careratings.com/", "CARE Ratings", SourceCategory.RATING, "IN", "Credit rating"),
    DataSource("https://www.iira.in/", "India Ratings Fitch", SourceCategory.RATING, "IN", "Credit rating"),
]

INDIA_FACTORIES_INDUSTRIAL = [
    # Oil & Gas
    DataSource("https://www.iocl.com/", "Indian Oil Corporation", SourceCategory.FACTORY, "IN", "Oil refining"),
    DataSource("https://www.bharatpetroleum.in/", "BPCL", SourceCategory.FACTORY, "IN", "Oil refining"),
    DataSource("https://www.hindustanpetroleum.com/", "HPCL", SourceCategory.FACTORY, "IN", "Oil refining"),
    DataSource("https://www.ongcindia.com/", "ONGC", SourceCategory.ENERGY, "IN", "Oil & Gas exploration"),
    DataSource("https://www.gailonline.com/", "GAIL", SourceCategory.ENERGY, "IN", "Natural gas"),
    DataSource("https://www.oil-india.com/", "Oil India Limited", SourceCategory.ENERGY, "IN", "Exploration"),
    DataSource("https://www.reliancepetroleum.com/", "Reliance Petroleum", SourceCategory.ENERGY, "IN", "Private oil"),
    
    # Power & Energy
    DataSource("https://www.ntpc.co.in/", "NTPC", SourceCategory.ENERGY, "IN", "Power generation"),
    DataSource("https://www.powergridindia.com/", "Power Grid Corporation", SourceCategory.ENERGY, "IN", "Power transmission"),
    DataSource("https://www.nhpcindia.com/", "NHPC", SourceCategory.ENERGY, "IN", "Hydropower"),
    DataSource("https://www.npcil.nic.in/", "NPCIL", SourceCategory.ENERGY, "IN", "Nuclear power"),
    DataSource("https://www.seci.co.in/", "SECI", SourceCategory.ENERGY, "IN", "Solar energy"),
    DataSource("https://www.adanigreen.com/", "Adani Green Energy", SourceCategory.ENERGY, "IN", "Renewable"),
    DataSource("https://www.tatapowerses.com/", "Tata Power Solar", SourceCategory.ENERGY, "IN", "Solar"),
    
    # Steel & Metals
    DataSource("https://www.sail.co.in/", "SAIL", SourceCategory.FACTORY, "IN", "Steel PSU"),
    DataSource("https://www.tatasteel.com/", "Tata Steel", SourceCategory.FACTORY, "IN", "Private steel"),
    DataSource("https://www.jsw.in/", "JSW Steel", SourceCategory.FACTORY, "IN", "Private steel"),
    DataSource("https://www.jindalsteelpower.com/", "Jindal Steel Power", SourceCategory.FACTORY, "IN", "Steel"),
    DataSource("https://www.hindalco.com/", "Hindalco", SourceCategory.FACTORY, "IN", "Aluminum"),
    DataSource("https://www.vedanta.com/", "Vedanta", SourceCategory.FACTORY, "IN", "Mining metals"),
    DataSource("https://www.nmdc.co.in/", "NMDC", SourceCategory.FACTORY, "IN", "Iron ore mining"),
    DataSource("https://www.coalindia.in/", "Coal India", SourceCategory.FACTORY, "IN", "Coal mining"),
    
    # Automotive
    DataSource("https://www.tatamotors.com/", "Tata Motors", SourceCategory.FACTORY, "IN", "Automotive"),
    DataSource("https://www.mahindraauto.com/", "Mahindra Automotive", SourceCategory.FACTORY, "IN", "Automotive"),
    DataSource("https://www.marutisuzuki.com/", "Maruti Suzuki", SourceCategory.FACTORY, "IN", "Largest carmaker"),
    DataSource("https://www.hyundai.co.in/", "Hyundai India", SourceCategory.FACTORY, "IN", "Korean auto"),
    DataSource("https://www.honda.co.in/", "Honda India", SourceCategory.FACTORY, "IN", "Japanese auto"),
    DataSource("https://www.hero.com/", "Hero MotoCorp", SourceCategory.FACTORY, "IN", "Two-wheelers"),
    DataSource("https://www.bajaj.com/", "Bajaj Auto", SourceCategory.FACTORY, "IN", "Two-wheelers"),
    DataSource("https://www.tvsmotor.com/", "TVS Motor", SourceCategory.FACTORY, "IN", "Two-wheelers"),
    DataSource("https://www.ashokleyland.com/", "Ashok Leyland", SourceCategory.FACTORY, "IN", "Commercial vehicles"),
    DataSource("https://www.elorauto.com/", "Eicher Motors", SourceCategory.FACTORY, "IN", "Royal Enfield"),
    
    # IT & Electronics
    DataSource("https://www.tcs.com/", "TCS", SourceCategory.FACTORY, "IN", "IT services"),
    DataSource("https://www.infosys.com/", "Infosys", SourceCategory.FACTORY, "IN", "IT services"),
    DataSource("https://www.wipro.com/", "Wipro", SourceCategory.FACTORY, "IN", "IT services"),
    DataSource("https://www.hcltech.com/", "HCL Technologies", SourceCategory.FACTORY, "IN", "IT services"),
    DataSource("https://www.techmahindra.com/", "Tech Mahindra", SourceCategory.FACTORY, "IN", "IT services"),
    DataSource("https://www.larsentoubro.com/", "L&T Infotech", SourceCategory.FACTORY, "IN", "IT services"),
    DataSource("https://www.mphasis.com/", "Mphasis", SourceCategory.FACTORY, "IN", "IT services"),
    DataSource("https://www.mindtree.com/", "Mindtree", SourceCategory.FACTORY, "IN", "IT services"),
    
    # Pharmaceuticals
    DataSource("https://www.sunpharma.com/", "Sun Pharma", SourceCategory.FACTORY, "IN", "Largest pharma"),
    DataSource("https://www.cipla.com/", "Cipla", SourceCategory.FACTORY, "IN", "Pharmaceuticals"),
    DataSource("https://www.drreddys.com/", "Dr Reddy's", SourceCategory.FACTORY, "IN", "Pharmaceuticals"),
    DataSource("https://www.lupin.com/", "Lupin", SourceCategory.FACTORY, "IN", "Pharmaceuticals"),
    DataSource("https://www.aurobindo.com/", "Aurobindo Pharma", SourceCategory.FACTORY, "IN", "Generics"),
    DataSource("https://www.divislabs.com/", "Divi's Laboratories", SourceCategory.FACTORY, "IN", "API"),
    DataSource("https://www.biocon.com/", "Biocon", SourceCategory.FACTORY, "IN", "Biotech"),
    DataSource("https://www.zyduscadila.com/", "Zydus Cadila", SourceCategory.FACTORY, "IN", "Pharmaceuticals"),
    DataSource("https://www.glenmarkpharma.com/", "Glenmark", SourceCategory.FACTORY, "IN", "Pharmaceuticals"),
    DataSource("https://www.torrrentpharma.com/", "Torrent Pharma", SourceCategory.FACTORY, "IN", "Pharmaceuticals"),
    DataSource("https://www.seruminstitute.com/", "Serum Institute India", SourceCategory.FACTORY, "IN", "Vaccines"),
    
    # Conglomerates
    DataSource("https://www.tata.com/", "Tata Group", SourceCategory.FACTORY, "IN", "Conglomerate"),
    DataSource("https://www.ril.com/", "Reliance Industries", SourceCategory.FACTORY, "IN", "Largest private"),
    DataSource("https://www.adani.com/", "Adani Group", SourceCategory.FACTORY, "IN", "Infrastructure"),
    DataSource("https://www.mahindra.com/", "Mahindra Group", SourceCategory.FACTORY, "IN", "Diversified"),
    DataSource("https://www.birla.com/", "Aditya Birla Group", SourceCategory.FACTORY, "IN", "Diversified"),
    DataSource("https://www.godrejindustries.com/", "Godrej Group", SourceCategory.FACTORY, "IN", "Diversified"),
    DataSource("https://www.larsentoubro.com/", "L&T", SourceCategory.FACTORY, "IN", "Engineering"),
    DataSource("https://www.bhartienterprises.com/", "Bharti Group", SourceCategory.FACTORY, "IN", "Telecom"),
    DataSource("https://www.rpggroup.in/", "RPG Group", SourceCategory.FACTORY, "IN", "Diversified"),
    DataSource("https://www.esselgroup.com/", "Essel Group", SourceCategory.FACTORY, "IN", "Media diversified"),
    
    # Telecom
    DataSource("https://www.airtel.in/", "Bharti Airtel", SourceCategory.TELECOM, "IN", "Telecom"),
    DataSource("https://www.jio.com/", "Reliance Jio", SourceCategory.TELECOM, "IN", "Telecom"),
    DataSource("https://www.myvi.in/", "Vodafone Idea", SourceCategory.TELECOM, "IN", "Telecom"),
    DataSource("https://www.bsnl.co.in/", "BSNL", SourceCategory.TELECOM, "IN", "State telecom"),
    DataSource("https://www.mtnl.net.in/", "MTNL", SourceCategory.TELECOM, "IN", "Metro telecom"),
    
    # FMCG & Consumer
    DataSource("https://www.hul.co.in/", "Hindustan Unilever", SourceCategory.FACTORY, "IN", "FMCG"),
    DataSource("https://www.itcportal.com/", "ITC Limited", SourceCategory.FACTORY, "IN", "Conglomerate FMCG"),
    DataSource("https://www.nestle.in/", "Nestle India", SourceCategory.FACTORY, "IN", "Food"),
    DataSource("https://www.britannia.co.in/", "Britannia", SourceCategory.FACTORY, "IN", "Food"),
    DataSource("https://www.dabur.com/", "Dabur", SourceCategory.FACTORY, "IN", "Ayurveda FMCG"),
    DataSource("https://www.marico.com/", "Marico", SourceCategory.FACTORY, "IN", "FMCG"),
    DataSource("https://www.patanjaliayurved.net/", "Patanjali", SourceCategory.FACTORY, "IN", "Ayurveda"),
    DataSource("https://www.emamiltd.in/", "Emami", SourceCategory.FACTORY, "IN", "FMCG"),
]

INDIA_NEWS_MEDIA = [
    DataSource("https://www.thehindu.com/", "The Hindu", SourceCategory.NEWS, "IN", "National newspaper"),
    DataSource("https://timesofindia.indiatimes.com/", "Times of India", SourceCategory.NEWS, "IN", "Largest English"),
    DataSource("https://www.hindustantimes.com/", "Hindustan Times", SourceCategory.NEWS, "IN", "National newspaper"),
    DataSource("https://indianexpress.com/", "Indian Express", SourceCategory.NEWS, "IN", "National newspaper"),
    DataSource("https://www.ndtv.com/", "NDTV", SourceCategory.NEWS, "IN", "News channel"),
    DataSource("https://economictimes.indiatimes.com/", "Economic Times", SourceCategory.NEWS, "IN", "Business news"),
    DataSource("https://www.livemint.com/", "Livemint", SourceCategory.NEWS, "IN", "Business news"),
    DataSource("https://www.businessstandard.com/", "Business Standard", SourceCategory.NEWS, "IN", "Business news"),
    DataSource("https://www.moneycontrol.com/", "Moneycontrol", SourceCategory.NEWS, "IN", "Financial news"),
    DataSource("https://www.financialexpress.com/", "Financial Express", SourceCategory.NEWS, "IN", "Business news"),
    DataSource("https://www.deccanherald.com/", "Deccan Herald", SourceCategory.NEWS, "IN", "Regional newspaper"),
    DataSource("https://www.telegraphindia.com/", "Telegraph India", SourceCategory.NEWS, "IN", "Kolkata paper"),
    DataSource("https://www.thestatesman.com/", "Statesman", SourceCategory.NEWS, "IN", "Historic paper"),
    DataSource("https://www.tribuneindia.com/", "Tribune", SourceCategory.NEWS, "IN", "Punjab paper"),
    DataSource("https://www.thequint.com/", "The Quint", SourceCategory.NEWS, "IN", "Digital news"),
    DataSource("https://scroll.in/", "Scroll.in", SourceCategory.NEWS, "IN", "Digital news"),
    DataSource("https://www.news18.com/", "News18", SourceCategory.NEWS, "IN", "News network"),
    DataSource("https://www.abplive.com/", "ABP News", SourceCategory.NEWS, "IN", "News network"),
    DataSource("https://www.aajtak.in/", "Aaj Tak", SourceCategory.NEWS, "IN", "Hindi news"),
    DataSource("https://www.india.com/", "India.com", SourceCategory.NEWS, "IN", "News portal"),
    DataSource("https://www.reuters.com/places/india/", "Reuters India", SourceCategory.NEWS, "IN", "International"),
    DataSource("https://www.pti.in/", "PTI", SourceCategory.NEWS, "IN", "News agency"),
    DataSource("https://www.ani.in/", "ANI", SourceCategory.NEWS, "IN", "News agency"),
    DataSource("https://www.ians.in/", "IANS", SourceCategory.NEWS, "IN", "News agency"),
    DataSource("https://www.doordarshan.gov.in/", "Doordarshan", SourceCategory.NEWS, "IN", "State broadcaster"),
    DataSource("https://newsonair.com/", "All India Radio", SourceCategory.NEWS, "IN", "State radio"),
]

INDIA_CULTURE = [
    DataSource("https://nationalmuseumindia.gov.in/", "National Museum India", SourceCategory.CULTURE, "IN", "National museum"),
    DataSource("https://www.ngmaindia.gov.in/", "National Gallery Modern Art", SourceCategory.CULTURE, "IN", "Art museum"),
    DataSource("https://www.nationalgallery.org.in/", "NGMA Mumbai", SourceCategory.CULTURE, "IN", "Art museum"),
    DataSource("https://www.indianmuseumkolkata.org/", "Indian Museum Kolkata", SourceCategory.CULTURE, "IN", "Oldest museum"),
    DataSource("https://www.salarjungmuseum.in/", "Salar Jung Museum", SourceCategory.CULTURE, "IN", "Art museum"),
    DataSource("https://www.csmvs.in/", "Chhatrapati Shivaji Museum Mumbai", SourceCategory.CULTURE, "IN", "Historic museum"),
    DataSource("https://www.nationalarchives.nic.in/", "National Archives India", SourceCategory.CULTURE, "IN", "Archives", True),
    DataSource("https://www.nationallibrary.gov.in/", "National Library Kolkata", SourceCategory.CULTURE, "IN", "National library"),
    DataSource("https://www.ignca.gov.in/", "IGNCA Delhi", SourceCategory.CULTURE, "IN", "Cultural center"),
    DataSource("https://www.sangeetnatak.gov.in/", "Sangeet Natak Akademi", SourceCategory.CULTURE, "IN", "Performing arts"),
    DataSource("https://www.sahitya-akademi.gov.in/", "Sahitya Akademi", SourceCategory.CULTURE, "IN", "Literature"),
    DataSource("https://www.laikitkalaakademi.gov.in/", "Lalit Kala Akademi", SourceCategory.CULTURE, "IN", "Visual arts"),
    DataSource("https://www.nczcc.gov.in/", "Zonal Cultural Centers", SourceCategory.CULTURE, "IN", "Regional culture"),
    DataSource("https://www.indiaculture.nic.in/", "Ministry of Culture", SourceCategory.CULTURE, "IN", "Heritage"),
    DataSource("https://www.asi.nic.in/", "Archaeological Survey India", SourceCategory.CULTURE, "IN", "Archaeology", True),
]

INDIA_RESEARCH = [
    DataSource("https://www.csir.res.in/", "CSIR", SourceCategory.RESEARCH, "IN", "Science research", True),
    DataSource("https://www.dae.gov.in/", "Dept of Atomic Energy", SourceCategory.RESEARCH, "IN", "Nuclear research"),
    DataSource("https://www.barc.gov.in/", "BARC", SourceCategory.RESEARCH, "IN", "Atomic research"),
    DataSource("https://www.igcar.gov.in/", "IGCAR", SourceCategory.RESEARCH, "IN", "Fast reactor"),
    DataSource("https://www.icmr.nic.in/", "ICMR", SourceCategory.RESEARCH, "IN", "Medical research", True),
    DataSource("https://www.icar.org.in/", "ICAR", SourceCategory.RESEARCH, "IN", "Agricultural research", True),
    DataSource("https://www.icssr.org/", "ICSSR", SourceCategory.RESEARCH, "IN", "Social science"),
    DataSource("https://www.ichr.ac.in/", "ICHR", SourceCategory.RESEARCH, "IN", "Historical research"),
    DataSource("https://www.cdri.res.in/", "CDRI Lucknow", SourceCategory.RESEARCH, "IN", "Drug research"),
    DataSource("https://www.ccmb.res.in/", "CCMB Hyderabad", SourceCategory.RESEARCH, "IN", "Cell biology"),
    DataSource("https://www.ncl.res.in/", "NCL Pune", SourceCategory.RESEARCH, "IN", "Chemical research"),
    DataSource("https://www.nal.res.in/", "NAL Bangalore", SourceCategory.RESEARCH, "IN", "Aerospace"),
    DataSource("https://www.c-dac.in/", "C-DAC", SourceCategory.RESEARCH, "IN", "Computing"),
    DataSource("https://www.iicb.res.in/", "IICB Kolkata", SourceCategory.RESEARCH, "IN", "Chemical biology"),
    DataSource("https://www.nipgr.ac.in/", "NIPGR Delhi", SourceCategory.RESEARCH, "IN", "Plant genomics"),
    DataSource("https://www.tifr.res.in/", "TIFR Mumbai", SourceCategory.RESEARCH, "IN", "Fundamental research"),
    DataSource("https://www.aries.res.in/", "ARIES Nainital", SourceCategory.RESEARCH, "IN", "Astronomy"),
    DataSource("https://www.iia.res.in/", "IIA Bangalore", SourceCategory.RESEARCH, "IN", "Astrophysics"),
    DataSource("https://www.rri.res.in/", "RRI Bangalore", SourceCategory.RESEARCH, "IN", "Raman Research"),
    DataSource("https://www.imsc.res.in/", "IMSc Chennai", SourceCategory.RESEARCH, "IN", "Mathematical sciences"),
    DataSource("https://www.hri.res.in/", "HRI Allahabad", SourceCategory.RESEARCH, "IN", "Math physics"),
    DataSource("https://www.nii.ac.in/", "NII Delhi", SourceCategory.RESEARCH, "IN", "Immunology"),
    DataSource("https://www.ncbs.res.in/", "NCBS Bangalore", SourceCategory.RESEARCH, "IN", "Biological sciences"),
    DataSource("https://www.insa.nic.in/", "INSA", SourceCategory.RESEARCH, "IN", "National academy"),
    DataSource("https://www.ias.ac.in/", "IAS Bangalore", SourceCategory.RESEARCH, "IN", "Science academy"),
    DataSource("https://www.nasi.nic.in/", "NASI Allahabad", SourceCategory.RESEARCH, "IN", "Science academy"),
]

# ============================================================
# 🇵🇰 PAKISTAN
# ============================================================

PAKISTAN_SOURCES = [
    DataSource("https://www.pakistan.gov.pk/", "Government of Pakistan", SourceCategory.GOVERNMENT, "PK", "Government portal"),
    DataSource("https://www.pbs.gov.pk/", "Pakistan Bureau of Statistics", SourceCategory.STATISTICS, "PK", "Statistics", True),
    DataSource("https://www.sbp.org.pk/", "State Bank of Pakistan", SourceCategory.BANK, "PK", "Central Bank", True),
    DataSource("https://www.finance.gov.pk/", "Ministry of Finance Pakistan", SourceCategory.GOVERNMENT, "PK", "Financial data"),
    DataSource("https://www.nhsrc.gov.pk/", "Ministry of Health Pakistan", SourceCategory.GOVERNMENT, "PK", "Health data"),
    DataSource("https://www.hec.gov.pk/", "Higher Education Commission", SourceCategory.GOVERNMENT, "PK", "Education"),
    DataSource("https://www.qau.edu.pk/", "Quaid-i-Azam University", SourceCategory.UNIVERSITY, "PK", "Top university"),
    DataSource("https://www.lums.edu.pk/", "LUMS", SourceCategory.UNIVERSITY, "PK", "Top private"),
    DataSource("https://www.nust.edu.pk/", "NUST Islamabad", SourceCategory.UNIVERSITY, "PK", "Technology"),
    DataSource("https://www.uet.edu.pk/", "UET Lahore", SourceCategory.UNIVERSITY, "PK", "Engineering"),
    DataSource("https://www.pu.edu.pk/", "University of Punjab", SourceCategory.UNIVERSITY, "PK", "Largest university"),
    DataSource("https://www.uok.edu.pk/", "University of Karachi", SourceCategory.UNIVERSITY, "PK", "Research"),
    DataSource("https://www.aku.edu/", "Aga Khan University", SourceCategory.UNIVERSITY, "PK", "Medical"),
    DataSource("https://www.giki.edu.pk/", "GIKI", SourceCategory.UNIVERSITY, "PK", "Engineering"),
    DataSource("https://www.comsats.edu.pk/", "COMSATS", SourceCategory.UNIVERSITY, "PK", "IT"),
    DataSource("https://www.fast.edu.pk/", "FAST-NU", SourceCategory.UNIVERSITY, "PK", "Computing"),
    DataSource("https://www.pieas.edu.pk/", "PIEAS", SourceCategory.UNIVERSITY, "PK", "Nuclear engineering"),
    DataSource("https://www.shifa.com.pk/", "Shifa International Hospital", SourceCategory.HOSPITAL, "PK", "Major hospital"),
    DataSource("https://www.akuh.org/", "Aga Khan University Hospital", SourceCategory.HOSPITAL, "PK", "Top hospital"),
    DataSource("https://www.cmh.edu.pk/", "CMH Rawalpindi", SourceCategory.HOSPITAL, "PK", "Military hospital"),
    DataSource("https://www.hbljob.com/", "HBL Bank", SourceCategory.BANK, "PK", "Major bank"),
    DataSource("https://www.ubl.com.pk/", "UBL", SourceCategory.BANK, "PK", "Major bank"),
    DataSource("https://www.mcb.com.pk/", "MCB Bank", SourceCategory.BANK, "PK", "Major bank"),
    DataSource("https://www.allidbankpak.com/", "Allied Bank", SourceCategory.BANK, "PK", "Major bank"),
    DataSource("https://www.nbp.com.pk/", "National Bank Pakistan", SourceCategory.BANK, "PK", "Largest bank"),
    DataSource("https://www.psx.com.pk/", "Pakistan Stock Exchange", SourceCategory.BANK, "PK", "Stock exchange", True),
    DataSource("https://www.secp.gov.pk/", "SECP Pakistan", SourceCategory.RATING, "PK", "Securities regulator"),
    DataSource("https://www.ogra.org.pk/", "OGRA Pakistan", SourceCategory.ENERGY, "PK", "Oil gas regulator"),
    DataSource("https://www.nepra.org.pk/", "NEPRA", SourceCategory.ENERGY, "PK", "Power regulator"),
    DataSource("https://www.pta.gov.pk/", "PTA Pakistan", SourceCategory.TELECOM, "PK", "Telecom regulator", True),
    DataSource("https://www.dawn.com/", "Dawn", SourceCategory.NEWS, "PK", "Major newspaper"),
    DataSource("https://www.geo.tv/", "Geo News", SourceCategory.NEWS, "PK", "News channel"),
    DataSource("https://www.thenews.com.pk/", "The News", SourceCategory.NEWS, "PK", "Newspaper"),
    DataSource("https://www.express.pk/", "Express Tribune", SourceCategory.NEWS, "PK", "English newspaper"),
    DataSource("https://www.ptv.com.pk/", "PTV", SourceCategory.NEWS, "PK", "State broadcaster"),
    DataSource("https://www.radio.gov.pk/", "Radio Pakistan", SourceCategory.NEWS, "PK", "State radio"),
    DataSource("https://www.app.gov.pk/", "APP", SourceCategory.NEWS, "PK", "News agency"),
    DataSource("https://www.pakmuseum.gov.pk/", "Pakistan Museum", SourceCategory.CULTURE, "PK", "National museum"),
    DataSource("https://www.nlp.gov.pk/", "National Library Pakistan", SourceCategory.CULTURE, "PK", "National library"),
]

# ============================================================
# 🇧🇩 BANGLADESH
# ============================================================

BANGLADESH_SOURCES = [
    DataSource("https://www.bangladesh.gov.bd/", "Government of Bangladesh", SourceCategory.GOVERNMENT, "BD", "Government portal"),
    DataSource("https://data.gov.bd/", "Bangladesh Open Data", SourceCategory.GOVERNMENT, "BD", "Open data portal", True),
    DataSource("https://www.bbs.gov.bd/", "Bangladesh Bureau of Statistics", SourceCategory.STATISTICS, "BD", "Statistics", True),
    DataSource("https://www.bb.org.bd/", "Bangladesh Bank", SourceCategory.BANK, "BD", "Central Bank", True),
    DataSource("https://www.mof.gov.bd/", "Ministry of Finance Bangladesh", SourceCategory.GOVERNMENT, "BD", "Financial data"),
    DataSource("https://www.du.ac.bd/", "University of Dhaka", SourceCategory.UNIVERSITY, "BD", "Top university"),
    DataSource("https://www.buet.ac.bd/", "BUET", SourceCategory.UNIVERSITY, "BD", "Engineering"),
    DataSource("https://www.ru.ac.bd/", "University of Rajshahi", SourceCategory.UNIVERSITY, "BD", "Research"),
    DataSource("https://www.cu.ac.bd/", "University of Chittagong", SourceCategory.UNIVERSITY, "BD", "Research"),
    DataSource("https://www.ju.edu.bd/", "Jahangirnagar University", SourceCategory.UNIVERSITY, "BD", "Research"),
    DataSource("https://www.sust.edu/", "SUST", SourceCategory.UNIVERSITY, "BD", "Science technology"),
    DataSource("https://www.kuet.ac.bd/", "KUET", SourceCategory.UNIVERSITY, "BD", "Engineering"),
    DataSource("https://www.bracu.ac.bd/", "BRAC University", SourceCategory.UNIVERSITY, "BD", "Private"),
    DataSource("https://www.northsouth.edu/", "North South University", SourceCategory.UNIVERSITY, "BD", "Private"),
    DataSource("https://www.iub.edu.bd/", "IUB", SourceCategory.UNIVERSITY, "BD", "Private"),
    DataSource("https://www.dmch.gov.bd/", "Dhaka Medical College Hospital", SourceCategory.HOSPITAL, "BD", "Top hospital"),
    DataSource("https://www.bsmmu.edu.bd/", "BSMMU", SourceCategory.HOSPITAL, "BD", "Medical university"),
    DataSource("https://www.squarehospitals.com/", "Square Hospital", SourceCategory.HOSPITAL, "BD", "Private hospital"),
    DataSource("https://www.dhakabank.com.bd/", "Dhaka Bank", SourceCategory.BANK, "BD", "Major bank"),
    DataSource("https://www.bracbank.com/", "BRAC Bank", SourceCategory.BANK, "BD", "Major bank"),
    DataSource("https://www.dutchbanglabank.com/", "Dutch-Bangla Bank", SourceCategory.BANK, "BD", "Major bank"),
    DataSource("https://www.sonalibank.com.bd/", "Sonali Bank", SourceCategory.BANK, "BD", "State bank"),
    DataSource("https://www.dsebd.org/", "Dhaka Stock Exchange", SourceCategory.BANK, "BD", "Stock exchange", True),
    DataSource("https://www.bsec.gov.bd/", "BSEC", SourceCategory.RATING, "BD", "Securities regulator"),
    DataSource("https://www.btrc.gov.bd/", "BTRC", SourceCategory.TELECOM, "BD", "Telecom regulator", True),
    DataSource("https://www.prothomalo.com/", "Prothom Alo", SourceCategory.NEWS, "BD", "Largest newspaper"),
    DataSource("https://www.thedailystar.net/", "Daily Star", SourceCategory.NEWS, "BD", "English newspaper"),
    DataSource("https://www.bdnews24.com/", "bdnews24", SourceCategory.NEWS, "BD", "Digital news"),
    DataSource("https://www.bssnews.net/", "BSS", SourceCategory.NEWS, "BD", "State news agency"),
    DataSource("https://www.btv.gov.bd/", "BTV", SourceCategory.NEWS, "BD", "State broadcaster"),
    DataSource("https://www.bangladeshmuseum.gov.bd/", "Bangladesh National Museum", SourceCategory.CULTURE, "BD", "National museum"),
    DataSource("https://www.nlb.gov.bd/", "National Library Bangladesh", SourceCategory.CULTURE, "BD", "National library"),
]

# ============================================================
# 🇱🇰 SRI LANKA
# ============================================================

SRI_LANKA_SOURCES = [
    DataSource("https://www.gov.lk/", "Government of Sri Lanka", SourceCategory.GOVERNMENT, "LK", "Government portal"),
    DataSource("https://www.statistics.gov.lk/", "Dept of Census Statistics", SourceCategory.STATISTICS, "LK", "Statistics", True),
    DataSource("https://www.cbsl.gov.lk/", "Central Bank Sri Lanka", SourceCategory.BANK, "LK", "Central Bank", True),
    DataSource("https://www.treasury.gov.lk/", "Ministry of Finance Sri Lanka", SourceCategory.GOVERNMENT, "LK", "Financial data"),
    DataSource("https://www.cmb.ac.lk/", "University of Colombo", SourceCategory.UNIVERSITY, "LK", "Top university"),
    DataSource("https://www.pdn.ac.lk/", "University of Peradeniya", SourceCategory.UNIVERSITY, "LK", "Research"),
    DataSource("https://www.mrt.ac.lk/", "University of Moratuwa", SourceCategory.UNIVERSITY, "LK", "Technology"),
    DataSource("https://www.sjp.ac.lk/", "University of Sri Jayewardenepura", SourceCategory.UNIVERSITY, "LK", "Research"),
    DataSource("https://www.nhsl.health.gov.lk/", "National Hospital Sri Lanka", SourceCategory.HOSPITAL, "LK", "National hospital"),
    DataSource("https://www.asiri.lk/", "Asiri Hospital", SourceCategory.HOSPITAL, "LK", "Private hospital"),
    DataSource("https://www.lankahospitals.com/", "Lanka Hospitals", SourceCategory.HOSPITAL, "LK", "Private hospital"),
    DataSource("https://www.boc.lk/", "Bank of Ceylon", SourceCategory.BANK, "LK", "State bank"),
    DataSource("https://www.peoplesbank.lk/", "People's Bank", SourceCategory.BANK, "LK", "State bank"),
    DataSource("https://www.combank.lk/", "Commercial Bank Ceylon", SourceCategory.BANK, "LK", "Major bank"),
    DataSource("https://www.cse.lk/", "Colombo Stock Exchange", SourceCategory.BANK, "LK", "Stock exchange", True),
    DataSource("https://www.sec.gov.lk/", "SEC Sri Lanka", SourceCategory.RATING, "LK", "Securities regulator"),
    DataSource("https://www.trcsl.gov.lk/", "TRCSL", SourceCategory.TELECOM, "LK", "Telecom regulator"),
    DataSource("https://www.dailymirror.lk/", "Daily Mirror", SourceCategory.NEWS, "LK", "English newspaper"),
    DataSource("https://www.sundaytimes.lk/", "Sunday Times", SourceCategory.NEWS, "LK", "Sunday paper"),
    DataSource("https://www.island.lk/", "The Island", SourceCategory.NEWS, "LK", "English newspaper"),
    DataSource("https://www.newsfirst.lk/", "NewsFirst", SourceCategory.NEWS, "LK", "News channel"),
    DataSource("https://www.rupavahini.lk/", "Rupavahini", SourceCategory.NEWS, "LK", "State broadcaster"),
    DataSource("https://www.museum.gov.lk/", "National Museum Sri Lanka", SourceCategory.CULTURE, "LK", "National museum"),
]

# ============================================================
# 🇳🇵 NEPAL
# ============================================================

NEPAL_SOURCES = [
    DataSource("https://www.nepal.gov.np/", "Government of Nepal", SourceCategory.GOVERNMENT, "NP", "Government portal"),
    DataSource("https://cbs.gov.np/", "Central Bureau of Statistics Nepal", SourceCategory.STATISTICS, "NP", "Statistics", True),
    DataSource("https://www.nrb.org.np/", "Nepal Rastra Bank", SourceCategory.BANK, "NP", "Central Bank", True),
    DataSource("https://www.mof.gov.np/", "Ministry of Finance Nepal", SourceCategory.GOVERNMENT, "NP", "Financial data"),
    DataSource("https://www.tu.edu.np/", "Tribhuvan University", SourceCategory.UNIVERSITY, "NP", "Largest university"),
    DataSource("https://www.ku.edu.np/", "Kathmandu University", SourceCategory.UNIVERSITY, "NP", "Private university"),
    DataSource("https://www.pu.edu.np/", "Pokhara University", SourceCategory.UNIVERSITY, "NP", "Research"),
    DataSource("https://www.iom.edu.np/", "Institute of Medicine", SourceCategory.HOSPITAL, "NP", "Teaching hospital"),
    DataSource("https://www.nbl.com.np/", "Nepal Bank Limited", SourceCategory.BANK, "NP", "State bank"),
    DataSource("https://www.rbb.com.np/", "Rastriya Banijya Bank", SourceCategory.BANK, "NP", "State bank"),
    DataSource("https://www.nepalstock.com.np/", "Nepal Stock Exchange", SourceCategory.BANK, "NP", "Stock exchange", True),
    DataSource("https://www.sebon.gov.np/", "SEBON", SourceCategory.RATING, "NP", "Securities regulator"),
    DataSource("https://www.nta.gov.np/", "NTA Nepal", SourceCategory.TELECOM, "NP", "Telecom regulator"),
    DataSource("https://www.kantipuronline.com/", "Kantipur", SourceCategory.NEWS, "NP", "Major newspaper"),
    DataSource("https://kathmandupost.com/", "Kathmandu Post", SourceCategory.NEWS, "NP", "English newspaper"),
    DataSource("https://risingnepaldaily.com/", "Rising Nepal", SourceCategory.NEWS, "NP", "State newspaper"),
    DataSource("https://www.ntv.org.np/", "Nepal Television", SourceCategory.NEWS, "NP", "State broadcaster"),
    DataSource("https://www.nationalmuseum.gov.np/", "National Museum Nepal", SourceCategory.CULTURE, "NP", "National museum"),
]

# ============================================================
# 🇧🇹 BHUTAN
# ============================================================

BHUTAN_SOURCES = [
    DataSource("https://www.gov.bt/", "Government of Bhutan", SourceCategory.GOVERNMENT, "BT", "Government portal"),
    DataSource("https://www.nsb.gov.bt/", "National Statistics Bureau", SourceCategory.STATISTICS, "BT", "Statistics", True),
    DataSource("https://www.rma.org.bt/", "Royal Monetary Authority", SourceCategory.BANK, "BT", "Central Bank", True),
    DataSource("https://www.mof.gov.bt/", "Ministry of Finance Bhutan", SourceCategory.GOVERNMENT, "BT", "Financial data"),
    DataSource("https://www.rub.edu.bt/", "Royal University of Bhutan", SourceCategory.UNIVERSITY, "BT", "National university"),
    DataSource("https://www.jdwnrh.gov.bt/", "Jigme Dorji Wangchuck Hospital", SourceCategory.HOSPITAL, "BT", "National hospital"),
    DataSource("https://www.bnb.bt/", "Bank of Bhutan", SourceCategory.BANK, "BT", "State bank"),
    DataSource("https://www.kuenselonline.com/", "Kuensel", SourceCategory.NEWS, "BT", "National newspaper"),
    DataSource("https://www.bbs.bt/", "BBS", SourceCategory.NEWS, "BT", "State broadcaster"),
    DataSource("https://www.nationalmuseum.gov.bt/", "National Museum Bhutan", SourceCategory.CULTURE, "BT", "National museum"),
]

# ============================================================
# 🇲🇻 MALDIVES
# ============================================================

MALDIVES_SOURCES = [
    DataSource("https://www.gov.mv/", "Government of Maldives", SourceCategory.GOVERNMENT, "MV", "Government portal"),
    DataSource("https://statisticsmaldives.gov.mv/", "National Bureau Statistics", SourceCategory.STATISTICS, "MV", "Statistics", True),
    DataSource("https://www.mma.gov.mv/", "Maldives Monetary Authority", SourceCategory.BANK, "MV", "Central Bank", True),
    DataSource("https://www.mnu.edu.mv/", "Maldives National University", SourceCategory.UNIVERSITY, "MV", "National university"),
    DataSource("https://igmh.gov.mv/", "IGMH", SourceCategory.HOSPITAL, "MV", "Main hospital"),
    DataSource("https://www.bml.com.mv/", "Bank of Maldives", SourceCategory.BANK, "MV", "State bank"),
    DataSource("https://www.mse.com.mv/", "Maldives Stock Exchange", SourceCategory.BANK, "MV", "Stock exchange"),
    DataSource("https://edition.mv/", "Edition Maldives", SourceCategory.NEWS, "MV", "News portal"),
    DataSource("https://www.psm.mv/", "PSM", SourceCategory.NEWS, "MV", "State media"),
]

# ============================================================
# 🇦🇫 AFGHANISTAN
# ============================================================

AFGHANISTAN_SOURCES = [
    DataSource("https://www.nsia.gov.af/", "National Statistics Afghanistan", SourceCategory.STATISTICS, "AF", "Statistics"),
    DataSource("https://www.dab.gov.af/", "Da Afghanistan Bank", SourceCategory.BANK, "AF", "Central Bank"),
    DataSource("https://www.ku.edu.af/", "Kabul University", SourceCategory.UNIVERSITY, "AF", "Main university"),
    DataSource("https://tolonews.com/", "Tolo News", SourceCategory.NEWS, "AF", "News channel"),
    DataSource("https://www.rta.org.af/", "RTA", SourceCategory.NEWS, "AF", "State broadcaster"),
]

# ============================================================
# 🏆 GLOBAL SPORT SOURCES
# ============================================================

GLOBAL_SPORT_SOURCES = [
    DataSource("https://www.fifa.com/", "FIFA", SourceCategory.SPORT, "GLOBAL", "Football global federation", True),
    DataSource("https://www.uefa.com/", "UEFA", SourceCategory.SPORT, "EU", "European football federation", True),
    DataSource("https://www.olympics.com/", "Olympic Games", SourceCategory.SPORT, "GLOBAL", "Official Olympic data", True),
    DataSource("https://www.nba.com/", "NBA", SourceCategory.SPORT, "US", "Basketball league", True),
    DataSource("https://www.nfl.com/", "NFL", SourceCategory.SPORT, "US", "American football league", True),
    DataSource("https://www.mlb.com/", "MLB", SourceCategory.SPORT, "US", "Baseball league", True),
    DataSource("https://www.nhl.com/", "NHL", SourceCategory.SPORT, "US", "Ice hockey league", True),
    DataSource("https://www.formula1.com/", "Formula 1", SourceCategory.SPORT, "GLOBAL", "Motorsport data", True),
    DataSource("https://www.motogp.com/", "MotoGP", SourceCategory.SPORT, "GLOBAL", "Motorcycle racing", True),
    DataSource("https://www.atptour.com/", "ATP Tennis", SourceCategory.SPORT, "GLOBAL", "Men's tennis rankings", True),
    DataSource("https://www.wtatennis.com/", "WTA Tennis", SourceCategory.SPORT, "GLOBAL", "Women's tennis rankings", True),
    DataSource("https://www.pgatour.com/", "PGA Tour Golf", SourceCategory.SPORT, "GLOBAL", "Golf tour", True),
    DataSource("https://www.uci.org/", "UCI Cycling", SourceCategory.SPORT, "GLOBAL", "Cycling federation", True),
    DataSource("https://www.worldathletics.org/", "World Athletics", SourceCategory.SPORT, "GLOBAL", "Track and field", True),
    DataSource("https://www.fiba.basketball/", "FIBA Basketball", SourceCategory.SPORT, "GLOBAL", "World basketball", True),
    DataSource("https://www.iihf.com/", "IIHF Hockey", SourceCategory.SPORT, "GLOBAL", "Ice hockey world", True),
    DataSource("https://www.fivb.com/", "FIVB Volleyball", SourceCategory.SPORT, "GLOBAL", "Volleyball federation", True),
    DataSource("https://www.worldrugby.org/", "World Rugby", SourceCategory.SPORT, "GLOBAL", "Rugby union", True),
    DataSource("https://www.icc-cricket.com/", "ICC Cricket", SourceCategory.SPORT, "GLOBAL", "Cricket world", True),
    DataSource("https://www.iwf.net/", "IWF Weightlifting", SourceCategory.SPORT, "GLOBAL", "Weightlifting", True),
    DataSource("https://www.ufc.com/", "UFC MMA", SourceCategory.SPORT, "GLOBAL", "Mixed martial arts", True),
    DataSource("https://www.boxing.com/", "Boxing", SourceCategory.SPORT, "GLOBAL", "Boxing news rankings", True),
    DataSource("https://www.wwe.com/", "WWE Wrestling", SourceCategory.SPORT, "GLOBAL", "Wrestling entertainment", True),
    DataSource("https://www.fia.com/", "FIA Motorsport", SourceCategory.SPORT, "GLOBAL", "Motorsport federation", True),
    DataSource("https://www.wrc.com/", "WRC Rally", SourceCategory.SPORT, "GLOBAL", "World rally championship", True),
    DataSource("https://www.indycar.com/", "IndyCar", SourceCategory.SPORT, "US", "American open-wheel racing", True),
    DataSource("https://www.nascar.com/", "NASCAR", SourceCategory.SPORT, "US", "Stock car racing", True),
    DataSource("https://www.premierleague.com/", "Premier League", SourceCategory.SPORT, "UK", "English football", True),
    DataSource("https://www.laliga.com/", "La Liga", SourceCategory.SPORT, "ES", "Spanish football", True),
    DataSource("https://www.bundesliga.com/", "Bundesliga", SourceCategory.SPORT, "DE", "German football", True),
    DataSource("https://www.legaseriea.it/", "Serie A", SourceCategory.SPORT, "IT", "Italian football", True),
    DataSource("https://www.ligue1.com/", "Ligue 1", SourceCategory.SPORT, "FR", "French football", True),
]

# ============================================================
# 🎨 GLOBAL HOBBY SOURCES
# ============================================================

GLOBAL_HOBBY_SOURCES = [
    DataSource("https://www.goodreads.com/", "Goodreads", SourceCategory.HOBBY, "GLOBAL", "Books, reading, literature", True),
    DataSource("https://www.imdb.com/", "IMDb", SourceCategory.ENTERTAINMENT, "GLOBAL", "Movies, actors, ratings", True),
    DataSource("https://www.allrecipes.com/", "AllRecipes", SourceCategory.HOBBY, "GLOBAL", "Cooking, recipes, food", True),
    DataSource("https://www.last.fm/", "LastFM", SourceCategory.HOBBY, "GLOBAL", "Music discovery", True),
    DataSource("https://www.boardgamegeek.com/", "BoardGameGeek", SourceCategory.HOBBY, "GLOBAL", "Board games database", True),
    DataSource("https://www.artstation.com/", "ArtStation", SourceCategory.HOBBY, "GLOBAL", "Digital art, 3D, design", True),
    DataSource("https://www.deviantart.com/", "DeviantArt", SourceCategory.HOBBY, "GLOBAL", "Art community", True),
    DataSource("https://www.behance.net/", "Behance", SourceCategory.HOBBY, "GLOBAL", "Creative portfolios", True),
    DataSource("https://www.dribbble.com/", "Dribbble", SourceCategory.HOBBY, "GLOBAL", "Design inspiration", True),
    DataSource("https://www.instructables.com/", "Instructables", SourceCategory.HOBBY, "GLOBAL", "DIY projects", True),
    DataSource("https://www.ravelry.com/", "Ravelry", SourceCategory.HOBBY, "GLOBAL", "Knitting, crochet", True),
    DataSource("https://www.chess.com/", "Chess.com", SourceCategory.HOBBY, "GLOBAL", "Online chess", True),
    DataSource("https://www.lichess.org/", "Lichess", SourceCategory.HOBBY, "GLOBAL", "Free chess platform", True),
    DataSource("https://www.discogs.com/", "Discogs", SourceCategory.HOBBY, "GLOBAL", "Music database, vinyl", True),
    DataSource("https://www.letterboxd.com/", "Letterboxd", SourceCategory.HOBBY, "GLOBAL", "Film diary, reviews", True),
    DataSource("https://www.myanimelist.net/", "MyAnimeList", SourceCategory.HOBBY, "GLOBAL", "Anime, manga database", True),
    DataSource("https://www.epicurious.com/", "Epicurious", SourceCategory.HOBBY, "GLOBAL", "Recipes, cooking", True),
    DataSource("https://www.seriouseats.com/", "Serious Eats", SourceCategory.HOBBY, "GLOBAL", "Food science, recipes", True),
    DataSource("https://www.500px.com/", "500px", SourceCategory.HOBBY, "GLOBAL", "Photography community", True),
    DataSource("https://www.flickr.com/", "Flickr", SourceCategory.HOBBY, "GLOBAL", "Photo sharing", True),
    DataSource("https://www.unsplash.com/", "Unsplash", SourceCategory.HOBBY, "GLOBAL", "Free photos", True),
    DataSource("https://www.pexels.com/", "Pexels", SourceCategory.HOBBY, "GLOBAL", "Free stock photos", True),
]

# ============================================================
# 🎬 GLOBAL ENTERTAINMENT SOURCES
# ============================================================

GLOBAL_ENTERTAINMENT_SOURCES = [
    DataSource("https://www.netflix.com/", "Netflix", SourceCategory.ENTERTAINMENT, "GLOBAL", "Streaming platform", False),
    DataSource("https://www.spotify.com/", "Spotify", SourceCategory.ENTERTAINMENT, "GLOBAL", "Music streaming", True),
    DataSource("https://www.tiktok.com/", "TikTok", SourceCategory.ENTERTAINMENT, "GLOBAL", "Short video platform", False),
    DataSource("https://www.youtube.com/", "YouTube", SourceCategory.ENTERTAINMENT, "GLOBAL", "Video platform", True),
    DataSource("https://www.twitch.tv/", "Twitch", SourceCategory.ENTERTAINMENT, "GLOBAL", "Gaming livestreams", True),
    DataSource("https://www.disneyplus.com/", "Disney+", SourceCategory.ENTERTAINMENT, "GLOBAL", "Disney streaming", False),
    DataSource("https://www.hbomax.com/", "HBO Max", SourceCategory.ENTERTAINMENT, "GLOBAL", "HBO streaming", False),
    DataSource("https://www.primevideo.com/", "Prime Video", SourceCategory.ENTERTAINMENT, "GLOBAL", "Amazon streaming", False),
    DataSource("https://www.hulu.com/", "Hulu", SourceCategory.ENTERTAINMENT, "US", "Streaming platform", False),
    DataSource("https://www.peacocktv.com/", "Peacock", SourceCategory.ENTERTAINMENT, "US", "NBC streaming", False),
    DataSource("https://www.paramountplus.com/", "Paramount+", SourceCategory.ENTERTAINMENT, "GLOBAL", "CBS streaming", False),
    DataSource("https://www.applemusic.com/", "Apple Music", SourceCategory.ENTERTAINMENT, "GLOBAL", "Music streaming", True),
    DataSource("https://www.deezer.com/", "Deezer", SourceCategory.ENTERTAINMENT, "GLOBAL", "Music streaming", True),
    DataSource("https://www.soundcloud.com/", "SoundCloud", SourceCategory.ENTERTAINMENT, "GLOBAL", "Music sharing", True),
    DataSource("https://www.pandora.com/", "Pandora", SourceCategory.ENTERTAINMENT, "US", "Music radio", True),
    DataSource("https://www.rottentomatoes.com/", "Rotten Tomatoes", SourceCategory.ENTERTAINMENT, "GLOBAL", "Movie reviews", True),
    DataSource("https://www.metacritic.com/", "Metacritic", SourceCategory.ENTERTAINMENT, "GLOBAL", "Review aggregator", True),
    DataSource("https://www.crunchyroll.com/", "Crunchyroll", SourceCategory.ENTERTAINMENT, "GLOBAL", "Anime streaming", True),
    DataSource("https://www.funimation.com/", "Funimation", SourceCategory.ENTERTAINMENT, "GLOBAL", "Anime streaming", True),
    DataSource("https://www.viki.com/", "Viki", SourceCategory.ENTERTAINMENT, "GLOBAL", "Asian drama streaming", True),
]

# ============================================================
# ✈️ GLOBAL TOURISM SOURCES
# ============================================================

GLOBAL_TOURISM_SOURCES = [
    DataSource("https://www.lonelyplanet.com/", "Lonely Planet", SourceCategory.TOURISM, "GLOBAL", "Travel guides", True),
    DataSource("https://www.tripadvisor.com/", "TripAdvisor", SourceCategory.TOURISM, "GLOBAL", "Hotels, restaurants", True),
    DataSource("https://www.booking.com/", "Booking.com", SourceCategory.TOURISM, "GLOBAL", "Hotels and travel", True),
    DataSource("https://www.airbnb.com/", "Airbnb", SourceCategory.TOURISM, "GLOBAL", "Short-term rentals", True),
    DataSource("https://www.kayak.com/", "Kayak", SourceCategory.TOURISM, "GLOBAL", "Flights, hotels", True),
    DataSource("https://www.expedia.com/", "Expedia", SourceCategory.TOURISM, "GLOBAL", "Travel booking", True),
    DataSource("https://www.skyscanner.com/", "Skyscanner", SourceCategory.TOURISM, "GLOBAL", "Flight search", True),
    DataSource("https://www.google.com/travel/", "Google Travel", SourceCategory.TOURISM, "GLOBAL", "Travel planning", True),
    DataSource("https://www.hotels.com/", "Hotels.com", SourceCategory.TOURISM, "GLOBAL", "Hotel booking", True),
    DataSource("https://www.agoda.com/", "Agoda", SourceCategory.TOURISM, "GLOBAL", "Asia-focused hotels", True),
    DataSource("https://www.hostelworld.com/", "Hostelworld", SourceCategory.TOURISM, "GLOBAL", "Hostel booking", True),
    DataSource("https://www.couchsurfing.com/", "Couchsurfing", SourceCategory.TOURISM, "GLOBAL", "Free stays", True),
    DataSource("https://www.vrbo.com/", "Vrbo", SourceCategory.TOURISM, "GLOBAL", "Vacation rentals", True),
    DataSource("https://www.viator.com/", "Viator", SourceCategory.TOURISM, "GLOBAL", "Tours, activities", True),
    DataSource("https://www.getyourguide.com/", "GetYourGuide", SourceCategory.TOURISM, "GLOBAL", "Tours, experiences", True),
    DataSource("https://www.klook.com/", "Klook", SourceCategory.TOURISM, "GLOBAL", "Asia activities", True),
    DataSource("https://www.rome2rio.com/", "Rome2Rio", SourceCategory.TOURISM, "GLOBAL", "Transport search", True),
    DataSource("https://www.flightradar24.com/", "Flightradar24", SourceCategory.TOURISM, "GLOBAL", "Live flight tracking", True),
    DataSource("https://www.flightaware.com/", "FlightAware", SourceCategory.TOURISM, "GLOBAL", "Flight tracking", True),
    DataSource("https://www.seatguru.com/", "SeatGuru", SourceCategory.TOURISM, "GLOBAL", "Airplane seat maps", True),
    DataSource("https://www.unwto.org/", "UNWTO", SourceCategory.TOURISM, "GLOBAL", "World tourism organization", True),
    DataSource("https://www.wttc.org/", "WTTC", SourceCategory.TOURISM, "GLOBAL", "Travel & tourism council", True),
]

# ============================================================
# 🎭 GLOBAL EVENTS & LIFESTYLE SOURCES
# ============================================================

GLOBAL_EVENTS_SOURCES = [
    DataSource("https://www.eventbrite.com/", "Eventbrite", SourceCategory.EVENTS, "GLOBAL", "Events, conferences", True),
    DataSource("https://www.meetup.com/", "Meetup", SourceCategory.LIFESTYLE, "GLOBAL", "Communities, gatherings", True),
    DataSource("https://www.timeout.com/", "TimeOut", SourceCategory.LIFESTYLE, "GLOBAL", "City guides, events", True),
    DataSource("https://www.ticketmaster.com/", "Ticketmaster", SourceCategory.EVENTS, "GLOBAL", "Concert tickets", True),
    DataSource("https://www.stubhub.com/", "StubHub", SourceCategory.EVENTS, "GLOBAL", "Ticket marketplace", True),
    DataSource("https://www.bandsintown.com/", "Bandsintown", SourceCategory.EVENTS, "GLOBAL", "Concert tracking", True),
    DataSource("https://www.songkick.com/", "Songkick", SourceCategory.EVENTS, "GLOBAL", "Live music events", True),
    DataSource("https://www.dice.fm/", "Dice", SourceCategory.EVENTS, "GLOBAL", "Music events", True),
    DataSource("https://www.seetickets.com/", "See Tickets", SourceCategory.EVENTS, "UK", "Event tickets", True),
    DataSource("https://www.festivalflyer.com/", "Festival Flyer", SourceCategory.EVENTS, "GLOBAL", "Festival calendar", True),
    DataSource("https://www.residentadvisor.net/", "Resident Advisor", SourceCategory.EVENTS, "GLOBAL", "Electronic music events", True),
    DataSource("https://www.yelp.com/", "Yelp", SourceCategory.LIFESTYLE, "GLOBAL", "Local business reviews", True),
    DataSource("https://www.foursquare.com/", "Foursquare", SourceCategory.LIFESTYLE, "GLOBAL", "Location discovery", True),
    DataSource("https://www.zomato.com/", "Zomato", SourceCategory.LIFESTYLE, "GLOBAL", "Restaurant discovery", True),
    DataSource("https://www.opentable.com/", "OpenTable", SourceCategory.LIFESTYLE, "GLOBAL", "Restaurant reservations", True),
    DataSource("https://www.thrillist.com/", "Thrillist", SourceCategory.LIFESTYLE, "GLOBAL", "Food, travel, culture", True),
    DataSource("https://www.eater.com/", "Eater", SourceCategory.LIFESTYLE, "GLOBAL", "Food news, guides", True),
    DataSource("https://www.infatuation.com/", "The Infatuation", SourceCategory.LIFESTYLE, "GLOBAL", "Restaurant reviews", True),
]

# ============================================================
# 🏏 INDIA SPORT SOURCES
# ============================================================

INDIA_SPORT = [
    DataSource("https://www.bcci.tv/", "BCCI Cricket India", SourceCategory.SPORT, "IN", "Cricket governing body", True),
    DataSource("https://www.iplt20.com/", "IPL – Indian Premier League", SourceCategory.SPORT, "IN", "Cricket league", True),
    DataSource("https://www.hockeyindia.org/", "Hockey India", SourceCategory.SPORT, "IN", "National hockey federation", True),
    DataSource("https://www.aiff.com/", "AIFF Football India", SourceCategory.SPORT, "IN", "Football federation", True),
    DataSource("https://www.badmintonindia.org/", "Badminton Association India", SourceCategory.SPORT, "IN", "Badminton federation", True),
    DataSource("https://www.indiansuperleague.com/", "ISL Indian Super League", SourceCategory.SPORT, "IN", "Football league", True),
    DataSource("https://www.prokabaddi.com/", "Pro Kabaddi League", SourceCategory.SPORT, "IN", "Kabaddi league", True),
    DataSource("https://www.prokabaddi.org/", "Kabaddi Federation", SourceCategory.SPORT, "IN", "Kabaddi federation", True),
    DataSource("https://www.tabletennis.in/", "Table Tennis India", SourceCategory.SPORT, "IN", "TT federation", True),
    DataSource("https://www.wrestlingindia.org/", "Wrestling India", SourceCategory.SPORT, "IN", "Wrestling federation", True),
    DataSource("https://www.boxingindia.org/", "Boxing Federation India", SourceCategory.SPORT, "IN", "Boxing federation", True),
    DataSource("https://www.indianga.org/", "Indian Golf Association", SourceCategory.SPORT, "IN", "Golf federation", True),
    DataSource("https://www.afi.org.in/", "Athletics Federation India", SourceCategory.SPORT, "IN", "Athletics federation", True),
    DataSource("https://www.swimmingindia.in/", "Swimming Federation India", SourceCategory.SPORT, "IN", "Swimming federation", True),
    DataSource("https://www.archeryindia.in/", "Archery Association India", SourceCategory.SPORT, "IN", "Archery federation", True),
    DataSource("https://www.volleyballindia.com/", "Volleyball India", SourceCategory.SPORT, "IN", "Volleyball federation", True),
    DataSource("https://www.espncricinfo.com/", "ESPNcricinfo", SourceCategory.SPORT, "IN", "Cricket news, stats", True),
    DataSource("https://www.cricbuzz.com/", "Cricbuzz", SourceCategory.SPORT, "IN", "Cricket scores, news", True),
]

# ============================================================
# 🎬 INDIA ENTERTAINMENT SOURCES
# ============================================================

INDIA_ENTERTAINMENT = [
    DataSource("https://www.hotstar.com/", "Hotstar", SourceCategory.ENTERTAINMENT, "IN", "Streaming platform", True),
    DataSource("https://www.zee5.com/", "ZEE5", SourceCategory.ENTERTAINMENT, "IN", "Streaming platform", True),
    DataSource("https://www.sonyliv.com/", "SonyLiv", SourceCategory.ENTERTAINMENT, "IN", "Streaming platform", True),
    DataSource("https://www.voot.com/", "Voot", SourceCategory.ENTERTAINMENT, "IN", "Entertainment platform", True),
    DataSource("https://www.bollywoodhungama.com/", "Bollywood Hungama", SourceCategory.ENTERTAINMENT, "IN", "Bollywood news", True),
    DataSource("https://www.jiocinema.com/", "JioCinema", SourceCategory.ENTERTAINMENT, "IN", "Jio streaming", True),
    DataSource("https://www.mxplayer.in/", "MX Player", SourceCategory.ENTERTAINMENT, "IN", "Free streaming", True),
    DataSource("https://www.altbalaji.com/", "ALTBalaji", SourceCategory.ENTERTAINMENT, "IN", "OTT platform", True),
    DataSource("https://www.erosnow.com/", "Eros Now", SourceCategory.ENTERTAINMENT, "IN", "Bollywood streaming", True),
    DataSource("https://www.filmfare.com/", "Filmfare", SourceCategory.ENTERTAINMENT, "IN", "Bollywood magazine", True),
    DataSource("https://www.pinkvilla.com/", "Pinkvilla", SourceCategory.ENTERTAINMENT, "IN", "Entertainment news", True),
    DataSource("https://www.missmalini.com/", "MissMalini", SourceCategory.ENTERTAINMENT, "IN", "Celebrity gossip", True),
    DataSource("https://www.radiomirchi.com/", "Radio Mirchi", SourceCategory.ENTERTAINMENT, "IN", "Radio station", True),
    DataSource("https://www.gaana.com/", "Gaana", SourceCategory.ENTERTAINMENT, "IN", "Music streaming", True),
    DataSource("https://www.jiosaavn.com/", "JioSaavn", SourceCategory.ENTERTAINMENT, "IN", "Music streaming", True),
    DataSource("https://www.wynk.in/", "Wynk Music", SourceCategory.ENTERTAINMENT, "IN", "Airtel music", True),
    DataSource("https://www.hungama.com/", "Hungama Music", SourceCategory.ENTERTAINMENT, "IN", "Music platform", True),
]

# ============================================================
# 🏝️ INDIA TOURISM SOURCES
# ============================================================

INDIA_TOURISM = [
    DataSource("https://www.incredibleindia.org/", "Incredible India", SourceCategory.TOURISM, "IN", "Official tourism", True),
    DataSource("https://www.tourism.gov.in/", "Ministry of Tourism India", SourceCategory.TOURISM, "IN", "Government tourism"),
    DataSource("https://www.keralatourism.org/", "Kerala Tourism", SourceCategory.TOURISM, "IN", "Kerala state tourism", True),
    DataSource("https://www.rajasthantourism.gov.in/", "Rajasthan Tourism", SourceCategory.TOURISM, "IN", "Rajasthan tourism", True),
    DataSource("https://www.goatourism.gov.in/", "Goa Tourism", SourceCategory.TOURISM, "IN", "Goa tourism", True),
    DataSource("https://www.gujarattourism.com/", "Gujarat Tourism", SourceCategory.TOURISM, "IN", "Gujarat tourism", True),
    DataSource("https://www.maharashtratourism.gov.in/", "Maharashtra Tourism", SourceCategory.TOURISM, "IN", "Maharashtra tourism", True),
    DataSource("https://www.karnatakatourism.org/", "Karnataka Tourism", SourceCategory.TOURISM, "IN", "Karnataka tourism", True),
    DataSource("https://www.tamilnadutourism.org/", "Tamil Nadu Tourism", SourceCategory.TOURISM, "IN", "TN tourism", True),
    DataSource("https://www.uttarakhandtourism.gov.in/", "Uttarakhand Tourism", SourceCategory.TOURISM, "IN", "Uttarakhand tourism", True),
    DataSource("https://www.himachaltourism.gov.in/", "Himachal Tourism", SourceCategory.TOURISM, "IN", "HP tourism", True),
    DataSource("https://www.jktourism.jk.gov.in/", "J&K Tourism", SourceCategory.TOURISM, "IN", "Kashmir tourism", True),
    DataSource("https://www.sikkim.gov.in/tourism/", "Sikkim Tourism", SourceCategory.TOURISM, "IN", "Sikkim tourism", True),
    DataSource("https://www.arunachaltourism.com/", "Arunachal Tourism", SourceCategory.TOURISM, "IN", "Northeast tourism", True),
    DataSource("https://www.irctc.co.in/", "IRCTC", SourceCategory.TOURISM, "IN", "Railway booking", True),
    DataSource("https://www.makemytrip.com/", "MakeMyTrip", SourceCategory.TOURISM, "IN", "Travel booking", True),
    DataSource("https://www.goibibo.com/", "Goibibo", SourceCategory.TOURISM, "IN", "Travel booking", True),
    DataSource("https://www.yatra.com/", "Yatra", SourceCategory.TOURISM, "IN", "Travel booking", True),
    DataSource("https://www.cleartrip.com/", "Cleartrip", SourceCategory.TOURISM, "IN", "Flight booking", True),
    DataSource("https://www.ixigo.com/", "Ixigo", SourceCategory.TOURISM, "IN", "Travel search", True),
    DataSource("https://www.oyorooms.com/", "OYO Rooms", SourceCategory.TOURISM, "IN", "Budget hotels", True),
    DataSource("https://www.treebo.com/", "Treebo", SourceCategory.TOURISM, "IN", "Budget hotels", True),
    DataSource("https://www.fabhotels.com/", "FabHotels", SourceCategory.TOURISM, "IN", "Budget hotels", True),
    DataSource("https://www.tajhotels.com/", "Taj Hotels", SourceCategory.TOURISM, "IN", "Luxury hotels", True),
    DataSource("https://www.oberoihotels.com/", "Oberoi Hotels", SourceCategory.TOURISM, "IN", "Luxury hotels", True),
    DataSource("https://www.itchotels.in/", "ITC Hotels", SourceCategory.TOURISM, "IN", "Luxury hotels", True),
]

# ============================================================
# 🎭 INDIA EVENTS & LIFESTYLE SOURCES
# ============================================================

INDIA_EVENTS_LIFESTYLE = [
    DataSource("https://www.bookmyshow.com/", "BookMyShow", SourceCategory.EVENTS, "IN", "Movie, event tickets", True),
    DataSource("https://www.paytminsider.com/", "Paytm Insider", SourceCategory.EVENTS, "IN", "Events, experiences", True),
    DataSource("https://www.in.bookmyshow.com/", "BMS Events", SourceCategory.EVENTS, "IN", "Live events", True),
    DataSource("https://www.swiggy.com/", "Swiggy", SourceCategory.LIFESTYLE, "IN", "Food delivery", True),
    DataSource("https://www.zomato.com/india/", "Zomato India", SourceCategory.LIFESTYLE, "IN", "Food delivery, reviews", True),
    DataSource("https://www.dineout.co.in/", "Dineout", SourceCategory.LIFESTYLE, "IN", "Restaurant discovery", True),
    DataSource("https://www.eazydiner.com/", "EazyDiner", SourceCategory.LIFESTYLE, "IN", "Restaurant booking", True),
    DataSource("https://www.urbanclap.com/", "Urban Company", SourceCategory.LIFESTYLE, "IN", "Home services", True),
    DataSource("https://www.justdial.com/", "Justdial", SourceCategory.LIFESTYLE, "IN", "Local search", True),
    DataSource("https://www.sulekha.com/", "Sulekha", SourceCategory.LIFESTYLE, "IN", "Local services", True),
    DataSource("https://www.nykaa.com/", "Nykaa", SourceCategory.LIFESTYLE, "IN", "Beauty, fashion", True),
    DataSource("https://www.myntra.com/", "Myntra", SourceCategory.LIFESTYLE, "IN", "Fashion shopping", True),
    DataSource("https://www.ajio.com/", "AJIO", SourceCategory.LIFESTYLE, "IN", "Fashion shopping", True),
    DataSource("https://www.lenskart.com/", "Lenskart", SourceCategory.LIFESTYLE, "IN", "Eyewear", True),
    DataSource("https://www.healthifyme.com/", "HealthifyMe", SourceCategory.LIFESTYLE, "IN", "Fitness app", True),
    DataSource("https://www.cult.fit/", "Cult.fit", SourceCategory.LIFESTYLE, "IN", "Fitness platform", True),
]

# ============================================================
# COMBINED EXPORT
# ============================================================

ALL_INDIA_SOUTH_ASIA_SOURCES = (
    INDIA_GOVERNMENT + INDIA_UNIVERSITIES_IIT + INDIA_UNIVERSITIES_IIM +
    INDIA_UNIVERSITIES_OTHER + INDIA_HOSPITALS + INDIA_BANKS +
    INDIA_FACTORIES_INDUSTRIAL + INDIA_NEWS_MEDIA + INDIA_CULTURE + INDIA_RESEARCH +
    INDIA_SPORT + INDIA_ENTERTAINMENT + INDIA_TOURISM + INDIA_EVENTS_LIFESTYLE +
    PAKISTAN_SOURCES + BANGLADESH_SOURCES + SRI_LANKA_SOURCES +
    NEPAL_SOURCES + BHUTAN_SOURCES + MALDIVES_SOURCES + AFGHANISTAN_SOURCES +
    GLOBAL_SPORT_SOURCES + GLOBAL_HOBBY_SOURCES + GLOBAL_ENTERTAINMENT_SOURCES +
    GLOBAL_TOURISM_SOURCES + GLOBAL_EVENTS_SOURCES
)

def get_all_sources() -> List[DataSource]:
    """Return all India/South Asia data sources"""
    return ALL_INDIA_SOUTH_ASIA_SOURCES

def get_sources_by_country(country_code: str) -> List[DataSource]:
    """Return sources for a specific country"""
    return [s for s in ALL_INDIA_SOUTH_ASIA_SOURCES if s.country == country_code]

def get_sources_by_category(category: SourceCategory) -> List[DataSource]:
    """Return sources for a specific category"""
    return [s for s in ALL_INDIA_SOUTH_ASIA_SOURCES if s.category == category]

def get_api_sources() -> List[DataSource]:
    """Return only sources with API access"""
    return [s for s in ALL_INDIA_SOUTH_ASIA_SOURCES if s.api_available]

def get_india_only() -> List[DataSource]:
    """Return only India sources"""
    return get_sources_by_country("IN")

# Statistics
print(f"Total India/South Asia Sources: {len(ALL_INDIA_SOUTH_ASIA_SOURCES)}")
print(f"India sources: {len(get_india_only())}")
print(f"Countries covered: IN, PK, BD, LK, NP, BT, MV, AF")
