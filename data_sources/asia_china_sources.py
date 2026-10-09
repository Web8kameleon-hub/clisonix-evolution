# -*- coding: utf-8 -*-
"""
🇨🇳 CHINA & EAST ASIA - COMPLETE DATA SOURCES
================================================
800+ Free Open Data Sources from China, Japan, Korea, Taiwan, Hong Kong, Mongolia

Categories:
- Government & Statistics
- Universities & Research
- Hospitals & Healthcare  
- Banks & Financial
- Factories & Industrial
- News & Media
- Culture & Museums
- Rating Agencies
- Information Centers
"""

from dataclasses import dataclass
from enum import Enum
from typing import List


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
# 🇨🇳 CHINA - PEOPLE'S REPUBLIC OF CHINA
# ============================================================

CHINA_GOVERNMENT = [
    DataSource("https://data.stats.gov.cn/", "National Bureau of Statistics China", SourceCategory.STATISTICS, "CN", "Official statistics", True),
    DataSource("http://www.gov.cn/", "State Council of China", SourceCategory.GOVERNMENT, "CN", "Government portal"),
    DataSource("http://www.mof.gov.cn/", "Ministry of Finance China", SourceCategory.GOVERNMENT, "CN", "Financial data"),
    DataSource("http://www.moe.gov.cn/", "Ministry of Education China", SourceCategory.GOVERNMENT, "CN", "Education data"),
    DataSource("http://www.nhc.gov.cn/", "National Health Commission", SourceCategory.GOVERNMENT, "CN", "Health data"),
    DataSource("http://www.miit.gov.cn/", "Ministry of Industry & IT", SourceCategory.GOVERNMENT, "CN", "Industrial data"),
    DataSource("http://www.moa.gov.cn/", "Ministry of Agriculture", SourceCategory.AGRICULTURE, "CN", "Agriculture data"),
    DataSource("http://www.mee.gov.cn/", "Ministry of Ecology & Environment", SourceCategory.ENVIRONMENTAL, "CN", "Environmental data"),
    DataSource("http://www.mot.gov.cn/", "Ministry of Transport", SourceCategory.TRANSPORT, "CN", "Transport data"),
    DataSource("http://www.nea.gov.cn/", "National Energy Administration", SourceCategory.ENERGY, "CN", "Energy data"),
    DataSource("http://www.safe.gov.cn/", "State Administration of Foreign Exchange", SourceCategory.BANK, "CN", "Forex data", True),
    DataSource("http://www.chinatax.gov.cn/", "State Taxation Administration", SourceCategory.GOVERNMENT, "CN", "Tax data"),
    DataSource("http://www.customs.gov.cn/", "General Administration of Customs", SourceCategory.GOVERNMENT, "CN", "Trade data", True),
    DataSource("http://www.samr.gov.cn/", "State Administration Market Regulation", SourceCategory.GOVERNMENT, "CN", "Business data"),
    DataSource("http://www.cma.gov.cn/", "China Meteorological Administration", SourceCategory.ENVIRONMENTAL, "CN", "Weather data", True),
    DataSource("http://www.cea.gov.cn/", "China Earthquake Administration", SourceCategory.RESEARCH, "CN", "Seismic data"),
    DataSource("http://www.cnsa.gov.cn/", "China National Space Administration", SourceCategory.RESEARCH, "CN", "Space data"),
    DataSource("http://www.sastind.gov.cn/", "State Admin Science Technology", SourceCategory.RESEARCH, "CN", "Science data"),
    DataSource("https://data.beijing.gov.cn/", "Beijing Open Data", SourceCategory.GOVERNMENT, "CN", "Beijing data", True),
    DataSource("https://data.sh.gov.cn/", "Shanghai Open Data", SourceCategory.GOVERNMENT, "CN", "Shanghai data", True),
    DataSource("https://opendata.sz.gov.cn/", "Shenzhen Open Data", SourceCategory.GOVERNMENT, "CN", "Shenzhen data", True),
    DataSource("https://data.gd.gov.cn/", "Guangdong Open Data", SourceCategory.GOVERNMENT, "CN", "Guangdong data", True),
    DataSource("https://data.zj.gov.cn/", "Zhejiang Open Data", SourceCategory.GOVERNMENT, "CN", "Zhejiang data", True),
    DataSource("https://data.js.gov.cn/", "Jiangsu Open Data", SourceCategory.GOVERNMENT, "CN", "Jiangsu data", True),
    DataSource("https://data.sd.gov.cn/", "Shandong Open Data", SourceCategory.GOVERNMENT, "CN", "Shandong data", True),
    DataSource("https://data.fj.gov.cn/", "Fujian Open Data", SourceCategory.GOVERNMENT, "CN", "Fujian data", True),
    DataSource("https://data.sc.gov.cn/", "Sichuan Open Data", SourceCategory.GOVERNMENT, "CN", "Sichuan data", True),
    DataSource("https://data.hn.gov.cn/", "Hunan Open Data", SourceCategory.GOVERNMENT, "CN", "Hunan data", True),
    DataSource("https://data.hb.gov.cn/", "Hubei Open Data", SourceCategory.GOVERNMENT, "CN", "Hubei data", True),
    DataSource("https://data.cq.gov.cn/", "Chongqing Open Data", SourceCategory.GOVERNMENT, "CN", "Chongqing data", True),
]

CHINA_UNIVERSITIES = [
    DataSource("https://www.tsinghua.edu.cn/", "Tsinghua University", SourceCategory.UNIVERSITY, "CN", "Top university"),
    DataSource("https://www.pku.edu.cn/", "Peking University", SourceCategory.UNIVERSITY, "CN", "Top university"),
    DataSource("https://www.fudan.edu.cn/", "Fudan University", SourceCategory.UNIVERSITY, "CN", "Shanghai"),
    DataSource("https://www.sjtu.edu.cn/", "Shanghai Jiao Tong University", SourceCategory.UNIVERSITY, "CN", "Engineering"),
    DataSource("https://www.zju.edu.cn/", "Zhejiang University", SourceCategory.UNIVERSITY, "CN", "Research"),
    DataSource("https://www.ustc.edu.cn/", "University of Science & Technology China", SourceCategory.UNIVERSITY, "CN", "Science"),
    DataSource("https://www.nju.edu.cn/", "Nanjing University", SourceCategory.UNIVERSITY, "CN", "Research"),
    DataSource("https://www.whu.edu.cn/", "Wuhan University", SourceCategory.UNIVERSITY, "CN", "Research"),
    DataSource("https://www.sysu.edu.cn/", "Sun Yat-sen University", SourceCategory.UNIVERSITY, "CN", "Guangzhou"),
    DataSource("https://www.hust.edu.cn/", "Huazhong University Science Technology", SourceCategory.UNIVERSITY, "CN", "Technology"),
    DataSource("https://www.hit.edu.cn/", "Harbin Institute of Technology", SourceCategory.UNIVERSITY, "CN", "Engineering"),
    DataSource("https://www.xjtu.edu.cn/", "Xi'an Jiaotong University", SourceCategory.UNIVERSITY, "CN", "Engineering"),
    DataSource("https://www.sdu.edu.cn/", "Shandong University", SourceCategory.UNIVERSITY, "CN", "Research"),
    DataSource("https://www.cuhk.edu.cn/", "Chinese University Hong Kong Shenzhen", SourceCategory.UNIVERSITY, "CN", "Research"),
    DataSource("https://www.sustech.edu.cn/", "Southern University Science Technology", SourceCategory.UNIVERSITY, "CN", "Innovation"),
    DataSource("https://www.bit.edu.cn/", "Beijing Institute of Technology", SourceCategory.UNIVERSITY, "CN", "Technology"),
    DataSource("https://www.buaa.edu.cn/", "Beihang University", SourceCategory.UNIVERSITY, "CN", "Aerospace"),
    DataSource("https://www.tongji.edu.cn/", "Tongji University", SourceCategory.UNIVERSITY, "CN", "Engineering"),
    DataSource("https://www.seu.edu.cn/", "Southeast University", SourceCategory.UNIVERSITY, "CN", "Engineering"),
    DataSource("https://www.nankai.edu.cn/", "Nankai University", SourceCategory.UNIVERSITY, "CN", "Research"),
    DataSource("https://www.tju.edu.cn/", "Tianjin University", SourceCategory.UNIVERSITY, "CN", "Engineering"),
    DataSource("https://www.dlut.edu.cn/", "Dalian University of Technology", SourceCategory.UNIVERSITY, "CN", "Engineering"),
    DataSource("https://www.jlu.edu.cn/", "Jilin University", SourceCategory.UNIVERSITY, "CN", "Research"),
    DataSource("https://www.cau.edu.cn/", "China Agricultural University", SourceCategory.UNIVERSITY, "CN", "Agriculture"),
    DataSource("https://www.ruc.edu.cn/", "Renmin University of China", SourceCategory.UNIVERSITY, "CN", "Social Science"),
]

CHINA_HOSPITALS = [
    DataSource("https://www.pumch.cn/", "Peking Union Medical College Hospital", SourceCategory.HOSPITAL, "CN", "Top hospital"),
    DataSource("https://www.301hospital.com.cn/", "PLA General Hospital (301)", SourceCategory.HOSPITAL, "CN", "Military hospital"),
    DataSource("https://www.pkuph.cn/", "Peking University People's Hospital", SourceCategory.HOSPITAL, "CN", "Teaching hospital"),
    DataSource("https://www.xhyy.com.cn/", "Xiehe Hospital Wuhan", SourceCategory.HOSPITAL, "CN", "Central China"),
    DataSource("https://www.shsmu.edu.cn/", "Shanghai Medical University Hospitals", SourceCategory.HOSPITAL, "CN", "Shanghai"),
    DataSource("https://www.zs-hospital.sh.cn/", "Zhongshan Hospital Fudan", SourceCategory.HOSPITAL, "CN", "Shanghai"),
    DataSource("https://www.huashan.org.cn/", "Huashan Hospital Fudan", SourceCategory.HOSPITAL, "CN", "Neurology"),
    DataSource("https://www.xyeyy.com/", "Xiangya Hospital", SourceCategory.HOSPITAL, "CN", "Hunan"),
    DataSource("https://www.srrsh.com/", "Sir Run Run Shaw Hospital", SourceCategory.HOSPITAL, "CN", "Zhejiang"),
    DataSource("https://www.shchildren.com.cn/", "Shanghai Children's Hospital", SourceCategory.HOSPITAL, "CN", "Pediatric"),
    DataSource("https://www.syshospital.com/", "First Affiliated Hospital Sun Yat-sen", SourceCategory.HOSPITAL, "CN", "Guangzhou"),
    DataSource("https://www.hzgh.com/", "Hangzhou First People's Hospital", SourceCategory.HOSPITAL, "CN", "Hangzhou"),
    DataSource("https://www.bjcancer.org/", "Beijing Cancer Hospital", SourceCategory.HOSPITAL, "CN", "Oncology"),
    DataSource("https://www.fuwai.com/", "Fuwai Hospital", SourceCategory.HOSPITAL, "CN", "Cardiology"),
    DataSource("https://www.puth.net.cn/", "Peking University Third Hospital", SourceCategory.HOSPITAL, "CN", "Sports Medicine"),
]

