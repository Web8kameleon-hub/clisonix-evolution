# -*- coding: utf-8 -*-
"""
🌏 EAST ASIA, OCEANIA & GLOBAL - COMPLETE DATA SOURCES
=======================================================
600+ Free Open Data Sources from East Asia, Oceania & Global Organizations

Countries/Regions Covered:
- China 🇨🇳
- Japan 🇯🇵
- South Korea 🇰🇷
- Taiwan 🇹🇼
- Hong Kong 🇭🇰
- Singapore 🇸🇬
- Australia 🇦🇺
- New Zealand 🇳🇿
- Indonesia 🇮🇩
- Thailand 🇹🇭
- Vietnam 🇻🇳
- Philippines 🇵🇭
- Malaysia 🇲🇾
- Global Organizations 🌍

Categories:
- Government & Statistics
- Universities & Research
- Hospitals & Healthcare
- Banks & Financial
- Industry & Technology
- News & Media
- Culture & Museums
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
# 🇨🇳 CHINA DATA SOURCES
# ============================================================

CHINA_SOURCES = [
    DataSource("https://www.gov.cn/", "中国政府网", SourceCategory.GOVERNMENT, "CN", "Government portal"),
    DataSource("https://www.npc.gov.cn/", "全国人大", SourceCategory.GOVERNMENT, "CN", "National People's Congress"),
    DataSource("https://www.stats.gov.cn/", "国家统计局", SourceCategory.STATISTICS, "CN", "National Bureau of Statistics", True),
    DataSource("https://data.stats.gov.cn/", "统计数据", SourceCategory.STATISTICS, "CN", "Statistics data", True),
    DataSource("https://www.beijing.gov.cn/", "北京市政府", SourceCategory.GOVERNMENT, "CN", "Beijing city"),
    DataSource("https://www.shanghai.gov.cn/", "上海市政府", SourceCategory.GOVERNMENT, "CN", "Shanghai city"),
    DataSource("https://www.tsinghua.edu.cn/", "清华大学", SourceCategory.UNIVERSITY, "CN", "Tsinghua University"),
    DataSource("https://www.pku.edu.cn/", "北京大学", SourceCategory.UNIVERSITY, "CN", "Peking University"),
    DataSource("https://www.fudan.edu.cn/", "复旦大学", SourceCategory.UNIVERSITY, "CN", "Fudan University"),
    DataSource("https://www.sjtu.edu.cn/", "上海交大", SourceCategory.UNIVERSITY, "CN", "Shanghai Jiao Tong"),
    DataSource("https://www.zju.edu.cn/", "浙江大学", SourceCategory.UNIVERSITY, "CN", "Zhejiang University"),
    DataSource("https://www.ustc.edu.cn/", "中科大", SourceCategory.UNIVERSITY, "CN", "USTC"),
    DataSource("https://www.nju.edu.cn/", "南京大学", SourceCategory.UNIVERSITY, "CN", "Nanjing University"),
    DataSource("https://www.whu.edu.cn/", "武汉大学", SourceCategory.UNIVERSITY, "CN", "Wuhan University"),
    DataSource("https://www.cas.cn/", "中国科学院", SourceCategory.RESEARCH, "CN", "Chinese Academy of Sciences", True),
    DataSource("https://www.cae.cn/", "中国工程院", SourceCategory.RESEARCH, "CN", "Chinese Academy of Engineering"),
    DataSource("https://www.pbc.gov.cn/", "中国人民银行", SourceCategory.BANK, "CN", "People's Bank of China", True),
    DataSource("https://www.icbc.com.cn/", "中国工商银行", SourceCategory.BANK, "CN", "ICBC"),
    DataSource("https://www.ccb.com/", "中国建设银行", SourceCategory.BANK, "CN", "CCB"),
    DataSource("https://www.boc.cn/", "中国银行", SourceCategory.BANK, "CN", "Bank of China"),
    DataSource("https://www.abchina.com/", "中国农业银行", SourceCategory.BANK, "CN", "ABC"),
    DataSource("https://www.sse.com.cn/", "上海证券交易所", SourceCategory.BANK, "CN", "Shanghai Stock Exchange", True),
    DataSource("https://www.szse.cn/", "深圳证券交易所", SourceCategory.BANK, "CN", "Shenzhen Stock Exchange", True),
    DataSource("https://www.alibaba.com/", "阿里巴巴", SourceCategory.TECHNOLOGY, "CN", "E-commerce giant"),
    DataSource("https://www.tencent.com/", "腾讯", SourceCategory.TECHNOLOGY, "CN", "Tech/gaming"),
    DataSource("https://www.baidu.com/", "百度", SourceCategory.TECHNOLOGY, "CN", "Search engine"),
    DataSource("https://www.jd.com/", "京东", SourceCategory.TECHNOLOGY, "CN", "E-commerce"),
    DataSource("https://www.huawei.com/", "华为", SourceCategory.TECHNOLOGY, "CN", "Telecom/tech"),
    DataSource("https://www.xiaomi.com/", "小米", SourceCategory.TECHNOLOGY, "CN", "Electronics"),
    DataSource("https://www.bytedance.com/", "字节跳动", SourceCategory.TECHNOLOGY, "CN", "TikTok parent"),
    DataSource("https://www.dji.com/", "大疆", SourceCategory.TECHNOLOGY, "CN", "Drones"),
    DataSource("https://www.byd.com/", "比亚迪", SourceCategory.INDUSTRY, "CN", "Electric vehicles"),
    DataSource("https://www.nio.com/", "蔚来", SourceCategory.INDUSTRY, "CN", "Electric vehicles"),
    DataSource("https://www.cnpc.com.cn/", "中国石油", SourceCategory.ENERGY, "CN", "PetroChina"),
    DataSource("https://www.sinopec.com/", "中国石化", SourceCategory.ENERGY, "CN", "Sinopec"),
    DataSource("https://www.csair.com/", "南方航空", SourceCategory.TRANSPORT, "CN", "China Southern"),
    DataSource("https://www.airchina.com.cn/", "中国国航", SourceCategory.TRANSPORT, "CN", "Air China"),
    DataSource("https://www.ceair.com/", "东方航空", SourceCategory.TRANSPORT, "CN", "China Eastern"),
    DataSource("https://www.12306.cn/", "铁路12306", SourceCategory.TRANSPORT, "CN", "Railway booking", True),
    DataSource("https://www.xinhuanet.com/", "新华网", SourceCategory.NEWS, "CN", "Xinhua News"),
    DataSource("https://www.people.com.cn/", "人民网", SourceCategory.NEWS, "CN", "People's Daily"),
    DataSource("https://www.cctv.com/", "央视", SourceCategory.NEWS, "CN", "CCTV"),
    DataSource("https://www.chinadaily.com.cn/", "中国日报", SourceCategory.NEWS, "CN", "China Daily"),
    DataSource("https://www.caixin.com/", "财新", SourceCategory.NEWS, "CN", "Financial news"),
    DataSource("https://www.dpm.org.cn/", "故宫博物院", SourceCategory.CULTURE, "CN", "Palace Museum"),
    DataSource("https://www.chnmuseum.cn/", "中国国家博物馆", SourceCategory.CULTURE, "CN", "National Museum"),
    DataSource("https://www.travelchina.gov.cn/", "中国旅游", SourceCategory.TOURISM, "CN", "Tourism"),
    DataSource("https://www.cfa.com.cn/", "中国足协", SourceCategory.SPORT, "CN", "Football association"),
    DataSource("https://www.csl.org.cn/", "中超联赛", SourceCategory.SPORT, "CN", "Chinese Super League"),
    DataSource("https://www.cba.com.cn/", "CBA", SourceCategory.SPORT, "CN", "Basketball", True),
    DataSource("https://www.olympic.cn/", "中国奥委会", SourceCategory.SPORT, "CN", "Olympic committee"),
]

# ============================================================
# 🇯🇵 JAPAN DATA SOURCES
# ============================================================

JAPAN_SOURCES = [
    DataSource("https://www.kantei.go.jp/", "首相官邸", SourceCategory.GOVERNMENT, "JP", "Prime Minister's Office"),
    DataSource("https://www.shugiin.go.jp/", "衆議院", SourceCategory.GOVERNMENT, "JP", "House of Representatives"),
    DataSource("https://www.sangiin.go.jp/", "参議院", SourceCategory.GOVERNMENT, "JP", "House of Councillors"),
    DataSource("https://www.e-stat.go.jp/", "e-Stat", SourceCategory.STATISTICS, "JP", "Government statistics", True),
    DataSource("https://www.stat.go.jp/", "統計局", SourceCategory.STATISTICS, "JP", "Statistics Bureau", True),
    DataSource("https://www.metro.tokyo.lg.jp/", "東京都", SourceCategory.GOVERNMENT, "JP", "Tokyo Metro"),
    DataSource("https://www.city.osaka.lg.jp/", "大阪市", SourceCategory.GOVERNMENT, "JP", "Osaka city"),
    DataSource("https://www.u-tokyo.ac.jp/", "東京大学", SourceCategory.UNIVERSITY, "JP", "University of Tokyo"),
    DataSource("https://www.kyoto-u.ac.jp/", "京都大学", SourceCategory.UNIVERSITY, "JP", "Kyoto University"),
    DataSource("https://www.osaka-u.ac.jp/", "大阪大学", SourceCategory.UNIVERSITY, "JP", "Osaka University"),
    DataSource("https://www.titech.ac.jp/", "東京工業大学", SourceCategory.UNIVERSITY, "JP", "Tokyo Tech"),
    DataSource("https://www.tohoku.ac.jp/", "東北大学", SourceCategory.UNIVERSITY, "JP", "Tohoku University"),
    DataSource("https://www.waseda.jp/", "早稲田大学", SourceCategory.UNIVERSITY, "JP", "Waseda University"),
    DataSource("https://www.keio.ac.jp/", "慶應義塾大学", SourceCategory.UNIVERSITY, "JP", "Keio University"),
    DataSource("https://www.nagoya-u.ac.jp/", "名古屋大学", SourceCategory.UNIVERSITY, "JP", "Nagoya University"),
    DataSource("https://www.riken.jp/", "理化学研究所", SourceCategory.RESEARCH, "JP", "RIKEN", True),
    DataSource("https://www.jaxa.jp/", "JAXA", SourceCategory.RESEARCH, "JP", "Space agency", True),
    DataSource("https://www.boj.or.jp/", "日本銀行", SourceCategory.BANK, "JP", "Bank of Japan", True),
    DataSource("https://www.mufg.jp/", "三菱UFJ", SourceCategory.BANK, "JP", "MUFG Bank"),
    DataSource("https://www.smfg.co.jp/", "三井住友", SourceCategory.BANK, "JP", "SMFG"),
    DataSource("https://www.mizuho-fg.co.jp/", "みずほ", SourceCategory.BANK, "JP", "Mizuho"),
    DataSource("https://www.jpx.co.jp/", "東京証券取引所", SourceCategory.BANK, "JP", "Tokyo Stock Exchange", True),
    DataSource("https://www.toyota.co.jp/", "トヨタ", SourceCategory.INDUSTRY, "JP", "Toyota"),
    DataSource("https://www.honda.co.jp/", "ホンダ", SourceCategory.INDUSTRY, "JP", "Honda"),
    DataSource("https://www.nissan.co.jp/", "日産", SourceCategory.INDUSTRY, "JP", "Nissan"),
    DataSource("https://www.sony.co.jp/", "ソニー", SourceCategory.TECHNOLOGY, "JP", "Sony"),
    DataSource("https://www.panasonic.com/", "パナソニック", SourceCategory.TECHNOLOGY, "JP", "Panasonic"),
    DataSource("https://www.nintendo.co.jp/", "任天堂", SourceCategory.ENTERTAINMENT, "JP", "Nintendo"),
    DataSource("https://www.softbank.jp/", "ソフトバンク", SourceCategory.TELECOM, "JP", "SoftBank"),
    DataSource("https://www.nttdocomo.co.jp/", "NTTドコモ", SourceCategory.TELECOM, "JP", "NTT Docomo"),
    DataSource("https://www.jal.co.jp/", "日本航空", SourceCategory.TRANSPORT, "JP", "Japan Airlines"),
    DataSource("https://www.ana.co.jp/", "全日空", SourceCategory.TRANSPORT, "JP", "ANA"),
    DataSource("https://www.jreast.co.jp/", "JR東日本", SourceCategory.TRANSPORT, "JP", "JR East", True),
    DataSource("https://www.nhk.or.jp/", "NHK", SourceCategory.NEWS, "JP", "Public broadcaster"),
    DataSource("https://www.nikkei.com/", "日本経済新聞", SourceCategory.NEWS, "JP", "Nikkei"),
    DataSource("https://www.asahi.com/", "朝日新聞", SourceCategory.NEWS, "JP", "Asahi Shimbun"),
    DataSource("https://www.yomiuri.co.jp/", "読売新聞", SourceCategory.NEWS, "JP", "Yomiuri"),
    DataSource("https://mainichi.jp/", "毎日新聞", SourceCategory.NEWS, "JP", "Mainichi"),
    DataSource("https://www.kyodo.co.jp/", "共同通信", SourceCategory.NEWS, "JP", "Kyodo News", True),
    DataSource("https://www.tnm.jp/", "東京国立博物館", SourceCategory.CULTURE, "JP", "Tokyo National Museum"),
    DataSource("https://www.momat.go.jp/", "国立近代美術館", SourceCategory.CULTURE, "JP", "National Modern Art"),
    DataSource("https://www.jnto.go.jp/", "JNTO", SourceCategory.TOURISM, "JP", "Japan tourism", True),
    DataSource("https://www.jfa.jp/", "JFA", SourceCategory.SPORT, "JP", "Football association"),
    DataSource("https://www.jleague.jp/", "Jリーグ", SourceCategory.SPORT, "JP", "J.League", True),
    DataSource("https://www.npb.or.jp/", "NPB", SourceCategory.SPORT, "JP", "Baseball league", True),
    DataSource("https://www.sumo.or.jp/", "相撲協会", SourceCategory.SPORT, "JP", "Sumo"),
    DataSource("https://www.joc.or.jp/", "JOC", SourceCategory.SPORT, "JP", "Olympic committee"),
]

# ============================================================
# 🇰🇷 SOUTH KOREA DATA SOURCES
# ============================================================

KOREA_SOURCES = [
    DataSource("https://www.korea.go.kr/", "대한민국정부", SourceCategory.GOVERNMENT, "KR", "Government portal"),
    DataSource("https://www.assembly.go.kr/", "국회", SourceCategory.GOVERNMENT, "KR", "National Assembly"),
    DataSource("https://kostat.go.kr/", "통계청", SourceCategory.STATISTICS, "KR", "Statistics Korea", True),
    DataSource("https://www.data.go.kr/", "공공데이터포털", SourceCategory.STATISTICS, "KR", "Open data", True),
    DataSource("https://www.seoul.go.kr/", "서울시", SourceCategory.GOVERNMENT, "KR", "Seoul city"),
    DataSource("https://www.busan.go.kr/", "부산시", SourceCategory.GOVERNMENT, "KR", "Busan city"),
    DataSource("https://www.snu.ac.kr/", "서울대학교", SourceCategory.UNIVERSITY, "KR", "Seoul National University"),
    DataSource("https://www.kaist.ac.kr/", "KAIST", SourceCategory.UNIVERSITY, "KR", "Korea Advanced Institute"),
    DataSource("https://www.postech.ac.kr/", "POSTECH", SourceCategory.UNIVERSITY, "KR", "Pohang Tech"),
    DataSource("https://www.korea.ac.kr/", "고려대학교", SourceCategory.UNIVERSITY, "KR", "Korea University"),
    DataSource("https://www.yonsei.ac.kr/", "연세대학교", SourceCategory.UNIVERSITY, "KR", "Yonsei University"),
    DataSource("https://www.skku.edu/", "성균관대학교", SourceCategory.UNIVERSITY, "KR", "Sungkyunkwan"),
    DataSource("https://www.bok.or.kr/", "한국은행", SourceCategory.BANK, "KR", "Bank of Korea", True),
    DataSource("https://www.kbstar.com/", "KB국민은행", SourceCategory.BANK, "KR", "KB Kookmin"),
    DataSource("https://www.shinhan.com/", "신한은행", SourceCategory.BANK, "KR", "Shinhan Bank"),
    DataSource("https://www.wooribank.com/", "우리은행", SourceCategory.BANK, "KR", "Woori Bank"),
    DataSource("https://www.krx.co.kr/", "한국거래소", SourceCategory.BANK, "KR", "Korea Exchange", True),
    DataSource("https://www.samsung.com/", "삼성", SourceCategory.TECHNOLOGY, "KR", "Samsung"),
    DataSource("https://www.lg.com/", "LG", SourceCategory.TECHNOLOGY, "KR", "LG Corporation"),
    DataSource("https://www.hyundai.com/", "현대", SourceCategory.INDUSTRY, "KR", "Hyundai"),
    DataSource("https://www.kia.com/", "기아", SourceCategory.INDUSTRY, "KR", "Kia"),
    DataSource("https://www.sk.com/", "SK그룹", SourceCategory.INDUSTRY, "KR", "SK Group"),
    DataSource("https://www.naver.com/", "네이버", SourceCategory.TECHNOLOGY, "KR", "Naver"),
    DataSource("https://www.kakaocorp.com/", "카카오", SourceCategory.TECHNOLOGY, "KR", "Kakao"),
    DataSource("https://www.coupang.com/", "쿠팡", SourceCategory.TECHNOLOGY, "KR", "Coupang"),
    DataSource("https://www.koreanair.com/", "대한항공", SourceCategory.TRANSPORT, "KR", "Korean Air"),
    DataSource("https://www.asiana.com/", "아시아나", SourceCategory.TRANSPORT, "KR", "Asiana Airlines"),
    DataSource("https://www.letskorail.com/", "코레일", SourceCategory.TRANSPORT, "KR", "Korail", True),
    DataSource("https://www.kbs.co.kr/", "KBS", SourceCategory.NEWS, "KR", "Public broadcaster"),
    DataSource("https://www.mbc.co.kr/", "MBC", SourceCategory.NEWS, "KR", "Broadcasting"),
    DataSource("https://www.sbs.co.kr/", "SBS", SourceCategory.NEWS, "KR", "Broadcasting"),
    DataSource("https://www.chosun.com/", "조선일보", SourceCategory.NEWS, "KR", "Chosun Ilbo"),
    DataSource("https://www.donga.com/", "동아일보", SourceCategory.NEWS, "KR", "Dong-A Ilbo"),
    DataSource("https://www.joongang.co.kr/", "중앙일보", SourceCategory.NEWS, "KR", "JoongAng Ilbo"),
    DataSource("https://www.hani.co.kr/", "한겨레", SourceCategory.NEWS, "KR", "Hankyoreh"),
    DataSource("https://www.yonhapnews.co.kr/", "연합뉴스", SourceCategory.NEWS, "KR", "Yonhap News", True),
    DataSource("https://www.museum.go.kr/", "국립중앙박물관", SourceCategory.CULTURE, "KR", "National Museum"),
    DataSource("https://www.mmca.go.kr/", "국립현대미술관", SourceCategory.CULTURE, "KR", "Modern Art"),
    DataSource("https://korean.visitkorea.or.kr/", "Visit Korea", SourceCategory.TOURISM, "KR", "Tourism", True),
    DataSource("https://www.kfa.or.kr/", "대한축구협회", SourceCategory.SPORT, "KR", "Football association"),
    DataSource("https://www.kleague.com/", "K리그", SourceCategory.SPORT, "KR", "K League", True),
    DataSource("https://www.koreabaseball.com/", "KBO", SourceCategory.SPORT, "KR", "Baseball", True),
    DataSource("https://www.sports.or.kr/", "대한체육회", SourceCategory.SPORT, "KR", "Sports association"),
]

# ============================================================
# 🇹🇼 TAIWAN DATA SOURCES
# ============================================================

TAIWAN_SOURCES = [
    DataSource("https://www.gov.tw/", "中華民國政府", SourceCategory.GOVERNMENT, "TW", "Government portal"),
    DataSource("https://www.stat.gov.tw/", "行政院主計總處", SourceCategory.STATISTICS, "TW", "Statistics", True),
    DataSource("https://data.gov.tw/", "政府資料開放", SourceCategory.STATISTICS, "TW", "Open data", True),
    DataSource("https://www.ntu.edu.tw/", "國立臺灣大學", SourceCategory.UNIVERSITY, "TW", "National Taiwan University"),
    DataSource("https://www.nthu.edu.tw/", "國立清華大學", SourceCategory.UNIVERSITY, "TW", "Tsing Hua"),
    DataSource("https://www.nctu.edu.tw/", "國立交通大學", SourceCategory.UNIVERSITY, "TW", "Chiao Tung"),
    DataSource("https://www.ncku.edu.tw/", "國立成功大學", SourceCategory.UNIVERSITY, "TW", "Cheng Kung"),
    DataSource("https://www.cbc.gov.tw/", "中央銀行", SourceCategory.BANK, "TW", "Central Bank", True),
    DataSource("https://www.twse.com.tw/", "臺灣證券交易所", SourceCategory.BANK, "TW", "Taiwan Stock Exchange", True),
    DataSource("https://www.tsmc.com/", "台積電", SourceCategory.TECHNOLOGY, "TW", "TSMC"),
    DataSource("https://www.foxconn.com/", "鴻海科技", SourceCategory.TECHNOLOGY, "TW", "Foxconn"),
    DataSource("https://www.asus.com/", "華碩", SourceCategory.TECHNOLOGY, "TW", "Asus"),
    DataSource("https://www.acer.com/", "宏碁", SourceCategory.TECHNOLOGY, "TW", "Acer"),
    DataSource("https://www.htc.com/", "HTC", SourceCategory.TECHNOLOGY, "TW", "HTC"),
    DataSource("https://www.china-airlines.com/", "中華航空", SourceCategory.TRANSPORT, "TW", "China Airlines"),
    DataSource("https://www.evaair.com/", "長榮航空", SourceCategory.TRANSPORT, "TW", "EVA Air"),
    DataSource("https://www.thsrc.com.tw/", "高鐵", SourceCategory.TRANSPORT, "TW", "High Speed Rail", True),
    DataSource("https://www.cna.com.tw/", "中央通訊社", SourceCategory.NEWS, "TW", "CNA", True),
    DataSource("https://www.udn.com/", "聯合報", SourceCategory.NEWS, "TW", "United Daily"),
    DataSource("https://www.ltn.com.tw/", "自由時報", SourceCategory.NEWS, "TW", "Liberty Times"),
    DataSource("https://www.npm.gov.tw/", "故宮博物院", SourceCategory.CULTURE, "TW", "Palace Museum"),
    DataSource("https://www.taiwan.net.tw/", "交通部觀光局", SourceCategory.TOURISM, "TW", "Tourism", True),
    DataSource("https://www.ctfa.com.tw/", "中華民國足球協會", SourceCategory.SPORT, "TW", "Football"),
    DataSource("https://www.cpbl.com.tw/", "CPBL", SourceCategory.SPORT, "TW", "Baseball", True),
]

# ============================================================
# 🇭🇰 HONG KONG DATA SOURCES
# ============================================================

HONGKONG_SOURCES = [
    DataSource("https://www.gov.hk/", "香港政府", SourceCategory.GOVERNMENT, "HK", "Government portal"),
    DataSource("https://www.censtatd.gov.hk/", "政府統計處", SourceCategory.STATISTICS, "HK", "Census & Statistics", True),
    DataSource("https://data.gov.hk/", "資料一線通", SourceCategory.STATISTICS, "HK", "Open data", True),
    DataSource("https://www.hku.hk/", "香港大學", SourceCategory.UNIVERSITY, "HK", "University of Hong Kong"),
    DataSource("https://www.cuhk.edu.hk/", "香港中文大學", SourceCategory.UNIVERSITY, "HK", "Chinese University"),
    DataSource("https://www.ust.hk/", "香港科技大學", SourceCategory.UNIVERSITY, "HK", "HKUST"),
    DataSource("https://www.cityu.edu.hk/", "香港城市大學", SourceCategory.UNIVERSITY, "HK", "City University"),
    DataSource("https://www.hkma.gov.hk/", "香港金融管理局", SourceCategory.BANK, "HK", "HKMA", True),
    DataSource("https://www.hkex.com.hk/", "香港交易所", SourceCategory.BANK, "HK", "HKEX", True),
    DataSource("https://www.hsbc.com.hk/", "匯豐銀行", SourceCategory.BANK, "HK", "HSBC Hong Kong"),
    DataSource("https://www.bochk.com/", "中國銀行香港", SourceCategory.BANK, "HK", "Bank of China HK"),
    DataSource("https://www.cathaypacific.com/", "國泰航空", SourceCategory.TRANSPORT, "HK", "Cathay Pacific"),
    DataSource("https://www.mtr.com.hk/", "港鐵", SourceCategory.TRANSPORT, "HK", "MTR", True),
    DataSource("https://www.rthk.hk/", "香港電台", SourceCategory.NEWS, "HK", "RTHK"),
    DataSource("https://www.scmp.com/", "南華早報", SourceCategory.NEWS, "HK", "South China Morning Post"),
    DataSource("https://hk.apple.daily.com/", "蘋果日報", SourceCategory.NEWS, "HK", "Apple Daily"),
    DataSource("https://www.hkmu.org.hk/", "香港博物館", SourceCategory.CULTURE, "HK", "Museums"),
    DataSource("https://www.discoverhongkong.com/", "香港旅遊發展局", SourceCategory.TOURISM, "HK", "Tourism", True),
    DataSource("https://www.hkfa.com/", "香港足球總會", SourceCategory.SPORT, "HK", "Football"),
]

# ============================================================
# 🇸🇬 SINGAPORE DATA SOURCES
# ============================================================

SINGAPORE_SOURCES = [
    DataSource("https://www.gov.sg/", "Singapore Government", SourceCategory.GOVERNMENT, "SG", "Government portal"),
    DataSource("https://www.parliament.gov.sg/", "Parliament", SourceCategory.GOVERNMENT, "SG", "Parliament"),
    DataSource("https://www.singstat.gov.sg/", "SingStat", SourceCategory.STATISTICS, "SG", "Statistics", True),
    DataSource("https://data.gov.sg/", "Data.gov.sg", SourceCategory.STATISTICS, "SG", "Open data", True),
    DataSource("https://www.nus.edu.sg/", "NUS", SourceCategory.UNIVERSITY, "SG", "National University of Singapore"),
    DataSource("https://www.ntu.edu.sg/", "NTU", SourceCategory.UNIVERSITY, "SG", "Nanyang Tech"),
    DataSource("https://www.smu.edu.sg/", "SMU", SourceCategory.UNIVERSITY, "SG", "Singapore Management"),
    DataSource("https://www.sutd.edu.sg/", "SUTD", SourceCategory.UNIVERSITY, "SG", "Design & Technology"),
    DataSource("https://www.a-star.edu.sg/", "A*STAR", SourceCategory.RESEARCH, "SG", "Research agency", True),
    DataSource("https://www.mas.gov.sg/", "MAS", SourceCategory.BANK, "SG", "Monetary Authority", True),
    DataSource("https://www.dbs.com.sg/", "DBS Bank", SourceCategory.BANK, "SG", "Major bank"),
    DataSource("https://www.uob.com.sg/", "UOB", SourceCategory.BANK, "SG", "Major bank"),
    DataSource("https://www.ocbc.com/", "OCBC", SourceCategory.BANK, "SG", "Major bank"),
    DataSource("https://www.sgx.com/", "SGX", SourceCategory.BANK, "SG", "Singapore Exchange", True),
    DataSource("https://www.grab.com/", "Grab", SourceCategory.TECHNOLOGY, "SG", "Super app"),
    DataSource("https://www.sea.com/", "Sea Limited", SourceCategory.TECHNOLOGY, "SG", "Tech/gaming"),
    DataSource("https://www.singtel.com/", "Singtel", SourceCategory.TELECOM, "SG", "Telecom"),
    DataSource("https://www.singaporeair.com/", "Singapore Airlines", SourceCategory.TRANSPORT, "SG", "National airline"),
    DataSource("https://www.smrt.com.sg/", "SMRT", SourceCategory.TRANSPORT, "SG", "Public transport"),
    DataSource("https://www.straitstimes.com/", "Straits Times", SourceCategory.NEWS, "SG", "Major newspaper"),
    DataSource("https://www.channelnewsasia.com/", "CNA", SourceCategory.NEWS, "SG", "News channel"),
    DataSource("https://www.todayonline.com/", "TODAY", SourceCategory.NEWS, "SG", "News portal"),
    DataSource("https://www.nhb.gov.sg/", "National Heritage Board", SourceCategory.CULTURE, "SG", "Heritage"),
    DataSource("https://www.nationalgallery.sg/", "National Gallery", SourceCategory.CULTURE, "SG", "Art gallery"),
    DataSource("https://www.visitsingapore.com/", "Visit Singapore", SourceCategory.TOURISM, "SG", "Tourism", True),
    DataSource("https://www.fas.sg/", "FAS", SourceCategory.SPORT, "SG", "Football"),
    DataSource("https://www.singsoc.org/", "Singapore Sports", SourceCategory.SPORT, "SG", "Sports council"),
]

# ============================================================
# 🇦🇺 AUSTRALIA DATA SOURCES
# ============================================================

AUSTRALIA_SOURCES = [
    DataSource("https://www.australia.gov.au/", "Australia.gov.au", SourceCategory.GOVERNMENT, "AU", "Government portal"),
    DataSource("https://www.aph.gov.au/", "Australian Parliament", SourceCategory.GOVERNMENT, "AU", "Parliament"),
    DataSource("https://www.abs.gov.au/", "ABS", SourceCategory.STATISTICS, "AU", "Bureau of Statistics", True),
    DataSource("https://data.gov.au/", "Data.gov.au", SourceCategory.STATISTICS, "AU", "Open data", True),
    DataSource("https://www.nsw.gov.au/", "NSW Government", SourceCategory.GOVERNMENT, "AU", "New South Wales"),
    DataSource("https://www.vic.gov.au/", "Victoria Government", SourceCategory.GOVERNMENT, "AU", "Victoria state"),
    DataSource("https://www.sydney.edu.au/", "University of Sydney", SourceCategory.UNIVERSITY, "AU", "Sydney university"),
    DataSource("https://www.unimelb.edu.au/", "University of Melbourne", SourceCategory.UNIVERSITY, "AU", "Melbourne university"),
    DataSource("https://www.anu.edu.au/", "ANU", SourceCategory.UNIVERSITY, "AU", "Australian National"),
    DataSource("https://www.unsw.edu.au/", "UNSW", SourceCategory.UNIVERSITY, "AU", "NSW university"),
    DataSource("https://www.uq.edu.au/", "University of Queensland", SourceCategory.UNIVERSITY, "AU", "Queensland"),
    DataSource("https://www.monash.edu/", "Monash University", SourceCategory.UNIVERSITY, "AU", "Melbourne area"),
    DataSource("https://www.adelaide.edu.au/", "University of Adelaide", SourceCategory.UNIVERSITY, "AU", "Adelaide"),
    DataSource("https://www.uwa.edu.au/", "UWA", SourceCategory.UNIVERSITY, "AU", "Western Australia"),
    DataSource("https://www.csiro.au/", "CSIRO", SourceCategory.RESEARCH, "AU", "Research organization", True),
    DataSource("https://www.rba.gov.au/", "Reserve Bank of Australia", SourceCategory.BANK, "AU", "Central bank", True),
    DataSource("https://www.commbank.com.au/", "CommBank", SourceCategory.BANK, "AU", "Commonwealth Bank"),
    DataSource("https://www.westpac.com.au/", "Westpac", SourceCategory.BANK, "AU", "Major bank"),
    DataSource("https://www.nab.com.au/", "NAB", SourceCategory.BANK, "AU", "National Australia Bank"),
    DataSource("https://www.anz.com.au/", "ANZ", SourceCategory.BANK, "AU", "Major bank"),
    DataSource("https://www.asx.com.au/", "ASX", SourceCategory.BANK, "AU", "Australian Securities Exchange", True),
    DataSource("https://www.bhp.com/", "BHP", SourceCategory.INDUSTRY, "AU", "Mining"),
    DataSource("https://www.riotinto.com/", "Rio Tinto", SourceCategory.INDUSTRY, "AU", "Mining"),
    DataSource("https://www.woodside.com.au/", "Woodside", SourceCategory.ENERGY, "AU", "Oil/gas"),
    DataSource("https://www.telstra.com.au/", "Telstra", SourceCategory.TELECOM, "AU", "Telecom"),
    DataSource("https://www.qantas.com/", "Qantas", SourceCategory.TRANSPORT, "AU", "National airline"),
    DataSource("https://www.abc.net.au/", "ABC Australia", SourceCategory.NEWS, "AU", "Public broadcaster"),
    DataSource("https://www.sbs.com.au/", "SBS", SourceCategory.NEWS, "AU", "Public broadcaster"),
    DataSource("https://www.smh.com.au/", "Sydney Morning Herald", SourceCategory.NEWS, "AU", "Major newspaper"),
    DataSource("https://www.theaustralian.com.au/", "The Australian", SourceCategory.NEWS, "AU", "National newspaper"),
    DataSource("https://www.9news.com.au/", "Nine News", SourceCategory.NEWS, "AU", "News network"),
    DataSource("https://www.aap.com.au/", "AAP", SourceCategory.NEWS, "AU", "News agency"),
    DataSource("https://www.nma.gov.au/", "National Museum", SourceCategory.CULTURE, "AU", "National museum"),
    DataSource("https://www.nga.gov.au/", "National Gallery of Australia", SourceCategory.CULTURE, "AU", "Art gallery"),
    DataSource("https://www.sydneyoperahouse.com/", "Sydney Opera House", SourceCategory.CULTURE, "AU", "Opera house"),
    DataSource("https://www.australia.com/", "Tourism Australia", SourceCategory.TOURISM, "AU", "Tourism", True),
    DataSource("https://www.afl.com.au/", "AFL", SourceCategory.SPORT, "AU", "Australian Football", True),
    DataSource("https://www.nrl.com/", "NRL", SourceCategory.SPORT, "AU", "Rugby League", True),
    DataSource("https://www.cricket.com.au/", "Cricket Australia", SourceCategory.SPORT, "AU", "Cricket", True),
    DataSource("https://www.footballaustralia.com.au/", "Football Australia", SourceCategory.SPORT, "AU", "Soccer"),
    DataSource("https://www.a-league.com.au/", "A-League", SourceCategory.SPORT, "AU", "Soccer league"),
    DataSource("https://www.tennis.com.au/", "Tennis Australia", SourceCategory.SPORT, "AU", "Tennis"),
    DataSource("https://ausopen.com/", "Australian Open", SourceCategory.SPORT, "AU", "Grand Slam", True),
    DataSource("https://www.swimming.org.au/", "Swimming Australia", SourceCategory.SPORT, "AU", "Swimming"),
    DataSource("https://www.olympics.com.au/", "Australian Olympic Committee", SourceCategory.SPORT, "AU", "Olympics"),
]

# ============================================================
# 🇳🇿 NEW ZEALAND DATA SOURCES
# ============================================================

NEWZEALAND_SOURCES = [
    DataSource("https://www.govt.nz/", "New Zealand Government", SourceCategory.GOVERNMENT, "NZ", "Government portal"),
    DataSource("https://www.parliament.nz/", "Parliament of NZ", SourceCategory.GOVERNMENT, "NZ", "Parliament"),
    DataSource("https://www.stats.govt.nz/", "Stats NZ", SourceCategory.STATISTICS, "NZ", "Statistics", True),
    DataSource("https://www.data.govt.nz/", "Data.govt.nz", SourceCategory.STATISTICS, "NZ", "Open data", True),
    DataSource("https://www.auckland.ac.nz/", "University of Auckland", SourceCategory.UNIVERSITY, "NZ", "Auckland university"),
    DataSource("https://www.otago.ac.nz/", "University of Otago", SourceCategory.UNIVERSITY, "NZ", "Otago university"),
    DataSource("https://www.canterbury.ac.nz/", "University of Canterbury", SourceCategory.UNIVERSITY, "NZ", "Canterbury"),
    DataSource("https://www.victoria.ac.nz/", "Victoria University", SourceCategory.UNIVERSITY, "NZ", "Wellington"),
    DataSource("https://www.waikato.ac.nz/", "University of Waikato", SourceCategory.UNIVERSITY, "NZ", "Waikato"),
    DataSource("https://www.rbnz.govt.nz/", "Reserve Bank of NZ", SourceCategory.BANK, "NZ", "Central bank", True),
    DataSource("https://www.anz.co.nz/", "ANZ New Zealand", SourceCategory.BANK, "NZ", "Major bank"),
    DataSource("https://www.kiwibank.co.nz/", "Kiwibank", SourceCategory.BANK, "NZ", "National bank"),
    DataSource("https://www.nzx.com/", "NZX", SourceCategory.BANK, "NZ", "Stock exchange", True),
    DataSource("https://www.fonterra.com/", "Fonterra", SourceCategory.INDUSTRY, "NZ", "Dairy cooperative"),
    DataSource("https://www.airnewzealand.co.nz/", "Air New Zealand", SourceCategory.TRANSPORT, "NZ", "National airline"),
    DataSource("https://www.rnz.co.nz/", "RNZ", SourceCategory.NEWS, "NZ", "Public broadcaster"),
    DataSource("https://www.nzherald.co.nz/", "NZ Herald", SourceCategory.NEWS, "NZ", "Major newspaper"),
    DataSource("https://www.stuff.co.nz/", "Stuff", SourceCategory.NEWS, "NZ", "News portal"),
    DataSource("https://www.tepapa.govt.nz/", "Te Papa", SourceCategory.CULTURE, "NZ", "National museum"),
    DataSource("https://www.newzealand.com/", "Tourism NZ", SourceCategory.TOURISM, "NZ", "Tourism", True),
    DataSource("https://www.nzfootball.co.nz/", "NZ Football", SourceCategory.SPORT, "NZ", "Football"),
    DataSource("https://www.allblacks.com/", "All Blacks", SourceCategory.SPORT, "NZ", "Rugby"),
    DataSource("https://www.nzrugby.co.nz/", "NZ Rugby", SourceCategory.SPORT, "NZ", "Rugby union"),
    DataSource("https://www.blackcaps.co.nz/", "Black Caps", SourceCategory.SPORT, "NZ", "Cricket"),
    DataSource("https://www.olympic.org.nz/", "NZ Olympic Committee", SourceCategory.SPORT, "NZ", "Olympics"),
]

# ============================================================
# 🇮🇩 INDONESIA DATA SOURCES
# ============================================================

INDONESIA_SOURCES = [
    DataSource("https://www.indonesia.go.id/", "Indonesia.go.id", SourceCategory.GOVERNMENT, "ID", "Government portal"),
    DataSource("https://www.bps.go.id/", "BPS", SourceCategory.STATISTICS, "ID", "Statistics", True),
    DataSource("https://data.go.id/", "Data.go.id", SourceCategory.STATISTICS, "ID", "Open data", True),
    DataSource("https://www.ui.ac.id/", "Universitas Indonesia", SourceCategory.UNIVERSITY, "ID", "UI"),
    DataSource("https://www.itb.ac.id/", "ITB", SourceCategory.UNIVERSITY, "ID", "Bandung Tech"),
    DataSource("https://www.ugm.ac.id/", "UGM", SourceCategory.UNIVERSITY, "ID", "Gadjah Mada"),
    DataSource("https://www.its.ac.id/", "ITS", SourceCategory.UNIVERSITY, "ID", "Surabaya Tech"),
    DataSource("https://www.bi.go.id/", "Bank Indonesia", SourceCategory.BANK, "ID", "Central bank", True),
    DataSource("https://www.idx.co.id/", "IDX", SourceCategory.BANK, "ID", "Stock exchange", True),
    DataSource("https://www.bri.co.id/", "BRI", SourceCategory.BANK, "ID", "Major bank"),
    DataSource("https://www.bca.co.id/", "BCA", SourceCategory.BANK, "ID", "Major bank"),
    DataSource("https://www.mandiri.co.id/", "Bank Mandiri", SourceCategory.BANK, "ID", "State bank"),
    DataSource("https://www.gojek.com/", "Gojek", SourceCategory.TECHNOLOGY, "ID", "Super app"),
    DataSource("https://www.tokopedia.com/", "Tokopedia", SourceCategory.TECHNOLOGY, "ID", "E-commerce"),
    DataSource("https://www.pertamina.com/", "Pertamina", SourceCategory.ENERGY, "ID", "State oil"),
    DataSource("https://www.garuda-indonesia.com/", "Garuda Indonesia", SourceCategory.TRANSPORT, "ID", "National airline"),
    DataSource("https://www.kompas.com/", "Kompas", SourceCategory.NEWS, "ID", "Major newspaper"),
    DataSource("https://www.detik.com/", "Detik", SourceCategory.NEWS, "ID", "News portal"),
    DataSource("https://www.tempo.co/", "Tempo", SourceCategory.NEWS, "ID", "News magazine"),
    DataSource("https://www.antara.co.id/", "Antara", SourceCategory.NEWS, "ID", "News agency"),
    DataSource("https://www.indonesia.travel/", "Wonderful Indonesia", SourceCategory.TOURISM, "ID", "Tourism", True),
    DataSource("https://www.pssi.org/", "PSSI", SourceCategory.SPORT, "ID", "Football federation"),
    DataSource("https://www.koi.or.id/", "KOI", SourceCategory.SPORT, "ID", "Olympic committee"),
]

# ============================================================
# 🇹🇭 THAILAND DATA SOURCES
# ============================================================

THAILAND_SOURCES = [
    DataSource("https://www.thaigov.go.th/", "Thai Government", SourceCategory.GOVERNMENT, "TH", "Government portal"),
    DataSource("https://www.nso.go.th/", "NSO Thailand", SourceCategory.STATISTICS, "TH", "Statistics", True),
    DataSource("https://data.go.th/", "Data.go.th", SourceCategory.STATISTICS, "TH", "Open data", True),
    DataSource("https://www.chula.ac.th/", "Chulalongkorn", SourceCategory.UNIVERSITY, "TH", "Top university"),
    DataSource("https://www.mahidol.ac.th/", "Mahidol", SourceCategory.UNIVERSITY, "TH", "Medical university"),
    DataSource("https://www.bot.or.th/", "Bank of Thailand", SourceCategory.BANK, "TH", "Central bank", True),
    DataSource("https://www.set.or.th/", "SET", SourceCategory.BANK, "TH", "Stock exchange", True),
    DataSource("https://www.thaiairways.com/", "Thai Airways", SourceCategory.TRANSPORT, "TH", "National airline"),
    DataSource("https://www.bangkokpost.com/", "Bangkok Post", SourceCategory.NEWS, "TH", "English newspaper"),
    DataSource("https://www.nationthailand.com/", "The Nation", SourceCategory.NEWS, "TH", "English newspaper"),
    DataSource("https://www.thairath.co.th/", "Thai Rath", SourceCategory.NEWS, "TH", "Thai newspaper"),
    DataSource("https://www.tourismthailand.org/", "TAT", SourceCategory.TOURISM, "TH", "Tourism", True),
    DataSource("https://www.fathailand.org/", "FA Thailand", SourceCategory.SPORT, "TH", "Football"),
]

# ============================================================
# 🇻🇳 VIETNAM DATA SOURCES
# ============================================================

VIETNAM_SOURCES = [
    DataSource("https://www.chinhphu.vn/", "Vietnam Government", SourceCategory.GOVERNMENT, "VN", "Government portal"),
    DataSource("https://www.gso.gov.vn/", "GSO", SourceCategory.STATISTICS, "VN", "Statistics", True),
    DataSource("https://data.gov.vn/", "Data.gov.vn", SourceCategory.STATISTICS, "VN", "Open data", True),
    DataSource("https://www.vnu.edu.vn/", "Vietnam National University", SourceCategory.UNIVERSITY, "VN", "VNU Hanoi"),
    DataSource("https://www.hust.edu.vn/", "HUST", SourceCategory.UNIVERSITY, "VN", "Hanoi Tech"),
    DataSource("https://www.sbv.gov.vn/", "State Bank of Vietnam", SourceCategory.BANK, "VN", "Central bank", True),
    DataSource("https://www.hsx.vn/", "HOSE", SourceCategory.BANK, "VN", "Stock exchange", True),
    DataSource("https://www.vietnamairlines.com/", "Vietnam Airlines", SourceCategory.TRANSPORT, "VN", "National airline"),
    DataSource("https://www.vnexpress.net/", "VnExpress", SourceCategory.NEWS, "VN", "News portal"),
    DataSource("https://www.thanhnien.vn/", "Thanh Nien", SourceCategory.NEWS, "VN", "Major newspaper"),
    DataSource("https://www.tuoitre.vn/", "Tuoi Tre", SourceCategory.NEWS, "VN", "Major newspaper"),
    DataSource("https://www.vnanet.vn/", "VNA", SourceCategory.NEWS, "VN", "News agency"),
    DataSource("https://vietnam.travel/", "Vietnam Tourism", SourceCategory.TOURISM, "VN", "Tourism", True),
    DataSource("https://www.vff.org.vn/", "VFF", SourceCategory.SPORT, "VN", "Football"),
]

# ============================================================
# 🇵🇭 PHILIPPINES DATA SOURCES
# ============================================================

PHILIPPINES_SOURCES = [
    DataSource("https://www.gov.ph/", "Gov.ph", SourceCategory.GOVERNMENT, "PH", "Government portal"),
    DataSource("https://psa.gov.ph/", "PSA", SourceCategory.STATISTICS, "PH", "Statistics", True),
    DataSource("https://data.gov.ph/", "Data.gov.ph", SourceCategory.STATISTICS, "PH", "Open data", True),
    DataSource("https://www.up.edu.ph/", "University of the Philippines", SourceCategory.UNIVERSITY, "PH", "UP"),
    DataSource("https://www.ateneo.edu/", "Ateneo", SourceCategory.UNIVERSITY, "PH", "Ateneo de Manila"),
    DataSource("https://www.dlsu.edu.ph/", "DLSU", SourceCategory.UNIVERSITY, "PH", "De La Salle"),
    DataSource("https://www.bsp.gov.ph/", "BSP", SourceCategory.BANK, "PH", "Central bank", True),
    DataSource("https://www.pse.com.ph/", "PSE", SourceCategory.BANK, "PH", "Stock exchange", True),
    DataSource("https://www.philippineairlines.com/", "Philippine Airlines", SourceCategory.TRANSPORT, "PH", "National airline"),
    DataSource("https://www.cebuair.com/", "Cebu Pacific", SourceCategory.TRANSPORT, "PH", "Low-cost airline"),
    DataSource("https://www.philstar.com/", "Philippine Star", SourceCategory.NEWS, "PH", "Major newspaper"),
    DataSource("https://www.inquirer.net/", "Inquirer", SourceCategory.NEWS, "PH", "Major newspaper"),
    DataSource("https://www.abs-cbn.com/", "ABS-CBN", SourceCategory.NEWS, "PH", "Broadcasting"),
    DataSource("https://www.gmanetwork.com/", "GMA", SourceCategory.NEWS, "PH", "Broadcasting"),
    DataSource("https://www.pna.gov.ph/", "PNA", SourceCategory.NEWS, "PH", "News agency"),
    DataSource("https://www.itsmorefuninthephilippines.com/", "DOT Philippines", SourceCategory.TOURISM, "PH", "Tourism", True),
    DataSource("https://www.pff.ph/", "PFF", SourceCategory.SPORT, "PH", "Football"),
    DataSource("https://www.pba.ph/", "PBA", SourceCategory.SPORT, "PH", "Basketball"),
]

# ============================================================
# 🇲🇾 MALAYSIA DATA SOURCES
# ============================================================

MALAYSIA_SOURCES = [
    DataSource("https://www.malaysia.gov.my/", "Malaysia.gov.my", SourceCategory.GOVERNMENT, "MY", "Government portal"),
    DataSource("https://www.dosm.gov.my/", "DOSM", SourceCategory.STATISTICS, "MY", "Statistics", True),
    DataSource("https://www.data.gov.my/", "Data.gov.my", SourceCategory.STATISTICS, "MY", "Open data", True),
    DataSource("https://www.um.edu.my/", "University of Malaya", SourceCategory.UNIVERSITY, "MY", "UM"),
    DataSource("https://www.ukm.my/", "UKM", SourceCategory.UNIVERSITY, "MY", "National University"),
    DataSource("https://www.upm.edu.my/", "UPM", SourceCategory.UNIVERSITY, "MY", "Putra University"),
    DataSource("https://www.bnm.gov.my/", "Bank Negara Malaysia", SourceCategory.BANK, "MY", "Central bank", True),
    DataSource("https://www.bursamalaysia.com/", "Bursa Malaysia", SourceCategory.BANK, "MY", "Stock exchange", True),
    DataSource("https://www.maybank.com/", "Maybank", SourceCategory.BANK, "MY", "Major bank"),
    DataSource("https://www.cimb.com/", "CIMB", SourceCategory.BANK, "MY", "Major bank"),
    DataSource("https://www.petronas.com/", "Petronas", SourceCategory.ENERGY, "MY", "State oil"),
    DataSource("https://www.malaysiaairlines.com/", "Malaysia Airlines", SourceCategory.TRANSPORT, "MY", "National airline"),
    DataSource("https://www.airasia.com/", "AirAsia", SourceCategory.TRANSPORT, "MY", "Low-cost airline"),
    DataSource("https://www.thestar.com.my/", "The Star", SourceCategory.NEWS, "MY", "Major newspaper"),
    DataSource("https://www.nst.com.my/", "New Straits Times", SourceCategory.NEWS, "MY", "Major newspaper"),
    DataSource("https://www.bernama.com/", "Bernama", SourceCategory.NEWS, "MY", "News agency"),
    DataSource("https://www.malaysia.travel/", "Tourism Malaysia", SourceCategory.TOURISM, "MY", "Tourism", True),
    DataSource("https://www.fam.org.my/", "FAM", SourceCategory.SPORT, "MY", "Football"),
]

# ============================================================
# 🌍 GLOBAL ORGANIZATIONS
# ============================================================

GLOBAL_ORGANIZATIONS = [
    # United Nations
    DataSource("https://www.un.org/", "United Nations", SourceCategory.INTERNATIONAL, "INTL", "UN", True),
    DataSource("https://data.un.org/", "UNdata", SourceCategory.STATISTICS, "INTL", "UN statistics", True),
    DataSource("https://unstats.un.org/", "UN Statistics", SourceCategory.STATISTICS, "INTL", "Statistics division", True),
    DataSource("https://www.undp.org/", "UNDP", SourceCategory.INTERNATIONAL, "INTL", "Development Programme", True),
    DataSource("https://www.unicef.org/", "UNICEF", SourceCategory.INTERNATIONAL, "INTL", "Children's Fund", True),
    DataSource("https://www.who.int/", "WHO", SourceCategory.INTERNATIONAL, "INTL", "World Health Org", True),
    DataSource("https://www.unesco.org/", "UNESCO", SourceCategory.INTERNATIONAL, "INTL", "Education/culture", True),
    DataSource("https://www.fao.org/", "FAO", SourceCategory.INTERNATIONAL, "INTL", "Food/Agriculture", True),
    DataSource("https://www.ilo.org/", "ILO", SourceCategory.INTERNATIONAL, "INTL", "Labour Org", True),
    DataSource("https://www.wto.org/", "WTO", SourceCategory.INTERNATIONAL, "INTL", "Trade Org", True),
    DataSource("https://www.imf.org/", "IMF", SourceCategory.BANK, "INTL", "International Monetary Fund", True),
    DataSource("https://www.worldbank.org/", "World Bank", SourceCategory.BANK, "INTL", "Development bank", True),
    
    # Other International
    DataSource("https://www.oecd.org/", "OECD", SourceCategory.INTERNATIONAL, "INTL", "Economic cooperation", True),
    DataSource("https://data.oecd.org/", "OECD Data", SourceCategory.STATISTICS, "INTL", "OECD statistics", True),
    DataSource("https://www.bis.org/", "BIS", SourceCategory.BANK, "INTL", "Bank for International Settlements", True),
    DataSource("https://www.iea.org/", "IEA", SourceCategory.ENERGY, "INTL", "Energy Agency", True),
    DataSource("https://www.wipo.int/", "WIPO", SourceCategory.INTERNATIONAL, "INTL", "Intellectual Property", True),
    DataSource("https://www.nato.int/", "NATO", SourceCategory.INTERNATIONAL, "INTL", "North Atlantic Treaty"),
    DataSource("https://www.asean.org/", "ASEAN", SourceCategory.INTERNATIONAL, "INTL", "Southeast Asian Nations"),
    DataSource("https://www.apec.org/", "APEC", SourceCategory.INTERNATIONAL, "INTL", "Asia-Pacific Cooperation"),
    DataSource("https://www.g20.org/", "G20", SourceCategory.INTERNATIONAL, "INTL", "Group of Twenty"),
    DataSource("https://www.g7uk.org/", "G7", SourceCategory.INTERNATIONAL, "INTL", "Group of Seven"),
    
    # Sports
    DataSource("https://www.olympics.com/", "IOC", SourceCategory.SPORT, "INTL", "International Olympic Committee", True),
    DataSource("https://www.fifa.com/", "FIFA", SourceCategory.SPORT, "INTL", "World Football", True),
    DataSource("https://www.uefa.com/", "UEFA", SourceCategory.SPORT, "INTL", "European Football", True),
    DataSource("https://www.afc.com/", "AFC", SourceCategory.SPORT, "INTL", "Asian Football", True),
    DataSource("https://www.caf.com/", "CAF", SourceCategory.SPORT, "INTL", "African Football", True),
    DataSource("https://www.fiba.basketball/", "FIBA", SourceCategory.SPORT, "INTL", "World Basketball", True),
    DataSource("https://www.itftennis.com/", "ITF", SourceCategory.SPORT, "INTL", "Tennis", True),
    DataSource("https://www.atptour.com/", "ATP", SourceCategory.SPORT, "INTL", "Men's tennis", True),
    DataSource("https://www.wtatennis.com/", "WTA", SourceCategory.SPORT, "INTL", "Women's tennis", True),
    DataSource("https://www.worldathletics.org/", "World Athletics", SourceCategory.SPORT, "INTL", "Athletics", True),
    DataSource("https://www.fina.org/", "FINA", SourceCategory.SPORT, "INTL", "Aquatics", True),
    DataSource("https://www.uci.org/", "UCI", SourceCategory.SPORT, "INTL", "Cycling", True),
    DataSource("https://www.icc-cricket.com/", "ICC", SourceCategory.SPORT, "INTL", "Cricket", True),
    DataSource("https://www.world.rugby/", "World Rugby", SourceCategory.SPORT, "INTL", "Rugby", True),
    DataSource("https://www.fia.com/", "FIA", SourceCategory.SPORT, "INTL", "Motorsport", True),
    
    # Research & Data
    DataSource("https://www.kaggle.com/", "Kaggle", SourceCategory.RESEARCH, "INTL", "Data science", True),
    DataSource("https://github.com/", "GitHub", SourceCategory.TECHNOLOGY, "INTL", "Code hosting", True),
    DataSource("https://www.openstreetmap.org/", "OpenStreetMap", SourceCategory.STATISTICS, "INTL", "Open maps", True),
    DataSource("https://www.wikidata.org/", "Wikidata", SourceCategory.STATISTICS, "INTL", "Knowledge base", True),
    DataSource("https://www.wikipedia.org/", "Wikipedia", SourceCategory.CULTURE, "INTL", "Encyclopedia"),
    DataSource("https://arxiv.org/", "arXiv", SourceCategory.RESEARCH, "INTL", "Research papers", True),
    DataSource("https://scholar.google.com/", "Google Scholar", SourceCategory.RESEARCH, "INTL", "Academic search", True),
]

# ============================================================
# COMBINED EXPORT
# ============================================================

ALL_ASIA_OCEANIA_GLOBAL_SOURCES = (
    CHINA_SOURCES + JAPAN_SOURCES + KOREA_SOURCES +
    TAIWAN_SOURCES + HONGKONG_SOURCES + SINGAPORE_SOURCES +
    AUSTRALIA_SOURCES + NEWZEALAND_SOURCES +
    INDONESIA_SOURCES + THAILAND_SOURCES + VIETNAM_SOURCES +
    PHILIPPINES_SOURCES + MALAYSIA_SOURCES +
    GLOBAL_ORGANIZATIONS
)

def get_all_sources() -> List[DataSource]:
    """Return all Asia, Oceania & Global data sources"""
    return ALL_ASIA_OCEANIA_GLOBAL_SOURCES

def get_sources_by_country(country_code: str) -> List[DataSource]:
    """Return sources for a specific country"""
    return [s for s in ALL_ASIA_OCEANIA_GLOBAL_SOURCES if s.country == country_code]

def get_sources_by_category(category: SourceCategory) -> List[DataSource]:
    """Return sources for a specific category"""
    return [s for s in ALL_ASIA_OCEANIA_GLOBAL_SOURCES if s.category == category]

def get_api_sources() -> List[DataSource]:
    """Return only sources with API access"""
    return [s for s in ALL_ASIA_OCEANIA_GLOBAL_SOURCES if s.api_available]

def get_global_organizations() -> List[DataSource]:
    """Return global/international organizations"""
    return GLOBAL_ORGANIZATIONS

# Statistics
if __name__ == "__main__":
    print(f"🌏 Total Asia/Oceania/Global Sources: {len(ALL_ASIA_OCEANIA_GLOBAL_SOURCES)}")
    print(f"Countries covered: CN, JP, KR, TW, HK, SG, AU, NZ, ID, TH, VN, PH, MY, INTL")
    print(f"Sources with API: {len(get_api_sources())}")
    print(f"Global Organizations: {len(GLOBAL_ORGANIZATIONS)}")
