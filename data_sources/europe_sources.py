# -*- coding: utf-8 -*-
"""
🇪🇺 EUROPE - COMPLETE DATA SOURCES
================================================
800+ Free Open Data Sources from European Countries

Countries Covered:
- Germany 🇩🇪
- France 🇫🇷
- United Kingdom 🇬🇧
- Italy 🇮🇹
- Spain 🇪🇸
- Netherlands 🇳🇱
- Switzerland 🇨🇭
- Austria 🇦🇹
- Belgium 🇧🇪
- Poland 🇵🇱
- Sweden 🇸🇪
- Norway 🇳🇴
- Denmark 🇩🇰
- Finland 🇫🇮
- Ireland 🇮🇪
- Portugal 🇵🇹
- Greece 🇬🇷
- Czech Republic 🇨🇿
- Romania 🇷🇴
- Hungary 🇭🇺

Categories:
- Government & Statistics
- Universities & Research
- Hospitals & Healthcare
- Banks & Financial
- Industry & Manufacturing
- News & Media
- Culture & Museums
- Sport & Entertainment
- Tourism & Travel
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
    AGRICULTURE = "agriculture"
    SPORT = "sport"
    ENTERTAINMENT = "entertainment"
    TOURISM = "tourism"
    EVENTS = "events"
    LIFESTYLE = "lifestyle"
    HOBBY = "hobby"

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
# 🇪🇺 EUROPEAN UNION INSTITUTIONS
# ============================================================

EU_INSTITUTIONS = [
    DataSource("https://europa.eu/", "European Union Portal", SourceCategory.GOVERNMENT, "EU", "EU official portal", True),
    DataSource("https://ec.europa.eu/", "European Commission", SourceCategory.GOVERNMENT, "EU", "EU executive"),
    DataSource("https://www.europarl.europa.eu/", "European Parliament", SourceCategory.GOVERNMENT, "EU", "EU legislature"),
    DataSource("https://www.consilium.europa.eu/", "European Council", SourceCategory.GOVERNMENT, "EU", "EU Council"),
    DataSource("https://curia.europa.eu/", "Court of Justice EU", SourceCategory.GOVERNMENT, "EU", "EU court"),
    DataSource("https://www.ecb.europa.eu/", "European Central Bank", SourceCategory.BANK, "EU", "Central bank", True),
    DataSource("https://data.europa.eu/", "European Data Portal", SourceCategory.STATISTICS, "EU", "Open data", True),
    DataSource("https://ec.europa.eu/eurostat/", "Eurostat", SourceCategory.STATISTICS, "EU", "EU statistics", True),
    DataSource("https://www.eea.europa.eu/", "European Environment Agency", SourceCategory.ENVIRONMENTAL, "EU", "Environment"),
    DataSource("https://www.eba.europa.eu/", "European Banking Authority", SourceCategory.BANK, "EU", "Banking regulation"),
    DataSource("https://www.esma.europa.eu/", "ESMA", SourceCategory.BANK, "EU", "Securities markets"),
    DataSource("https://www.eiopa.europa.eu/", "EIOPA", SourceCategory.BANK, "EU", "Insurance pensions"),
    DataSource("https://www.ema.europa.eu/", "European Medicines Agency", SourceCategory.HOSPITAL, "EU", "Medicines authority"),
    DataSource("https://www.efsa.europa.eu/", "EFSA", SourceCategory.RESEARCH, "EU", "Food safety"),
    DataSource("https://www.erc.europa.eu/", "European Research Council", SourceCategory.RESEARCH, "EU", "Research funding"),
    DataSource("https://cordis.europa.eu/", "CORDIS", SourceCategory.RESEARCH, "EU", "Research projects", True),
]

# ============================================================
# 🇩🇪 GERMANY DATA SOURCES
# ============================================================

GERMANY_GOVERNMENT = [
    DataSource("https://www.bundesregierung.de/", "German Federal Government", SourceCategory.GOVERNMENT, "DE", "Federal government"),
    DataSource("https://www.bundestag.de/", "Bundestag", SourceCategory.GOVERNMENT, "DE", "Parliament"),
    DataSource("https://www.bundesrat.de/", "Bundesrat", SourceCategory.GOVERNMENT, "DE", "Federal Council"),
    DataSource("https://www.bmi.bund.de/", "Federal Ministry of Interior", SourceCategory.GOVERNMENT, "DE", "Interior ministry"),
    DataSource("https://www.bmwk.de/", "Federal Ministry of Economy", SourceCategory.GOVERNMENT, "DE", "Economy ministry"),
    DataSource("https://www.destatis.de/", "Destatis", SourceCategory.STATISTICS, "DE", "Federal statistics", True),
    DataSource("https://www.govdata.de/", "GovData", SourceCategory.STATISTICS, "DE", "Open government data", True),
    DataSource("https://www.berlin.de/", "Berlin Portal", SourceCategory.GOVERNMENT, "DE", "Capital city"),
    DataSource("https://www.muenchen.de/", "Munich Portal", SourceCategory.GOVERNMENT, "DE", "Bavaria capital"),
    DataSource("https://www.hamburg.de/", "Hamburg Portal", SourceCategory.GOVERNMENT, "DE", "Hamburg city"),
    DataSource("https://www.frankfurt.de/", "Frankfurt Portal", SourceCategory.GOVERNMENT, "DE", "Financial center"),
    DataSource("https://www.koeln.de/", "Cologne Portal", SourceCategory.GOVERNMENT, "DE", "Cologne city"),
]

GERMANY_UNIVERSITIES = [
    DataSource("https://www.lmu.de/", "LMU Munich", SourceCategory.UNIVERSITY, "DE", "Top university"),
    DataSource("https://www.tum.de/", "TU Munich", SourceCategory.UNIVERSITY, "DE", "Technical university"),
    DataSource("https://www.hu-berlin.de/", "Humboldt University", SourceCategory.UNIVERSITY, "DE", "Berlin university"),
    DataSource("https://www.fu-berlin.de/", "Free University Berlin", SourceCategory.UNIVERSITY, "DE", "Research university"),
    DataSource("https://www.tu-berlin.de/", "TU Berlin", SourceCategory.UNIVERSITY, "DE", "Technical university"),
    DataSource("https://www.uni-heidelberg.de/", "Heidelberg University", SourceCategory.UNIVERSITY, "DE", "Oldest German university"),
    DataSource("https://www.uni-bonn.de/", "University of Bonn", SourceCategory.UNIVERSITY, "DE", "Research university"),
    DataSource("https://www.rwth-aachen.de/", "RWTH Aachen", SourceCategory.UNIVERSITY, "DE", "Technical university"),
    DataSource("https://www.kit.edu/", "Karlsruhe Institute", SourceCategory.UNIVERSITY, "DE", "KIT"),
    DataSource("https://www.uni-freiburg.de/", "University of Freiburg", SourceCategory.UNIVERSITY, "DE", "Research university"),
    DataSource("https://www.uni-koeln.de/", "University of Cologne", SourceCategory.UNIVERSITY, "DE", "Major university"),
    DataSource("https://www.uni-goettingen.de/", "University of Göttingen", SourceCategory.UNIVERSITY, "DE", "Historic university"),
    DataSource("https://www.tu-dresden.de/", "TU Dresden", SourceCategory.UNIVERSITY, "DE", "Technical university"),
    DataSource("https://www.uni-frankfurt.de/", "Goethe University", SourceCategory.UNIVERSITY, "DE", "Frankfurt university"),
    DataSource("https://www.uni-stuttgart.de/", "University of Stuttgart", SourceCategory.UNIVERSITY, "DE", "Technical focus"),
    DataSource("https://www.mpg.de/", "Max Planck Society", SourceCategory.RESEARCH, "DE", "Research institutes", True),
    DataSource("https://www.fraunhofer.de/", "Fraunhofer Society", SourceCategory.RESEARCH, "DE", "Applied research", True),
    DataSource("https://www.helmholtz.de/", "Helmholtz Association", SourceCategory.RESEARCH, "DE", "Research centers"),
    DataSource("https://www.leibniz-gemeinschaft.de/", "Leibniz Association", SourceCategory.RESEARCH, "DE", "Research institutes"),
]

GERMANY_HOSPITALS = [
    DataSource("https://www.charite.de/", "Charité Berlin", SourceCategory.HOSPITAL, "DE", "University hospital"),
    DataSource("https://www.ukm.de/", "University Hospital Münster", SourceCategory.HOSPITAL, "DE", "Medical center"),
    DataSource("https://www.uk-koeln.de/", "University Hospital Cologne", SourceCategory.HOSPITAL, "DE", "Medical center"),
    DataSource("https://www.klinikum.uni-muenchen.de/", "LMU Hospital Munich", SourceCategory.HOSPITAL, "DE", "University hospital"),
    DataSource("https://www.mri.tum.de/", "Rechts der Isar Hospital", SourceCategory.HOSPITAL, "DE", "TUM hospital"),
    DataSource("https://www.uksh.de/", "University Hospital Schleswig-Holstein", SourceCategory.HOSPITAL, "DE", "Medical center"),
    DataSource("https://www.uniklinik-heidelberg.de/", "Heidelberg University Hospital", SourceCategory.HOSPITAL, "DE", "Research hospital"),
    DataSource("https://www.uniklinik-frankfurt.de/", "Frankfurt University Hospital", SourceCategory.HOSPITAL, "DE", "Medical center"),
    DataSource("https://www.uniklinik-freiburg.de/", "Freiburg University Hospital", SourceCategory.HOSPITAL, "DE", "Medical center"),
    DataSource("https://www.med.uni-goettingen.de/", "Göttingen University Hospital", SourceCategory.HOSPITAL, "DE", "Medical center"),
]

GERMANY_BANKS = [
    DataSource("https://www.bundesbank.de/", "Deutsche Bundesbank", SourceCategory.BANK, "DE", "Central bank", True),
    DataSource("https://www.deutsche-bank.de/", "Deutsche Bank", SourceCategory.BANK, "DE", "Major bank"),
    DataSource("https://www.commerzbank.de/", "Commerzbank", SourceCategory.BANK, "DE", "Major bank"),
    DataSource("https://www.unicredit.de/", "HypoVereinsbank", SourceCategory.BANK, "DE", "Major bank"),
    DataSource("https://www.kfw.de/", "KfW", SourceCategory.BANK, "DE", "Development bank", True),
    DataSource("https://www.dz-bank.de/", "DZ Bank", SourceCategory.BANK, "DE", "Cooperative bank"),
    DataSource("https://www.lbbw.de/", "LBBW", SourceCategory.BANK, "DE", "Landesbank"),
    DataSource("https://www.bayernlb.de/", "BayernLB", SourceCategory.BANK, "DE", "Landesbank"),
    DataSource("https://www.xetra.com/", "Xetra", SourceCategory.BANK, "DE", "Electronic exchange", True),
    DataSource("https://www.boerse-frankfurt.de/", "Frankfurt Stock Exchange", SourceCategory.BANK, "DE", "Stock exchange", True),
    DataSource("https://www.bafin.de/", "BaFin", SourceCategory.BANK, "DE", "Financial supervision"),
]

GERMANY_INDUSTRY = [
    DataSource("https://www.volkswagen.de/", "Volkswagen", SourceCategory.INDUSTRY, "DE", "Automotive"),
    DataSource("https://www.mercedes-benz.de/", "Mercedes-Benz", SourceCategory.INDUSTRY, "DE", "Automotive"),
    DataSource("https://www.bmw.de/", "BMW", SourceCategory.INDUSTRY, "DE", "Automotive"),
    DataSource("https://www.audi.de/", "Audi", SourceCategory.INDUSTRY, "DE", "Automotive"),
    DataSource("https://www.porsche.com/", "Porsche", SourceCategory.INDUSTRY, "DE", "Automotive"),
    DataSource("https://www.siemens.de/", "Siemens", SourceCategory.INDUSTRY, "DE", "Engineering"),
    DataSource("https://www.basf.de/", "BASF", SourceCategory.INDUSTRY, "DE", "Chemicals"),
    DataSource("https://www.bayer.de/", "Bayer", SourceCategory.INDUSTRY, "DE", "Pharma/chemicals"),
    DataSource("https://www.sap.de/", "SAP", SourceCategory.INDUSTRY, "DE", "Software"),
    DataSource("https://www.bosch.de/", "Bosch", SourceCategory.INDUSTRY, "DE", "Engineering"),
    DataSource("https://www.allianz.de/", "Allianz", SourceCategory.INDUSTRY, "DE", "Insurance"),
    DataSource("https://www.thyssenkrupp.de/", "ThyssenKrupp", SourceCategory.INDUSTRY, "DE", "Steel/engineering"),
    DataSource("https://www.lufthansa.de/", "Lufthansa", SourceCategory.TRANSPORT, "DE", "Airline"),
    DataSource("https://www.bahn.de/", "Deutsche Bahn", SourceCategory.TRANSPORT, "DE", "Railways", True),
]

GERMANY_NEWS = [
    DataSource("https://www.spiegel.de/", "Der Spiegel", SourceCategory.NEWS, "DE", "News magazine"),
    DataSource("https://www.zeit.de/", "Die Zeit", SourceCategory.NEWS, "DE", "Weekly newspaper"),
    DataSource("https://www.sueddeutsche.de/", "Süddeutsche Zeitung", SourceCategory.NEWS, "DE", "Daily newspaper"),
    DataSource("https://www.faz.net/", "FAZ", SourceCategory.NEWS, "DE", "Daily newspaper"),
    DataSource("https://www.welt.de/", "Die Welt", SourceCategory.NEWS, "DE", "Daily newspaper"),
    DataSource("https://www.handelsblatt.com/", "Handelsblatt", SourceCategory.NEWS, "DE", "Business news"),
    DataSource("https://www.tagesschau.de/", "Tagesschau", SourceCategory.NEWS, "DE", "ARD news", True),
    DataSource("https://www.zdf.de/nachrichten/", "ZDF Nachrichten", SourceCategory.NEWS, "DE", "ZDF news"),
    DataSource("https://www.n-tv.de/", "n-tv", SourceCategory.NEWS, "DE", "News channel"),
    DataSource("https://www.focus.de/", "Focus", SourceCategory.NEWS, "DE", "News magazine"),
    DataSource("https://www.stern.de/", "Stern", SourceCategory.NEWS, "DE", "Magazine"),
]

GERMANY_CULTURE = [
    DataSource("https://www.smb.museum/", "Berlin State Museums", SourceCategory.CULTURE, "DE", "Museum complex"),
    DataSource("https://www.deutsches-museum.de/", "Deutsches Museum", SourceCategory.CULTURE, "DE", "Science museum"),
    DataSource("https://www.alte-pinakothek.de/", "Alte Pinakothek", SourceCategory.CULTURE, "DE", "Art museum"),
    DataSource("https://www.neues-museum.de/", "Neues Museum", SourceCategory.CULTURE, "DE", "Berlin museum"),
    DataSource("https://www.pergamonmuseum.de/", "Pergamon Museum", SourceCategory.CULTURE, "DE", "Ancient art"),
    DataSource("https://www.bundesarchiv.de/", "Bundesarchiv", SourceCategory.CULTURE, "DE", "Federal archives"),
    DataSource("https://www.dnb.de/", "German National Library", SourceCategory.CULTURE, "DE", "National library"),
    DataSource("https://www.goethe.de/", "Goethe Institut", SourceCategory.CULTURE, "DE", "Cultural institute"),
]

GERMANY_SPORT = [
    DataSource("https://www.dfb.de/", "DFB", SourceCategory.SPORT, "DE", "Football federation"),
    DataSource("https://www.bundesliga.com/", "Bundesliga", SourceCategory.SPORT, "DE", "Football league", True),
    DataSource("https://www.fcbayern.com/", "FC Bayern Munich", SourceCategory.SPORT, "DE", "Football club"),
    DataSource("https://www.bvb.de/", "Borussia Dortmund", SourceCategory.SPORT, "DE", "Football club"),
    DataSource("https://www.dhb.de/", "German Handball Federation", SourceCategory.SPORT, "DE", "Handball"),
    DataSource("https://www.basketball-bund.de/", "German Basketball Federation", SourceCategory.SPORT, "DE", "Basketball"),
    DataSource("https://www.dosb.de/", "German Olympic Committee", SourceCategory.SPORT, "DE", "Olympic committee"),
    DataSource("https://www.dtb-tennis.de/", "German Tennis Federation", SourceCategory.SPORT, "DE", "Tennis"),
    DataSource("https://www.schwimmen.de/", "German Swimming Federation", SourceCategory.SPORT, "DE", "Swimming"),
    DataSource("https://www.ski-online.de/", "German Ski Association", SourceCategory.SPORT, "DE", "Skiing"),
]

# ============================================================
# 🇫🇷 FRANCE DATA SOURCES
# ============================================================

FRANCE_GOVERNMENT = [
    DataSource("https://www.gouvernement.fr/", "French Government", SourceCategory.GOVERNMENT, "FR", "Government portal"),
    DataSource("https://www.assemblee-nationale.fr/", "National Assembly", SourceCategory.GOVERNMENT, "FR", "Parliament"),
    DataSource("https://www.senat.fr/", "Senate", SourceCategory.GOVERNMENT, "FR", "Upper house"),
    DataSource("https://www.elysee.fr/", "Élysée Palace", SourceCategory.GOVERNMENT, "FR", "Presidency"),
    DataSource("https://www.service-public.fr/", "Service Public", SourceCategory.GOVERNMENT, "FR", "Government services"),
    DataSource("https://www.insee.fr/", "INSEE", SourceCategory.STATISTICS, "FR", "Statistics", True),
    DataSource("https://www.data.gouv.fr/", "Data.gouv.fr", SourceCategory.STATISTICS, "FR", "Open data", True),
    DataSource("https://www.paris.fr/", "Paris Portal", SourceCategory.GOVERNMENT, "FR", "Capital city"),
    DataSource("https://www.lyon.fr/", "Lyon Portal", SourceCategory.GOVERNMENT, "FR", "Lyon city"),
    DataSource("https://www.marseille.fr/", "Marseille Portal", SourceCategory.GOVERNMENT, "FR", "Marseille city"),
]

FRANCE_UNIVERSITIES = [
    DataSource("https://www.sorbonne-universite.fr/", "Sorbonne University", SourceCategory.UNIVERSITY, "FR", "Historic university"),
    DataSource("https://www.universite-paris-saclay.fr/", "Paris-Saclay", SourceCategory.UNIVERSITY, "FR", "Research university"),
    DataSource("https://www.psl.eu/", "PSL University", SourceCategory.UNIVERSITY, "FR", "University cluster"),
    DataSource("https://www.ens.fr/", "ENS Paris", SourceCategory.UNIVERSITY, "FR", "Grande école"),
    DataSource("https://www.polytechnique.edu/", "École Polytechnique", SourceCategory.UNIVERSITY, "FR", "Engineering school"),
    DataSource("https://www.hec.edu/", "HEC Paris", SourceCategory.UNIVERSITY, "FR", "Business school"),
    DataSource("https://www.sciencespo.fr/", "Sciences Po", SourceCategory.UNIVERSITY, "FR", "Political science"),
    DataSource("https://www.universite-lyon.fr/", "University of Lyon", SourceCategory.UNIVERSITY, "FR", "University cluster"),
    DataSource("https://www.u-bordeaux.fr/", "University of Bordeaux", SourceCategory.UNIVERSITY, "FR", "Research university"),
    DataSource("https://www.univ-toulouse.fr/", "University of Toulouse", SourceCategory.UNIVERSITY, "FR", "University cluster"),
    DataSource("https://www.amu.fr/", "Aix-Marseille University", SourceCategory.UNIVERSITY, "FR", "Research university"),
    DataSource("https://www.centralesupelec.fr/", "CentraleSupélec", SourceCategory.UNIVERSITY, "FR", "Engineering school"),
    DataSource("https://www.cnrs.fr/", "CNRS", SourceCategory.RESEARCH, "FR", "National research", True),
    DataSource("https://www.inserm.fr/", "INSERM", SourceCategory.RESEARCH, "FR", "Medical research", True),
    DataSource("https://www.inria.fr/", "INRIA", SourceCategory.RESEARCH, "FR", "IT research", True),
    DataSource("https://www.cea.fr/", "CEA", SourceCategory.RESEARCH, "FR", "Atomic energy"),
    DataSource("https://www.pasteur.fr/", "Institut Pasteur", SourceCategory.RESEARCH, "FR", "Biomedical research"),
]

FRANCE_HOSPITALS = [
    DataSource("https://www.aphp.fr/", "AP-HP Paris Hospitals", SourceCategory.HOSPITAL, "FR", "Paris hospitals"),
    DataSource("https://www.chu-lyon.fr/", "Hospices Civils de Lyon", SourceCategory.HOSPITAL, "FR", "Lyon hospitals"),
    DataSource("https://www.ap-hm.fr/", "AP-HM Marseille", SourceCategory.HOSPITAL, "FR", "Marseille hospitals"),
    DataSource("https://www.chu-toulouse.fr/", "CHU Toulouse", SourceCategory.HOSPITAL, "FR", "Toulouse hospital"),
    DataSource("https://www.chu-bordeaux.fr/", "CHU Bordeaux", SourceCategory.HOSPITAL, "FR", "Bordeaux hospital"),
    DataSource("https://www.chu-lille.fr/", "CHU Lille", SourceCategory.HOSPITAL, "FR", "Lille hospital"),
    DataSource("https://www.chu-nantes.fr/", "CHU Nantes", SourceCategory.HOSPITAL, "FR", "Nantes hospital"),
    DataSource("https://www.gustave-roussy.fr/", "Gustave Roussy", SourceCategory.HOSPITAL, "FR", "Cancer center"),
    DataSource("https://www.institut-curie.org/", "Institut Curie", SourceCategory.HOSPITAL, "FR", "Cancer research"),
]

FRANCE_BANKS = [
    DataSource("https://www.banque-france.fr/", "Banque de France", SourceCategory.BANK, "FR", "Central bank", True),
    DataSource("https://www.bnpparibas.fr/", "BNP Paribas", SourceCategory.BANK, "FR", "Major bank"),
    DataSource("https://www.societegenerale.fr/", "Société Générale", SourceCategory.BANK, "FR", "Major bank"),
    DataSource("https://www.credit-agricole.fr/", "Crédit Agricole", SourceCategory.BANK, "FR", "Major bank"),
    DataSource("https://www.creditmutuel.fr/", "Crédit Mutuel", SourceCategory.BANK, "FR", "Cooperative bank"),
    DataSource("https://www.axa.fr/", "AXA", SourceCategory.BANK, "FR", "Insurance"),
    DataSource("https://www.euronext.com/", "Euronext Paris", SourceCategory.BANK, "FR", "Stock exchange", True),
    DataSource("https://www.amf-france.org/", "AMF", SourceCategory.BANK, "FR", "Financial markets authority"),
]

FRANCE_INDUSTRY = [
    DataSource("https://www.renault.fr/", "Renault", SourceCategory.INDUSTRY, "FR", "Automotive"),
    DataSource("https://www.peugeot.fr/", "Peugeot", SourceCategory.INDUSTRY, "FR", "Automotive"),
    DataSource("https://www.citroen.fr/", "Citroën", SourceCategory.INDUSTRY, "FR", "Automotive"),
    DataSource("https://www.airbus.com/", "Airbus", SourceCategory.INDUSTRY, "FR", "Aerospace"),
    DataSource("https://www.safran-group.com/", "Safran", SourceCategory.INDUSTRY, "FR", "Aerospace"),
    DataSource("https://www.thalesgroup.com/", "Thales", SourceCategory.INDUSTRY, "FR", "Defense/electronics"),
    DataSource("https://www.loreal.com/", "L'Oréal", SourceCategory.INDUSTRY, "FR", "Cosmetics"),
    DataSource("https://www.lvmh.com/", "LVMH", SourceCategory.INDUSTRY, "FR", "Luxury goods"),
    DataSource("https://www.total.com/", "TotalEnergies", SourceCategory.ENERGY, "FR", "Energy"),
    DataSource("https://www.engie.com/", "Engie", SourceCategory.ENERGY, "FR", "Utilities"),
    DataSource("https://www.edf.fr/", "EDF", SourceCategory.ENERGY, "FR", "Electricity"),
    DataSource("https://www.sncf.com/", "SNCF", SourceCategory.TRANSPORT, "FR", "Railways"),
    DataSource("https://www.airfrance.com/", "Air France", SourceCategory.TRANSPORT, "FR", "Airline"),
    DataSource("https://www.orange.fr/", "Orange", SourceCategory.TELECOM, "FR", "Telecom"),
]

FRANCE_NEWS = [
    DataSource("https://www.lemonde.fr/", "Le Monde", SourceCategory.NEWS, "FR", "Daily newspaper"),
    DataSource("https://www.lefigaro.fr/", "Le Figaro", SourceCategory.NEWS, "FR", "Daily newspaper"),
    DataSource("https://www.liberation.fr/", "Libération", SourceCategory.NEWS, "FR", "Daily newspaper"),
    DataSource("https://www.france24.com/", "France 24", SourceCategory.NEWS, "FR", "News channel"),
    DataSource("https://www.rfi.fr/", "RFI", SourceCategory.NEWS, "FR", "International radio"),
    DataSource("https://www.francetvinfo.fr/", "France TV Info", SourceCategory.NEWS, "FR", "Public TV news"),
    DataSource("https://www.bfmtv.com/", "BFM TV", SourceCategory.NEWS, "FR", "News channel"),
    DataSource("https://www.leparisien.fr/", "Le Parisien", SourceCategory.NEWS, "FR", "Daily newspaper"),
    DataSource("https://www.lesechos.fr/", "Les Echos", SourceCategory.NEWS, "FR", "Business news"),
    DataSource("https://www.afp.com/", "AFP", SourceCategory.NEWS, "FR", "News agency", True),
]

FRANCE_CULTURE = [
    DataSource("https://www.louvre.fr/", "Louvre Museum", SourceCategory.CULTURE, "FR", "Art museum"),
    DataSource("https://www.musee-orsay.fr/", "Musée d'Orsay", SourceCategory.CULTURE, "FR", "Impressionist art"),
    DataSource("https://www.centrepompidou.fr/", "Centre Pompidou", SourceCategory.CULTURE, "FR", "Modern art"),
    DataSource("https://www.chateauversailles.fr/", "Palace of Versailles", SourceCategory.CULTURE, "FR", "Historic palace"),
    DataSource("https://www.bnf.fr/", "Bibliothèque nationale de France", SourceCategory.CULTURE, "FR", "National library", True),
    DataSource("https://www.culture.gouv.fr/", "Ministry of Culture", SourceCategory.CULTURE, "FR", "Culture ministry"),
    DataSource("https://www.opera-paris.fr/", "Paris Opera", SourceCategory.CULTURE, "FR", "Opera house"),
    DataSource("https://www.quaibranly.fr/", "Quai Branly Museum", SourceCategory.CULTURE, "FR", "Indigenous arts"),
]

FRANCE_SPORT = [
    DataSource("https://www.fff.fr/", "French Football Federation", SourceCategory.SPORT, "FR", "Football"),
    DataSource("https://www.ligue1.fr/", "Ligue 1", SourceCategory.SPORT, "FR", "Football league", True),
    DataSource("https://www.psg.fr/", "Paris Saint-Germain", SourceCategory.SPORT, "FR", "Football club"),
    DataSource("https://www.asmonaco.com/", "AS Monaco", SourceCategory.SPORT, "FR", "Football club"),
    DataSource("https://www.ol.fr/", "Olympique Lyonnais", SourceCategory.SPORT, "FR", "Football club"),
    DataSource("https://www.om.fr/", "Olympique Marseille", SourceCategory.SPORT, "FR", "Football club"),
    DataSource("https://www.fft.fr/", "French Tennis Federation", SourceCategory.SPORT, "FR", "Tennis"),
    DataSource("https://www.rolandgarros.com/", "Roland Garros", SourceCategory.SPORT, "FR", "Tennis tournament", True),
    DataSource("https://www.letour.fr/", "Tour de France", SourceCategory.SPORT, "FR", "Cycling", True),
    DataSource("https://www.ffr.fr/", "French Rugby Federation", SourceCategory.SPORT, "FR", "Rugby"),
    DataSource("https://www.cnosf.org/", "French Olympic Committee", SourceCategory.SPORT, "FR", "Olympic committee"),
    DataSource("https://www.24h-lemans.com/", "24 Hours of Le Mans", SourceCategory.SPORT, "FR", "Motorsport"),
]

# ============================================================
# 🇬🇧 UNITED KINGDOM DATA SOURCES
# ============================================================

UK_GOVERNMENT = [
    DataSource("https://www.gov.uk/", "UK Government", SourceCategory.GOVERNMENT, "GB", "Government portal", True),
    DataSource("https://www.parliament.uk/", "UK Parliament", SourceCategory.GOVERNMENT, "GB", "Parliament"),
    DataSource("https://www.royal.uk/", "Royal Family", SourceCategory.GOVERNMENT, "GB", "Monarchy"),
    DataSource("https://www.ons.gov.uk/", "Office for National Statistics", SourceCategory.STATISTICS, "GB", "Statistics", True),
    DataSource("https://data.gov.uk/", "Data.gov.uk", SourceCategory.STATISTICS, "GB", "Open data", True),
    DataSource("https://www.london.gov.uk/", "London.gov.uk", SourceCategory.GOVERNMENT, "GB", "London government"),
    DataSource("https://www.manchester.gov.uk/", "Manchester Council", SourceCategory.GOVERNMENT, "GB", "Manchester city"),
    DataSource("https://www.birmingham.gov.uk/", "Birmingham Council", SourceCategory.GOVERNMENT, "GB", "Birmingham city"),
    DataSource("https://www.edinburgh.gov.uk/", "Edinburgh Council", SourceCategory.GOVERNMENT, "GB", "Edinburgh city"),
    DataSource("https://www.gov.scot/", "Scottish Government", SourceCategory.GOVERNMENT, "GB", "Scotland"),
    DataSource("https://www.gov.wales/", "Welsh Government", SourceCategory.GOVERNMENT, "GB", "Wales"),
]

UK_UNIVERSITIES = [
    DataSource("https://www.ox.ac.uk/", "University of Oxford", SourceCategory.UNIVERSITY, "GB", "Top university"),
    DataSource("https://www.cam.ac.uk/", "University of Cambridge", SourceCategory.UNIVERSITY, "GB", "Top university"),
    DataSource("https://www.imperial.ac.uk/", "Imperial College London", SourceCategory.UNIVERSITY, "GB", "Science/engineering"),
    DataSource("https://www.ucl.ac.uk/", "UCL", SourceCategory.UNIVERSITY, "GB", "London university"),
    DataSource("https://www.lse.ac.uk/", "LSE", SourceCategory.UNIVERSITY, "GB", "Social sciences"),
    DataSource("https://www.kcl.ac.uk/", "King's College London", SourceCategory.UNIVERSITY, "GB", "London university"),
    DataSource("https://www.ed.ac.uk/", "University of Edinburgh", SourceCategory.UNIVERSITY, "GB", "Scottish university"),
    DataSource("https://www.manchester.ac.uk/", "University of Manchester", SourceCategory.UNIVERSITY, "GB", "Russell Group"),
    DataSource("https://www.bristol.ac.uk/", "University of Bristol", SourceCategory.UNIVERSITY, "GB", "Research university"),
    DataSource("https://www.warwick.ac.uk/", "University of Warwick", SourceCategory.UNIVERSITY, "GB", "Research university"),
    DataSource("https://www.durham.ac.uk/", "Durham University", SourceCategory.UNIVERSITY, "GB", "Historic university"),
    DataSource("https://www.st-andrews.ac.uk/", "University of St Andrews", SourceCategory.UNIVERSITY, "GB", "Scottish university"),
    DataSource("https://www.gla.ac.uk/", "University of Glasgow", SourceCategory.UNIVERSITY, "GB", "Scottish university"),
    DataSource("https://www.birmingham.ac.uk/", "University of Birmingham", SourceCategory.UNIVERSITY, "GB", "Russell Group"),
    DataSource("https://www.leeds.ac.uk/", "University of Leeds", SourceCategory.UNIVERSITY, "GB", "Russell Group"),
    DataSource("https://www.ukri.org/", "UK Research and Innovation", SourceCategory.RESEARCH, "GB", "Research funding", True),
]

UK_HOSPITALS = [
    DataSource("https://www.nhs.uk/", "NHS", SourceCategory.HOSPITAL, "GB", "National health service", True),
    DataSource("https://www.guysandstthomas.nhs.uk/", "Guy's and St Thomas'", SourceCategory.HOSPITAL, "GB", "London hospital"),
    DataSource("https://www.uclh.nhs.uk/", "UCLH", SourceCategory.HOSPITAL, "GB", "University hospital"),
    DataSource("https://www.imperial.nhs.uk/", "Imperial Healthcare", SourceCategory.HOSPITAL, "GB", "London hospitals"),
    DataSource("https://www.royalmarsden.nhs.uk/", "Royal Marsden", SourceCategory.HOSPITAL, "GB", "Cancer hospital"),
    DataSource("https://www.gosh.nhs.uk/", "Great Ormond Street", SourceCategory.HOSPITAL, "GB", "Children's hospital"),
    DataSource("https://www.moorfields.nhs.uk/", "Moorfields Eye Hospital", SourceCategory.HOSPITAL, "GB", "Eye hospital"),
    DataSource("https://www.christie.nhs.uk/", "Christie Hospital", SourceCategory.HOSPITAL, "GB", "Cancer center"),
    DataSource("https://www.addenbrookes.nhs.uk/", "Addenbrooke's Hospital", SourceCategory.HOSPITAL, "GB", "Cambridge hospital"),
    DataSource("https://www.ouh.nhs.uk/", "Oxford University Hospitals", SourceCategory.HOSPITAL, "GB", "Oxford hospital"),
]

UK_BANKS = [
    DataSource("https://www.bankofengland.co.uk/", "Bank of England", SourceCategory.BANK, "GB", "Central bank", True),
    DataSource("https://www.hsbc.co.uk/", "HSBC UK", SourceCategory.BANK, "GB", "Major bank"),
    DataSource("https://www.barclays.co.uk/", "Barclays", SourceCategory.BANK, "GB", "Major bank"),
    DataSource("https://www.lloydsbank.com/", "Lloyds Bank", SourceCategory.BANK, "GB", "Major bank"),
    DataSource("https://www.natwest.com/", "NatWest", SourceCategory.BANK, "GB", "Major bank"),
    DataSource("https://www.rbs.com/", "Royal Bank of Scotland", SourceCategory.BANK, "GB", "Major bank"),
    DataSource("https://www.standardchartered.com/", "Standard Chartered", SourceCategory.BANK, "GB", "International bank"),
    DataSource("https://www.londonstockexchange.com/", "London Stock Exchange", SourceCategory.BANK, "GB", "Stock exchange", True),
    DataSource("https://www.fca.org.uk/", "FCA", SourceCategory.BANK, "GB", "Financial Conduct Authority"),
]

UK_INDUSTRY = [
    DataSource("https://www.bp.com/", "BP", SourceCategory.ENERGY, "GB", "Oil/gas"),
    DataSource("https://www.shell.co.uk/", "Shell UK", SourceCategory.ENERGY, "GB", "Oil/gas"),
    DataSource("https://www.gsk.com/", "GSK", SourceCategory.INDUSTRY, "GB", "Pharmaceuticals"),
    DataSource("https://www.astrazeneca.com/", "AstraZeneca", SourceCategory.INDUSTRY, "GB", "Pharmaceuticals"),
    DataSource("https://www.unilever.co.uk/", "Unilever UK", SourceCategory.INDUSTRY, "GB", "Consumer goods"),
    DataSource("https://www.rolls-royce.com/", "Rolls-Royce", SourceCategory.INDUSTRY, "GB", "Aerospace"),
    DataSource("https://www.bae-systems.com/", "BAE Systems", SourceCategory.INDUSTRY, "GB", "Defense"),
    DataSource("https://www.jaguarlandrover.com/", "Jaguar Land Rover", SourceCategory.INDUSTRY, "GB", "Automotive"),
    DataSource("https://www.bt.com/", "BT", SourceCategory.TELECOM, "GB", "Telecom"),
    DataSource("https://www.vodafone.co.uk/", "Vodafone UK", SourceCategory.TELECOM, "GB", "Telecom"),
    DataSource("https://www.britishairways.com/", "British Airways", SourceCategory.TRANSPORT, "GB", "Airline"),
    DataSource("https://www.nationalrail.co.uk/", "National Rail", SourceCategory.TRANSPORT, "GB", "Railways", True),
]

UK_NEWS = [
    DataSource("https://www.bbc.com/", "BBC", SourceCategory.NEWS, "GB", "Public broadcaster", True),
    DataSource("https://www.theguardian.com/", "The Guardian", SourceCategory.NEWS, "GB", "Newspaper"),
    DataSource("https://www.thetimes.co.uk/", "The Times", SourceCategory.NEWS, "GB", "Newspaper"),
    DataSource("https://www.telegraph.co.uk/", "The Telegraph", SourceCategory.NEWS, "GB", "Newspaper"),
    DataSource("https://www.ft.com/", "Financial Times", SourceCategory.NEWS, "GB", "Business news"),
    DataSource("https://www.economist.com/", "The Economist", SourceCategory.NEWS, "GB", "Weekly magazine"),
    DataSource("https://www.independent.co.uk/", "The Independent", SourceCategory.NEWS, "GB", "Online news"),
    DataSource("https://www.reuters.com/", "Reuters", SourceCategory.NEWS, "GB", "News agency", True),
    DataSource("https://www.sky.com/news/", "Sky News", SourceCategory.NEWS, "GB", "News channel"),
    DataSource("https://www.itv.com/news/", "ITV News", SourceCategory.NEWS, "GB", "TV news"),
]

UK_CULTURE = [
    DataSource("https://www.britishmuseum.org/", "British Museum", SourceCategory.CULTURE, "GB", "World museum"),
    DataSource("https://www.nationalgallery.org.uk/", "National Gallery", SourceCategory.CULTURE, "GB", "Art gallery"),
    DataSource("https://www.tate.org.uk/", "Tate", SourceCategory.CULTURE, "GB", "Art museums"),
    DataSource("https://www.vam.ac.uk/", "V&A Museum", SourceCategory.CULTURE, "GB", "Design museum"),
    DataSource("https://www.nhm.ac.uk/", "Natural History Museum", SourceCategory.CULTURE, "GB", "Natural history"),
    DataSource("https://www.sciencemuseum.org.uk/", "Science Museum", SourceCategory.CULTURE, "GB", "Science museum"),
    DataSource("https://www.bl.uk/", "British Library", SourceCategory.CULTURE, "GB", "National library", True),
    DataSource("https://www.roh.org.uk/", "Royal Opera House", SourceCategory.CULTURE, "GB", "Opera/ballet"),
    DataSource("https://www.nationaltheatre.org.uk/", "National Theatre", SourceCategory.CULTURE, "GB", "Theatre"),
    DataSource("https://www.shakespearesglobe.com/", "Shakespeare's Globe", SourceCategory.CULTURE, "GB", "Theatre"),
]

UK_SPORT = [
    DataSource("https://www.thefa.com/", "Football Association", SourceCategory.SPORT, "GB", "Football"),
    DataSource("https://www.premierleague.com/", "Premier League", SourceCategory.SPORT, "GB", "Football league", True),
    DataSource("https://www.mancity.com/", "Manchester City", SourceCategory.SPORT, "GB", "Football club"),
    DataSource("https://www.manutd.com/", "Manchester United", SourceCategory.SPORT, "GB", "Football club"),
    DataSource("https://www.liverpoolfc.com/", "Liverpool FC", SourceCategory.SPORT, "GB", "Football club"),
    DataSource("https://www.arsenal.com/", "Arsenal", SourceCategory.SPORT, "GB", "Football club"),
    DataSource("https://www.chelseafc.com/", "Chelsea FC", SourceCategory.SPORT, "GB", "Football club"),
    DataSource("https://www.tottenhamhotspur.com/", "Tottenham Hotspur", SourceCategory.SPORT, "GB", "Football club"),
    DataSource("https://www.englandrugby.com/", "England Rugby", SourceCategory.SPORT, "GB", "Rugby union"),
    DataSource("https://www.lta.org.uk/", "LTA Tennis", SourceCategory.SPORT, "GB", "Tennis"),
    DataSource("https://www.wimbledon.com/", "Wimbledon", SourceCategory.SPORT, "GB", "Tennis tournament", True),
    DataSource("https://www.ecb.co.uk/", "England Cricket Board", SourceCategory.SPORT, "GB", "Cricket"),
    DataSource("https://www.britishcycling.org.uk/", "British Cycling", SourceCategory.SPORT, "GB", "Cycling"),
    DataSource("https://www.thejockeyclub.co.uk/", "Jockey Club", SourceCategory.SPORT, "GB", "Horse racing"),
    DataSource("https://formula1.com/", "Formula 1", SourceCategory.SPORT, "GB", "Motorsport", True),
    DataSource("https://www.teamgb.com/", "Team GB", SourceCategory.SPORT, "GB", "Olympic team"),
]

# ============================================================
# 🇮🇹 ITALY DATA SOURCES
# ============================================================

ITALY_GOVERNMENT = [
    DataSource("https://www.governo.it/", "Italian Government", SourceCategory.GOVERNMENT, "IT", "Government portal"),
    DataSource("https://www.camera.it/", "Chamber of Deputies", SourceCategory.GOVERNMENT, "IT", "Lower house"),
    DataSource("https://www.senato.it/", "Senate", SourceCategory.GOVERNMENT, "IT", "Upper house"),
    DataSource("https://www.istat.it/", "ISTAT", SourceCategory.STATISTICS, "IT", "National statistics", True),
    DataSource("https://www.dati.gov.it/", "Dati.gov.it", SourceCategory.STATISTICS, "IT", "Open data", True),
    DataSource("https://www.comune.roma.it/", "Rome Portal", SourceCategory.GOVERNMENT, "IT", "Capital city"),
    DataSource("https://www.comune.milano.it/", "Milan Portal", SourceCategory.GOVERNMENT, "IT", "Milan city"),
    DataSource("https://www.comune.firenze.it/", "Florence Portal", SourceCategory.GOVERNMENT, "IT", "Florence city"),
    DataSource("https://www.comune.venezia.it/", "Venice Portal", SourceCategory.GOVERNMENT, "IT", "Venice city"),
]

ITALY_UNIVERSITIES = [
    DataSource("https://www.unimi.it/", "University of Milan", SourceCategory.UNIVERSITY, "IT", "Major university"),
    DataSource("https://www.polimi.it/", "Politecnico di Milano", SourceCategory.UNIVERSITY, "IT", "Technical university"),
    DataSource("https://www.unibo.it/", "University of Bologna", SourceCategory.UNIVERSITY, "IT", "Oldest university"),
    DataSource("https://www.unipd.it/", "University of Padua", SourceCategory.UNIVERSITY, "IT", "Historic university"),
    DataSource("https://www.uniroma1.it/", "Sapienza University", SourceCategory.UNIVERSITY, "IT", "Rome university"),
    DataSource("https://www.unifi.it/", "University of Florence", SourceCategory.UNIVERSITY, "IT", "Florence university"),
    DataSource("https://www.unito.it/", "University of Turin", SourceCategory.UNIVERSITY, "IT", "Turin university"),
    DataSource("https://www.unina.it/", "University of Naples", SourceCategory.UNIVERSITY, "IT", "Naples university"),
    DataSource("https://www.sissa.it/", "SISSA Trieste", SourceCategory.RESEARCH, "IT", "Advanced studies"),
    DataSource("https://www.sns.it/", "Scuola Normale Superiore", SourceCategory.UNIVERSITY, "IT", "Elite institution"),
    DataSource("https://www.unibocconi.it/", "Bocconi University", SourceCategory.UNIVERSITY, "IT", "Business school"),
    DataSource("https://www.cnr.it/", "CNR Italy", SourceCategory.RESEARCH, "IT", "National research", True),
    DataSource("https://www.infn.it/", "INFN", SourceCategory.RESEARCH, "IT", "Nuclear physics", True),
]

ITALY_BANKS = [
    DataSource("https://www.bancaditalia.it/", "Bank of Italy", SourceCategory.BANK, "IT", "Central bank", True),
    DataSource("https://www.unicredit.it/", "UniCredit", SourceCategory.BANK, "IT", "Major bank"),
    DataSource("https://www.intesasanpaolo.com/", "Intesa Sanpaolo", SourceCategory.BANK, "IT", "Major bank"),
    DataSource("https://www.mps.it/", "Monte dei Paschi", SourceCategory.BANK, "IT", "Historic bank"),
    DataSource("https://www.ubibanca.it/", "UBI Banca", SourceCategory.BANK, "IT", "Major bank"),
    DataSource("https://www.borsaitaliana.it/", "Borsa Italiana", SourceCategory.BANK, "IT", "Stock exchange", True),
    DataSource("https://www.consob.it/", "CONSOB", SourceCategory.BANK, "IT", "Securities regulator"),
]

ITALY_INDUSTRY = [
    DataSource("https://www.ferrari.com/", "Ferrari", SourceCategory.INDUSTRY, "IT", "Automotive luxury"),
    DataSource("https://www.lamborghini.com/", "Lamborghini", SourceCategory.INDUSTRY, "IT", "Sports cars"),
    DataSource("https://www.fiat.it/", "Fiat", SourceCategory.INDUSTRY, "IT", "Automotive"),
    DataSource("https://www.alfaomeo.it/", "Alfa Romeo", SourceCategory.INDUSTRY, "IT", "Automotive"),
    DataSource("https://www.maserati.com/", "Maserati", SourceCategory.INDUSTRY, "IT", "Luxury cars"),
    DataSource("https://www.eni.com/", "Eni", SourceCategory.ENERGY, "IT", "Energy company"),
    DataSource("https://www.enel.com/", "Enel", SourceCategory.ENERGY, "IT", "Electric utility"),
    DataSource("https://www.generali.com/", "Generali", SourceCategory.INDUSTRY, "IT", "Insurance"),
    DataSource("https://www.prada.com/", "Prada", SourceCategory.INDUSTRY, "IT", "Fashion"),
    DataSource("https://www.gucci.com/", "Gucci", SourceCategory.INDUSTRY, "IT", "Fashion"),
    DataSource("https://www.armani.com/", "Armani", SourceCategory.INDUSTRY, "IT", "Fashion"),
    DataSource("https://www.alitalia.com/", "ITA Airways", SourceCategory.TRANSPORT, "IT", "Airline"),
    DataSource("https://www.trenitalia.com/", "Trenitalia", SourceCategory.TRANSPORT, "IT", "Railways", True),
    DataSource("https://www.tim.it/", "TIM", SourceCategory.TELECOM, "IT", "Telecom"),
]

ITALY_NEWS = [
    DataSource("https://www.corriere.it/", "Corriere della Sera", SourceCategory.NEWS, "IT", "Daily newspaper"),
    DataSource("https://www.repubblica.it/", "La Repubblica", SourceCategory.NEWS, "IT", "Daily newspaper"),
    DataSource("https://www.lastampa.it/", "La Stampa", SourceCategory.NEWS, "IT", "Daily newspaper"),
    DataSource("https://www.ilsole24ore.com/", "Il Sole 24 Ore", SourceCategory.NEWS, "IT", "Business news"),
    DataSource("https://www.ansa.it/", "ANSA", SourceCategory.NEWS, "IT", "News agency", True),
    DataSource("https://www.rainews.it/", "Rai News", SourceCategory.NEWS, "IT", "Public broadcaster"),
    DataSource("https://tg.la7.it/", "La7", SourceCategory.NEWS, "IT", "TV channel"),
    DataSource("https://www.gazzetta.it/", "Gazzetta dello Sport", SourceCategory.NEWS, "IT", "Sports news"),
]

ITALY_CULTURE = [
    DataSource("https://www.uffizi.it/", "Uffizi Gallery", SourceCategory.CULTURE, "IT", "Art museum"),
    DataSource("https://www.museivaticani.va/", "Vatican Museums", SourceCategory.CULTURE, "IT", "Vatican museums"),
    DataSource("https://www.gallerieaccademia.it/", "Galleria dell'Accademia", SourceCategory.CULTURE, "IT", "Florence art"),
    DataSource("https://www.colosseo.it/", "Colosseum", SourceCategory.CULTURE, "IT", "Roman amphitheater"),
    DataSource("https://www.museonazionaleromano.beniculturali.it/", "National Roman Museum", SourceCategory.CULTURE, "IT", "Roman art"),
    DataSource("https://www.teatroallascala.org/", "La Scala", SourceCategory.CULTURE, "IT", "Opera house"),
    DataSource("https://www.palazzopitti.it/", "Palazzo Pitti", SourceCategory.CULTURE, "IT", "Florence palace"),
    DataSource("https://www.pompeisites.org/", "Pompeii", SourceCategory.CULTURE, "IT", "Archaeological site"),
]

ITALY_SPORT = [
    DataSource("https://www.figc.it/", "FIGC", SourceCategory.SPORT, "IT", "Football federation"),
    DataSource("https://www.legaseriea.it/", "Serie A", SourceCategory.SPORT, "IT", "Football league", True),
    DataSource("https://www.juventus.com/", "Juventus", SourceCategory.SPORT, "IT", "Football club"),
    DataSource("https://www.acmilan.com/", "AC Milan", SourceCategory.SPORT, "IT", "Football club"),
    DataSource("https://www.inter.it/", "Inter Milan", SourceCategory.SPORT, "IT", "Football club"),
    DataSource("https://www.asroma.com/", "AS Roma", SourceCategory.SPORT, "IT", "Football club"),
    DataSource("https://www.sslazio.it/", "SS Lazio", SourceCategory.SPORT, "IT", "Football club"),
    DataSource("https://www.sscnapoli.it/", "SSC Napoli", SourceCategory.SPORT, "IT", "Football club"),
    DataSource("https://www.giroditalia.it/", "Giro d'Italia", SourceCategory.SPORT, "IT", "Cycling race", True),
    DataSource("https://www.coni.it/", "CONI", SourceCategory.SPORT, "IT", "Olympic committee"),
    DataSource("https://www.fisi.org/", "FISI", SourceCategory.SPORT, "IT", "Winter sports"),
]

# ============================================================
# 🇪🇸 SPAIN DATA SOURCES
# ============================================================

SPAIN_GOVERNMENT = [
    DataSource("https://www.lamoncloa.gob.es/", "Spanish Government", SourceCategory.GOVERNMENT, "ES", "Government portal"),
    DataSource("https://www.congreso.es/", "Congress of Deputies", SourceCategory.GOVERNMENT, "ES", "Lower house"),
    DataSource("https://www.senado.es/", "Senate", SourceCategory.GOVERNMENT, "ES", "Upper house"),
    DataSource("https://www.ine.es/", "INE Spain", SourceCategory.STATISTICS, "ES", "National statistics", True),
    DataSource("https://datos.gob.es/", "Datos.gob.es", SourceCategory.STATISTICS, "ES", "Open data", True),
    DataSource("https://www.madrid.es/", "Madrid Portal", SourceCategory.GOVERNMENT, "ES", "Capital city"),
    DataSource("https://www.barcelona.cat/", "Barcelona Portal", SourceCategory.GOVERNMENT, "ES", "Barcelona city"),
    DataSource("https://www.sevilla.org/", "Seville Portal", SourceCategory.GOVERNMENT, "ES", "Seville city"),
    DataSource("https://www.valencia.es/", "Valencia Portal", SourceCategory.GOVERNMENT, "ES", "Valencia city"),
]

SPAIN_UNIVERSITIES = [
    DataSource("https://www.ub.edu/", "University of Barcelona", SourceCategory.UNIVERSITY, "ES", "Barcelona university"),
    DataSource("https://www.uam.es/", "Universidad Autónoma Madrid", SourceCategory.UNIVERSITY, "ES", "Madrid university"),
    DataSource("https://www.ucm.es/", "Complutense University", SourceCategory.UNIVERSITY, "ES", "Madrid university"),
    DataSource("https://www.uab.cat/", "Universidad Autónoma Barcelona", SourceCategory.UNIVERSITY, "ES", "Autonomous Barcelona"),
    DataSource("https://www.upf.edu/", "Pompeu Fabra University", SourceCategory.UNIVERSITY, "ES", "Barcelona university"),
    DataSource("https://www.upc.edu/", "UPC Barcelona", SourceCategory.UNIVERSITY, "ES", "Technical university"),
    DataSource("https://www.upm.es/", "UPM Madrid", SourceCategory.UNIVERSITY, "ES", "Technical university"),
    DataSource("https://www.uv.es/", "University of Valencia", SourceCategory.UNIVERSITY, "ES", "Valencia university"),
    DataSource("https://www.us.es/", "University of Seville", SourceCategory.UNIVERSITY, "ES", "Seville university"),
    DataSource("https://www.ugr.es/", "University of Granada", SourceCategory.UNIVERSITY, "ES", "Granada university"),
    DataSource("https://www.csic.es/", "CSIC", SourceCategory.RESEARCH, "ES", "Scientific research", True),
    DataSource("https://www.iese.edu/", "IESE Business School", SourceCategory.UNIVERSITY, "ES", "Business school"),
    DataSource("https://www.ie.edu/", "IE University", SourceCategory.UNIVERSITY, "ES", "Business school"),
]

SPAIN_BANKS = [
    DataSource("https://www.bde.es/", "Bank of Spain", SourceCategory.BANK, "ES", "Central bank", True),
    DataSource("https://www.santander.com/", "Santander", SourceCategory.BANK, "ES", "Major bank"),
    DataSource("https://www.bbva.es/", "BBVA", SourceCategory.BANK, "ES", "Major bank"),
    DataSource("https://www.caixabank.es/", "CaixaBank", SourceCategory.BANK, "ES", "Major bank"),
    DataSource("https://www.bankia.es/", "Bankia", SourceCategory.BANK, "ES", "Major bank"),
    DataSource("https://www.bolsamadrid.es/", "Madrid Stock Exchange", SourceCategory.BANK, "ES", "Stock exchange", True),
    DataSource("https://www.cnmv.es/", "CNMV", SourceCategory.BANK, "ES", "Securities regulator"),
]

SPAIN_INDUSTRY = [
    DataSource("https://www.inditex.com/", "Inditex", SourceCategory.INDUSTRY, "ES", "Zara parent company"),
    DataSource("https://www.zara.com/", "Zara", SourceCategory.INDUSTRY, "ES", "Fashion retail"),
    DataSource("https://www.seat.es/", "SEAT", SourceCategory.INDUSTRY, "ES", "Automotive"),
    DataSource("https://www.repsol.com/", "Repsol", SourceCategory.ENERGY, "ES", "Energy company"),
    DataSource("https://www.iberdrola.com/", "Iberdrola", SourceCategory.ENERGY, "ES", "Electric utility"),
    DataSource("https://www.endesa.com/", "Endesa", SourceCategory.ENERGY, "ES", "Electric utility"),
    DataSource("https://www.telefonica.com/", "Telefónica", SourceCategory.TELECOM, "ES", "Telecom"),
    DataSource("https://www.iberia.com/", "Iberia", SourceCategory.TRANSPORT, "ES", "Airline"),
    DataSource("https://www.renfe.com/", "Renfe", SourceCategory.TRANSPORT, "ES", "Railways", True),
    DataSource("https://www.ferrovial.com/", "Ferrovial", SourceCategory.INDUSTRY, "ES", "Infrastructure"),
]

SPAIN_NEWS = [
    DataSource("https://elpais.com/", "El País", SourceCategory.NEWS, "ES", "Daily newspaper"),
    DataSource("https://www.elmundo.es/", "El Mundo", SourceCategory.NEWS, "ES", "Daily newspaper"),
    DataSource("https://www.abc.es/", "ABC", SourceCategory.NEWS, "ES", "Daily newspaper"),
    DataSource("https://www.lavanguardia.com/", "La Vanguardia", SourceCategory.NEWS, "ES", "Catalan newspaper"),
    DataSource("https://www.rtve.es/", "RTVE", SourceCategory.NEWS, "ES", "Public broadcaster"),
    DataSource("https://www.efe.com/", "EFE", SourceCategory.NEWS, "ES", "News agency", True),
    DataSource("https://www.expansion.com/", "Expansión", SourceCategory.NEWS, "ES", "Business news"),
    DataSource("https://www.marca.com/", "Marca", SourceCategory.NEWS, "ES", "Sports news"),
    DataSource("https://as.com/", "AS", SourceCategory.NEWS, "ES", "Sports news"),
]

SPAIN_CULTURE = [
    DataSource("https://www.museodelprado.es/", "Museo del Prado", SourceCategory.CULTURE, "ES", "Art museum"),
    DataSource("https://www.museoreinasofia.es/", "Reina Sofía Museum", SourceCategory.CULTURE, "ES", "Modern art"),
    DataSource("https://www.museothyssen.org/", "Thyssen-Bornemisza", SourceCategory.CULTURE, "ES", "Art museum"),
    DataSource("https://www.alhambra-patronato.es/", "Alhambra", SourceCategory.CULTURE, "ES", "Moorish palace"),
    DataSource("https://www.sagradafamilia.org/", "Sagrada Familia", SourceCategory.CULTURE, "ES", "Gaudí basilica"),
    DataSource("https://www.bne.es/", "National Library of Spain", SourceCategory.CULTURE, "ES", "National library"),
    DataSource("https://www.teatroreal.es/", "Teatro Real", SourceCategory.CULTURE, "ES", "Opera house"),
    DataSource("https://www.patrimonionacional.es/", "Patrimonio Nacional", SourceCategory.CULTURE, "ES", "Royal heritage"),
]

SPAIN_SPORT = [
    DataSource("https://www.rfef.es/", "RFEF", SourceCategory.SPORT, "ES", "Football federation"),
    DataSource("https://www.laliga.com/", "La Liga", SourceCategory.SPORT, "ES", "Football league", True),
    DataSource("https://www.realmadrid.com/", "Real Madrid", SourceCategory.SPORT, "ES", "Football club"),
    DataSource("https://www.fcbarcelona.com/", "FC Barcelona", SourceCategory.SPORT, "ES", "Football club"),
    DataSource("https://www.atleticodemadrid.com/", "Atlético Madrid", SourceCategory.SPORT, "ES", "Football club"),
    DataSource("https://www.sevillafc.es/", "Sevilla FC", SourceCategory.SPORT, "ES", "Football club"),
    DataSource("https://www.valenciacf.com/", "Valencia CF", SourceCategory.SPORT, "ES", "Football club"),
    DataSource("https://www.acb.com/", "ACB Basketball", SourceCategory.SPORT, "ES", "Basketball league", True),
    DataSource("https://www.lavuelta.es/", "La Vuelta", SourceCategory.SPORT, "ES", "Cycling race", True),
    DataSource("https://www.motogp.com/", "MotoGP", SourceCategory.SPORT, "ES", "Motorcycle racing", True),
    DataSource("https://www.coe.es/", "COE Spain", SourceCategory.SPORT, "ES", "Olympic committee"),
    DataSource("https://www.rfet.es/", "RFET Tennis", SourceCategory.SPORT, "ES", "Tennis federation"),
]

# ============================================================
# 🇳🇱 NETHERLANDS DATA SOURCES
# ============================================================

NETHERLANDS_SOURCES = [
    DataSource("https://www.rijksoverheid.nl/", "Dutch Government", SourceCategory.GOVERNMENT, "NL", "Government portal"),
    DataSource("https://www.tweedekamer.nl/", "House of Representatives", SourceCategory.GOVERNMENT, "NL", "Parliament"),
    DataSource("https://www.cbs.nl/", "CBS Statistics", SourceCategory.STATISTICS, "NL", "National statistics", True),
    DataSource("https://data.overheid.nl/", "Open Data NL", SourceCategory.STATISTICS, "NL", "Open data", True),
    DataSource("https://www.amsterdam.nl/", "Amsterdam Portal", SourceCategory.GOVERNMENT, "NL", "Capital city"),
    DataSource("https://www.uu.nl/", "Utrecht University", SourceCategory.UNIVERSITY, "NL", "Research university"),
    DataSource("https://www.uva.nl/", "University of Amsterdam", SourceCategory.UNIVERSITY, "NL", "Amsterdam university"),
    DataSource("https://www.tudelft.nl/", "TU Delft", SourceCategory.UNIVERSITY, "NL", "Technical university"),
    DataSource("https://www.leiden.edu/", "Leiden University", SourceCategory.UNIVERSITY, "NL", "Oldest university"),
    DataSource("https://www.eur.nl/", "Erasmus University", SourceCategory.UNIVERSITY, "NL", "Rotterdam university"),
    DataSource("https://www.tue.nl/", "TU Eindhoven", SourceCategory.UNIVERSITY, "NL", "Technical university"),
    DataSource("https://www.wur.nl/", "Wageningen University", SourceCategory.UNIVERSITY, "NL", "Agriculture"),
    DataSource("https://www.rug.nl/", "University of Groningen", SourceCategory.UNIVERSITY, "NL", "Research university"),
    DataSource("https://www.dnb.nl/", "Dutch Central Bank", SourceCategory.BANK, "NL", "Central bank", True),
    DataSource("https://www.ing.nl/", "ING", SourceCategory.BANK, "NL", "Major bank"),
    DataSource("https://www.abnamro.nl/", "ABN AMRO", SourceCategory.BANK, "NL", "Major bank"),
    DataSource("https://www.rabobank.nl/", "Rabobank", SourceCategory.BANK, "NL", "Cooperative bank"),
    DataSource("https://www.euronext.com/en/markets/amsterdam", "Euronext Amsterdam", SourceCategory.BANK, "NL", "Stock exchange", True),
    DataSource("https://www.shell.nl/", "Shell Netherlands", SourceCategory.ENERGY, "NL", "Energy"),
    DataSource("https://www.philips.nl/", "Philips", SourceCategory.INDUSTRY, "NL", "Electronics"),
    DataSource("https://www.asml.com/", "ASML", SourceCategory.INDUSTRY, "NL", "Semiconductors"),
    DataSource("https://www.heineken.nl/", "Heineken", SourceCategory.INDUSTRY, "NL", "Beverages"),
    DataSource("https://www.unilever.nl/", "Unilever NL", SourceCategory.INDUSTRY, "NL", "Consumer goods"),
    DataSource("https://www.klm.nl/", "KLM", SourceCategory.TRANSPORT, "NL", "Airline"),
    DataSource("https://www.ns.nl/", "NS Railways", SourceCategory.TRANSPORT, "NL", "Railways", True),
    DataSource("https://www.schiphol.nl/", "Schiphol Airport", SourceCategory.TRANSPORT, "NL", "Airport", True),
    DataSource("https://nos.nl/", "NOS", SourceCategory.NEWS, "NL", "Public broadcaster"),
    DataSource("https://www.volkskrant.nl/", "De Volkskrant", SourceCategory.NEWS, "NL", "Daily newspaper"),
    DataSource("https://www.nrc.nl/", "NRC", SourceCategory.NEWS, "NL", "Daily newspaper"),
    DataSource("https://www.rijksmuseum.nl/", "Rijksmuseum", SourceCategory.CULTURE, "NL", "National museum"),
    DataSource("https://www.vangoghmuseum.nl/", "Van Gogh Museum", SourceCategory.CULTURE, "NL", "Art museum"),
    DataSource("https://www.mauritshuis.nl/", "Mauritshuis", SourceCategory.CULTURE, "NL", "Art gallery"),
    DataSource("https://www.annefrank.org/", "Anne Frank House", SourceCategory.CULTURE, "NL", "Historic site"),
    DataSource("https://www.knvb.nl/", "KNVB", SourceCategory.SPORT, "NL", "Football federation"),
    DataSource("https://www.eredivisie.nl/", "Eredivisie", SourceCategory.SPORT, "NL", "Football league", True),
    DataSource("https://www.ajax.nl/", "Ajax", SourceCategory.SPORT, "NL", "Football club"),
    DataSource("https://www.psv.nl/", "PSV Eindhoven", SourceCategory.SPORT, "NL", "Football club"),
    DataSource("https://www.feyenoord.nl/", "Feyenoord", SourceCategory.SPORT, "NL", "Football club"),
    DataSource("https://www.nocnsf.nl/", "NOC*NSF", SourceCategory.SPORT, "NL", "Olympic committee"),
    DataSource("https://www.knwu.nl/", "KNWU Cycling", SourceCategory.SPORT, "NL", "Cycling federation"),
]

# ============================================================
# 🇨🇭 SWITZERLAND DATA SOURCES
# ============================================================

SWITZERLAND_SOURCES = [
    DataSource("https://www.admin.ch/", "Swiss Government", SourceCategory.GOVERNMENT, "CH", "Federal government"),
    DataSource("https://www.parlament.ch/", "Swiss Parliament", SourceCategory.GOVERNMENT, "CH", "Parliament"),
    DataSource("https://www.bfs.admin.ch/", "Federal Statistics Office", SourceCategory.STATISTICS, "CH", "Statistics", True),
    DataSource("https://opendata.swiss/", "OpenData Swiss", SourceCategory.STATISTICS, "CH", "Open data", True),
    DataSource("https://www.bern.ch/", "Bern Portal", SourceCategory.GOVERNMENT, "CH", "Capital city"),
    DataSource("https://www.stadt-zuerich.ch/", "Zurich Portal", SourceCategory.GOVERNMENT, "CH", "Zurich city"),
    DataSource("https://www.geneve.ch/", "Geneva Portal", SourceCategory.GOVERNMENT, "CH", "Geneva city"),
    DataSource("https://www.ethz.ch/", "ETH Zurich", SourceCategory.UNIVERSITY, "CH", "Top tech university"),
    DataSource("https://www.epfl.ch/", "EPFL", SourceCategory.UNIVERSITY, "CH", "Tech university"),
    DataSource("https://www.uzh.ch/", "University of Zurich", SourceCategory.UNIVERSITY, "CH", "Largest university"),
    DataSource("https://www.unibas.ch/", "University of Basel", SourceCategory.UNIVERSITY, "CH", "Basel university"),
    DataSource("https://www.unige.ch/", "University of Geneva", SourceCategory.UNIVERSITY, "CH", "Geneva university"),
    DataSource("https://www.unil.ch/", "University of Lausanne", SourceCategory.UNIVERSITY, "CH", "Lausanne university"),
    DataSource("https://home.cern/", "CERN", SourceCategory.RESEARCH, "CH", "Particle physics", True),
    DataSource("https://www.snb.ch/", "Swiss National Bank", SourceCategory.BANK, "CH", "Central bank", True),
    DataSource("https://www.ubs.com/", "UBS", SourceCategory.BANK, "CH", "Major bank"),
    DataSource("https://www.credit-suisse.com/", "Credit Suisse", SourceCategory.BANK, "CH", "Major bank"),
    DataSource("https://www.six-group.com/", "SIX Swiss Exchange", SourceCategory.BANK, "CH", "Stock exchange", True),
    DataSource("https://www.nestle.ch/", "Nestlé", SourceCategory.INDUSTRY, "CH", "Food/beverage"),
    DataSource("https://www.novartis.ch/", "Novartis", SourceCategory.INDUSTRY, "CH", "Pharmaceuticals"),
    DataSource("https://www.roche.ch/", "Roche", SourceCategory.INDUSTRY, "CH", "Pharmaceuticals"),
    DataSource("https://www.abb.ch/", "ABB", SourceCategory.INDUSTRY, "CH", "Engineering"),
    DataSource("https://www.swisscom.ch/", "Swisscom", SourceCategory.TELECOM, "CH", "Telecom"),
    DataSource("https://www.swiss.com/", "Swiss Air", SourceCategory.TRANSPORT, "CH", "Airline"),
    DataSource("https://www.sbb.ch/", "SBB Railways", SourceCategory.TRANSPORT, "CH", "Railways", True),
    DataSource("https://www.srf.ch/", "SRF", SourceCategory.NEWS, "CH", "German public broadcaster"),
    DataSource("https://www.rts.ch/", "RTS", SourceCategory.NEWS, "CH", "French public broadcaster"),
    DataSource("https://www.nzz.ch/", "NZZ", SourceCategory.NEWS, "CH", "Daily newspaper"),
    DataSource("https://www.swissinfo.ch/", "Swissinfo", SourceCategory.NEWS, "CH", "International news"),
    DataSource("https://www.nationalmuseum.ch/", "Swiss National Museum", SourceCategory.CULTURE, "CH", "National museum"),
    DataSource("https://www.kunsthaus.ch/", "Kunsthaus Zurich", SourceCategory.CULTURE, "CH", "Art museum"),
    DataSource("https://www.myswitzerland.com/", "MySwitzerland", SourceCategory.TOURISM, "CH", "Tourism", True),
    DataSource("https://www.swiss-ski.ch/", "Swiss Ski", SourceCategory.SPORT, "CH", "Skiing"),
    DataSource("https://www.football.ch/", "Swiss Football", SourceCategory.SPORT, "CH", "Football federation"),
    DataSource("https://www.swiss-cycling.ch/", "Swiss Cycling", SourceCategory.SPORT, "CH", "Cycling"),
]

# ============================================================
# 🇦🇹 AUSTRIA DATA SOURCES
# ============================================================

AUSTRIA_SOURCES = [
    DataSource("https://www.austria.gv.at/", "Austrian Government", SourceCategory.GOVERNMENT, "AT", "Government portal"),
    DataSource("https://www.parlament.gv.at/", "Austrian Parliament", SourceCategory.GOVERNMENT, "AT", "Parliament"),
    DataSource("https://www.statistik.at/", "Statistics Austria", SourceCategory.STATISTICS, "AT", "National statistics", True),
    DataSource("https://www.data.gv.at/", "Open Data Austria", SourceCategory.STATISTICS, "AT", "Open data", True),
    DataSource("https://www.wien.gv.at/", "Vienna Portal", SourceCategory.GOVERNMENT, "AT", "Capital city"),
    DataSource("https://www.univie.ac.at/", "University of Vienna", SourceCategory.UNIVERSITY, "AT", "Vienna university"),
    DataSource("https://www.tuwien.at/", "TU Vienna", SourceCategory.UNIVERSITY, "AT", "Technical university"),
    DataSource("https://www.plus.ac.at/", "University of Salzburg", SourceCategory.UNIVERSITY, "AT", "Salzburg university"),
    DataSource("https://www.uibk.ac.at/", "University of Innsbruck", SourceCategory.UNIVERSITY, "AT", "Innsbruck university"),
    DataSource("https://www.tugraz.at/", "TU Graz", SourceCategory.UNIVERSITY, "AT", "Technical university"),
    DataSource("https://www.oenb.at/", "Austrian National Bank", SourceCategory.BANK, "AT", "Central bank", True),
    DataSource("https://www.erstegroup.com/", "Erste Group", SourceCategory.BANK, "AT", "Major bank"),
    DataSource("https://www.raiffeisen.at/", "Raiffeisen Bank", SourceCategory.BANK, "AT", "Major bank"),
    DataSource("https://www.wienerborse.at/", "Vienna Stock Exchange", SourceCategory.BANK, "AT", "Stock exchange", True),
    DataSource("https://www.omv.at/", "OMV", SourceCategory.ENERGY, "AT", "Energy company"),
    DataSource("https://www.voestalpine.com/", "Voestalpine", SourceCategory.INDUSTRY, "AT", "Steel/metals"),
    DataSource("https://www.redbull.com/", "Red Bull", SourceCategory.INDUSTRY, "AT", "Beverages/media"),
    DataSource("https://www.swarovski.com/", "Swarovski", SourceCategory.INDUSTRY, "AT", "Crystal/jewelry"),
    DataSource("https://www.austrian.com/", "Austrian Airlines", SourceCategory.TRANSPORT, "AT", "Airline"),
    DataSource("https://www.oebb.at/", "ÖBB Railways", SourceCategory.TRANSPORT, "AT", "Railways", True),
    DataSource("https://orf.at/", "ORF", SourceCategory.NEWS, "AT", "Public broadcaster"),
    DataSource("https://www.derstandard.at/", "Der Standard", SourceCategory.NEWS, "AT", "Daily newspaper"),
    DataSource("https://www.diepresse.com/", "Die Presse", SourceCategory.NEWS, "AT", "Daily newspaper"),
    DataSource("https://www.khm.at/", "Kunsthistorisches Museum", SourceCategory.CULTURE, "AT", "Art museum"),
    DataSource("https://www.staatsoper.at/", "Vienna State Opera", SourceCategory.CULTURE, "AT", "Opera house"),
    DataSource("https://www.schoenbrunn.at/", "Schönbrunn Palace", SourceCategory.CULTURE, "AT", "Imperial palace"),
    DataSource("https://www.salzburg.info/", "Salzburg Tourism", SourceCategory.TOURISM, "AT", "Tourism"),
    DataSource("https://www.austria.info/", "Austria Tourism", SourceCategory.TOURISM, "AT", "National tourism", True),
    DataSource("https://www.oefb.at/", "ÖFB", SourceCategory.SPORT, "AT", "Football federation"),
    DataSource("https://www.oesv.at/", "ÖSV", SourceCategory.SPORT, "AT", "Skiing federation"),
    DataSource("https://www.redbullsalzburg.at/", "Red Bull Salzburg", SourceCategory.SPORT, "AT", "Football club"),
]

# ============================================================
# 🇧🇪 BELGIUM DATA SOURCES
# ============================================================

BELGIUM_SOURCES = [
    DataSource("https://www.belgium.be/", "Belgian Government", SourceCategory.GOVERNMENT, "BE", "Federal government"),
    DataSource("https://www.dekamer.be/", "Belgian Parliament", SourceCategory.GOVERNMENT, "BE", "Parliament"),
    DataSource("https://statbel.fgov.be/", "Statbel", SourceCategory.STATISTICS, "BE", "National statistics", True),
    DataSource("https://data.gov.be/", "Open Data Belgium", SourceCategory.STATISTICS, "BE", "Open data", True),
    DataSource("https://www.brussels.be/", "Brussels Portal", SourceCategory.GOVERNMENT, "BE", "Capital city"),
    DataSource("https://www.kuleuven.be/", "KU Leuven", SourceCategory.UNIVERSITY, "BE", "Top university"),
    DataSource("https://www.ugent.be/", "Ghent University", SourceCategory.UNIVERSITY, "BE", "Ghent university"),
    DataSource("https://www.uclouvain.be/", "UCLouvain", SourceCategory.UNIVERSITY, "BE", "French university"),
    DataSource("https://www.ulb.be/", "ULB Brussels", SourceCategory.UNIVERSITY, "BE", "Brussels university"),
    DataSource("https://www.vub.be/", "VUB Brussels", SourceCategory.UNIVERSITY, "BE", "Dutch Brussels university"),
    DataSource("https://www.nbb.be/", "National Bank of Belgium", SourceCategory.BANK, "BE", "Central bank", True),
    DataSource("https://www.ing.be/", "ING Belgium", SourceCategory.BANK, "BE", "Major bank"),
    DataSource("https://www.kbc.be/", "KBC", SourceCategory.BANK, "BE", "Major bank"),
    DataSource("https://www.bpost.be/", "Bpost", SourceCategory.TRANSPORT, "BE", "Postal service"),
    DataSource("https://www.brusselsairlines.com/", "Brussels Airlines", SourceCategory.TRANSPORT, "BE", "Airline"),
    DataSource("https://www.belgiantrain.be/", "NMBS/SNCB", SourceCategory.TRANSPORT, "BE", "Railways", True),
    DataSource("https://www.ab-inbev.com/", "AB InBev", SourceCategory.INDUSTRY, "BE", "Brewing"),
    DataSource("https://www.umicore.com/", "Umicore", SourceCategory.INDUSTRY, "BE", "Materials"),
    DataSource("https://www.vrt.be/", "VRT", SourceCategory.NEWS, "BE", "Dutch public broadcaster"),
    DataSource("https://www.rtbf.be/", "RTBF", SourceCategory.NEWS, "BE", "French public broadcaster"),
    DataSource("https://www.standaard.be/", "De Standaard", SourceCategory.NEWS, "BE", "Dutch newspaper"),
    DataSource("https://www.lesoir.be/", "Le Soir", SourceCategory.NEWS, "BE", "French newspaper"),
    DataSource("https://www.fine-arts-museum.be/", "Royal Museums Belgium", SourceCategory.CULTURE, "BE", "Art museums"),
    DataSource("https://www.atomium.be/", "Atomium", SourceCategory.CULTURE, "BE", "Landmark"),
    DataSource("https://www.visitbrussels.be/", "Visit Brussels", SourceCategory.TOURISM, "BE", "Tourism"),
    DataSource("https://www.rbfa.be/", "Belgian Football Association", SourceCategory.SPORT, "BE", "Football federation"),
    DataSource("https://www.proleague.be/", "Pro League Belgium", SourceCategory.SPORT, "BE", "Football league", True),
    DataSource("https://www.olympic.be/", "Belgian Olympic Committee", SourceCategory.SPORT, "BE", "Olympic committee"),
]

# ============================================================
# 🇵🇱 POLAND DATA SOURCES
# ============================================================

POLAND_SOURCES = [
    DataSource("https://www.gov.pl/", "Polish Government", SourceCategory.GOVERNMENT, "PL", "Government portal"),
    DataSource("https://www.sejm.gov.pl/", "Sejm", SourceCategory.GOVERNMENT, "PL", "Lower house"),
    DataSource("https://www.senat.gov.pl/", "Senate", SourceCategory.GOVERNMENT, "PL", "Upper house"),
    DataSource("https://stat.gov.pl/", "GUS Statistics", SourceCategory.STATISTICS, "PL", "National statistics", True),
    DataSource("https://dane.gov.pl/", "Dane.gov.pl", SourceCategory.STATISTICS, "PL", "Open data", True),
    DataSource("https://www.warszawa.pl/", "Warsaw Portal", SourceCategory.GOVERNMENT, "PL", "Capital city"),
    DataSource("https://www.krakow.pl/", "Krakow Portal", SourceCategory.GOVERNMENT, "PL", "Krakow city"),
    DataSource("https://www.uw.edu.pl/", "University of Warsaw", SourceCategory.UNIVERSITY, "PL", "Warsaw university"),
    DataSource("https://www.uj.edu.pl/", "Jagiellonian University", SourceCategory.UNIVERSITY, "PL", "Krakow university"),
    DataSource("https://www.pw.edu.pl/", "Warsaw University of Technology", SourceCategory.UNIVERSITY, "PL", "Technical university"),
    DataSource("https://www.agh.edu.pl/", "AGH Krakow", SourceCategory.UNIVERSITY, "PL", "Technical university"),
    DataSource("https://www.put.poznan.pl/", "Poznan University of Technology", SourceCategory.UNIVERSITY, "PL", "Technical university"),
    DataSource("https://www.nbp.pl/", "National Bank of Poland", SourceCategory.BANK, "PL", "Central bank", True),
    DataSource("https://www.pkobp.pl/", "PKO BP", SourceCategory.BANK, "PL", "Major bank"),
    DataSource("https://www.santander.pl/", "Santander Bank Polska", SourceCategory.BANK, "PL", "Major bank"),
    DataSource("https://www.gpw.pl/", "Warsaw Stock Exchange", SourceCategory.BANK, "PL", "Stock exchange", True),
    DataSource("https://www.orlen.pl/", "PKN Orlen", SourceCategory.ENERGY, "PL", "Energy company"),
    DataSource("https://www.pgnig.pl/", "PGNiG", SourceCategory.ENERGY, "PL", "Gas company"),
    DataSource("https://www.lot.com/", "LOT Polish Airlines", SourceCategory.TRANSPORT, "PL", "Airline"),
    DataSource("https://www.pkp.pl/", "PKP Railways", SourceCategory.TRANSPORT, "PL", "Railways", True),
    DataSource("https://www.tvp.pl/", "TVP", SourceCategory.NEWS, "PL", "Public broadcaster"),
    DataSource("https://www.tvn24.pl/", "TVN24", SourceCategory.NEWS, "PL", "News channel"),
    DataSource("https://wyborcza.pl/", "Gazeta Wyborcza", SourceCategory.NEWS, "PL", "Daily newspaper"),
    DataSource("https://www.pap.pl/", "PAP", SourceCategory.NEWS, "PL", "News agency", True),
    DataSource("https://www.mnw.art.pl/", "National Museum Warsaw", SourceCategory.CULTURE, "PL", "National museum"),
    DataSource("https://www.wawel.krakow.pl/", "Wawel Castle", SourceCategory.CULTURE, "PL", "Royal castle"),
    DataSource("https://www.auschwitz.org/", "Auschwitz-Birkenau", SourceCategory.CULTURE, "PL", "Memorial site"),
    DataSource("https://www.poland.travel/", "Poland Travel", SourceCategory.TOURISM, "PL", "Tourism", True),
    DataSource("https://www.pzpn.pl/", "PZPN", SourceCategory.SPORT, "PL", "Football federation"),
    DataSource("https://www.ekstraklasa.org/", "Ekstraklasa", SourceCategory.SPORT, "PL", "Football league", True),
    DataSource("https://www.pzn.pl/", "PZN", SourceCategory.SPORT, "PL", "Skiing federation"),
]

# ============================================================
# 🇸🇪 SWEDEN DATA SOURCES
# ============================================================

SWEDEN_SOURCES = [
    DataSource("https://www.regeringen.se/", "Swedish Government", SourceCategory.GOVERNMENT, "SE", "Government portal"),
    DataSource("https://www.riksdagen.se/", "Riksdag", SourceCategory.GOVERNMENT, "SE", "Parliament"),
    DataSource("https://www.scb.se/", "Statistics Sweden", SourceCategory.STATISTICS, "SE", "National statistics", True),
    DataSource("https://oppnadata.se/", "Open Data Sweden", SourceCategory.STATISTICS, "SE", "Open data", True),
    DataSource("https://start.stockholm/", "Stockholm Portal", SourceCategory.GOVERNMENT, "SE", "Capital city"),
    DataSource("https://www.uu.se/", "Uppsala University", SourceCategory.UNIVERSITY, "SE", "Uppsala university"),
    DataSource("https://www.lu.se/", "Lund University", SourceCategory.UNIVERSITY, "SE", "Lund university"),
    DataSource("https://www.kth.se/", "KTH Stockholm", SourceCategory.UNIVERSITY, "SE", "Technical university"),
    DataSource("https://www.su.se/", "Stockholm University", SourceCategory.UNIVERSITY, "SE", "Stockholm university"),
    DataSource("https://www.gu.se/", "University of Gothenburg", SourceCategory.UNIVERSITY, "SE", "Gothenburg university"),
    DataSource("https://www.chalmers.se/", "Chalmers University", SourceCategory.UNIVERSITY, "SE", "Technical university"),
    DataSource("https://www.ki.se/", "Karolinska Institute", SourceCategory.RESEARCH, "SE", "Medical research"),
    DataSource("https://www.riksbank.se/", "Sveriges Riksbank", SourceCategory.BANK, "SE", "Central bank", True),
    DataSource("https://www.seb.se/", "SEB", SourceCategory.BANK, "SE", "Major bank"),
    DataSource("https://www.nordea.se/", "Nordea Sweden", SourceCategory.BANK, "SE", "Major bank"),
    DataSource("https://www.handelsbanken.se/", "Handelsbanken", SourceCategory.BANK, "SE", "Major bank"),
    DataSource("https://www.spotify.com/", "Spotify", SourceCategory.INDUSTRY, "SE", "Music streaming"),
    DataSource("https://www.ikea.se/", "IKEA", SourceCategory.INDUSTRY, "SE", "Furniture retail"),
    DataSource("https://www.hm.com/", "H&M", SourceCategory.INDUSTRY, "SE", "Fashion retail"),
    DataSource("https://www.volvo.com/", "Volvo", SourceCategory.INDUSTRY, "SE", "Automotive"),
    DataSource("https://www.ericsson.com/", "Ericsson", SourceCategory.TELECOM, "SE", "Telecom"),
    DataSource("https://www.sas.se/", "SAS", SourceCategory.TRANSPORT, "SE", "Airline"),
    DataSource("https://www.sj.se/", "SJ Railways", SourceCategory.TRANSPORT, "SE", "Railways", True),
    DataSource("https://www.svt.se/", "SVT", SourceCategory.NEWS, "SE", "Public broadcaster"),
    DataSource("https://www.dn.se/", "Dagens Nyheter", SourceCategory.NEWS, "SE", "Daily newspaper"),
    DataSource("https://www.svd.se/", "Svenska Dagbladet", SourceCategory.NEWS, "SE", "Daily newspaper"),
    DataSource("https://www.tt.se/", "TT News Agency", SourceCategory.NEWS, "SE", "News agency", True),
    DataSource("https://www.nationalmuseum.se/", "National Museum Sweden", SourceCategory.CULTURE, "SE", "Art museum"),
    DataSource("https://www.nobelprize.org/", "Nobel Prize", SourceCategory.CULTURE, "SE", "Nobel Foundation"),
    DataSource("https://www.visitsweden.com/", "Visit Sweden", SourceCategory.TOURISM, "SE", "Tourism", True),
    DataSource("https://www.svenskfotboll.se/", "Swedish Football", SourceCategory.SPORT, "SE", "Football federation"),
    DataSource("https://www.allsvenskan.se/", "Allsvenskan", SourceCategory.SPORT, "SE", "Football league", True),
    DataSource("https://www.sok.se/", "Swedish Olympic Committee", SourceCategory.SPORT, "SE", "Olympic committee"),
]

# ============================================================
# 🇳🇴 NORWAY DATA SOURCES
# ============================================================

NORWAY_SOURCES = [
    DataSource("https://www.regjeringen.no/", "Norwegian Government", SourceCategory.GOVERNMENT, "NO", "Government portal"),
    DataSource("https://www.stortinget.no/", "Stortinget", SourceCategory.GOVERNMENT, "NO", "Parliament"),
    DataSource("https://www.ssb.no/", "Statistics Norway", SourceCategory.STATISTICS, "NO", "National statistics", True),
    DataSource("https://data.norge.no/", "Open Data Norway", SourceCategory.STATISTICS, "NO", "Open data", True),
    DataSource("https://www.oslo.kommune.no/", "Oslo Portal", SourceCategory.GOVERNMENT, "NO", "Capital city"),
    DataSource("https://www.uio.no/", "University of Oslo", SourceCategory.UNIVERSITY, "NO", "Oslo university"),
    DataSource("https://www.uib.no/", "University of Bergen", SourceCategory.UNIVERSITY, "NO", "Bergen university"),
    DataSource("https://www.ntnu.no/", "NTNU", SourceCategory.UNIVERSITY, "NO", "Trondheim university"),
    DataSource("https://www.uit.no/", "UiT Arctic University", SourceCategory.UNIVERSITY, "NO", "Tromsø university"),
    DataSource("https://www.norges-bank.no/", "Norges Bank", SourceCategory.BANK, "NO", "Central bank", True),
    DataSource("https://www.dnb.no/", "DNB", SourceCategory.BANK, "NO", "Major bank"),
    DataSource("https://www.equinor.com/", "Equinor", SourceCategory.ENERGY, "NO", "Oil/gas/energy"),
    DataSource("https://www.norwegian.com/", "Norwegian Air", SourceCategory.TRANSPORT, "NO", "Airline"),
    DataSource("https://www.vy.no/", "Vy Railways", SourceCategory.TRANSPORT, "NO", "Railways", True),
    DataSource("https://www.nrk.no/", "NRK", SourceCategory.NEWS, "NO", "Public broadcaster"),
    DataSource("https://www.vg.no/", "VG", SourceCategory.NEWS, "NO", "Daily newspaper"),
    DataSource("https://www.aftenposten.no/", "Aftenposten", SourceCategory.NEWS, "NO", "Daily newspaper"),
    DataSource("https://www.nasjonalmuseet.no/", "National Museum Norway", SourceCategory.CULTURE, "NO", "National museum"),
    DataSource("https://www.visitnorway.com/", "Visit Norway", SourceCategory.TOURISM, "NO", "Tourism", True),
    DataSource("https://www.fotball.no/", "Norwegian Football", SourceCategory.SPORT, "NO", "Football federation"),
    DataSource("https://www.skiforbundet.no/", "Norwegian Ski Federation", SourceCategory.SPORT, "NO", "Skiing"),
    DataSource("https://www.olympiatoppen.no/", "Olympiatoppen", SourceCategory.SPORT, "NO", "Olympic center"),
]

# ============================================================
# 🇩🇰 DENMARK DATA SOURCES
# ============================================================

DENMARK_SOURCES = [
    DataSource("https://www.regeringen.dk/", "Danish Government", SourceCategory.GOVERNMENT, "DK", "Government portal"),
    DataSource("https://www.ft.dk/", "Folketing", SourceCategory.GOVERNMENT, "DK", "Parliament"),
    DataSource("https://www.dst.dk/", "Statistics Denmark", SourceCategory.STATISTICS, "DK", "National statistics", True),
    DataSource("https://portal.opendata.dk/", "Open Data Denmark", SourceCategory.STATISTICS, "DK", "Open data", True),
    DataSource("https://www.kk.dk/", "Copenhagen Portal", SourceCategory.GOVERNMENT, "DK", "Capital city"),
    DataSource("https://www.ku.dk/", "University of Copenhagen", SourceCategory.UNIVERSITY, "DK", "Copenhagen university"),
    DataSource("https://www.dtu.dk/", "DTU", SourceCategory.UNIVERSITY, "DK", "Technical university"),
    DataSource("https://www.au.dk/", "Aarhus University", SourceCategory.UNIVERSITY, "DK", "Aarhus university"),
    DataSource("https://www.cbs.dk/", "Copenhagen Business School", SourceCategory.UNIVERSITY, "DK", "Business school"),
    DataSource("https://www.nationalbanken.dk/", "Danmarks Nationalbank", SourceCategory.BANK, "DK", "Central bank", True),
    DataSource("https://www.danskebank.dk/", "Danske Bank", SourceCategory.BANK, "DK", "Major bank"),
    DataSource("https://www.maersk.com/", "Maersk", SourceCategory.TRANSPORT, "DK", "Shipping"),
    DataSource("https://www.novonordisk.com/", "Novo Nordisk", SourceCategory.INDUSTRY, "DK", "Pharmaceuticals"),
    DataSource("https://www.carlsberg.com/", "Carlsberg", SourceCategory.INDUSTRY, "DK", "Brewing"),
    DataSource("https://www.lego.com/", "LEGO", SourceCategory.INDUSTRY, "DK", "Toys"),
    DataSource("https://www.sas.dk/", "SAS Denmark", SourceCategory.TRANSPORT, "DK", "Airline"),
    DataSource("https://www.dsb.dk/", "DSB Railways", SourceCategory.TRANSPORT, "DK", "Railways", True),
    DataSource("https://www.dr.dk/", "DR", SourceCategory.NEWS, "DK", "Public broadcaster"),
    DataSource("https://politiken.dk/", "Politiken", SourceCategory.NEWS, "DK", "Daily newspaper"),
    DataSource("https://jyllands-posten.dk/", "Jyllands-Posten", SourceCategory.NEWS, "DK", "Daily newspaper"),
    DataSource("https://www.smk.dk/", "SMK National Gallery", SourceCategory.CULTURE, "DK", "Art museum"),
    DataSource("https://natmus.dk/", "National Museum Denmark", SourceCategory.CULTURE, "DK", "National museum"),
    DataSource("https://www.visitdenmark.com/", "Visit Denmark", SourceCategory.TOURISM, "DK", "Tourism", True),
    DataSource("https://www.dbu.dk/", "DBU", SourceCategory.SPORT, "DK", "Football federation"),
    DataSource("https://www.superliga.dk/", "Superliga", SourceCategory.SPORT, "DK", "Football league", True),
    DataSource("https://www.dif.dk/", "Danish Sports Confederation", SourceCategory.SPORT, "DK", "Sports federation"),
]

# ============================================================
# 🇫🇮 FINLAND DATA SOURCES
# ============================================================

FINLAND_SOURCES = [
    DataSource("https://valtioneuvosto.fi/", "Finnish Government", SourceCategory.GOVERNMENT, "FI", "Government portal"),
    DataSource("https://www.eduskunta.fi/", "Eduskunta", SourceCategory.GOVERNMENT, "FI", "Parliament"),
    DataSource("https://www.stat.fi/", "Statistics Finland", SourceCategory.STATISTICS, "FI", "National statistics", True),
    DataSource("https://www.avoindata.fi/", "Open Data Finland", SourceCategory.STATISTICS, "FI", "Open data", True),
    DataSource("https://www.hel.fi/", "Helsinki Portal", SourceCategory.GOVERNMENT, "FI", "Capital city"),
    DataSource("https://www.helsinki.fi/", "University of Helsinki", SourceCategory.UNIVERSITY, "FI", "Helsinki university"),
    DataSource("https://www.aalto.fi/", "Aalto University", SourceCategory.UNIVERSITY, "FI", "Technology/design"),
    DataSource("https://www.tuni.fi/", "Tampere University", SourceCategory.UNIVERSITY, "FI", "Tampere university"),
    DataSource("https://www.oulu.fi/", "University of Oulu", SourceCategory.UNIVERSITY, "FI", "Oulu university"),
    DataSource("https://www.suomenpankki.fi/", "Bank of Finland", SourceCategory.BANK, "FI", "Central bank", True),
    DataSource("https://www.nordea.fi/", "Nordea Finland", SourceCategory.BANK, "FI", "Major bank"),
    DataSource("https://www.op.fi/", "OP Group", SourceCategory.BANK, "FI", "Cooperative bank"),
    DataSource("https://www.nokia.com/", "Nokia", SourceCategory.TELECOM, "FI", "Telecom/tech"),
    DataSource("https://www.finnair.com/", "Finnair", SourceCategory.TRANSPORT, "FI", "Airline"),
    DataSource("https://www.vr.fi/", "VR Railways", SourceCategory.TRANSPORT, "FI", "Railways", True),
    DataSource("https://www.yle.fi/", "YLE", SourceCategory.NEWS, "FI", "Public broadcaster"),
    DataSource("https://www.hs.fi/", "Helsingin Sanomat", SourceCategory.NEWS, "FI", "Daily newspaper"),
    DataSource("https://www.kansallismuseo.fi/", "National Museum Finland", SourceCategory.CULTURE, "FI", "National museum"),
    DataSource("https://www.visitfinland.com/", "Visit Finland", SourceCategory.TOURISM, "FI", "Tourism", True),
    DataSource("https://www.palloliitto.fi/", "Football Association Finland", SourceCategory.SPORT, "FI", "Football federation"),
    DataSource("https://www.hiihtoliitto.fi/", "Finnish Ski Association", SourceCategory.SPORT, "FI", "Skiing"),
    DataSource("https://www.olympiakomitea.fi/", "Finnish Olympic Committee", SourceCategory.SPORT, "FI", "Olympic committee"),
]

# ============================================================
# 🇮🇪 IRELAND DATA SOURCES
# ============================================================

IRELAND_SOURCES = [
    DataSource("https://www.gov.ie/", "Irish Government", SourceCategory.GOVERNMENT, "IE", "Government portal"),
    DataSource("https://www.oireachtas.ie/", "Oireachtas", SourceCategory.GOVERNMENT, "IE", "Parliament"),
    DataSource("https://www.cso.ie/", "CSO Ireland", SourceCategory.STATISTICS, "IE", "National statistics", True),
    DataSource("https://data.gov.ie/", "Open Data Ireland", SourceCategory.STATISTICS, "IE", "Open data", True),
    DataSource("https://www.dublincity.ie/", "Dublin Portal", SourceCategory.GOVERNMENT, "IE", "Capital city"),
    DataSource("https://www.tcd.ie/", "Trinity College Dublin", SourceCategory.UNIVERSITY, "IE", "Top university"),
    DataSource("https://www.ucd.ie/", "UCD", SourceCategory.UNIVERSITY, "IE", "Dublin university"),
    DataSource("https://www.dcu.ie/", "DCU", SourceCategory.UNIVERSITY, "IE", "Dublin city university"),
    DataSource("https://www.nuigalway.ie/", "NUI Galway", SourceCategory.UNIVERSITY, "IE", "Galway university"),
    DataSource("https://www.ucc.ie/", "UCC", SourceCategory.UNIVERSITY, "IE", "Cork university"),
    DataSource("https://www.centralbank.ie/", "Central Bank of Ireland", SourceCategory.BANK, "IE", "Central bank", True),
    DataSource("https://www.bankofireland.com/", "Bank of Ireland", SourceCategory.BANK, "IE", "Major bank"),
    DataSource("https://www.aib.ie/", "AIB", SourceCategory.BANK, "IE", "Major bank"),
    DataSource("https://www.ise.ie/", "Irish Stock Exchange", SourceCategory.BANK, "IE", "Stock exchange", True),
    DataSource("https://www.aerlingus.com/", "Aer Lingus", SourceCategory.TRANSPORT, "IE", "Airline"),
    DataSource("https://www.ryanair.com/", "Ryanair", SourceCategory.TRANSPORT, "IE", "Budget airline"),
    DataSource("https://www.irishrail.ie/", "Irish Rail", SourceCategory.TRANSPORT, "IE", "Railways", True),
    DataSource("https://www.rte.ie/", "RTÉ", SourceCategory.NEWS, "IE", "Public broadcaster"),
    DataSource("https://www.irishtimes.com/", "Irish Times", SourceCategory.NEWS, "IE", "Daily newspaper"),
    DataSource("https://www.independent.ie/", "Irish Independent", SourceCategory.NEWS, "IE", "Daily newspaper"),
    DataSource("https://www.museum.ie/", "National Museum of Ireland", SourceCategory.CULTURE, "IE", "National museum"),
    DataSource("https://www.nationalgallery.ie/", "National Gallery Ireland", SourceCategory.CULTURE, "IE", "Art gallery"),
    DataSource("https://www.ireland.com/", "Tourism Ireland", SourceCategory.TOURISM, "IE", "Tourism", True),
    DataSource("https://www.fai.ie/", "FAI", SourceCategory.SPORT, "IE", "Football federation"),
    DataSource("https://www.irfu.ie/", "IRFU", SourceCategory.SPORT, "IE", "Rugby union"),
    DataSource("https://www.gaa.ie/", "GAA", SourceCategory.SPORT, "IE", "Gaelic games"),
    DataSource("https://www.olympicsport.ie/", "Olympic Federation Ireland", SourceCategory.SPORT, "IE", "Olympic committee"),
]

# ============================================================
# 🇵🇹 PORTUGAL DATA SOURCES
# ============================================================

PORTUGAL_SOURCES = [
    DataSource("https://www.portugal.gov.pt/", "Portuguese Government", SourceCategory.GOVERNMENT, "PT", "Government portal"),
    DataSource("https://www.parlamento.pt/", "Assembleia da República", SourceCategory.GOVERNMENT, "PT", "Parliament"),
    DataSource("https://www.ine.pt/", "INE Portugal", SourceCategory.STATISTICS, "PT", "National statistics", True),
    DataSource("https://dados.gov.pt/", "Dados.gov.pt", SourceCategory.STATISTICS, "PT", "Open data", True),
    DataSource("https://www.cm-lisboa.pt/", "Lisbon Portal", SourceCategory.GOVERNMENT, "PT", "Capital city"),
    DataSource("https://www.cm-porto.pt/", "Porto Portal", SourceCategory.GOVERNMENT, "PT", "Porto city"),
    DataSource("https://www.ulisboa.pt/", "University of Lisbon", SourceCategory.UNIVERSITY, "PT", "Lisbon university"),
    DataSource("https://www.up.pt/", "University of Porto", SourceCategory.UNIVERSITY, "PT", "Porto university"),
    DataSource("https://www.uc.pt/", "University of Coimbra", SourceCategory.UNIVERSITY, "PT", "Historic university"),
    DataSource("https://tecnico.ulisboa.pt/", "Instituto Superior Técnico", SourceCategory.UNIVERSITY, "PT", "Technical university"),
    DataSource("https://www.bportugal.pt/", "Banco de Portugal", SourceCategory.BANK, "PT", "Central bank", True),
    DataSource("https://www.cgd.pt/", "Caixa Geral de Depósitos", SourceCategory.BANK, "PT", "Major bank"),
    DataSource("https://www.millenniumbcp.pt/", "Millennium BCP", SourceCategory.BANK, "PT", "Major bank"),
    DataSource("https://www.edp.pt/", "EDP", SourceCategory.ENERGY, "PT", "Energy company"),
    DataSource("https://www.tap.pt/", "TAP Portugal", SourceCategory.TRANSPORT, "PT", "Airline"),
    DataSource("https://www.cp.pt/", "CP Railways", SourceCategory.TRANSPORT, "PT", "Railways", True),
    DataSource("https://www.rtp.pt/", "RTP", SourceCategory.NEWS, "PT", "Public broadcaster"),
    DataSource("https://www.publico.pt/", "Público", SourceCategory.NEWS, "PT", "Daily newspaper"),
    DataSource("https://www.jn.pt/", "Jornal de Notícias", SourceCategory.NEWS, "PT", "Daily newspaper"),
    DataSource("https://www.lusa.pt/", "Lusa", SourceCategory.NEWS, "PT", "News agency", True),
    DataSource("https://www.museudoazulejo.gov.pt/", "National Tile Museum", SourceCategory.CULTURE, "PT", "Art museum"),
    DataSource("https://www.visitportugal.com/", "Visit Portugal", SourceCategory.TOURISM, "PT", "Tourism", True),
    DataSource("https://www.fpf.pt/", "Portuguese Football Federation", SourceCategory.SPORT, "PT", "Football federation"),
    DataSource("https://www.ligaportugal.pt/", "Liga Portugal", SourceCategory.SPORT, "PT", "Football league", True),
    DataSource("https://www.fcporto.pt/", "FC Porto", SourceCategory.SPORT, "PT", "Football club"),
    DataSource("https://www.slbenfica.pt/", "Benfica", SourceCategory.SPORT, "PT", "Football club"),
    DataSource("https://www.sporting.pt/", "Sporting CP", SourceCategory.SPORT, "PT", "Football club"),
    DataSource("https://comiteolimpicoportugal.pt/", "Portuguese Olympic Committee", SourceCategory.SPORT, "PT", "Olympic committee"),
]

# ============================================================
# 🇬🇷 GREECE DATA SOURCES
# ============================================================

GREECE_SOURCES = [
    DataSource("https://www.gov.gr/", "Greek Government", SourceCategory.GOVERNMENT, "GR", "Government portal"),
    DataSource("https://www.hellenicparliament.gr/", "Hellenic Parliament", SourceCategory.GOVERNMENT, "GR", "Parliament"),
    DataSource("https://www.statistics.gr/", "ELSTAT", SourceCategory.STATISTICS, "GR", "National statistics", True),
    DataSource("https://data.gov.gr/", "Data.gov.gr", SourceCategory.STATISTICS, "GR", "Open data", True),
    DataSource("https://www.cityofathens.gr/", "Athens Portal", SourceCategory.GOVERNMENT, "GR", "Capital city"),
    DataSource("https://www.uoa.gr/", "University of Athens", SourceCategory.UNIVERSITY, "GR", "Athens university"),
    DataSource("https://www.auth.gr/", "Aristotle University", SourceCategory.UNIVERSITY, "GR", "Thessaloniki university"),
    DataSource("https://www.ntua.gr/", "National Technical University", SourceCategory.UNIVERSITY, "GR", "Athens Polytechnic"),
    DataSource("https://www.bankofgreece.gr/", "Bank of Greece", SourceCategory.BANK, "GR", "Central bank", True),
    DataSource("https://www.nbg.gr/", "National Bank of Greece", SourceCategory.BANK, "GR", "Major bank"),
    DataSource("https://www.piraeusbank.gr/", "Piraeus Bank", SourceCategory.BANK, "GR", "Major bank"),
    DataSource("https://www.athexgroup.gr/", "Athens Stock Exchange", SourceCategory.BANK, "GR", "Stock exchange", True),
    DataSource("https://www.dei.gr/", "PPC", SourceCategory.ENERGY, "GR", "Public Power Corporation"),
    DataSource("https://www.aegeanair.com/", "Aegean Airlines", SourceCategory.TRANSPORT, "GR", "Airline"),
    DataSource("https://www.ert.gr/", "ERT", SourceCategory.NEWS, "GR", "Public broadcaster"),
    DataSource("https://www.kathimerini.gr/", "Kathimerini", SourceCategory.NEWS, "GR", "Daily newspaper"),
    DataSource("https://www.tanea.gr/", "Ta Nea", SourceCategory.NEWS, "GR", "Daily newspaper"),
    DataSource("https://www.ana.gr/", "ANA-MPA", SourceCategory.NEWS, "GR", "News agency", True),
    DataSource("https://www.namuseum.gr/", "National Archaeological Museum", SourceCategory.CULTURE, "GR", "Archaeology"),
    DataSource("https://www.theacropolismuseum.gr/", "Acropolis Museum", SourceCategory.CULTURE, "GR", "Ancient Greek art"),
    DataSource("https://www.visitgreece.gr/", "Visit Greece", SourceCategory.TOURISM, "GR", "Tourism", True),
    DataSource("https://www.epo.gr/", "Hellenic Football Federation", SourceCategory.SPORT, "GR", "Football federation"),
    DataSource("https://www.superleague.gr/", "Super League Greece", SourceCategory.SPORT, "GR", "Football league", True),
    DataSource("https://www.olympiacos.org/", "Olympiacos", SourceCategory.SPORT, "GR", "Football club"),
    DataSource("https://www.panathinaikos.gr/", "Panathinaikos", SourceCategory.SPORT, "GR", "Football club"),
    DataSource("https://www.hoc.gr/", "Hellenic Olympic Committee", SourceCategory.SPORT, "GR", "Olympic committee"),
]

# ============================================================
# 🌍 EUROPEAN TOURISM
# ============================================================

EUROPE_TOURISM = [
    DataSource("https://www.visiteurope.com/", "Visit Europe", SourceCategory.TOURISM, "EU", "European tourism"),
    DataSource("https://www.raileurope.com/", "Rail Europe", SourceCategory.TOURISM, "EU", "Train travel", True),
    DataSource("https://www.eurostar.com/", "Eurostar", SourceCategory.TOURISM, "EU", "High-speed rail"),
    DataSource("https://www.booking.com/", "Booking.com", SourceCategory.TOURISM, "NL", "Hotel booking", True),
    DataSource("https://www.airbnb.com/", "Airbnb", SourceCategory.TOURISM, "US", "Vacation rentals", True),
    DataSource("https://www.tripadvisor.com/", "TripAdvisor", SourceCategory.TOURISM, "US", "Travel reviews", True),
    DataSource("https://www.skyscanner.com/", "Skyscanner", SourceCategory.TOURISM, "GB", "Flight search", True),
    DataSource("https://www.kayak.com/", "Kayak", SourceCategory.TOURISM, "US", "Travel search", True),
]

# ============================================================
# 🎭 EUROPEAN ENTERTAINMENT
# ============================================================

EUROPE_ENTERTAINMENT = [
    DataSource("https://www.eurovision.tv/", "Eurovision", SourceCategory.ENTERTAINMENT, "EU", "Song contest"),
    DataSource("https://www.netflix.com/", "Netflix", SourceCategory.ENTERTAINMENT, "US", "Streaming", True),
    DataSource("https://www.spotify.com/", "Spotify", SourceCategory.ENTERTAINMENT, "SE", "Music streaming", True),
    DataSource("https://www.deezer.com/", "Deezer", SourceCategory.ENTERTAINMENT, "FR", "Music streaming"),
    DataSource("https://www.arte.tv/", "Arte", SourceCategory.ENTERTAINMENT, "FR", "Cultural TV"),
    DataSource("https://www.europeanfilmawards.eu/", "European Film Awards", SourceCategory.ENTERTAINMENT, "DE", "Film awards"),
    DataSource("https://www.europeantheatre.eu/", "European Theatre", SourceCategory.ENTERTAINMENT, "EU", "Theatre network"),
    DataSource("https://www.operaeuropa.org/", "Opera Europa", SourceCategory.ENTERTAINMENT, "EU", "Opera network"),
]

# ============================================================
# 🎪 EUROPEAN EVENTS
# ============================================================

EUROPE_EVENTS = [
    DataSource("https://www.oktoberfest.de/", "Oktoberfest", SourceCategory.EVENTS, "DE", "Beer festival"),
    DataSource("https://www.carnaval.rio/", "Carnival", SourceCategory.EVENTS, "EU", "Pre-Lent festivals"),
    DataSource("https://www.festival-cannes.com/", "Cannes Film Festival", SourceCategory.EVENTS, "FR", "Film festival"),
    DataSource("https://www.berlinale.de/", "Berlinale", SourceCategory.EVENTS, "DE", "Film festival"),
    DataSource("https://www.labiennale.org/", "Venice Biennale", SourceCategory.EVENTS, "IT", "Art exhibition"),
    DataSource("https://www.artbasel.com/", "Art Basel", SourceCategory.EVENTS, "CH", "Art fair"),
    DataSource("https://www.cebit.de/", "CeBIT", SourceCategory.EVENTS, "DE", "Tech expo"),
    DataSource("https://www.mwcbarcelona.com/", "Mobile World Congress", SourceCategory.EVENTS, "ES", "Mobile tech"),
    DataSource("https://www.gamescom.global/", "Gamescom", SourceCategory.EVENTS, "DE", "Gaming expo"),
    DataSource("https://www.tomorrowland.com/", "Tomorrowland", SourceCategory.EVENTS, "BE", "Music festival"),
    DataSource("https://www.glastonburyfestivals.co.uk/", "Glastonbury", SourceCategory.EVENTS, "GB", "Music festival"),
    DataSource("https://www.strictlysailing.net/", "Strictly Sail", SourceCategory.EVENTS, "GB", "Sailing"),
]

# ============================================================
# COMBINED EXPORT
# ============================================================

ALL_EUROPE_SOURCES = (
    EU_INSTITUTIONS +
    GERMANY_GOVERNMENT + GERMANY_UNIVERSITIES + GERMANY_HOSPITALS +
    GERMANY_BANKS + GERMANY_INDUSTRY + GERMANY_NEWS + GERMANY_CULTURE + GERMANY_SPORT +
    FRANCE_GOVERNMENT + FRANCE_UNIVERSITIES + FRANCE_HOSPITALS +
    FRANCE_BANKS + FRANCE_INDUSTRY + FRANCE_NEWS + FRANCE_CULTURE + FRANCE_SPORT +
    UK_GOVERNMENT + UK_UNIVERSITIES + UK_HOSPITALS +
    UK_BANKS + UK_INDUSTRY + UK_NEWS + UK_CULTURE + UK_SPORT +
    ITALY_GOVERNMENT + ITALY_UNIVERSITIES + ITALY_BANKS +
    ITALY_INDUSTRY + ITALY_NEWS + ITALY_CULTURE + ITALY_SPORT +
    SPAIN_GOVERNMENT + SPAIN_UNIVERSITIES + SPAIN_BANKS +
    SPAIN_INDUSTRY + SPAIN_NEWS + SPAIN_CULTURE + SPAIN_SPORT +
    NETHERLANDS_SOURCES + SWITZERLAND_SOURCES + AUSTRIA_SOURCES +
    BELGIUM_SOURCES + POLAND_SOURCES + SWEDEN_SOURCES +
    NORWAY_SOURCES + DENMARK_SOURCES + FINLAND_SOURCES +
    IRELAND_SOURCES + PORTUGAL_SOURCES + GREECE_SOURCES +
    EUROPE_TOURISM + EUROPE_ENTERTAINMENT + EUROPE_EVENTS
)

def get_all_sources() -> List[DataSource]:
    """Return all European data sources"""
    return ALL_EUROPE_SOURCES

def get_sources_by_country(country_code: str) -> List[DataSource]:
    """Return sources for a specific country"""
    return [s for s in ALL_EUROPE_SOURCES if s.country == country_code]

def get_sources_by_category(category: SourceCategory) -> List[DataSource]:
    """Return sources for a specific category"""
    return [s for s in ALL_EUROPE_SOURCES if s.category == category]

def get_api_sources() -> List[DataSource]:
    """Return only sources with API access"""
    return [s for s in ALL_EUROPE_SOURCES if s.api_available]

# Statistics
if __name__ == "__main__":
    print(f"🇪🇺 Total European Sources: {len(ALL_EUROPE_SOURCES)}")
    print(f"Countries covered: EU, DE, FR, GB, IT, ES, NL, CH, AT, BE, PL, SE, NO, DK, FI, IE, PT, GR")
    print(f"Sources with API: {len(get_api_sources())}")