CHINA_BANKS = [
    DataSource("http://www.pbc.gov.cn/", "People's Bank of China (PBOC)", SourceCategory.BANK, "CN", "Central Bank", True),
    DataSource("https://www.icbc.com.cn/", "ICBC - Industrial Commercial Bank", SourceCategory.BANK, "CN", "Largest bank"),
    DataSource("https://www.ccb.com/", "China Construction Bank", SourceCategory.BANK, "CN", "Big 4"),
    DataSource("https://www.abchina.com/", "Agricultural Bank of China", SourceCategory.BANK, "CN", "Big 4"),
    DataSource("https://www.boc.cn/", "Bank of China", SourceCategory.BANK, "CN", "Big 4"),
    DataSource("https://www.cmbchina.com/", "China Merchants Bank", SourceCategory.BANK, "CN", "Private bank"),
    DataSource("https://www.bankcomm.com/", "Bank of Communications", SourceCategory.BANK, "CN", "State bank"),
    DataSource("https://www.citic.com/", "CITIC Bank", SourceCategory.BANK, "CN", "Investment"),
    DataSource("https://www.pingan.cn/", "Ping An Bank", SourceCategory.BANK, "CN", "Insurance bank"),
    DataSource("https://www.spdb.com.cn/", "Shanghai Pudong Development Bank", SourceCategory.BANK, "CN", "Shanghai"),
    DataSource("https://www.cib.com.cn/", "Industrial Bank", SourceCategory.BANK, "CN", "Commercial"),
    DataSource("https://www.cebbank.com/", "China Everbright Bank", SourceCategory.BANK, "CN", "Commercial"),
    DataSource("https://www.psbc.com/", "Postal Savings Bank China", SourceCategory.BANK, "CN", "Postal"),
    DataSource("http://www.cdb.com.cn/", "China Development Bank", SourceCategory.BANK, "CN", "Policy bank"),
    DataSource("http://www.eximbank.gov.cn/", "Export-Import Bank China", SourceCategory.BANK, "CN", "Trade finance"),
    DataSource("http://www.adbc.com.cn/", "Agricultural Development Bank", SourceCategory.BANK, "CN", "Agricultural finance"),
    DataSource("http://www.cbrc.gov.cn/", "China Banking Regulatory Commission", SourceCategory.RATING, "CN", "Bank regulator"),
    DataSource("http://www.csrc.gov.cn/", "China Securities Regulatory Commission", SourceCategory.RATING, "CN", "Securities regulator", True),
    DataSource("http://www.circ.gov.cn/", "China Insurance Regulatory Commission", SourceCategory.RATING, "CN", "Insurance regulator"),
]

CHINA_FACTORIES_INDUSTRIAL = [
    DataSource("https://www.sinopec.com/", "Sinopec", SourceCategory.FACTORY, "CN", "Oil & Petrochemical"),
    DataSource("https://www.cnpc.com.cn/", "China National Petroleum Corporation", SourceCategory.FACTORY, "CN", "Oil & Gas"),
    DataSource("https://www.cnooc.com.cn/", "CNOOC", SourceCategory.FACTORY, "CN", "Offshore Oil"),
    DataSource("https://www.sgcc.com.cn/", "State Grid Corporation", SourceCategory.ENERGY, "CN", "Power Grid"),
    DataSource("https://www.csg.cn/", "China Southern Power Grid", SourceCategory.ENERGY, "CN", "Power Grid"),
    DataSource("https://www.baogang.com.cn/", "Baosteel Group", SourceCategory.FACTORY, "CN", "Steel"),
    DataSource("https://www.hbisco.com/", "Hebei Iron and Steel", SourceCategory.FACTORY, "CN", "Steel"),
    DataSource("https://www.chinalco.com.cn/", "Aluminum Corporation of China", SourceCategory.FACTORY, "CN", "Aluminum"),
    DataSource("https://www.chalco.com.cn/", "Chalco", SourceCategory.FACTORY, "CN", "Metals"),
    DataSource("https://www.sinochem.com/", "Sinochem", SourceCategory.FACTORY, "CN", "Chemicals"),
    DataSource("https://www.cofco.com/", "COFCO", SourceCategory.FACTORY, "CN", "Food Processing"),
    DataSource("https://www.chemchina.com.cn/", "ChemChina", SourceCategory.FACTORY, "CN", "Chemicals"),
    DataSource("https://www.cscec.com/", "China State Construction", SourceCategory.FACTORY, "CN", "Construction"),
    DataSource("https://www.crec.cn/", "China Railway Engineering", SourceCategory.FACTORY, "CN", "Railway"),
    DataSource("https://www.crcc.cn/", "China Railway Construction", SourceCategory.FACTORY, "CN", "Construction"),
    DataSource("https://www.ccccltd.cn/", "China Communications Construction", SourceCategory.FACTORY, "CN", "Infrastructure"),
    DataSource("https://www.comac.cc/", "COMAC", SourceCategory.FACTORY, "CN", "Aircraft"),
    DataSource("https://www.avic.com/", "AVIC", SourceCategory.FACTORY, "CN", "Aviation Industry"),
    DataSource("https://www.norinco.com/", "NORINCO", SourceCategory.FACTORY, "CN", "Defense"),
    DataSource("https://www.casic.cn/", "CASIC", SourceCategory.FACTORY, "CN", "Aerospace"),
    DataSource("https://www.casc.cn/", "CASC", SourceCategory.FACTORY, "CN", "Space"),
    DataSource("https://www.saic.com.cn/", "SAIC Motor", SourceCategory.FACTORY, "CN", "Automotive"),
    DataSource("https://www.dongfeng.com/", "Dongfeng Motor", SourceCategory.FACTORY, "CN", "Automotive"),
    DataSource("https://www.faw.com/", "FAW Group", SourceCategory.FACTORY, "CN", "Automotive"),
    DataSource("https://www.gac.com.cn/", "GAC Group", SourceCategory.FACTORY, "CN", "Automotive"),
    DataSource("https://www.byd.com/", "BYD", SourceCategory.FACTORY, "CN", "Electric Vehicles"),
    DataSource("https://www.geelycv.com/", "Geely", SourceCategory.FACTORY, "CN", "Automotive"),
    DataSource("https://www.catl.com/", "CATL", SourceCategory.FACTORY, "CN", "Batteries"),
    DataSource("https://www.huawei.com/", "Huawei", SourceCategory.FACTORY, "CN", "Telecom Equipment"),
    DataSource("https://www.zte.com.cn/", "ZTE", SourceCategory.TELECOM, "CN", "Telecom Equipment"),
    DataSource("https://www.mi.com/", "Xiaomi", SourceCategory.FACTORY, "CN", "Electronics"),
    DataSource("https://www.oppo.com/", "OPPO", SourceCategory.FACTORY, "CN", "Electronics"),
    DataSource("https://www.vivo.com/", "Vivo", SourceCategory.FACTORY, "CN", "Electronics"),
    DataSource("https://www.lenovo.com/", "Lenovo", SourceCategory.FACTORY, "CN", "Computers"),
    DataSource("https://www.haier.com/", "Haier", SourceCategory.FACTORY, "CN", "Appliances"),
    DataSource("https://www.midea.com/", "Midea", SourceCategory.FACTORY, "CN", "Appliances"),
    DataSource("https://www.gree.com/", "Gree Electric", SourceCategory.FACTORY, "CN", "Air Conditioning"),
    DataSource("https://www.tcl.com/", "TCL", SourceCategory.FACTORY, "CN", "Electronics"),
    DataSource("https://www.smic.com/", "SMIC", SourceCategory.FACTORY, "CN", "Semiconductors"),
    DataSource("https://www.semiconductor-manufacturing.com/", "Hua Hong Semiconductor", SourceCategory.FACTORY, "CN", "Semiconductors"),
]

CHINA_NEWS_MEDIA = [
    DataSource("http://www.xinhuanet.com/", "Xinhua News Agency", SourceCategory.NEWS, "CN", "State news agency"),
    DataSource("http://www.people.com.cn/", "People's Daily", SourceCategory.NEWS, "CN", "Party newspaper"),
    DataSource("http://www.chinadaily.com.cn/", "China Daily", SourceCategory.NEWS, "CN", "English news"),
    DataSource("http://www.cctv.com/", "CCTV", SourceCategory.NEWS, "CN", "State TV"),
    DataSource("http://www.cnr.cn/", "China National Radio", SourceCategory.NEWS, "CN", "State radio"),
    DataSource("https://www.cgtn.com/", "CGTN", SourceCategory.NEWS, "CN", "Global TV network"),
    DataSource("https://www.thepaper.cn/", "The Paper", SourceCategory.NEWS, "CN", "Digital news"),
    DataSource("https://www.caixin.com/", "Caixin", SourceCategory.NEWS, "CN", "Financial news"),
    DataSource("https://www.yicai.com/", "Yicai", SourceCategory.NEWS, "CN", "Financial news"),
    DataSource("https://www.jiemian.com/", "Jiemian", SourceCategory.NEWS, "CN", "Business news"),
    DataSource("https://www.ifeng.com/", "Phoenix New Media", SourceCategory.NEWS, "CN", "News portal"),
    DataSource("https://www.sina.com.cn/", "Sina", SourceCategory.NEWS, "CN", "News portal"),
    DataSource("https://www.sohu.com/", "Sohu", SourceCategory.NEWS, "CN", "News portal"),
    DataSource("https://www.163.com/", "NetEase", SourceCategory.NEWS, "CN", "News portal"),
    DataSource("https://www.qq.com/", "QQ/Tencent News", SourceCategory.NEWS, "CN", "News portal"),
]

CHINA_CULTURE = [
    DataSource("http://www.dpm.org.cn/", "Palace Museum (Forbidden City)", SourceCategory.CULTURE, "CN", "Imperial museum"),
    DataSource("http://www.chnmuseum.cn/", "National Museum of China", SourceCategory.CULTURE, "CN", "National museum"),
    DataSource("http://www.nlc.cn/", "National Library of China", SourceCategory.CULTURE, "CN", "National library"),
    DataSource("http://www.shanghaimuseum.net/", "Shanghai Museum", SourceCategory.CULTURE, "CN", "Art museum"),
    DataSource("http://www.gdmuseum.com/", "Guangdong Museum", SourceCategory.CULTURE, "CN", "Regional museum"),
    DataSource("http://www.zjmuseum.com/", "Zhejiang Museum", SourceCategory.CULTURE, "CN", "Regional museum"),
    DataSource("http://www.namoc.org/", "National Art Museum of China", SourceCategory.CULTURE, "CN", "Art museum"),
    DataSource("http://www.ucca.org.cn/", "UCCA Center for Contemporary Art", SourceCategory.CULTURE, "CN", "Contemporary art"),
    DataSource("http://www.powerstationofart.com/", "Power Station of Art Shanghai", SourceCategory.CULTURE, "CN", "Contemporary art"),
    DataSource("http://www.cafa.edu.cn/", "Central Academy of Fine Arts", SourceCategory.CULTURE, "CN", "Art education"),
    DataSource("http://www.ccnt.com.cn/", "China Cultural Heritage", SourceCategory.CULTURE, "CN", "Heritage"),
]

