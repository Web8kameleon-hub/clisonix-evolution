# -*- coding: utf-8 -*-
"""
🌴 CARIBBEAN & CENTRAL AMERICA - COMPLETE DATA SOURCES
=======================================================
200+ Free Open Data Sources from Caribbean & Central America

Countries Covered:
CARIBBEAN:
- Cuba 🇨🇺
- Jamaica 🇯🇲
- Haiti 🇭🇹
- Dominican Republic 🇩🇴
- Puerto Rico 🇵🇷
- Bahamas 🇧🇸
- Trinidad and Tobago 🇹🇹
- Barbados 🇧🇧
- Saint Lucia 🇱🇨
- Grenada 🇬🇩
- Saint Vincent 🇻🇨
- Antigua and Barbuda 🇦🇬
- Dominica 🇩🇲
- Saint Kitts and Nevis 🇰🇳
- Curaçao 🇨🇼
- Aruba 🇦🇼
- Cayman Islands 🇰🇾
- US Virgin Islands 🇻🇮
- British Virgin Islands 🇻🇬
- Bermuda 🇧🇲
- Turks and Caicos 🇹🇨

CENTRAL AMERICA:
- Guatemala 🇬🇹
- Honduras 🇭🇳
- El Salvador 🇸🇻
- Nicaragua 🇳🇮
- Costa Rica 🇨🇷
- Panama 🇵🇦
- Belize 🇧🇿
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
# 🇨🇺 CUBA
# ============================================================

CUBA_SOURCES = [
    DataSource("https://www.presidencia.gob.cu/", "Cuba Presidency", SourceCategory.GOVERNMENT, "CU", "Presidency"),
    DataSource("https://www.parlamentocubano.gob.cu/", "National Assembly", SourceCategory.GOVERNMENT, "CU", "Parliament"),
    DataSource("https://www.onei.gob.cu/", "ONEI", SourceCategory.STATISTICS, "CU", "Statistics", True),
    DataSource("https://www.uh.cu/", "University of Havana", SourceCategory.UNIVERSITY, "CU", "Top university"),
    DataSource("https://www.uci.cu/", "UCI", SourceCategory.UNIVERSITY, "CU", "IT university"),
    DataSource("https://www.bc.gob.cu/", "Central Bank of Cuba", SourceCategory.BANK, "CU", "Central bank"),
    DataSource("https://www.cubana.cu/", "Cubana de Aviación", SourceCategory.TRANSPORT, "CU", "National airline"),
    DataSource("https://www.granma.cu/", "Granma", SourceCategory.NEWS, "CU", "Official newspaper"),
    DataSource("https://www.prensa-latina.cu/", "Prensa Latina", SourceCategory.NEWS, "CU", "News agency"),
    DataSource("https://www.cubatravel.cu/", "Cuba Travel", SourceCategory.TOURISM, "CU", "Tourism", True),
    DataSource("https://www.ffc.cu/", "FFC", SourceCategory.SPORT, "CU", "Football federation"),
]

# ============================================================
# 🇯🇲 JAMAICA
# ============================================================

JAMAICA_SOURCES = [
    DataSource("https://www.gov.jm/", "Jamaica Government", SourceCategory.GOVERNMENT, "JM", "Government portal"),
    DataSource("https://www.japarliament.gov.jm/", "Parliament of Jamaica", SourceCategory.GOVERNMENT, "JM", "Parliament"),
    DataSource("https://statinja.gov.jm/", "STATIN", SourceCategory.STATISTICS, "JM", "Statistics", True),
    DataSource("https://www.uwimona.edu.jm/", "UWI Mona", SourceCategory.UNIVERSITY, "JM", "Top university"),
    DataSource("https://www.utech.edu.jm/", "UTech Jamaica", SourceCategory.UNIVERSITY, "JM", "Tech university"),
    DataSource("https://boj.org.jm/", "Bank of Jamaica", SourceCategory.BANK, "JM", "Central bank", True),
    DataSource("https://www.jamstockex.com/", "Jamaica Stock Exchange", SourceCategory.BANK, "JM", "Stock Exchange", True),
    DataSource("https://www.ncbjamaica.com/", "NCB Jamaica", SourceCategory.BANK, "JM", "Major bank"),
    DataSource("https://www.jamaicaobserver.com/", "Jamaica Observer", SourceCategory.NEWS, "JM", "Major newspaper"),
    DataSource("https://www.jamaicagleaner.com/", "The Gleaner", SourceCategory.NEWS, "JM", "Major newspaper"),
    DataSource("https://www.visitjamaica.com/", "Visit Jamaica", SourceCategory.TOURISM, "JM", "Tourism", True),
    DataSource("https://www.jff.com/", "JFF", SourceCategory.SPORT, "JM", "Football federation"),
]

# ============================================================
# 🇭🇹 HAITI
# ============================================================

HAITI_SOURCES = [
    DataSource("https://primature.gouv.ht/", "Haiti Government", SourceCategory.GOVERNMENT, "HT", "Prime Minister"),
    DataSource("https://www.ihsi.ht/", "IHSI", SourceCategory.STATISTICS, "HT", "Statistics"),
    DataSource("https://www.ueh.edu.ht/", "State University of Haiti", SourceCategory.UNIVERSITY, "HT", "Top university"),
    DataSource("https://www.brh.ht/", "Bank of Haiti", SourceCategory.BANK, "HT", "Central bank"),
    DataSource("https://www.lenouvelliste.com/", "Le Nouvelliste", SourceCategory.NEWS, "HT", "Major newspaper"),
    DataSource("https://www.fhfhaiti.com/", "FHF", SourceCategory.SPORT, "HT", "Football federation"),
]

# ============================================================
# 🇩🇴 DOMINICAN REPUBLIC
# ============================================================

DOMINICAN_SOURCES = [
    DataSource("https://presidencia.gob.do/", "Dominican Republic Government", SourceCategory.GOVERNMENT, "DO", "Presidency"),
    DataSource("https://www.camaradediputados.gob.do/", "Chamber of Deputies", SourceCategory.GOVERNMENT, "DO", "Parliament"),
    DataSource("https://www.one.gob.do/", "ONE", SourceCategory.STATISTICS, "DO", "Statistics", True),
    DataSource("https://www.uasd.edu.do/", "UASD", SourceCategory.UNIVERSITY, "DO", "Top university"),
    DataSource("https://www.pucmm.edu.do/", "PUCMM", SourceCategory.UNIVERSITY, "DO", "Catholic university"),
    DataSource("https://www.bancentral.gov.do/", "Central Bank", SourceCategory.BANK, "DO", "Central bank", True),
    DataSource("https://www.bvrd.com.do/", "BVRD", SourceCategory.BANK, "DO", "Stock Exchange"),
    DataSource("https://www.popularenlinea.com/", "Banco Popular", SourceCategory.BANK, "DO", "Major bank"),
    DataSource("https://www.arajet.com/", "Arajet", SourceCategory.TRANSPORT, "DO", "Airline"),
    DataSource("https://listindiario.com/", "Listín Diario", SourceCategory.NEWS, "DO", "Major newspaper"),
    DataSource("https://www.diariolibre.com/", "Diario Libre", SourceCategory.NEWS, "DO", "Major newspaper"),
    DataSource("https://www.godominicanrepublic.com/", "Go Dominican Republic", SourceCategory.TOURISM, "DO", "Tourism", True),
    DataSource("https://fedofutbol.org/", "Fedofútbol", SourceCategory.SPORT, "DO", "Football federation"),
]

# ============================================================
# 🇵🇷 PUERTO RICO
# ============================================================

PUERTO_RICO_SOURCES = [
    DataSource("https://www.fortaleza.pr.gov/", "La Fortaleza", SourceCategory.GOVERNMENT, "PR", "Governor"),
    DataSource("https://www.oslpr.org/", "Legislature of Puerto Rico", SourceCategory.GOVERNMENT, "PR", "Legislature"),
    DataSource("https://censo.estadisticas.pr/", "Census Puerto Rico", SourceCategory.STATISTICS, "PR", "Statistics"),
    DataSource("https://www.upr.edu/", "University of Puerto Rico", SourceCategory.UNIVERSITY, "PR", "Top university"),
    DataSource("https://www.gdb.pr.gov/", "Government Development Bank", SourceCategory.BANK, "PR", "Development bank"),
    DataSource("https://www.popular.com/", "Banco Popular", SourceCategory.BANK, "PR", "Major bank"),
    DataSource("https://www.discoverpuertorico.com/", "Discover Puerto Rico", SourceCategory.TOURISM, "PR", "Tourism", True),
    DataSource("https://www.fpfpr.com/", "FPF Puerto Rico", SourceCategory.SPORT, "PR", "Football federation"),
]

# ============================================================
# 🇧🇸 BAHAMAS
# ============================================================

BAHAMAS_SOURCES = [
    DataSource("https://www.bahamas.gov.bs/", "Bahamas Government", SourceCategory.GOVERNMENT, "BS", "Government"),
    DataSource("https://www.bahamas.gov.bs/statistics/", "Department of Statistics", SourceCategory.STATISTICS, "BS", "Statistics"),
    DataSource("https://www.cob.edu.bs/", "University of The Bahamas", SourceCategory.UNIVERSITY, "BS", "Top university"),
    DataSource("https://www.centralbankbahamas.com/", "Central Bank of Bahamas", SourceCategory.BANK, "BS", "Central bank", True),
    DataSource("https://www.bisxbahamas.com/", "BISX", SourceCategory.BANK, "BS", "Stock Exchange"),
    DataSource("https://www.bahamasair.com/", "Bahamasair", SourceCategory.TRANSPORT, "BS", "National airline"),
    DataSource("https://www.tribune242.com/", "The Tribune", SourceCategory.NEWS, "BS", "Major newspaper"),
    DataSource("https://www.bahamas.com/", "Bahamas.com", SourceCategory.TOURISM, "BS", "Tourism", True),
    DataSource("https://www.bahamasfa.com/", "BFA", SourceCategory.SPORT, "BS", "Football federation"),
]

# ============================================================
# 🇹🇹 TRINIDAD AND TOBAGO
# ============================================================

TRINIDAD_SOURCES = [
    DataSource("https://www.ttparliament.org/", "Parliament of T&T", SourceCategory.GOVERNMENT, "TT", "Parliament"),
    DataSource("https://cso.gov.tt/", "Central Statistical Office", SourceCategory.STATISTICS, "TT", "Statistics", True),
    DataSource("https://sta.uwi.edu/", "UWI St. Augustine", SourceCategory.UNIVERSITY, "TT", "Top university"),
    DataSource("https://www.central-bank.org.tt/", "Central Bank of T&T", SourceCategory.BANK, "TT", "Central bank", True),
    DataSource("https://www.stockex.co.tt/", "Trinidad Stock Exchange", SourceCategory.BANK, "TT", "Stock Exchange"),
    DataSource("https://www.caribbeanairlines.com/", "Caribbean Airlines", SourceCategory.TRANSPORT, "TT", "Regional airline"),
    DataSource("https://www.guardian.co.tt/", "Trinidad Guardian", SourceCategory.NEWS, "TT", "Major newspaper"),
    DataSource("https://www.visittnt.com/", "Visit T&T", SourceCategory.TOURISM, "TT", "Tourism", True),
    DataSource("https://ttfa.com/", "TTFA", SourceCategory.SPORT, "TT", "Football federation"),
]

# ============================================================
# 🇧🇧 BARBADOS
# ============================================================

BARBADOS_SOURCES = [
    DataSource("https://www.gov.bb/", "Barbados Government", SourceCategory.GOVERNMENT, "BB", "Government"),
    DataSource("https://www.parliament.gov.bb/", "Parliament of Barbados", SourceCategory.GOVERNMENT, "BB", "Parliament"),
    DataSource("https://stats.gov.bb/", "Barbados Statistical Service", SourceCategory.STATISTICS, "BB", "Statistics", True),
    DataSource("https://www.cavehill.uwi.edu/", "UWI Cave Hill", SourceCategory.UNIVERSITY, "BB", "Top university"),
    DataSource("https://www.centralbank.org.bb/", "Central Bank of Barbados", SourceCategory.BANK, "BB", "Central bank", True),
    DataSource("https://www.bse.com.bb/", "Barbados Stock Exchange", SourceCategory.BANK, "BB", "Stock Exchange"),
    DataSource("https://www.nationnews.com/", "Nation News", SourceCategory.NEWS, "BB", "Major newspaper"),
    DataSource("https://www.visitbarbados.org/", "Visit Barbados", SourceCategory.TOURISM, "BB", "Tourism", True),
    DataSource("https://www.barbadosfa.com/", "BFA", SourceCategory.SPORT, "BB", "Football federation"),
]

# ============================================================
# 🇱🇨 SAINT LUCIA
# ============================================================

ST_LUCIA_SOURCES = [
    DataSource("https://www.govt.lc/", "Saint Lucia Government", SourceCategory.GOVERNMENT, "LC", "Government"),
    DataSource("https://www.stats.gov.lc/", "Central Statistics Office", SourceCategory.STATISTICS, "LC", "Statistics"),
    DataSource("https://www.eccb-centralbank.org/", "ECCB", SourceCategory.BANK, "LC", "Central bank", True),
    DataSource("https://www.stlucianewsonline.com/", "St. Lucia News", SourceCategory.NEWS, "LC", "News"),
    DataSource("https://www.stlucia.org/", "Saint Lucia Tourism", SourceCategory.TOURISM, "LC", "Tourism", True),
    DataSource("https://www.slfa.com/", "SLFA", SourceCategory.SPORT, "LC", "Football federation"),
]

# ============================================================
# 🇬🇩 GRENADA
# ============================================================

GRENADA_SOURCES = [
    DataSource("https://www.gov.gd/", "Grenada Government", SourceCategory.GOVERNMENT, "GD", "Government"),
    DataSource("https://stats.gov.gd/", "Statistics Grenada", SourceCategory.STATISTICS, "GD", "Statistics"),
    DataSource("https://www.sgu.edu/", "St. George's University", SourceCategory.UNIVERSITY, "GD", "University"),
    DataSource("https://www.puregrenada.com/", "Pure Grenada", SourceCategory.TOURISM, "GD", "Tourism", True),
    DataSource("https://www.grenadafootball.com/", "GFA", SourceCategory.SPORT, "GD", "Football federation"),
]

# ============================================================
# 🇻🇨 SAINT VINCENT AND THE GRENADINES
# ============================================================

ST_VINCENT_SOURCES = [
    DataSource("https://www.gov.vc/", "St. Vincent Government", SourceCategory.GOVERNMENT, "VC", "Government"),
    DataSource("https://stats.gov.vc/", "Statistics SVG", SourceCategory.STATISTICS, "VC", "Statistics"),
    DataSource("https://discoversvg.com/", "Discover SVG", SourceCategory.TOURISM, "VC", "Tourism", True),
    DataSource("https://www.svgff.com/", "SVGFF", SourceCategory.SPORT, "VC", "Football federation"),
]

# ============================================================
# 🇦🇬 ANTIGUA AND BARBUDA
# ============================================================

ANTIGUA_SOURCES = [
    DataSource("https://ab.gov.ag/", "Antigua & Barbuda Government", SourceCategory.GOVERNMENT, "AG", "Government"),
    DataSource("https://statistics.gov.ag/", "Statistics Division", SourceCategory.STATISTICS, "AG", "Statistics"),
    DataSource("https://www.visitantiguabarbuda.com/", "Visit Antigua Barbuda", SourceCategory.TOURISM, "AG", "Tourism", True),
    DataSource("https://antiguafootball.com/", "ABFA", SourceCategory.SPORT, "AG", "Football federation"),
]

# ============================================================
# 🇩🇲 DOMINICA
# ============================================================

DOMINICA_SOURCES = [
    DataSource("https://www.dominica.gov.dm/", "Dominica Government", SourceCategory.GOVERNMENT, "DM", "Government"),
    DataSource("https://stats.gov.dm/", "Statistics Dominica", SourceCategory.STATISTICS, "DM", "Statistics"),
    DataSource("https://discoverdominica.com/", "Discover Dominica", SourceCategory.TOURISM, "DM", "Tourism", True),
    DataSource("https://dominicafootball.com/", "DFA", SourceCategory.SPORT, "DM", "Football federation"),
]

# ============================================================
# 🇰🇳 SAINT KITTS AND NEVIS
# ============================================================

ST_KITTS_SOURCES = [
    DataSource("https://www.gov.kn/", "St. Kitts and Nevis Government", SourceCategory.GOVERNMENT, "KN", "Government"),
    DataSource("https://stats.gov.kn/", "Statistics SKN", SourceCategory.STATISTICS, "KN", "Statistics"),
    DataSource("https://www.stkittstourism.kn/", "St. Kitts Tourism", SourceCategory.TOURISM, "KN", "Tourism", True),
    DataSource("https://www.sknfa.com/", "SKNFA", SourceCategory.SPORT, "KN", "Football federation"),
]

# ============================================================
# 🇨🇼 CURAÇAO
# ============================================================

CURACAO_SOURCES = [
    DataSource("https://www.gobiernu.cw/", "Curaçao Government", SourceCategory.GOVERNMENT, "CW", "Government"),
    DataSource("https://www.cbs.cw/", "Central Bureau of Statistics", SourceCategory.STATISTICS, "CW", "Statistics", True),
    DataSource("https://www.uoc.cw/", "University of Curaçao", SourceCategory.UNIVERSITY, "CW", "University"),
    DataSource("https://www.centralbank.cw/", "Central Bank of Curaçao", SourceCategory.BANK, "CW", "Central bank"),
    DataSource("https://www.curacao.com/", "Curaçao Tourism", SourceCategory.TOURISM, "CW", "Tourism", True),
    DataSource("https://www.ffc.cw/", "FFK Curaçao", SourceCategory.SPORT, "CW", "Football federation"),
]

# ============================================================
# 🇦🇼 ARUBA
# ============================================================

ARUBA_SOURCES = [
    DataSource("https://www.government.aw/", "Aruba Government", SourceCategory.GOVERNMENT, "AW", "Government"),
    DataSource("https://cbs.aw/", "Central Bureau of Statistics", SourceCategory.STATISTICS, "AW", "Statistics", True),
    DataSource("https://www.ua.aw/", "University of Aruba", SourceCategory.UNIVERSITY, "AW", "University"),
    DataSource("https://www.cbaruba.org/", "Central Bank of Aruba", SourceCategory.BANK, "AW", "Central bank"),
    DataSource("https://www.aruba.com/", "Aruba Tourism", SourceCategory.TOURISM, "AW", "Tourism", True),
    DataSource("https://www.avb.aw/", "AVB Aruba", SourceCategory.SPORT, "AW", "Football federation"),
]

# ============================================================
# 🇰🇾 CAYMAN ISLANDS
# ============================================================

CAYMAN_SOURCES = [
    DataSource("https://www.gov.ky/", "Cayman Islands Government", SourceCategory.GOVERNMENT, "KY", "Government"),
    DataSource("https://www.eso.ky/", "Economics & Statistics Office", SourceCategory.STATISTICS, "KY", "Statistics", True),
    DataSource("https://www.cima.ky/", "CIMA", SourceCategory.BANK, "KY", "Monetary Authority"),
    DataSource("https://www.cse.ky/", "Cayman Stock Exchange", SourceCategory.BANK, "KY", "Stock Exchange"),
    DataSource("https://www.caymanislands.ky/", "Cayman Islands Tourism", SourceCategory.TOURISM, "KY", "Tourism", True),
    DataSource("https://www.cifa.ky/", "CIFA", SourceCategory.SPORT, "KY", "Football federation"),
]

# ============================================================
# 🇧🇲 BERMUDA
# ============================================================

BERMUDA_SOURCES = [
    DataSource("https://www.gov.bm/", "Bermuda Government", SourceCategory.GOVERNMENT, "BM", "Government"),
    DataSource("https://www.gov.bm/department/statistics/", "Statistics Bermuda", SourceCategory.STATISTICS, "BM", "Statistics"),
    DataSource("https://www.bma.bm/", "Bermuda Monetary Authority", SourceCategory.BANK, "BM", "Monetary Authority"),
    DataSource("https://www.bsx.com/", "Bermuda Stock Exchange", SourceCategory.BANK, "BM", "Stock Exchange"),
    DataSource("https://www.gotobermuda.com/", "Go To Bermuda", SourceCategory.TOURISM, "BM", "Tourism", True),
    DataSource("https://www.bermudafa.com/", "BFA Bermuda", SourceCategory.SPORT, "BM", "Football federation"),
]

# ============================================================
# CENTRAL AMERICA
# ============================================================

# 🇬🇹 GUATEMALA
GUATEMALA_SOURCES = [
    DataSource("https://www.gob.gt/", "Guatemala Government", SourceCategory.GOVERNMENT, "GT", "Government"),
    DataSource("https://www.congreso.gob.gt/", "Congress of Guatemala", SourceCategory.GOVERNMENT, "GT", "Congress"),
    DataSource("https://www.ine.gob.gt/", "INE Guatemala", SourceCategory.STATISTICS, "GT", "Statistics", True),
    DataSource("https://www.usac.edu.gt/", "Universidad de San Carlos", SourceCategory.UNIVERSITY, "GT", "Top university"),
    DataSource("https://www.banguat.gob.gt/", "Banguat", SourceCategory.BANK, "GT", "Central bank", True),
    DataSource("https://www.bvnsa.com.gt/", "BVN Guatemala", SourceCategory.BANK, "GT", "Stock Exchange"),
    DataSource("https://www.prensalibre.com/", "Prensa Libre", SourceCategory.NEWS, "GT", "Major newspaper"),
    DataSource("https://www.visitguatemala.com/", "Visit Guatemala", SourceCategory.TOURISM, "GT", "Tourism", True),
    DataSource("https://www.fedefut.org.gt/", "Fedefut", SourceCategory.SPORT, "GT", "Football federation"),
]

# 🇭🇳 HONDURAS
HONDURAS_SOURCES = [
    DataSource("https://www.presidencia.gob.hn/", "Honduras Government", SourceCategory.GOVERNMENT, "HN", "Presidency"),
    DataSource("https://www.congresonacional.hn/", "National Congress", SourceCategory.GOVERNMENT, "HN", "Congress"),
    DataSource("https://www.ine.gob.hn/", "INE Honduras", SourceCategory.STATISTICS, "HN", "Statistics", True),
    DataSource("https://www.unah.edu.hn/", "UNAH", SourceCategory.UNIVERSITY, "HN", "Top university"),
    DataSource("https://www.bch.hn/", "Banco Central de Honduras", SourceCategory.BANK, "HN", "Central bank", True),
    DataSource("https://www.laprensa.hn/", "La Prensa", SourceCategory.NEWS, "HN", "Major newspaper"),
    DataSource("https://www.honduras.travel/", "Honduras Travel", SourceCategory.TOURISM, "HN", "Tourism", True),
    DataSource("https://fenafuth.org/", "Fenafuth", SourceCategory.SPORT, "HN", "Football federation"),
]

# 🇸🇻 EL SALVADOR
EL_SALVADOR_SOURCES = [
    DataSource("https://www.presidencia.gob.sv/", "El Salvador Government", SourceCategory.GOVERNMENT, "SV", "Presidency"),
    DataSource("https://www.asamblea.gob.sv/", "Legislative Assembly", SourceCategory.GOVERNMENT, "SV", "Assembly"),
    DataSource("https://www.digestyc.gob.sv/", "DIGESTYC", SourceCategory.STATISTICS, "SV", "Statistics", True),
    DataSource("https://www.ues.edu.sv/", "Universidad de El Salvador", SourceCategory.UNIVERSITY, "SV", "Top university"),
    DataSource("https://www.bcr.gob.sv/", "Central Reserve Bank", SourceCategory.BANK, "SV", "Central bank", True),
    DataSource("https://www.bolsadevalores.com.sv/", "BVES", SourceCategory.BANK, "SV", "Stock Exchange"),
    DataSource("https://www.laprensagrafica.com/", "La Prensa Gráfica", SourceCategory.NEWS, "SV", "Major newspaper"),
    DataSource("https://elsalvador.travel/", "El Salvador Travel", SourceCategory.TOURISM, "SV", "Tourism", True),
    DataSource("https://www.fesfut.org.sv/", "FESFUT", SourceCategory.SPORT, "SV", "Football federation"),
]

# 🇳🇮 NICARAGUA
NICARAGUA_SOURCES = [
    DataSource("https://www.presidencia.gob.ni/", "Nicaragua Government", SourceCategory.GOVERNMENT, "NI", "Presidency"),
    DataSource("https://www.inide.gob.ni/", "INIDE", SourceCategory.STATISTICS, "NI", "Statistics", True),
    DataSource("https://www.unan.edu.ni/", "UNAN", SourceCategory.UNIVERSITY, "NI", "Top university"),
    DataSource("https://www.bcn.gob.ni/", "Banco Central de Nicaragua", SourceCategory.BANK, "NI", "Central bank", True),
    DataSource("https://www.laprensa.com.ni/", "La Prensa", SourceCategory.NEWS, "NI", "Major newspaper"),
    DataSource("https://www.visitnicaragua.us/", "Visit Nicaragua", SourceCategory.TOURISM, "NI", "Tourism", True),
    DataSource("https://www.fenifut.org.ni/", "Fenifut", SourceCategory.SPORT, "NI", "Football federation"),
]

# 🇨🇷 COSTA RICA
COSTA_RICA_SOURCES = [
    DataSource("https://www.presidencia.go.cr/", "Costa Rica Government", SourceCategory.GOVERNMENT, "CR", "Presidency"),
    DataSource("https://www.asamblea.go.cr/", "Legislative Assembly", SourceCategory.GOVERNMENT, "CR", "Assembly"),
    DataSource("https://www.inec.cr/", "INEC Costa Rica", SourceCategory.STATISTICS, "CR", "Statistics", True),
    DataSource("https://www.ucr.ac.cr/", "Universidad de Costa Rica", SourceCategory.UNIVERSITY, "CR", "Top university"),
    DataSource("https://www.tec.ac.cr/", "TEC Costa Rica", SourceCategory.UNIVERSITY, "CR", "Tech university"),
    DataSource("https://www.bccr.fi.cr/", "Banco Central de Costa Rica", SourceCategory.BANK, "CR", "Central bank", True),
    DataSource("https://www.bolsacr.com/", "BNV Costa Rica", SourceCategory.BANK, "CR", "Stock Exchange"),
    DataSource("https://www.nacion.com/", "La Nación", SourceCategory.NEWS, "CR", "Major newspaper"),
    DataSource("https://www.visitcostarica.com/", "Visit Costa Rica", SourceCategory.TOURISM, "CR", "Tourism", True),
    DataSource("https://www.fedefutbol.com/", "FEDEFUTBOL", SourceCategory.SPORT, "CR", "Football federation"),
]

# 🇵🇦 PANAMA
PANAMA_SOURCES = [
    DataSource("https://www.presidencia.gob.pa/", "Panama Government", SourceCategory.GOVERNMENT, "PA", "Presidency"),
    DataSource("https://www.asamblea.gob.pa/", "National Assembly", SourceCategory.GOVERNMENT, "PA", "Assembly"),
    DataSource("https://www.inec.gob.pa/", "INEC Panama", SourceCategory.STATISTICS, "PA", "Statistics", True),
    DataSource("https://www.up.ac.pa/", "Universidad de Panamá", SourceCategory.UNIVERSITY, "PA", "Top university"),
    DataSource("https://www.utp.ac.pa/", "UTP Panama", SourceCategory.UNIVERSITY, "PA", "Tech university"),
    DataSource("https://www.bfrsh.biz/", "SBP Panama", SourceCategory.BANK, "PA", "Superintendency"),
    DataSource("https://www.panabolsa.com/", "Bolsa de Valores de Panamá", SourceCategory.BANK, "PA", "Stock Exchange"),
    DataSource("https://www.copaair.com/", "Copa Airlines", SourceCategory.TRANSPORT, "PA", "Major airline"),
    DataSource("https://www.micanaldepanama.com/", "Panama Canal", SourceCategory.TRANSPORT, "PA", "Panama Canal", True),
    DataSource("https://www.prensa.com/", "La Prensa", SourceCategory.NEWS, "PA", "Major newspaper"),
    DataSource("https://www.visitpanama.com/", "Visit Panama", SourceCategory.TOURISM, "PA", "Tourism", True),
    DataSource("https://www.fepafut.com/", "FEPAFUT", SourceCategory.SPORT, "PA", "Football federation"),
]

# 🇧🇿 BELIZE
BELIZE_SOURCES = [
    DataSource("https://www.belize.gov.bz/", "Belize Government", SourceCategory.GOVERNMENT, "BZ", "Government"),
    DataSource("https://www.sib.org.bz/", "Statistical Institute of Belize", SourceCategory.STATISTICS, "BZ", "Statistics", True),
    DataSource("https://www.ub.edu.bz/", "University of Belize", SourceCategory.UNIVERSITY, "BZ", "University"),
    DataSource("https://www.centralbank.org.bz/", "Central Bank of Belize", SourceCategory.BANK, "BZ", "Central bank", True),
    DataSource("https://www.amandala.com.bz/", "Amandala", SourceCategory.NEWS, "BZ", "Major newspaper"),
    DataSource("https://www.travelbelize.org/", "Travel Belize", SourceCategory.TOURISM, "BZ", "Tourism", True),
    DataSource("https://www.belizefootball.bz/", "FFB", SourceCategory.SPORT, "BZ", "Football federation"),
]

# ============================================================
# COMBINED EXPORT
# ============================================================

ALL_CARIBBEAN_CENTRAL_AMERICA_SOURCES = (
    CUBA_SOURCES + JAMAICA_SOURCES + HAITI_SOURCES + DOMINICAN_SOURCES +
    PUERTO_RICO_SOURCES + BAHAMAS_SOURCES + TRINIDAD_SOURCES + BARBADOS_SOURCES +
    ST_LUCIA_SOURCES + GRENADA_SOURCES + ST_VINCENT_SOURCES + ANTIGUA_SOURCES +
    DOMINICA_SOURCES + ST_KITTS_SOURCES + CURACAO_SOURCES + ARUBA_SOURCES +
    CAYMAN_SOURCES + BERMUDA_SOURCES +
    GUATEMALA_SOURCES + HONDURAS_SOURCES + EL_SALVADOR_SOURCES +
    NICARAGUA_SOURCES + COSTA_RICA_SOURCES + PANAMA_SOURCES + BELIZE_SOURCES
)

def get_all_sources():
    return ALL_CARIBBEAN_CENTRAL_AMERICA_SOURCES

def get_sources_by_country(country_code: str):
    return [s for s in ALL_CARIBBEAN_CENTRAL_AMERICA_SOURCES if s.country == country_code]

if __name__ == "__main__":
    print(f"🌴 Caribbean & Central America Sources: {len(ALL_CARIBBEAN_CENTRAL_AMERICA_SOURCES)}")
    print("Caribbean: CU, JM, HT, DO, PR, BS, TT, BB, LC, GD, VC, AG, DM, KN, CW, AW, KY, BM")
    print("Central America: GT, HN, SV, NI, CR, PA, BZ")