CHINA_RESEARCH_INSTITUTES = [
    DataSource("http://www.cas.cn/", "Chinese Academy of Sciences", SourceCategory.RESEARCH, "CN", "Science research", True),
    DataSource("http://www.cass.cn/", "Chinese Academy of Social Sciences", SourceCategory.RESEARCH, "CN", "Social research"),
    DataSource("http://www.cae.cn/", "Chinese Academy of Engineering", SourceCategory.RESEARCH, "CN", "Engineering"),
    DataSource("http://www.nsfc.gov.cn/", "National Natural Science Foundation", SourceCategory.RESEARCH, "CN", "Science funding", True),
    DataSource("http://www.ihep.cas.cn/", "Institute of High Energy Physics", SourceCategory.RESEARCH, "CN", "Physics"),
    DataSource("http://www.itp.cas.cn/", "Institute of Theoretical Physics", SourceCategory.RESEARCH, "CN", "Physics"),
    DataSource("http://www.bgi.com/", "BGI Genomics", SourceCategory.RESEARCH, "CN", "Genomics", True),
    DataSource("http://www.sibs.cas.cn/", "Shanghai Institutes for Biological Sciences", SourceCategory.RESEARCH, "CN", "Biology"),
    DataSource("http://www.ibp.cas.cn/", "Institute of Biophysics", SourceCategory.RESEARCH, "CN", "Biophysics"),
    DataSource("http://www.ioz.cas.cn/", "Institute of Zoology", SourceCategory.RESEARCH, "CN", "Zoology"),
    DataSource("http://www.genetics.cas.cn/", "Institute of Genetics", SourceCategory.RESEARCH, "CN", "Genetics"),
    DataSource("http://www.ia.cas.cn/", "Institute of Automation", SourceCategory.RESEARCH, "CN", "AI Research"),
    DataSource("http://www.ict.cas.cn/", "Institute of Computing Technology", SourceCategory.RESEARCH, "CN", "Computing"),
    DataSource("http://www.is.cas.cn/", "Institute of Software", SourceCategory.RESEARCH, "CN", "Software"),
    DataSource("http://www.semi.cas.cn/", "Institute of Semiconductors", SourceCategory.RESEARCH, "CN", "Semiconductors"),
]

# ============================================================
# 🇯🇵 JAPAN
# ============================================================

JAPAN_GOVERNMENT = [
    DataSource("https://www.e-stat.go.jp/", "e-Stat Japan", SourceCategory.STATISTICS, "JP", "Official statistics", True),
    DataSource("https://www.data.go.jp/", "Data.go.jp", SourceCategory.GOVERNMENT, "JP", "Open data portal", True),
    DataSource("https://www.mof.go.jp/", "Ministry of Finance Japan", SourceCategory.GOVERNMENT, "JP", "Financial data"),
    DataSource("https://www.mhlw.go.jp/", "Ministry of Health Labour Welfare", SourceCategory.GOVERNMENT, "JP", "Health data", True),
    DataSource("https://www.mext.go.jp/", "Ministry of Education Japan", SourceCategory.GOVERNMENT, "JP", "Education data"),
    DataSource("https://www.meti.go.jp/", "Ministry of Economy Trade Industry", SourceCategory.GOVERNMENT, "JP", "Economic data", True),
    DataSource("https://www.maff.go.jp/", "Ministry of Agriculture Japan", SourceCategory.AGRICULTURE, "JP", "Agriculture data"),
    DataSource("https://www.mlit.go.jp/", "Ministry of Land Infrastructure Transport", SourceCategory.TRANSPORT, "JP", "Transport data"),
    DataSource("https://www.env.go.jp/", "Ministry of Environment Japan", SourceCategory.ENVIRONMENTAL, "JP", "Environmental data"),
    DataSource("https://www.jma.go.jp/", "Japan Meteorological Agency", SourceCategory.ENVIRONMENTAL, "JP", "Weather data", True),
    DataSource("https://www.stat.go.jp/", "Statistics Bureau Japan", SourceCategory.STATISTICS, "JP", "Demographics"),
    DataSource("https://www.cao.go.jp/", "Cabinet Office Japan", SourceCategory.GOVERNMENT, "JP", "Policy data"),
    DataSource("https://www.fsa.go.jp/", "Financial Services Agency Japan", SourceCategory.BANK, "JP", "Financial regulation"),
    DataSource("https://www.nta.go.jp/", "National Tax Agency Japan", SourceCategory.GOVERNMENT, "JP", "Tax data"),
    DataSource("https://www.jpo.go.jp/", "Japan Patent Office", SourceCategory.GOVERNMENT, "JP", "Patent data", True),
]

JAPAN_UNIVERSITIES = [
    DataSource("https://www.u-tokyo.ac.jp/", "University of Tokyo", SourceCategory.UNIVERSITY, "JP", "Top university"),
    DataSource("https://www.kyoto-u.ac.jp/", "Kyoto University", SourceCategory.UNIVERSITY, "JP", "Research university"),
    DataSource("https://www.osaka-u.ac.jp/", "Osaka University", SourceCategory.UNIVERSITY, "JP", "Research university"),
    DataSource("https://www.tohoku.ac.jp/", "Tohoku University", SourceCategory.UNIVERSITY, "JP", "Research university"),
    DataSource("https://www.nagoya-u.ac.jp/", "Nagoya University", SourceCategory.UNIVERSITY, "JP", "Research university"),
    DataSource("https://www.hokudai.ac.jp/", "Hokkaido University", SourceCategory.UNIVERSITY, "JP", "Research university"),
    DataSource("https://www.kyushu-u.ac.jp/", "Kyushu University", SourceCategory.UNIVERSITY, "JP", "Research university"),
    DataSource("https://www.titech.ac.jp/", "Tokyo Institute of Technology", SourceCategory.UNIVERSITY, "JP", "Technology"),
    DataSource("https://www.keio.ac.jp/", "Keio University", SourceCategory.UNIVERSITY, "JP", "Private university"),
    DataSource("https://www.waseda.jp/", "Waseda University", SourceCategory.UNIVERSITY, "JP", "Private university"),
    DataSource("https://www.tsukuba.ac.jp/", "University of Tsukuba", SourceCategory.UNIVERSITY, "JP", "Research"),
    DataSource("https://www.kobe-u.ac.jp/", "Kobe University", SourceCategory.UNIVERSITY, "JP", "Research"),
    DataSource("https://www.hiroshima-u.ac.jp/", "Hiroshima University", SourceCategory.UNIVERSITY, "JP", "Research"),
    DataSource("https://www.chiba-u.ac.jp/", "Chiba University", SourceCategory.UNIVERSITY, "JP", "Research"),
    DataSource("https://www.riken.jp/", "RIKEN", SourceCategory.RESEARCH, "JP", "Science research", True),
]

JAPAN_HOSPITALS = [
    DataSource("https://www.h.u-tokyo.ac.jp/", "University of Tokyo Hospital", SourceCategory.HOSPITAL, "JP", "Teaching hospital"),
    DataSource("https://www.kuhp.kyoto-u.ac.jp/", "Kyoto University Hospital", SourceCategory.HOSPITAL, "JP", "Teaching hospital"),
    DataSource("https://www.ncgm.go.jp/", "National Center for Global Health Medicine", SourceCategory.HOSPITAL, "JP", "National hospital"),
    DataSource("https://www.ncc.go.jp/", "National Cancer Center Japan", SourceCategory.HOSPITAL, "JP", "Cancer center"),
    DataSource("https://www.ncvc.go.jp/", "National Cardiovascular Center", SourceCategory.HOSPITAL, "JP", "Cardiology"),
    DataSource("https://www.ncnp.go.jp/", "National Center Neurology Psychiatry", SourceCategory.HOSPITAL, "JP", "Neurology"),
    DataSource("https://www.nch.go.jp/", "National Children's Hospital", SourceCategory.HOSPITAL, "JP", "Pediatric"),
    DataSource("https://www.keio-hospital.jp/", "Keio University Hospital", SourceCategory.HOSPITAL, "JP", "Teaching hospital"),
    DataSource("https://www.juntendo.ac.jp/hospital/", "Juntendo University Hospital", SourceCategory.HOSPITAL, "JP", "Teaching hospital"),
    DataSource("https://www.hosp.med.osaka-u.ac.jp/", "Osaka University Hospital", SourceCategory.HOSPITAL, "JP", "Teaching hospital"),
]

JAPAN_BANKS = [
    DataSource("https://www.boj.or.jp/", "Bank of Japan", SourceCategory.BANK, "JP", "Central Bank", True),
    DataSource("https://www.mufg.jp/", "MUFG Bank", SourceCategory.BANK, "JP", "Largest bank"),
    DataSource("https://www.smfg.co.jp/", "SMBC Group", SourceCategory.BANK, "JP", "Major bank"),
    DataSource("https://www.mizuho-fg.co.jp/", "Mizuho Financial Group", SourceCategory.BANK, "JP", "Major bank"),
    DataSource("https://www.shinseibank.com/", "Shinsei Bank", SourceCategory.BANK, "JP", "Commercial bank"),
    DataSource("https://www.resonaholdings.co.jp/", "Resona Holdings", SourceCategory.BANK, "JP", "Regional bank"),
    DataSource("https://www.japanpost.jp/", "Japan Post Bank", SourceCategory.BANK, "JP", "Postal bank"),
    DataSource("https://www.dbj.jp/", "Development Bank of Japan", SourceCategory.BANK, "JP", "Policy bank"),
    DataSource("https://www.jfc.go.jp/", "Japan Finance Corporation", SourceCategory.BANK, "JP", "Government bank"),
    DataSource("https://www.jbic.go.jp/", "Japan Bank for International Cooperation", SourceCategory.BANK, "JP", "Export bank"),
    DataSource("https://www.nomura.co.jp/", "Nomura Holdings", SourceCategory.BANK, "JP", "Securities"),
    DataSource("https://www.daiwa.co.jp/", "Daiwa Securities", SourceCategory.BANK, "JP", "Securities"),
    DataSource("https://www.nikko.co.jp/", "SMBC Nikko Securities", SourceCategory.BANK, "JP", "Securities"),
]

JAPAN_FACTORIES = [
    DataSource("https://www.toyota.co.jp/", "Toyota", SourceCategory.FACTORY, "JP", "Automotive"),
    DataSource("https://www.honda.co.jp/", "Honda", SourceCategory.FACTORY, "JP", "Automotive"),
    DataSource("https://www.nissan.co.jp/", "Nissan", SourceCategory.FACTORY, "JP", "Automotive"),
    DataSource("https://www.mazda.co.jp/", "Mazda", SourceCategory.FACTORY, "JP", "Automotive"),
    DataSource("https://www.subaru.co.jp/", "Subaru", SourceCategory.FACTORY, "JP", "Automotive"),
    DataSource("https://www.mitsubishi-motors.co.jp/", "Mitsubishi Motors", SourceCategory.FACTORY, "JP", "Automotive"),
    DataSource("https://www.suzuki.co.jp/", "Suzuki", SourceCategory.FACTORY, "JP", "Automotive"),
    DataSource("https://www.sony.co.jp/", "Sony", SourceCategory.FACTORY, "JP", "Electronics"),
    DataSource("https://www.panasonic.co.jp/", "Panasonic", SourceCategory.FACTORY, "JP", "Electronics"),
    DataSource("https://www.hitachi.co.jp/", "Hitachi", SourceCategory.FACTORY, "JP", "Electronics"),
    DataSource("https://www.toshiba.co.jp/", "Toshiba", SourceCategory.FACTORY, "JP", "Electronics"),
    DataSource("https://www.fujitsu.com/", "Fujitsu", SourceCategory.FACTORY, "JP", "IT & Electronics"),
    DataSource("https://www.nec.co.jp/", "NEC", SourceCategory.FACTORY, "JP", "IT & Electronics"),
    DataSource("https://www.canon.co.jp/", "Canon", SourceCategory.FACTORY, "JP", "Imaging"),
    DataSource("https://www.nikon.co.jp/", "Nikon", SourceCategory.FACTORY, "JP", "Imaging"),
    DataSource("https://www.sharp.co.jp/", "Sharp", SourceCategory.FACTORY, "JP", "Electronics"),
    DataSource("https://www.daikin.co.jp/", "Daikin", SourceCategory.FACTORY, "JP", "HVAC"),
    DataSource("https://www.komatsu.co.jp/", "Komatsu", SourceCategory.FACTORY, "JP", "Heavy machinery"),
    DataSource("https://www.kubota.co.jp/", "Kubota", SourceCategory.FACTORY, "JP", "Agricultural machinery"),
    DataSource("https://www.nipponsteel.com/", "Nippon Steel", SourceCategory.FACTORY, "JP", "Steel"),
    DataSource("https://www.jfe-holdings.co.jp/", "JFE Steel", SourceCategory.FACTORY, "JP", "Steel"),
    DataSource("https://www.bridgestone.co.jp/", "Bridgestone", SourceCategory.FACTORY, "JP", "Tires"),
    DataSource("https://www.denso.com/", "DENSO", SourceCategory.FACTORY, "JP", "Auto parts"),
    DataSource("https://www.aisin.co.jp/", "Aisin", SourceCategory.FACTORY, "JP", "Auto parts"),
]

JAPAN_NEWS = [
    DataSource("https://www.nhk.or.jp/", "NHK", SourceCategory.NEWS, "JP", "National broadcaster"),
    DataSource("https://www.asahi.com/", "Asahi Shimbun", SourceCategory.NEWS, "JP", "Major newspaper"),
    DataSource("https://www.yomiuri.co.jp/", "Yomiuri Shimbun", SourceCategory.NEWS, "JP", "Largest newspaper"),
    DataSource("https://mainichi.jp/", "Mainichi Shimbun", SourceCategory.NEWS, "JP", "Major newspaper"),
    DataSource("https://www.nikkei.com/", "Nikkei", SourceCategory.NEWS, "JP", "Financial newspaper"),
    DataSource("https://www.sankei.com/", "Sankei Shimbun", SourceCategory.NEWS, "JP", "Major newspaper"),
    DataSource("https://www.kyodonews.net/", "Kyodo News", SourceCategory.NEWS, "JP", "News agency"),
    DataSource("https://www.jiji.com/", "Jiji Press", SourceCategory.NEWS, "JP", "News agency"),
    DataSource("https://www.japantimes.co.jp/", "Japan Times", SourceCategory.NEWS, "JP", "English newspaper"),
    DataSource("https://www.reuters.co.jp/", "Reuters Japan", SourceCategory.NEWS, "JP", "International news"),
]

JAPAN_CULTURE = [
    DataSource("https://www.tnm.jp/", "Tokyo National Museum", SourceCategory.CULTURE, "JP", "National museum"),
    DataSource("https://www.kyohaku.go.jp/", "Kyoto National Museum", SourceCategory.CULTURE, "JP", "National museum"),
    DataSource("https://www.narahaku.go.jp/", "Nara National Museum", SourceCategory.CULTURE, "JP", "National museum"),
    DataSource("https://www.momat.go.jp/", "National Museum of Modern Art Tokyo", SourceCategory.CULTURE, "JP", "Modern art"),
    DataSource("https://www.ndl.go.jp/", "National Diet Library", SourceCategory.CULTURE, "JP", "National library", True),
    DataSource("https://www.bunka.go.jp/", "Agency for Cultural Affairs", SourceCategory.CULTURE, "JP", "Cultural heritage"),
    DataSource("https://www.nmwa.go.jp/", "National Museum of Western Art", SourceCategory.CULTURE, "JP", "Western art"),
    DataSource("https://www.mori.art.museum/", "Mori Art Museum", SourceCategory.CULTURE, "JP", "Contemporary art"),
]

# ============================================================
# 🇰🇷 SOUTH KOREA
# ============================================================

KOREA_GOVERNMENT = [
    DataSource("https://www.data.go.kr/", "Data.go.kr", SourceCategory.GOVERNMENT, "KR", "Open data portal", True),
    DataSource("https://kosis.kr/", "KOSIS Statistics Korea", SourceCategory.STATISTICS, "KR", "Statistics", True),
    DataSource("https://www.bok.or.kr/", "Bank of Korea", SourceCategory.BANK, "KR", "Central Bank", True),
    DataSource("https://www.moef.go.kr/", "Ministry of Economy Finance", SourceCategory.GOVERNMENT, "KR", "Economic data"),
    DataSource("https://www.moe.go.kr/", "Ministry of Education Korea", SourceCategory.GOVERNMENT, "KR", "Education data"),
    DataSource("https://www.mohw.go.kr/", "Ministry of Health Welfare", SourceCategory.GOVERNMENT, "KR", "Health data"),
    DataSource("https://www.motie.go.kr/", "Ministry of Trade Industry Energy", SourceCategory.GOVERNMENT, "KR", "Industry data"),
    DataSource("https://www.me.go.kr/", "Ministry of Environment Korea", SourceCategory.ENVIRONMENTAL, "KR", "Environmental data"),
    DataSource("https://www.molit.go.kr/", "Ministry of Land Infrastructure Transport", SourceCategory.TRANSPORT, "KR", "Transport data"),
    DataSource("https://www.weather.go.kr/", "Korea Meteorological Administration", SourceCategory.ENVIRONMENTAL, "KR", "Weather data", True),
    DataSource("https://www.customs.go.kr/", "Korea Customs Service", SourceCategory.GOVERNMENT, "KR", "Trade data"),
    DataSource("https://www.nts.go.kr/", "National Tax Service Korea", SourceCategory.GOVERNMENT, "KR", "Tax data"),
    DataSource("https://www.fss.or.kr/", "Financial Supervisory Service", SourceCategory.RATING, "KR", "Financial regulation"),
    DataSource("https://www.kipo.go.kr/", "Korean Intellectual Property Office", SourceCategory.GOVERNMENT, "KR", "Patent data", True),
]

KOREA_UNIVERSITIES = [
    DataSource("https://www.snu.ac.kr/", "Seoul National University", SourceCategory.UNIVERSITY, "KR", "Top university"),
    DataSource("https://www.kaist.ac.kr/", "KAIST", SourceCategory.UNIVERSITY, "KR", "Technology institute"),
    DataSource("https://www.postech.ac.kr/", "POSTECH", SourceCategory.UNIVERSITY, "KR", "Science technology"),
    DataSource("https://www.korea.ac.kr/", "Korea University", SourceCategory.UNIVERSITY, "KR", "SKY university"),
    DataSource("https://www.yonsei.ac.kr/", "Yonsei University", SourceCategory.UNIVERSITY, "KR", "SKY university"),
    DataSource("https://www.skku.edu/", "Sungkyunkwan University", SourceCategory.UNIVERSITY, "KR", "Research"),
    DataSource("https://www.hanyang.ac.kr/", "Hanyang University", SourceCategory.UNIVERSITY, "KR", "Engineering"),
    DataSource("https://www.unist.ac.kr/", "UNIST", SourceCategory.UNIVERSITY, "KR", "Science technology"),
    DataSource("https://www.gist.ac.kr/", "GIST", SourceCategory.UNIVERSITY, "KR", "Science technology"),
    DataSource("https://www.dgist.ac.kr/", "DGIST", SourceCategory.UNIVERSITY, "KR", "Science technology"),
    DataSource("https://www.ewha.ac.kr/", "Ewha Womans University", SourceCategory.UNIVERSITY, "KR", "Women's university"),
    DataSource("https://www.sogang.ac.kr/", "Sogang University", SourceCategory.UNIVERSITY, "KR", "Jesuit university"),
    DataSource("https://www.cau.ac.kr/", "Chung-Ang University", SourceCategory.UNIVERSITY, "KR", "Research"),
    DataSource("https://www.khu.ac.kr/", "Kyung Hee University", SourceCategory.UNIVERSITY, "KR", "Research"),
]

KOREA_HOSPITALS = [
    DataSource("https://www.snuh.org/", "Seoul National University Hospital", SourceCategory.HOSPITAL, "KR", "Top hospital"),
    DataSource("https://www.amc.seoul.kr/", "Asan Medical Center", SourceCategory.HOSPITAL, "KR", "Largest hospital"),
    DataSource("https://www.severance.healthcare/", "Severance Hospital Yonsei", SourceCategory.HOSPITAL, "KR", "Major hospital"),
    DataSource("https://www.samsunghospital.com/", "Samsung Medical Center", SourceCategory.HOSPITAL, "KR", "Major hospital"),
    DataSource("https://www.ncc.re.kr/", "National Cancer Center Korea", SourceCategory.HOSPITAL, "KR", "Cancer center"),
    DataSource("https://www.snubh.org/", "Seoul National University Bundang Hospital", SourceCategory.HOSPITAL, "KR", "Teaching hospital"),
    DataSource("https://www.kumc.or.kr/", "Korea University Medical Center", SourceCategory.HOSPITAL, "KR", "Teaching hospital"),
    DataSource("https://www.cmcseoul.or.kr/", "Catholic University Seoul St. Mary's", SourceCategory.HOSPITAL, "KR", "Teaching hospital"),
]

KOREA_BANKS = [
    DataSource("https://www.bok.or.kr/", "Bank of Korea", SourceCategory.BANK, "KR", "Central Bank", True),
    DataSource("https://www.kdb.co.kr/", "Korea Development Bank", SourceCategory.BANK, "KR", "Policy bank"),
    DataSource("https://www.ibk.co.kr/", "Industrial Bank of Korea", SourceCategory.BANK, "KR", "SME bank"),
    DataSource("https://www.kebhana.com/", "Hana Bank", SourceCategory.BANK, "KR", "Major bank"),
    DataSource("https://www.shinhan.com/", "Shinhan Bank", SourceCategory.BANK, "KR", "Major bank"),
    DataSource("https://www.kbstar.com/", "KB Kookmin Bank", SourceCategory.BANK, "KR", "Largest bank"),
    DataSource("https://www.wooribank.com/", "Woori Bank", SourceCategory.BANK, "KR", "Major bank"),
    DataSource("https://www.nonghyup.com/", "NH Bank", SourceCategory.BANK, "KR", "Agricultural bank"),
    DataSource("https://www.standardchartered.co.kr/", "SC First Bank Korea", SourceCategory.BANK, "KR", "Foreign bank"),
    DataSource("https://www.citibank.co.kr/", "Citibank Korea", SourceCategory.BANK, "KR", "Foreign bank"),
]

KOREA_FACTORIES = [
    DataSource("https://www.samsung.com/", "Samsung Electronics", SourceCategory.FACTORY, "KR", "Electronics"),
    DataSource("https://www.skhynix.com/", "SK Hynix", SourceCategory.FACTORY, "KR", "Semiconductors"),
    DataSource("https://www.lg.com/", "LG Electronics", SourceCategory.FACTORY, "KR", "Electronics"),
    DataSource("https://www.hyundai.com/", "Hyundai Motor", SourceCategory.FACTORY, "KR", "Automotive"),
    DataSource("https://www.kia.com/", "Kia Motors", SourceCategory.FACTORY, "KR", "Automotive"),
    DataSource("https://www.posco.com/", "POSCO", SourceCategory.FACTORY, "KR", "Steel"),
    DataSource("https://www.samsungsdi.com/", "Samsung SDI", SourceCategory.FACTORY, "KR", "Batteries"),
    DataSource("https://www.lgchem.com/", "LG Chem", SourceCategory.FACTORY, "KR", "Chemicals/Batteries"),
    DataSource("https://www.skenergy.com/", "SK Energy", SourceCategory.ENERGY, "KR", "Oil & Gas"),
    DataSource("https://www.s-oil.com/", "S-Oil", SourceCategory.ENERGY, "KR", "Oil refinery"),
    DataSource("https://www.gs.co.kr/", "GS Caltex", SourceCategory.ENERGY, "KR", "Oil refinery"),
    DataSource("https://www.hhi.co.kr/", "Hyundai Heavy Industries", SourceCategory.FACTORY, "KR", "Shipbuilding"),
    DataSource("https://www.samsungheavy.com/", "Samsung Heavy Industries", SourceCategory.FACTORY, "KR", "Shipbuilding"),
    DataSource("https://www.dsme.co.kr/", "Daewoo Shipbuilding", SourceCategory.FACTORY, "KR", "Shipbuilding"),
    DataSource("https://www.halla.com/", "Halla Holdings", SourceCategory.FACTORY, "KR", "Industrial"),
    DataSource("https://www.hanwha.com/", "Hanwha Group", SourceCategory.FACTORY, "KR", "Conglomerate"),
    DataSource("https://www.doosan.com/", "Doosan", SourceCategory.FACTORY, "KR", "Heavy industry"),
    DataSource("https://www.koreaelectric.co.kr/", "Korea Electric Power", SourceCategory.ENERGY, "KR", "Power utility"),
    DataSource("https://www.sktelecom.com/", "SK Telecom", SourceCategory.TELECOM, "KR", "Telecom"),
    DataSource("https://www.kt.com/", "KT Corporation", SourceCategory.TELECOM, "KR", "Telecom"),
    DataSource("https://www.lguplus.com/", "LG U+", SourceCategory.TELECOM, "KR", "Telecom"),
]

KOREA_NEWS = [
    DataSource("https://www.kbs.co.kr/", "KBS", SourceCategory.NEWS, "KR", "Public broadcaster"),
    DataSource("https://www.mbc.co.kr/", "MBC", SourceCategory.NEWS, "KR", "Major broadcaster"),
    DataSource("https://www.sbs.co.kr/", "SBS", SourceCategory.NEWS, "KR", "Major broadcaster"),
    DataSource("https://www.chosun.com/", "Chosun Ilbo", SourceCategory.NEWS, "KR", "Major newspaper"),
    DataSource("https://www.joongang.co.kr/", "JoongAng Ilbo", SourceCategory.NEWS, "KR", "Major newspaper"),
    DataSource("https://www.donga.com/", "Dong-A Ilbo", SourceCategory.NEWS, "KR", "Major newspaper"),
    DataSource("https://www.hani.co.kr/", "Hankyoreh", SourceCategory.NEWS, "KR", "Progressive newspaper"),
    DataSource("https://www.yna.co.kr/", "Yonhap News Agency", SourceCategory.NEWS, "KR", "News agency"),
    DataSource("https://www.mk.co.kr/", "Maeil Business Newspaper", SourceCategory.NEWS, "KR", "Business news"),
    DataSource("https://www.hankyung.com/", "Korea Economic Daily", SourceCategory.NEWS, "KR", "Business news"),
    DataSource("https://en.yna.co.kr/", "Yonhap English", SourceCategory.NEWS, "KR", "English news"),
    DataSource("https://www.koreaherald.com/", "Korea Herald", SourceCategory.NEWS, "KR", "English newspaper"),
]

KOREA_CULTURE = [
    DataSource("https://www.museum.go.kr/", "National Museum of Korea", SourceCategory.CULTURE, "KR", "National museum"),
    DataSource("https://www.mmca.go.kr/", "National Museum of Modern Contemporary Art", SourceCategory.CULTURE, "KR", "Modern art"),
    DataSource("https://www.nl.go.kr/", "National Library of Korea", SourceCategory.CULTURE, "KR", "National library", True),
    DataSource("https://www.cha.go.kr/", "Cultural Heritage Administration", SourceCategory.CULTURE, "KR", "Cultural heritage"),
    DataSource("https://www.kocca.kr/", "Korea Creative Content Agency", SourceCategory.CULTURE, "KR", "Content industry"),
    DataSource("https://www.arko.or.kr/", "Arts Council Korea", SourceCategory.CULTURE, "KR", "Arts council"),
]

KOREA_RESEARCH = [
    DataSource("https://www.kist.re.kr/", "Korea Institute Science Technology", SourceCategory.RESEARCH, "KR", "Science research"),
    DataSource("https://www.etri.re.kr/", "Electronics Telecommunications Research Institute", SourceCategory.RESEARCH, "KR", "IT research"),
    DataSource("https://www.kribb.re.kr/", "Korea Research Institute Bioscience Biotechnology", SourceCategory.RESEARCH, "KR", "Biotech"),
    DataSource("https://www.kari.re.kr/", "Korea Aerospace Research Institute", SourceCategory.RESEARCH, "KR", "Aerospace"),
    DataSource("https://www.kiost.ac.kr/", "Korea Institute Ocean Science Technology", SourceCategory.RESEARCH, "KR", "Ocean research"),
    DataSource("https://www.kigam.re.kr/", "Korea Institute Geoscience Mineral Resources", SourceCategory.RESEARCH, "KR", "Geoscience"),
    DataSource("https://www.kriss.re.kr/", "Korea Research Institute Standards Science", SourceCategory.RESEARCH, "KR", "Standards"),
    DataSource("https://www.nrf.re.kr/", "National Research Foundation Korea", SourceCategory.RESEARCH, "KR", "Research funding", True),
]

# ============================================================
# 🇹🇼 TAIWAN
# ============================================================

TAIWAN_SOURCES = [
    DataSource("https://data.gov.tw/", "Taiwan Open Data", SourceCategory.GOVERNMENT, "TW", "Open data portal", True),
    DataSource("https://www.stat.gov.tw/", "National Statistics Taiwan", SourceCategory.STATISTICS, "TW", "Statistics", True),
    DataSource("https://www.cbc.gov.tw/", "Central Bank Taiwan", SourceCategory.BANK, "TW", "Central Bank", True),
    DataSource("https://www.ntu.edu.tw/", "National Taiwan University", SourceCategory.UNIVERSITY, "TW", "Top university"),
    DataSource("https://www.nthu.edu.tw/", "National Tsing Hua University", SourceCategory.UNIVERSITY, "TW", "Research"),
    DataSource("https://www.nctu.edu.tw/", "National Chiao Tung University", SourceCategory.UNIVERSITY, "TW", "Technology"),
    DataSource("https://www.ntust.edu.tw/", "National Taiwan University Science Technology", SourceCategory.UNIVERSITY, "TW", "Technology"),
    DataSource("https://www.ncu.edu.tw/", "National Central University", SourceCategory.UNIVERSITY, "TW", "Research"),
    DataSource("https://www.sinica.edu.tw/", "Academia Sinica", SourceCategory.RESEARCH, "TW", "Research institute", True),
    DataSource("https://www.itri.org.tw/", "ITRI", SourceCategory.RESEARCH, "TW", "Industrial research"),
    DataSource("https://www.ntuh.gov.tw/", "National Taiwan University Hospital", SourceCategory.HOSPITAL, "TW", "Top hospital"),
    DataSource("https://www.cgmh.org.tw/", "Chang Gung Memorial Hospital", SourceCategory.HOSPITAL, "TW", "Major hospital"),
    DataSource("https://www.vghtpe.gov.tw/", "Taipei Veterans General Hospital", SourceCategory.HOSPITAL, "TW", "Major hospital"),
    DataSource("https://www.tsmc.com/", "TSMC", SourceCategory.FACTORY, "TW", "Semiconductors"),
    DataSource("https://www.umc.com/", "UMC", SourceCategory.FACTORY, "TW", "Semiconductors"),
    DataSource("https://www.mediatek.com/", "MediaTek", SourceCategory.FACTORY, "TW", "Chips"),
    DataSource("https://www.foxconn.com/", "Foxconn", SourceCategory.FACTORY, "TW", "Electronics manufacturing"),
    DataSource("https://www.asus.com/", "ASUS", SourceCategory.FACTORY, "TW", "Computers"),
    DataSource("https://www.acer.com/", "Acer", SourceCategory.FACTORY, "TW", "Computers"),
    DataSource("https://www.msi.com/", "MSI", SourceCategory.FACTORY, "TW", "Computers"),
    DataSource("https://www.htc.com/", "HTC", SourceCategory.FACTORY, "TW", "Electronics"),
    DataSource("https://www.cpc.com.tw/", "CPC Corporation", SourceCategory.ENERGY, "TW", "Oil & Gas"),
    DataSource("https://www.taipower.com.tw/", "Taipower", SourceCategory.ENERGY, "TW", "Power utility"),
    DataSource("https://www.cht.com.tw/", "Chunghwa Telecom", SourceCategory.TELECOM, "TW", "Telecom"),
    DataSource("https://www.npm.gov.tw/", "National Palace Museum", SourceCategory.CULTURE, "TW", "Museum"),
    DataSource("https://www.ncl.edu.tw/", "National Central Library", SourceCategory.CULTURE, "TW", "Library"),
    DataSource("https://www.cna.com.tw/", "Central News Agency Taiwan", SourceCategory.NEWS, "TW", "News agency"),
    DataSource("https://www.ltn.com.tw/", "Liberty Times", SourceCategory.NEWS, "TW", "Newspaper"),
    DataSource("https://www.chinatimes.com/", "China Times", SourceCategory.NEWS, "TW", "Newspaper"),
    DataSource("https://udn.com/", "United Daily News", SourceCategory.NEWS, "TW", "Newspaper"),
]

# ============================================================
# 🇭🇰 HONG KONG
# ============================================================

HONG_KONG_SOURCES = [
    DataSource("https://data.gov.hk/", "Data.gov.hk", SourceCategory.GOVERNMENT, "HK", "Open data portal", True),
    DataSource("https://www.censtatd.gov.hk/", "Census Statistics Hong Kong", SourceCategory.STATISTICS, "HK", "Statistics", True),
    DataSource("https://www.hkma.gov.hk/", "Hong Kong Monetary Authority", SourceCategory.BANK, "HK", "Central Bank", True),
    DataSource("https://www.sfc.hk/", "Securities Futures Commission HK", SourceCategory.RATING, "HK", "Financial regulator"),
    DataSource("https://www.hkex.com.hk/", "Hong Kong Stock Exchange", SourceCategory.BANK, "HK", "Stock exchange", True),
    DataSource("https://www.hku.hk/", "University of Hong Kong", SourceCategory.UNIVERSITY, "HK", "Top university"),
    DataSource("https://www.cuhk.edu.hk/", "Chinese University of Hong Kong", SourceCategory.UNIVERSITY, "HK", "Research"),
    DataSource("https://www.ust.hk/", "HKUST", SourceCategory.UNIVERSITY, "HK", "Science technology"),
    DataSource("https://www.polyu.edu.hk/", "Hong Kong Polytechnic University", SourceCategory.UNIVERSITY, "HK", "Technology"),
    DataSource("https://www.cityu.edu.hk/", "City University Hong Kong", SourceCategory.UNIVERSITY, "HK", "Research"),
    DataSource("https://www.ha.org.hk/", "Hospital Authority Hong Kong", SourceCategory.HOSPITAL, "HK", "Public hospitals"),
    DataSource("https://www.qmh.org.hk/", "Queen Mary Hospital", SourceCategory.HOSPITAL, "HK", "Teaching hospital"),
    DataSource("https://www.pyn.com.hk/", "Prince of Wales Hospital", SourceCategory.HOSPITAL, "HK", "Teaching hospital"),
    DataSource("https://www.hsbc.com.hk/", "HSBC Hong Kong", SourceCategory.BANK, "HK", "Major bank"),
    DataSource("https://www.bochk.com/", "Bank of China Hong Kong", SourceCategory.BANK, "HK", "Major bank"),
    DataSource("https://www.standardchartered.com.hk/", "Standard Chartered HK", SourceCategory.BANK, "HK", "Major bank"),
    DataSource("https://www.hangseng.com/", "Hang Seng Bank", SourceCategory.BANK, "HK", "Major bank"),
    DataSource("https://www.scmp.com/", "South China Morning Post", SourceCategory.NEWS, "HK", "Newspaper"),
    DataSource("https://www.hk01.com/", "HK01", SourceCategory.NEWS, "HK", "Digital news"),
    DataSource("https://www.rthk.hk/", "RTHK", SourceCategory.NEWS, "HK", "Public broadcaster"),
    DataSource("https://www.heritage.gov.hk/", "Hong Kong Heritage", SourceCategory.CULTURE, "HK", "Heritage"),
    DataSource("https://www.lcsd.gov.hk/", "Leisure Cultural Services HK", SourceCategory.CULTURE, "HK", "Museums libraries"),
]

# ============================================================
# 🇲🇳 MONGOLIA
# ============================================================

MONGOLIA_SOURCES = [
    DataSource("https://www.1212.mn/", "National Statistics Office Mongolia", SourceCategory.STATISTICS, "MN", "Statistics", True),
    DataSource("https://opendata.gov.mn/", "Mongolia Open Data", SourceCategory.GOVERNMENT, "MN", "Open data portal", True),
    DataSource("https://www.mongolbank.mn/", "Bank of Mongolia", SourceCategory.BANK, "MN", "Central Bank", True),
    DataSource("https://www.num.edu.mn/", "National University of Mongolia", SourceCategory.UNIVERSITY, "MN", "Top university"),
    DataSource("https://www.must.edu.mn/", "Mongolian University Science Technology", SourceCategory.UNIVERSITY, "MN", "Technology"),
    DataSource("https://www.montsame.mn/", "MONTSAME News Agency", SourceCategory.NEWS, "MN", "News agency"),
    DataSource("https://www.nationalmuseum.mn/", "National Museum of Mongolia", SourceCategory.CULTURE, "MN", "National museum"),
]

# ============================================================
# 🇸🇬 SINGAPORE
# ============================================================

SINGAPORE_SOURCES = [
    DataSource("https://data.gov.sg/", "Data.gov.sg", SourceCategory.GOVERNMENT, "SG", "Open data portal", True),
    DataSource("https://www.singstat.gov.sg/", "Singapore Statistics", SourceCategory.STATISTICS, "SG", "Statistics", True),
    DataSource("https://www.mas.gov.sg/", "Monetary Authority Singapore", SourceCategory.BANK, "SG", "Central Bank", True),
    DataSource("https://www.nus.edu.sg/", "National University of Singapore", SourceCategory.UNIVERSITY, "SG", "Top university"),
    DataSource("https://www.ntu.edu.sg/", "Nanyang Technological University", SourceCategory.UNIVERSITY, "SG", "Top university"),
    DataSource("https://www.sutd.edu.sg/", "Singapore University Technology Design", SourceCategory.UNIVERSITY, "SG", "Technology"),
    DataSource("https://www.smu.edu.sg/", "Singapore Management University", SourceCategory.UNIVERSITY, "SG", "Business"),
    DataSource("https://www.astar.edu.sg/", "A*STAR", SourceCategory.RESEARCH, "SG", "Science research", True),
    DataSource("https://www.sgh.com.sg/", "Singapore General Hospital", SourceCategory.HOSPITAL, "SG", "Largest hospital"),
    DataSource("https://www.nuhs.edu.sg/", "National University Hospital Singapore", SourceCategory.HOSPITAL, "SG", "Teaching hospital"),
    DataSource("https://www.dbs.com.sg/", "DBS Bank", SourceCategory.BANK, "SG", "Largest bank"),
    DataSource("https://www.ocbc.com/", "OCBC Bank", SourceCategory.BANK, "SG", "Major bank"),
    DataSource("https://www.uob.com.sg/", "UOB", SourceCategory.BANK, "SG", "Major bank"),
    DataSource("https://www.sgx.com/", "Singapore Exchange", SourceCategory.BANK, "SG", "Stock exchange", True),
    DataSource("https://www.singaporeair.com/", "Singapore Airlines", SourceCategory.TRANSPORT, "SG", "National airline"),
    DataSource("https://www.psa.com.sg/", "PSA Singapore", SourceCategory.TRANSPORT, "SG", "Port authority"),
    DataSource("https://www.channelnewsasia.com/", "Channel News Asia", SourceCategory.NEWS, "SG", "News channel"),
    DataSource("https://www.straitstimes.com/", "Straits Times", SourceCategory.NEWS, "SG", "Newspaper"),
    DataSource("https://www.todayonline.com/", "Today Online", SourceCategory.NEWS, "SG", "Digital news"),
    DataSource("https://www.nhb.gov.sg/", "National Heritage Board Singapore", SourceCategory.CULTURE, "SG", "Heritage"),
    DataSource("https://www.nlb.gov.sg/", "National Library Board Singapore", SourceCategory.CULTURE, "SG", "Library", True),
]

# ============================================================
# 🏅 CHINA & ASIA SPORT SOURCES
# ============================================================

CHINA_SPORT_SOURCES = [
    # 🇨🇳 CHINA SPORTS
    DataSource("https://www.sport.gov.cn/", "China General Administration of Sport", SourceCategory.SPORT, "CN", "National sports authority"),
    DataSource("https://www.cba.net.cn/", "Chinese Basketball Association", SourceCategory.SPORT, "CN", "CBA basketball"),
    DataSource("https://www.thecfa.cn/", "Chinese Football Association", SourceCategory.SPORT, "CN", "Football federation"),
    DataSource("https://www.chinese.volleyball.org/", "Chinese Volleyball Association", SourceCategory.SPORT, "CN", "Volleyball federation"),
    DataSource("https://www.ctta.cn/", "China Table Tennis Association", SourceCategory.SPORT, "CN", "Table tennis", True),
    DataSource("https://www.badmintonchina.cn/", "China Badminton Association", SourceCategory.SPORT, "CN", "Badminton federation"),
    DataSource("https://www.coc.org.cn/", "Chinese Olympic Committee", SourceCategory.SPORT, "CN", "Olympic committee"),
    DataSource("https://sports.sina.com.cn/", "Sina Sports", SourceCategory.SPORT, "CN", "Sports news portal"),
    DataSource("https://sports.qq.com/", "Tencent Sports", SourceCategory.SPORT, "CN", "Sports media"),
    DataSource("https://www.zhibo8.cc/", "Zhibo8", SourceCategory.SPORT, "CN", "Sports streaming"),
    DataSource("https://www.csl-china.com/", "Chinese Super League", SourceCategory.SPORT, "CN", "Football league"),
    DataSource("https://www.swimming.org.cn/", "China Swimming Association", SourceCategory.SPORT, "CN", "Swimming"),
    DataSource("https://www.athletics.org.cn/", "China Athletics Association", SourceCategory.SPORT, "CN", "Athletics"),
    DataSource("https://www.china-golf.org.cn/", "China Golf Association", SourceCategory.SPORT, "CN", "Golf federation"),
    DataSource("https://www.chess.org.cn/", "Chinese Chess Association", SourceCategory.SPORT, "CN", "Chess/Weiqi"),
    
    # 🇯🇵 JAPAN SPORTS
    DataSource("https://www.jpnsport.go.jp/", "Japan Sports Agency", SourceCategory.SPORT, "JP", "Government sports agency"),
    DataSource("https://www.jfa.jp/", "Japan Football Association", SourceCategory.SPORT, "JP", "Football federation"),
    DataSource("https://www.basketballjapan.or.jp/", "Japan Basketball Association", SourceCategory.SPORT, "JP", "Basketball"),
    DataSource("https://www.j-league.or.jp/", "J-League", SourceCategory.SPORT, "JP", "Professional football", True),
    DataSource("https://www.npb.or.jp/", "Nippon Professional Baseball", SourceCategory.SPORT, "JP", "Baseball league", True),
    DataSource("https://www.sumo.or.jp/", "Japan Sumo Association", SourceCategory.SPORT, "JP", "Sumo wrestling"),
    DataSource("https://www.jrfu.org/", "Japan Rugby Football Union", SourceCategory.SPORT, "JP", "Rugby union"),
    DataSource("https://www.joc.or.jp/", "Japanese Olympic Committee", SourceCategory.SPORT, "JP", "Olympic committee"),
    DataSource("https://www.swim.or.jp/", "Japan Swimming Federation", SourceCategory.SPORT, "JP", "Swimming"),
    DataSource("https://www.judo.or.jp/", "All Japan Judo Federation", SourceCategory.SPORT, "JP", "Judo"),
    DataSource("https://www.kendo.or.jp/", "All Japan Kendo Federation", SourceCategory.SPORT, "JP", "Kendo martial arts"),
    DataSource("https://www.karate.or.jp/", "Japan Karate Federation", SourceCategory.SPORT, "JP", "Karate"),
    
    # 🇰🇷 KOREA SPORTS
    DataSource("https://www.sports.or.kr/", "Korean Sports & Olympic Committee", SourceCategory.SPORT, "KR", "Olympic committee"),
    DataSource("https://www.kfa.or.kr/", "Korea Football Association", SourceCategory.SPORT, "KR", "Football federation"),
    DataSource("https://www.kleague.com/", "K League", SourceCategory.SPORT, "KR", "Football league", True),
    DataSource("https://www.koreabaseball.com/", "Korea Baseball Organization", SourceCategory.SPORT, "KR", "Baseball league", True),
    DataSource("https://www.kbl.or.kr/", "Korean Basketball League", SourceCategory.SPORT, "KR", "Basketball league"),
    DataSource("https://www.kva.or.kr/", "Korea Volleyball Association", SourceCategory.SPORT, "KR", "Volleyball"),
    DataSource("https://www.taekwondowon.or.kr/", "World Taekwondo Headquarters", SourceCategory.SPORT, "KR", "Taekwondo martial arts"),
    DataSource("https://www.badmintonkorea.org/", "Korea Badminton Association", SourceCategory.SPORT, "KR", "Badminton"),
    DataSource("https://www.skating.or.kr/", "Korea Skating Union", SourceCategory.SPORT, "KR", "Speed skating"),
    DataSource("https://www.golfkorea.or.kr/", "Korea Golf Association", SourceCategory.SPORT, "KR", "Golf"),
    DataSource("https://www.archery.or.kr/", "Korea Archery Association", SourceCategory.SPORT, "KR", "Archery"),
    DataSource("https://esports.or.kr/", "Korea e-Sports Association", SourceCategory.SPORT, "KR", "Esports", True),
]

# ============================================================
# 🎬 CHINA & ASIA ENTERTAINMENT SOURCES
# ============================================================

ASIA_ENTERTAINMENT_SOURCES = [
    # 🇨🇳 CHINA ENTERTAINMENT
    DataSource("https://www.iqiyi.com/", "iQIYI", SourceCategory.ENTERTAINMENT, "CN", "Streaming platform", True),
    DataSource("https://www.youku.com/", "Youku", SourceCategory.ENTERTAINMENT, "CN", "Video streaming"),
    DataSource("https://v.qq.com/", "Tencent Video", SourceCategory.ENTERTAINMENT, "CN", "Video platform"),
    DataSource("https://www.bilibili.com/", "Bilibili", SourceCategory.ENTERTAINMENT, "CN", "Anime/video platform", True),
    DataSource("https://www.mgtv.com/", "Mango TV", SourceCategory.ENTERTAINMENT, "CN", "Hunan TV streaming"),
    DataSource("https://www.douban.com/", "Douban", SourceCategory.ENTERTAINMENT, "CN", "Movies/books reviews", True),
    DataSource("https://movie.douban.com/", "Douban Movies", SourceCategory.ENTERTAINMENT, "CN", "Movie database"),
    DataSource("https://www.mtime.com/", "Mtime", SourceCategory.ENTERTAINMENT, "CN", "Movie portal"),
    DataSource("https://ent.sina.com.cn/", "Sina Entertainment", SourceCategory.ENTERTAINMENT, "CN", "Entertainment news"),
    DataSource("https://ent.qq.com/", "QQ Entertainment", SourceCategory.ENTERTAINMENT, "CN", "Entertainment portal"),
    DataSource("https://www.huanqiu.com/", "Huanqiu Entertainment", SourceCategory.ENTERTAINMENT, "CN", "Celebrity news"),
    DataSource("https://music.163.com/", "NetEase Music", SourceCategory.ENTERTAINMENT, "CN", "Music streaming", True),
    DataSource("https://y.qq.com/", "QQ Music", SourceCategory.ENTERTAINMENT, "CN", "Music platform"),
    DataSource("https://www.kugou.com/", "Kugou Music", SourceCategory.ENTERTAINMENT, "CN", "Music streaming"),
    DataSource("https://www.kuwo.cn/", "Kuwo Music", SourceCategory.ENTERTAINMENT, "CN", "Music platform"),
    DataSource("https://www.ximalaya.com/", "Ximalaya", SourceCategory.ENTERTAINMENT, "CN", "Podcast/audio", True),
    
    # 🇯🇵 JAPAN ENTERTAINMENT
    DataSource("https://www.oricon.co.jp/", "Oricon", SourceCategory.ENTERTAINMENT, "JP", "Music charts", True),
    DataSource("https://natalie.mu/", "Natalie", SourceCategory.ENTERTAINMENT, "JP", "Music/anime news"),
    DataSource("https://www.animenewsnetwork.com/", "Anime News Network", SourceCategory.ENTERTAINMENT, "JP", "Anime news"),
    DataSource("https://myanimelist.net/", "MyAnimeList", SourceCategory.ENTERTAINMENT, "JP", "Anime database", True),
    DataSource("https://anilist.co/", "AniList", SourceCategory.ENTERTAINMENT, "JP", "Anime tracking", True),
    DataSource("https://www.crunchyroll.com/", "Crunchyroll", SourceCategory.ENTERTAINMENT, "JP", "Anime streaming", True),
    DataSource("https://www.funimation.com/", "Funimation", SourceCategory.ENTERTAINMENT, "JP", "Anime streaming"),
    DataSource("https://www.joqr.co.jp/", "JOQR Radio", SourceCategory.ENTERTAINMENT, "JP", "Radio station"),
    DataSource("https://www.tfm.co.jp/", "Tokyo FM", SourceCategory.ENTERTAINMENT, "JP", "FM radio"),
    DataSource("https://mantan-web.jp/", "Mantan Web", SourceCategory.ENTERTAINMENT, "JP", "Entertainment news"),
    DataSource("https://www.sponichi.co.jp/", "Sponichi Annex", SourceCategory.ENTERTAINMENT, "JP", "Sports/entertainment"),
    DataSource("https://www.toei-anim.co.jp/", "Toei Animation", SourceCategory.ENTERTAINMENT, "JP", "Anime studio"),
    DataSource("https://www.production-ig.co.jp/", "Production I.G", SourceCategory.ENTERTAINMENT, "JP", "Anime studio"),
    DataSource("https://www.madhouse.co.jp/", "Madhouse", SourceCategory.ENTERTAINMENT, "JP", "Anime studio"),
    DataSource("https://www.kyotoanimation.co.jp/", "Kyoto Animation", SourceCategory.ENTERTAINMENT, "JP", "Anime studio"),
    
    # 🇰🇷 KOREA ENTERTAINMENT (K-POP, K-DRAMA)
    DataSource("https://www.melon.com/", "Melon", SourceCategory.ENTERTAINMENT, "KR", "Music streaming", True),
    DataSource("https://www.soompi.com/", "Soompi", SourceCategory.ENTERTAINMENT, "KR", "K-pop news", True),
    DataSource("https://www.allkpop.com/", "AllKPop", SourceCategory.ENTERTAINMENT, "KR", "K-pop news"),
    DataSource("https://www.viki.com/", "Viki", SourceCategory.ENTERTAINMENT, "KR", "K-drama streaming", True),
    DataSource("https://www.koreandrama.org/", "Korean Drama", SourceCategory.ENTERTAINMENT, "KR", "Drama database"),
    DataSource("https://www.mydramalist.com/", "MyDramaList", SourceCategory.ENTERTAINMENT, "KR", "Drama database", True),
    DataSource("https://www.hybe.co.kr/", "HYBE Corporation", SourceCategory.ENTERTAINMENT, "KR", "BTS label"),
    DataSource("https://www.smtown.com/", "SM Entertainment", SourceCategory.ENTERTAINMENT, "KR", "K-pop agency"),
    DataSource("https://www.ygfamily.com/", "YG Entertainment", SourceCategory.ENTERTAINMENT, "KR", "K-pop agency"),
    DataSource("https://www.jype.com/", "JYP Entertainment", SourceCategory.ENTERTAINMENT, "KR", "K-pop agency"),
    DataSource("https://www.kbs.co.kr/", "KBS", SourceCategory.ENTERTAINMENT, "KR", "Broadcasting"),
    DataSource("https://www.mbc.co.kr/", "MBC", SourceCategory.ENTERTAINMENT, "KR", "Broadcasting"),
    DataSource("https://www.sbs.co.kr/", "SBS", SourceCategory.ENTERTAINMENT, "KR", "Broadcasting"),
    DataSource("https://www.tvn.co.kr/", "tvN", SourceCategory.ENTERTAINMENT, "KR", "Cable channel"),
    DataSource("https://www.cjenm.com/", "CJ ENM", SourceCategory.ENTERTAINMENT, "KR", "Media conglomerate"),
    DataSource("https://weverse.io/", "Weverse", SourceCategory.ENTERTAINMENT, "KR", "Fan community", True),
]

# ============================================================
# ✈️ ASIA TOURISM SOURCES
# ============================================================

ASIA_TOURISM_SOURCES = [
    # 🇨🇳 CHINA TOURISM
    DataSource("https://www.cnta.gov.cn/", "China National Tourism Administration", SourceCategory.TOURISM, "CN", "National tourism"),
    DataSource("https://www.travelchina.gov.cn/", "Travel China Guide", SourceCategory.TOURISM, "CN", "Official tourism"),
    DataSource("https://www.trip.com/", "Trip.com", SourceCategory.TOURISM, "CN", "Travel booking", True),
    DataSource("https://www.ctrip.com/", "Ctrip", SourceCategory.TOURISM, "CN", "Travel platform"),
    DataSource("https://www.mafengwo.cn/", "Mafengwo", SourceCategory.TOURISM, "CN", "Travel community"),
    DataSource("https://www.qunar.com/", "Qunar", SourceCategory.TOURISM, "CN", "Travel search"),
    DataSource("https://www.tuniu.com/", "Tuniu", SourceCategory.TOURISM, "CN", "Tour packages"),
    DataSource("https://www.ly.com/", "LY.com", SourceCategory.TOURISM, "CN", "Travel booking"),
    DataSource("https://you.ctrip.com/", "Ctrip Travel Guide", SourceCategory.TOURISM, "CN", "Travel guides"),
    DataSource("https://www.bjtourism.gov.cn/", "Beijing Tourism", SourceCategory.TOURISM, "CN", "Beijing tourism"),
    DataSource("https://www.meet-in-shanghai.net/", "Shanghai Tourism", SourceCategory.TOURISM, "CN", "Shanghai tourism"),
    DataSource("https://www.visitxian.com/", "Visit Xi'an", SourceCategory.TOURISM, "CN", "Xi'an tourism"),
    
    # 🇯🇵 JAPAN TOURISM
    DataSource("https://www.japan.travel/", "Japan National Tourism", SourceCategory.TOURISM, "JP", "Official tourism", True),
    DataSource("https://www.jnto.go.jp/", "JNTO", SourceCategory.TOURISM, "JP", "Tourism organization"),
    DataSource("https://www.gotokyo.org/", "Go Tokyo", SourceCategory.TOURISM, "JP", "Tokyo tourism"),
    DataSource("https://kyoto.travel/", "Kyoto Tourism", SourceCategory.TOURISM, "JP", "Kyoto tourism"),
    DataSource("https://www.osaka-info.jp/", "Osaka Info", SourceCategory.TOURISM, "JP", "Osaka tourism"),
    DataSource("https://www.japan-guide.com/", "Japan Guide", SourceCategory.TOURISM, "JP", "Travel guide"),
    DataSource("https://www.jalan.net/", "Jalan", SourceCategory.TOURISM, "JP", "Travel booking"),
    DataSource("https://www.rakutentravel.com/", "Rakuten Travel", SourceCategory.TOURISM, "JP", "Hotel booking"),
    DataSource("https://www.japanican.com/", "Japanican", SourceCategory.TOURISM, "JP", "JTB booking"),
    DataSource("https://www.hiragana.jp/", "Japan Hoppers", SourceCategory.TOURISM, "JP", "Travel info"),
    
    # 🇰🇷 KOREA TOURISM
    DataSource("https://english.visitkorea.or.kr/", "Visit Korea", SourceCategory.TOURISM, "KR", "Official tourism", True),
    DataSource("https://www.kto.or.kr/", "Korea Tourism Organization", SourceCategory.TOURISM, "KR", "Tourism agency"),
    DataSource("https://english.seoul.go.kr/", "Visit Seoul", SourceCategory.TOURISM, "KR", "Seoul tourism"),
    DataSource("https://www.visitbusan.net/", "Visit Busan", SourceCategory.TOURISM, "KR", "Busan tourism"),
    DataSource("https://www.visitjeju.net/", "Visit Jeju", SourceCategory.TOURISM, "KR", "Jeju island"),
    DataSource("https://www.koreatravel.or.kr/", "Korea Travel", SourceCategory.TOURISM, "KR", "Travel info"),
    DataSource("https://www.yeogi.com/", "Yeogi", SourceCategory.TOURISM, "KR", "Hotel booking"),
    
    # 🇸🇬🇭🇰🇹🇼 OTHER ASIA TOURISM
    DataSource("https://www.visitsingapore.com/", "Visit Singapore", SourceCategory.TOURISM, "SG", "Singapore tourism", True),
    DataSource("https://www.stb.gov.sg/", "Singapore Tourism Board", SourceCategory.TOURISM, "SG", "Tourism board"),
    DataSource("https://www.discoverhongkong.com/", "Discover Hong Kong", SourceCategory.TOURISM, "HK", "Hong Kong tourism", True),
    DataSource("https://eng.taiwan.net.tw/", "Taiwan Tourism", SourceCategory.TOURISM, "TW", "Taiwan tourism"),
    DataSource("https://www.klook.com/", "Klook", SourceCategory.TOURISM, "HK", "Activity booking", True),
]

# ============================================================
# 🎮 ASIA HOBBY & LIFESTYLE SOURCES
# ============================================================

ASIA_HOBBY_SOURCES = [
    # Gaming & Esports
    DataSource("https://www.17173.com/", "17173 Gaming", SourceCategory.HOBBY, "CN", "Gaming portal"),
    DataSource("https://www.gamersky.com/", "Gamersky", SourceCategory.HOBBY, "CN", "Gaming news"),
    DataSource("https://www.3dmgame.com/", "3DM Game", SourceCategory.HOBBY, "CN", "Gaming community"),
    DataSource("https://nga.cn/", "NGA", SourceCategory.HOBBY, "CN", "Gaming forum"),
    DataSource("https://www.4gamer.net/", "4Gamer", SourceCategory.HOBBY, "JP", "Gaming news"),
    DataSource("https://www.famitsu.com/", "Famitsu", SourceCategory.HOBBY, "JP", "Gaming magazine", True),
    DataSource("https://www.dengekionline.com/", "Dengeki Online", SourceCategory.HOBBY, "JP", "Gaming news"),
    DataSource("https://www.inven.co.kr/", "Inven", SourceCategory.HOBBY, "KR", "Gaming portal"),
    DataSource("https://www.ruliweb.com/", "Ruliweb", SourceCategory.HOBBY, "KR", "Gaming forum"),
    
    # Manga & Comics
    DataSource("https://ac.qq.com/", "Tencent Comics", SourceCategory.HOBBY, "CN", "Manhua platform"),
    DataSource("https://www.dongmanmanhua.cn/", "Dongman", SourceCategory.HOBBY, "CN", "Comics platform"),
    DataSource("https://www.shonenjump.com/", "Shonen Jump", SourceCategory.HOBBY, "JP", "Manga magazine", True),
    DataSource("https://mangaplus.shueisha.co.jp/", "Manga Plus", SourceCategory.HOBBY, "JP", "Free manga", True),
    DataSource("https://webtoon.kakao.com/", "Kakao Webtoon", SourceCategory.HOBBY, "KR", "Webtoon platform"),
    DataSource("https://www.webtoons.com/", "Webtoons", SourceCategory.HOBBY, "KR", "Webtoon global", True),
    DataSource("https://comic.naver.com/", "Naver Webtoon", SourceCategory.HOBBY, "KR", "Webtoon platform"),
    
    # Cosplay & Collectibles
    DataSource("https://www.coser.com/", "Coser.com", SourceCategory.HOBBY, "CN", "Cosplay community"),
    DataSource("https://www.amiami.com/", "AmiAmi", SourceCategory.HOBBY, "JP", "Figure shop"),
    DataSource("https://www.goodsmile.info/", "Good Smile Company", SourceCategory.HOBBY, "JP", "Figure manufacturer"),
    DataSource("https://www.kotobukiya.co.jp/", "Kotobukiya", SourceCategory.HOBBY, "JP", "Figure/model kits"),
    DataSource("https://www.bandai.co.jp/", "Bandai", SourceCategory.HOBBY, "JP", "Toys/collectibles"),
    DataSource("https://tamashiinations.com/", "Tamashii Nations", SourceCategory.HOBBY, "JP", "Collectible figures"),
    
    # Food & Cooking
    DataSource("https://www.xiachufang.com/", "Xiachufang", SourceCategory.LIFESTYLE, "CN", "Recipe platform"),
    DataSource("https://www.meishij.net/", "Meishij", SourceCategory.LIFESTYLE, "CN", "Food recipes"),
    DataSource("https://cookpad.com/", "Cookpad Japan", SourceCategory.LIFESTYLE, "JP", "Recipe sharing"),
    DataSource("https://www.bob-an.com/", "Bob-an Recipes", SourceCategory.LIFESTYLE, "JP", "Cooking"),
    DataSource("https://www.haemukja.com/", "Haemukja", SourceCategory.LIFESTYLE, "KR", "Korean recipes"),
    DataSource("https://www.10000recipe.com/", "10000 Recipe", SourceCategory.LIFESTYLE, "KR", "Recipe platform"),
]

# ============================================================
# 🎪 ASIA EVENTS SOURCES
# ============================================================

ASIA_EVENTS_SOURCES = [
    # Trade Shows & Conventions
    DataSource("https://www.cantonfair.org.cn/", "Canton Fair", SourceCategory.EVENTS, "CN", "Trade fair"),
    DataSource("https://www.ciie.org/", "China Import Expo", SourceCategory.EVENTS, "CN", "Import expo"),
    DataSource("https://www.chinajoy.net/", "ChinaJoy", SourceCategory.EVENTS, "CN", "Gaming expo"),
    DataSource("https://comicup.com/", "Comicup", SourceCategory.EVENTS, "CN", "Comic convention"),
    DataSource("https://www.tokyo-gameshow.com/", "Tokyo Game Show", SourceCategory.EVENTS, "JP", "Gaming expo"),
    DataSource("https://www.comiket.co.jp/", "Comiket", SourceCategory.EVENTS, "JP", "Comic market"),
    DataSource("https://www.anime-japan.jp/", "AnimeJapan", SourceCategory.EVENTS, "JP", "Anime expo"),
    DataSource("https://www.jump-festa.com/", "Jump Festa", SourceCategory.EVENTS, "JP", "Manga expo"),
    DataSource("https://www.gstar.or.kr/", "G-STAR", SourceCategory.EVENTS, "KR", "Gaming expo"),
    DataSource("https://kcon.mnet.com/", "KCON", SourceCategory.EVENTS, "KR", "K-pop convention"),
    DataSource("https://www.mama.mwave.me/", "MAMA Awards", SourceCategory.EVENTS, "KR", "Music awards"),
    DataSource("https://www.formula1singapore.com/", "F1 Singapore", SourceCategory.EVENTS, "SG", "Grand Prix"),
    DataSource("https://www.marqueesingapore.com/", "Marquee Singapore", SourceCategory.EVENTS, "SG", "Nightlife"),
]

# ============================================================
# COMBINED EXPORT
# ============================================================

ALL_ASIA_CHINA_SOURCES = (
    CHINA_GOVERNMENT + CHINA_UNIVERSITIES + CHINA_HOSPITALS + 
    CHINA_BANKS + CHINA_FACTORIES_INDUSTRIAL + CHINA_NEWS_MEDIA +
    CHINA_CULTURE + CHINA_RESEARCH_INSTITUTES +
    JAPAN_GOVERNMENT + JAPAN_UNIVERSITIES + JAPAN_HOSPITALS +
    JAPAN_BANKS + JAPAN_FACTORIES + JAPAN_NEWS + JAPAN_CULTURE +
    KOREA_GOVERNMENT + KOREA_UNIVERSITIES + KOREA_HOSPITALS +
    KOREA_BANKS + KOREA_FACTORIES + KOREA_NEWS + KOREA_CULTURE + KOREA_RESEARCH +
    TAIWAN_SOURCES + HONG_KONG_SOURCES + MONGOLIA_SOURCES + SINGAPORE_SOURCES +
    CHINA_SPORT_SOURCES + ASIA_ENTERTAINMENT_SOURCES + ASIA_TOURISM_SOURCES +
    ASIA_HOBBY_SOURCES + ASIA_EVENTS_SOURCES
)

def get_all_sources() -> List[DataSource]:
    """Return all Asia/China data sources"""
    return ALL_ASIA_CHINA_SOURCES

def get_sources_by_country(country_code: str) -> List[DataSource]:
    """Return sources for a specific country"""
    return [s for s in ALL_ASIA_CHINA_SOURCES if s.country == country_code]

def get_sources_by_category(category: SourceCategory) -> List[DataSource]:
    """Return sources for a specific category"""
    return [s for s in ALL_ASIA_CHINA_SOURCES if s.category == category]

def get_api_sources() -> List[DataSource]:
    """Return only sources with API access"""
    return [s for s in ALL_ASIA_CHINA_SOURCES if s.api_available]

# Statistics
print(f"Total Asia/China Sources: {len(ALL_ASIA_CHINA_SOURCES)}")
print("Countries covered: CN, JP, KR, TW, HK, MN, SG")
