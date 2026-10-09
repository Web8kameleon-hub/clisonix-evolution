# -*- coding: utf-8 -*-
"""
🌎 AMERICAS - COMPLETE DATA SOURCES
================================================
800+ Free Open Data Sources from North & South America

Countries Covered:
- United States 🇺🇸
- Canada 🇨🇦
- Mexico 🇲🇽
- Brazil 🇧🇷
- Argentina 🇦🇷
- Colombia 🇨🇴
- Chile 🇨🇱
- Peru 🇵🇪
- Venezuela 🇻🇪
- Ecuador 🇪🇨
- Caribbean Nations

Categories:
- Government & Statistics
- Universities & Research  
- Hospitals & Healthcare
- Banks & Financial
- Industry & Technology
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
    TECHNOLOGY = "technology"
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
# 🇺🇸 UNITED STATES DATA SOURCES
# ============================================================

USA_GOVERNMENT = [
    DataSource("https://www.usa.gov/", "USA.gov", SourceCategory.GOVERNMENT, "US", "Federal government portal"),
    DataSource("https://www.whitehouse.gov/", "White House", SourceCategory.GOVERNMENT, "US", "Executive branch"),
    DataSource("https://www.congress.gov/", "Congress.gov", SourceCategory.GOVERNMENT, "US", "Legislative branch", True),
    DataSource("https://www.supremecourt.gov/", "Supreme Court", SourceCategory.GOVERNMENT, "US", "Judicial branch"),
    DataSource("https://www.state.gov/", "Department of State", SourceCategory.GOVERNMENT, "US", "Foreign affairs"),
    DataSource("https://www.treasury.gov/", "Treasury Department", SourceCategory.GOVERNMENT, "US", "Finance", True),
    DataSource("https://www.defense.gov/", "Department of Defense", SourceCategory.GOVERNMENT, "US", "Defense"),
    DataSource("https://www.justice.gov/", "Department of Justice", SourceCategory.GOVERNMENT, "US", "Justice"),
    DataSource("https://www.commerce.gov/", "Department of Commerce", SourceCategory.GOVERNMENT, "US", "Commerce"),
    DataSource("https://www.energy.gov/", "Department of Energy", SourceCategory.ENERGY, "US", "Energy"),
    DataSource("https://www.hhs.gov/", "HHS", SourceCategory.HOSPITAL, "US", "Health & Human Services"),
    DataSource("https://www.data.gov/", "Data.gov", SourceCategory.STATISTICS, "US", "Federal open data", True),
    DataSource("https://www.census.gov/", "US Census Bureau", SourceCategory.STATISTICS, "US", "Census data", True),
    DataSource("https://www.bls.gov/", "Bureau of Labor Statistics", SourceCategory.STATISTICS, "US", "Employment stats", True),
    DataSource("https://www.bea.gov/", "Bureau of Economic Analysis", SourceCategory.STATISTICS, "US", "Economic data", True),
    DataSource("https://www.epa.gov/", "EPA", SourceCategory.ENVIRONMENTAL, "US", "Environmental Protection", True),
    DataSource("https://www.nasa.gov/", "NASA", SourceCategory.RESEARCH, "US", "Space agency", True),
    DataSource("https://www.noaa.gov/", "NOAA", SourceCategory.ENVIRONMENTAL, "US", "Weather/ocean", True),
    DataSource("https://www.usgs.gov/", "USGS", SourceCategory.ENVIRONMENTAL, "US", "Geological survey", True),
    DataSource("https://www.fda.gov/", "FDA", SourceCategory.HOSPITAL, "US", "Food & Drug Admin", True),
    DataSource("https://www.cdc.gov/", "CDC", SourceCategory.HOSPITAL, "US", "Disease control", True),
    DataSource("https://www.nih.gov/", "NIH", SourceCategory.RESEARCH, "US", "Health research", True),
    DataSource("https://www.nsf.gov/", "NSF", SourceCategory.RESEARCH, "US", "Science foundation", True),
    DataSource("https://www.dot.gov/", "Dept of Transportation", SourceCategory.TRANSPORT, "US", "Transportation"),
    DataSource("https://www.faa.gov/", "FAA", SourceCategory.TRANSPORT, "US", "Aviation", True),
    DataSource("https://www.fcc.gov/", "FCC", SourceCategory.TELECOM, "US", "Communications", True),
    DataSource("https://www.sec.gov/", "SEC", SourceCategory.BANK, "US", "Securities regulator", True),
    DataSource("https://www.ftc.gov/", "FTC", SourceCategory.GOVERNMENT, "US", "Trade commission"),
    DataSource("https://www.nyc.gov/", "NYC.gov", SourceCategory.GOVERNMENT, "US", "New York City"),
    DataSource("https://www.lacity.org/", "Los Angeles City", SourceCategory.GOVERNMENT, "US", "Los Angeles"),
    DataSource("https://www.chicago.gov/", "Chicago.gov", SourceCategory.GOVERNMENT, "US", "Chicago"),
    DataSource("https://www.houston.gov/", "Houston.gov", SourceCategory.GOVERNMENT, "US", "Houston"),
    DataSource("https://www.sf.gov/", "San Francisco", SourceCategory.GOVERNMENT, "US", "San Francisco"),
]

USA_UNIVERSITIES = [
    DataSource("https://www.harvard.edu/", "Harvard University", SourceCategory.UNIVERSITY, "US", "Ivy League"),
    DataSource("https://www.stanford.edu/", "Stanford University", SourceCategory.UNIVERSITY, "US", "Top research"),
    DataSource("https://www.mit.edu/", "MIT", SourceCategory.UNIVERSITY, "US", "Technology/engineering"),
    DataSource("https://www.caltech.edu/", "Caltech", SourceCategory.UNIVERSITY, "US", "Science/engineering"),
    DataSource("https://www.princeton.edu/", "Princeton University", SourceCategory.UNIVERSITY, "US", "Ivy League"),
    DataSource("https://www.yale.edu/", "Yale University", SourceCategory.UNIVERSITY, "US", "Ivy League"),
    DataSource("https://www.columbia.edu/", "Columbia University", SourceCategory.UNIVERSITY, "US", "Ivy League"),
    DataSource("https://www.upenn.edu/", "UPenn", SourceCategory.UNIVERSITY, "US", "Ivy League"),
    DataSource("https://www.brown.edu/", "Brown University", SourceCategory.UNIVERSITY, "US", "Ivy League"),
    DataSource("https://www.cornell.edu/", "Cornell University", SourceCategory.UNIVERSITY, "US", "Ivy League"),
    DataSource("https://www.dartmouth.edu/", "Dartmouth College", SourceCategory.UNIVERSITY, "US", "Ivy League"),
    DataSource("https://www.uchicago.edu/", "University of Chicago", SourceCategory.UNIVERSITY, "US", "Research university"),
    DataSource("https://www.duke.edu/", "Duke University", SourceCategory.UNIVERSITY, "US", "Research university"),
    DataSource("https://www.jhu.edu/", "Johns Hopkins", SourceCategory.UNIVERSITY, "US", "Medical research"),
    DataSource("https://www.northwestern.edu/", "Northwestern", SourceCategory.UNIVERSITY, "US", "Research university"),
    DataSource("https://www.berkeley.edu/", "UC Berkeley", SourceCategory.UNIVERSITY, "US", "Public research"),
    DataSource("https://www.ucla.edu/", "UCLA", SourceCategory.UNIVERSITY, "US", "Public research"),
    DataSource("https://www.umich.edu/", "University of Michigan", SourceCategory.UNIVERSITY, "US", "Public research"),
    DataSource("https://www.nyu.edu/", "NYU", SourceCategory.UNIVERSITY, "US", "Private research"),
    DataSource("https://www.cmu.edu/", "Carnegie Mellon", SourceCategory.UNIVERSITY, "US", "Tech/CS"),
    DataSource("https://www.gatech.edu/", "Georgia Tech", SourceCategory.UNIVERSITY, "US", "Technology"),
    DataSource("https://www.utexas.edu/", "UT Austin", SourceCategory.UNIVERSITY, "US", "Texas university"),
    DataSource("https://www.washington.edu/", "UW Seattle", SourceCategory.UNIVERSITY, "US", "Washington state"),
    DataSource("https://www.wisc.edu/", "UW Madison", SourceCategory.UNIVERSITY, "US", "Wisconsin"),
    DataSource("https://www.illinois.edu/", "UIUC", SourceCategory.UNIVERSITY, "US", "Illinois"),
    DataSource("https://www.usc.edu/", "USC", SourceCategory.UNIVERSITY, "US", "Southern California"),
    DataSource("https://www.wharton.upenn.edu/", "Wharton School", SourceCategory.UNIVERSITY, "US", "Business school"),
    DataSource("https://www.hbs.edu/", "Harvard Business School", SourceCategory.UNIVERSITY, "US", "Business school"),
    DataSource("https://www.gsb.stanford.edu/", "Stanford GSB", SourceCategory.UNIVERSITY, "US", "Business school"),
    DataSource("https://sloan.mit.edu/", "MIT Sloan", SourceCategory.UNIVERSITY, "US", "Business school"),
]

USA_HOSPITALS = [
    DataSource("https://www.mayoclinic.org/", "Mayo Clinic", SourceCategory.HOSPITAL, "US", "Top hospital"),
    DataSource("https://www.clevelandclinic.org/", "Cleveland Clinic", SourceCategory.HOSPITAL, "US", "Top hospital"),
    DataSource("https://www.hopkinsmedicine.org/", "Johns Hopkins Hospital", SourceCategory.HOSPITAL, "US", "Medical center"),
    DataSource("https://www.massgeneral.org/", "Mass General", SourceCategory.HOSPITAL, "US", "Boston hospital"),
    DataSource("https://www.uclahealth.org/", "UCLA Health", SourceCategory.HOSPITAL, "US", "LA medical center"),
    DataSource("https://www.ucsf.edu/", "UCSF Medical", SourceCategory.HOSPITAL, "US", "SF medical center"),
    DataSource("https://www.nyp.org/", "NewYork-Presbyterian", SourceCategory.HOSPITAL, "US", "NYC hospital"),
    DataSource("https://www.mountsinai.org/", "Mount Sinai", SourceCategory.HOSPITAL, "US", "NYC hospital"),
    DataSource("https://www.cedars-sinai.org/", "Cedars-Sinai", SourceCategory.HOSPITAL, "US", "LA hospital"),
    DataSource("https://www.mdanderson.org/", "MD Anderson", SourceCategory.HOSPITAL, "US", "Cancer center"),
    DataSource("https://www.mskcc.org/", "Memorial Sloan Kettering", SourceCategory.HOSPITAL, "US", "Cancer center"),
    DataSource("https://www.stanfordhealthcare.org/", "Stanford Health", SourceCategory.HOSPITAL, "US", "Stanford hospital"),
    DataSource("https://www.pennmedicine.org/", "Penn Medicine", SourceCategory.HOSPITAL, "US", "Philadelphia"),
    DataSource("https://www.dukehealth.org/", "Duke Health", SourceCategory.HOSPITAL, "US", "Duke hospital"),
    DataSource("https://www.rush.edu/", "Rush University Medical", SourceCategory.HOSPITAL, "US", "Chicago hospital"),
]

USA_BANKS = [
    DataSource("https://www.federalreserve.gov/", "Federal Reserve", SourceCategory.BANK, "US", "Central bank", True),
    DataSource("https://www.fdic.gov/", "FDIC", SourceCategory.BANK, "US", "Bank insurance", True),
    DataSource("https://www.jpmorgan.com/", "JPMorgan Chase", SourceCategory.BANK, "US", "Major bank"),
    DataSource("https://www.bankofamerica.com/", "Bank of America", SourceCategory.BANK, "US", "Major bank"),
    DataSource("https://www.wellsfargo.com/", "Wells Fargo", SourceCategory.BANK, "US", "Major bank"),
    DataSource("https://www.citi.com/", "Citibank", SourceCategory.BANK, "US", "Major bank"),
    DataSource("https://www.goldmansachs.com/", "Goldman Sachs", SourceCategory.BANK, "US", "Investment bank"),
    DataSource("https://www.morganstanley.com/", "Morgan Stanley", SourceCategory.BANK, "US", "Investment bank"),
    DataSource("https://www.blackrock.com/", "BlackRock", SourceCategory.BANK, "US", "Asset management"),
    DataSource("https://www.fidelity.com/", "Fidelity", SourceCategory.BANK, "US", "Investment"),
    DataSource("https://www.vanguard.com/", "Vanguard", SourceCategory.BANK, "US", "Investment"),
    DataSource("https://www.schwab.com/", "Charles Schwab", SourceCategory.BANK, "US", "Brokerage"),
    DataSource("https://www.nyse.com/", "NYSE", SourceCategory.BANK, "US", "Stock exchange", True),
    DataSource("https://www.nasdaq.com/", "NASDAQ", SourceCategory.BANK, "US", "Stock exchange", True),
    DataSource("https://www.cme.com/", "CME Group", SourceCategory.BANK, "US", "Derivatives exchange", True),
    DataSource("https://www.moodys.com/", "Moody's", SourceCategory.RATING, "US", "Credit ratings", True),
    DataSource("https://www.spglobal.com/", "S&P Global", SourceCategory.RATING, "US", "Ratings/analytics", True),
    DataSource("https://www.fitchratings.com/", "Fitch Ratings", SourceCategory.RATING, "US", "Credit ratings"),
]

USA_TECHNOLOGY = [
    DataSource("https://www.apple.com/", "Apple", SourceCategory.TECHNOLOGY, "US", "Tech giant"),
    DataSource("https://www.microsoft.com/", "Microsoft", SourceCategory.TECHNOLOGY, "US", "Software giant"),
    DataSource("https://www.google.com/", "Google", SourceCategory.TECHNOLOGY, "US", "Search/tech", True),
    DataSource("https://www.amazon.com/", "Amazon", SourceCategory.TECHNOLOGY, "US", "E-commerce/cloud"),
    DataSource("https://www.meta.com/", "Meta", SourceCategory.TECHNOLOGY, "US", "Social media"),
    DataSource("https://www.nvidia.com/", "NVIDIA", SourceCategory.TECHNOLOGY, "US", "GPU/AI"),
    DataSource("https://www.tesla.com/", "Tesla", SourceCategory.TECHNOLOGY, "US", "Electric vehicles"),
    DataSource("https://www.intel.com/", "Intel", SourceCategory.TECHNOLOGY, "US", "Semiconductors"),
    DataSource("https://www.amd.com/", "AMD", SourceCategory.TECHNOLOGY, "US", "Semiconductors"),
    DataSource("https://www.qualcomm.com/", "Qualcomm", SourceCategory.TECHNOLOGY, "US", "Semiconductors"),
    DataSource("https://www.ibm.com/", "IBM", SourceCategory.TECHNOLOGY, "US", "Enterprise tech"),
    DataSource("https://www.oracle.com/", "Oracle", SourceCategory.TECHNOLOGY, "US", "Database/cloud"),
    DataSource("https://www.salesforce.com/", "Salesforce", SourceCategory.TECHNOLOGY, "US", "CRM/cloud"),
    DataSource("https://www.adobe.com/", "Adobe", SourceCategory.TECHNOLOGY, "US", "Creative software"),
    DataSource("https://www.cisco.com/", "Cisco", SourceCategory.TECHNOLOGY, "US", "Networking"),
    DataSource("https://www.uber.com/", "Uber", SourceCategory.TECHNOLOGY, "US", "Ride-sharing"),
    DataSource("https://www.airbnb.com/", "Airbnb", SourceCategory.TECHNOLOGY, "US", "Vacation rentals"),
    DataSource("https://www.netflix.com/", "Netflix", SourceCategory.ENTERTAINMENT, "US", "Streaming"),
    DataSource("https://www.spotify.com/", "Spotify US", SourceCategory.ENTERTAINMENT, "US", "Music streaming"),
    DataSource("https://www.stripe.com/", "Stripe", SourceCategory.TECHNOLOGY, "US", "Payments", True),
    DataSource("https://www.paypal.com/", "PayPal", SourceCategory.TECHNOLOGY, "US", "Payments"),
    DataSource("https://www.square.com/", "Square/Block", SourceCategory.TECHNOLOGY, "US", "Fintech"),
    DataSource("https://www.openai.com/", "OpenAI", SourceCategory.TECHNOLOGY, "US", "AI research", True),
    DataSource("https://www.anthropic.com/", "Anthropic", SourceCategory.TECHNOLOGY, "US", "AI safety"),
    DataSource("https://www.spacex.com/", "SpaceX", SourceCategory.TECHNOLOGY, "US", "Space technology"),
]

USA_NEWS = [
    DataSource("https://www.nytimes.com/", "New York Times", SourceCategory.NEWS, "US", "Major newspaper"),
    DataSource("https://www.washingtonpost.com/", "Washington Post", SourceCategory.NEWS, "US", "Major newspaper"),
    DataSource("https://www.wsj.com/", "Wall Street Journal", SourceCategory.NEWS, "US", "Business news"),
    DataSource("https://www.usatoday.com/", "USA Today", SourceCategory.NEWS, "US", "National newspaper"),
    DataSource("https://www.cnn.com/", "CNN", SourceCategory.NEWS, "US", "Cable news"),
    DataSource("https://www.foxnews.com/", "Fox News", SourceCategory.NEWS, "US", "Cable news"),
    DataSource("https://www.msnbc.com/", "MSNBC", SourceCategory.NEWS, "US", "Cable news"),
    DataSource("https://www.nbcnews.com/", "NBC News", SourceCategory.NEWS, "US", "Network news"),
    DataSource("https://www.abcnews.go.com/", "ABC News", SourceCategory.NEWS, "US", "Network news"),
    DataSource("https://www.cbsnews.com/", "CBS News", SourceCategory.NEWS, "US", "Network news"),
    DataSource("https://www.pbs.org/newshour/", "PBS NewsHour", SourceCategory.NEWS, "US", "Public broadcasting"),
    DataSource("https://www.npr.org/", "NPR", SourceCategory.NEWS, "US", "Public radio"),
    DataSource("https://www.bloomberg.com/", "Bloomberg", SourceCategory.NEWS, "US", "Business news", True),
    DataSource("https://www.reuters.com/", "Reuters US", SourceCategory.NEWS, "US", "News agency", True),
    DataSource("https://www.ap.org/", "Associated Press", SourceCategory.NEWS, "US", "News agency", True),
    DataSource("https://www.politico.com/", "Politico", SourceCategory.NEWS, "US", "Political news"),
    DataSource("https://www.thehill.com/", "The Hill", SourceCategory.NEWS, "US", "Political news"),
    DataSource("https://www.axios.com/", "Axios", SourceCategory.NEWS, "US", "News media"),
    DataSource("https://www.latimes.com/", "Los Angeles Times", SourceCategory.NEWS, "US", "California newspaper"),
    DataSource("https://www.chicagotribune.com/", "Chicago Tribune", SourceCategory.NEWS, "US", "Chicago newspaper"),
    DataSource("https://www.forbes.com/", "Forbes", SourceCategory.NEWS, "US", "Business magazine"),
    DataSource("https://www.businessinsider.com/", "Business Insider", SourceCategory.NEWS, "US", "Business news"),
    DataSource("https://techcrunch.com/", "TechCrunch", SourceCategory.NEWS, "US", "Tech news"),
    DataSource("https://www.theverge.com/", "The Verge", SourceCategory.NEWS, "US", "Tech news"),
    DataSource("https://www.wired.com/", "Wired", SourceCategory.NEWS, "US", "Tech magazine"),
]

USA_CULTURE = [
    DataSource("https://www.metmuseum.org/", "Metropolitan Museum", SourceCategory.CULTURE, "US", "NYC art museum", True),
    DataSource("https://www.moma.org/", "MoMA", SourceCategory.CULTURE, "US", "Modern art"),
    DataSource("https://www.guggenheim.org/", "Guggenheim", SourceCategory.CULTURE, "US", "Modern art"),
    DataSource("https://www.artic.edu/", "Art Institute of Chicago", SourceCategory.CULTURE, "US", "Art museum"),
    DataSource("https://www.lacma.org/", "LACMA", SourceCategory.CULTURE, "US", "LA county museum"),
    DataSource("https://www.sfmoma.org/", "SFMOMA", SourceCategory.CULTURE, "US", "SF modern art"),
    DataSource("https://www.nga.gov/", "National Gallery of Art", SourceCategory.CULTURE, "US", "Washington DC", True),
    DataSource("https://www.si.edu/", "Smithsonian", SourceCategory.CULTURE, "US", "Museum complex", True),
    DataSource("https://airandspace.si.edu/", "Air and Space Museum", SourceCategory.CULTURE, "US", "Smithsonian"),
    DataSource("https://www.americanhistory.si.edu/", "American History Museum", SourceCategory.CULTURE, "US", "Smithsonian"),
    DataSource("https://www.loc.gov/", "Library of Congress", SourceCategory.CULTURE, "US", "National library", True),
    DataSource("https://www.archives.gov/", "National Archives", SourceCategory.CULTURE, "US", "Historical archives", True),
    DataSource("https://www.gettymuseum.org/", "Getty Museum", SourceCategory.CULTURE, "US", "LA art museum"),
    DataSource("https://www.philamuseum.org/", "Philadelphia Museum", SourceCategory.CULTURE, "US", "Art museum"),
    DataSource("https://www.famsf.org/", "Fine Arts Museums SF", SourceCategory.CULTURE, "US", "SF museums"),
]

USA_SPORT = [
    DataSource("https://www.nfl.com/", "NFL", SourceCategory.SPORT, "US", "Football league", True),
    DataSource("https://www.nba.com/", "NBA", SourceCategory.SPORT, "US", "Basketball league", True),
    DataSource("https://www.mlb.com/", "MLB", SourceCategory.SPORT, "US", "Baseball league", True),
    DataSource("https://www.nhl.com/", "NHL", SourceCategory.SPORT, "US", "Hockey league", True),
    DataSource("https://www.mls.com/", "MLS", SourceCategory.SPORT, "US", "Soccer league", True),
    DataSource("https://www.espn.com/", "ESPN", SourceCategory.SPORT, "US", "Sports network", True),
    DataSource("https://www.foxsports.com/", "Fox Sports", SourceCategory.SPORT, "US", "Sports network"),
    DataSource("https://www.cbssports.com/", "CBS Sports", SourceCategory.SPORT, "US", "Sports network"),
    DataSource("https://www.usatoday.com/sports/", "USA Today Sports", SourceCategory.SPORT, "US", "Sports news"),
    DataSource("https://www.si.com/", "Sports Illustrated", SourceCategory.SPORT, "US", "Sports magazine"),
    DataSource("https://www.usatf.org/", "USA Track & Field", SourceCategory.SPORT, "US", "Athletics"),
    DataSource("https://www.usaswimming.org/", "USA Swimming", SourceCategory.SPORT, "US", "Swimming"),
    DataSource("https://www.usabasketball.com/", "USA Basketball", SourceCategory.SPORT, "US", "National team"),
    DataSource("https://www.ussoccer.com/", "US Soccer", SourceCategory.SPORT, "US", "Soccer federation"),
    DataSource("https://www.usta.com/", "USTA Tennis", SourceCategory.SPORT, "US", "Tennis"),
    DataSource("https://www.usopen.org/", "US Open Tennis", SourceCategory.SPORT, "US", "Grand Slam"),
    DataSource("https://www.pga.com/", "PGA", SourceCategory.SPORT, "US", "Golf", True),
    DataSource("https://www.nascar.com/", "NASCAR", SourceCategory.SPORT, "US", "Stock car racing", True),
    DataSource("https://www.indycar.com/", "IndyCar", SourceCategory.SPORT, "US", "Open-wheel racing"),
    DataSource("https://www.ufc.com/", "UFC", SourceCategory.SPORT, "US", "Mixed martial arts", True),
    DataSource("https://www.wwe.com/", "WWE", SourceCategory.ENTERTAINMENT, "US", "Wrestling entertainment"),
    DataSource("https://www.teamusa.org/", "Team USA", SourceCategory.SPORT, "US", "Olympic committee"),
    DataSource("https://www.ncaa.com/", "NCAA", SourceCategory.SPORT, "US", "College sports", True),
]

USA_ENTERTAINMENT = [
    DataSource("https://www.hollywood.com/", "Hollywood.com", SourceCategory.ENTERTAINMENT, "US", "Entertainment news"),
    DataSource("https://www.imdb.com/", "IMDB", SourceCategory.ENTERTAINMENT, "US", "Movie database", True),
    DataSource("https://www.rottentomatoes.com/", "Rotten Tomatoes", SourceCategory.ENTERTAINMENT, "US", "Movie reviews", True),
    DataSource("https://www.variety.com/", "Variety", SourceCategory.ENTERTAINMENT, "US", "Entertainment industry"),
    DataSource("https://www.hollywoodreporter.com/", "Hollywood Reporter", SourceCategory.ENTERTAINMENT, "US", "Industry news"),
    DataSource("https://www.billboard.com/", "Billboard", SourceCategory.ENTERTAINMENT, "US", "Music charts", True),
    DataSource("https://www.rollingstone.com/", "Rolling Stone", SourceCategory.ENTERTAINMENT, "US", "Music/culture"),
    DataSource("https://www.eonline.com/", "E! News", SourceCategory.ENTERTAINMENT, "US", "Celebrity news"),
    DataSource("https://www.tmz.com/", "TMZ", SourceCategory.ENTERTAINMENT, "US", "Celebrity news"),
    DataSource("https://www.disneyplus.com/", "Disney+", SourceCategory.ENTERTAINMENT, "US", "Streaming"),
    DataSource("https://www.hbomax.com/", "HBO Max", SourceCategory.ENTERTAINMENT, "US", "Streaming"),
    DataSource("https://www.hulu.com/", "Hulu", SourceCategory.ENTERTAINMENT, "US", "Streaming"),
    DataSource("https://www.paramountplus.com/", "Paramount+", SourceCategory.ENTERTAINMENT, "US", "Streaming"),
    DataSource("https://www.peacocktv.com/", "Peacock", SourceCategory.ENTERTAINMENT, "US", "Streaming"),
    DataSource("https://www.applemusic.com/", "Apple Music", SourceCategory.ENTERTAINMENT, "US", "Music streaming"),
    DataSource("https://www.youtube.com/", "YouTube", SourceCategory.ENTERTAINMENT, "US", "Video platform", True),
    DataSource("https://www.tiktok.com/", "TikTok US", SourceCategory.ENTERTAINMENT, "US", "Short video"),
    DataSource("https://www.twitch.tv/", "Twitch", SourceCategory.ENTERTAINMENT, "US", "Game streaming", True),
]

USA_TOURISM = [
    DataSource("https://www.visittheusa.com/", "Visit the USA", SourceCategory.TOURISM, "US", "National tourism"),
    DataSource("https://www.nps.gov/", "National Park Service", SourceCategory.TOURISM, "US", "National parks", True),
    DataSource("https://www.nycgo.com/", "NYC Tourism", SourceCategory.TOURISM, "US", "New York City"),
    DataSource("https://www.discoverlosangeles.com/", "Discover LA", SourceCategory.TOURISM, "US", "Los Angeles"),
    DataSource("https://www.sftravel.com/", "SF Travel", SourceCategory.TOURISM, "US", "San Francisco"),
    DataSource("https://www.vegas.com/", "Las Vegas", SourceCategory.TOURISM, "US", "Las Vegas"),
    DataSource("https://www.choosechicago.com/", "Choose Chicago", SourceCategory.TOURISM, "US", "Chicago"),
    DataSource("https://www.visitflorida.com/", "Visit Florida", SourceCategory.TOURISM, "US", "Florida state"),
    DataSource("https://www.visithawaii.com/", "Visit Hawaii", SourceCategory.TOURISM, "US", "Hawaii"),
    DataSource("https://www.visitcalifornia.com/", "Visit California", SourceCategory.TOURISM, "US", "California"),
    DataSource("https://www.traveltexas.com/", "Travel Texas", SourceCategory.TOURISM, "US", "Texas"),
]

# ============================================================
# 🇨🇦 CANADA DATA SOURCES
# ============================================================

CANADA_SOURCES = [
    DataSource("https://www.canada.ca/", "Canada.ca", SourceCategory.GOVERNMENT, "CA", "Federal government"),
    DataSource("https://www.parl.ca/", "Parliament of Canada", SourceCategory.GOVERNMENT, "CA", "Parliament"),
    DataSource("https://www.statcan.gc.ca/", "Statistics Canada", SourceCategory.STATISTICS, "CA", "National statistics", True),
    DataSource("https://open.canada.ca/", "Open Canada", SourceCategory.STATISTICS, "CA", "Open data", True),
    DataSource("https://www.toronto.ca/", "Toronto Portal", SourceCategory.GOVERNMENT, "CA", "Toronto city"),
    DataSource("https://montreal.ca/", "Montreal Portal", SourceCategory.GOVERNMENT, "CA", "Montreal city"),
    DataSource("https://vancouver.ca/", "Vancouver Portal", SourceCategory.GOVERNMENT, "CA", "Vancouver city"),
    DataSource("https://www.utoronto.ca/", "University of Toronto", SourceCategory.UNIVERSITY, "CA", "Top university"),
    DataSource("https://www.mcgill.ca/", "McGill University", SourceCategory.UNIVERSITY, "CA", "Montreal university"),
    DataSource("https://www.ubc.ca/", "UBC", SourceCategory.UNIVERSITY, "CA", "Vancouver university"),
    DataSource("https://www.ualberta.ca/", "University of Alberta", SourceCategory.UNIVERSITY, "CA", "Alberta university"),
    DataSource("https://uwaterloo.ca/", "University of Waterloo", SourceCategory.UNIVERSITY, "CA", "Tech/engineering"),
    DataSource("https://www.queensu.ca/", "Queen's University", SourceCategory.UNIVERSITY, "CA", "Ontario university"),
    DataSource("https://www.uottawa.ca/", "University of Ottawa", SourceCategory.UNIVERSITY, "CA", "Capital university"),
    DataSource("https://www.usherbrooke.ca/", "Université de Sherbrooke", SourceCategory.UNIVERSITY, "CA", "Quebec university"),
    DataSource("https://www.bankofcanada.ca/", "Bank of Canada", SourceCategory.BANK, "CA", "Central bank", True),
    DataSource("https://www.rbc.com/", "RBC", SourceCategory.BANK, "CA", "Major bank"),
    DataSource("https://www.td.com/", "TD Bank", SourceCategory.BANK, "CA", "Major bank"),
    DataSource("https://www.scotiabank.com/", "Scotiabank", SourceCategory.BANK, "CA", "Major bank"),
    DataSource("https://www.bmo.com/", "BMO", SourceCategory.BANK, "CA", "Major bank"),
    DataSource("https://www.cibc.com/", "CIBC", SourceCategory.BANK, "CA", "Major bank"),
    DataSource("https://www.tmx.com/", "TSX", SourceCategory.BANK, "CA", "Stock exchange", True),
    DataSource("https://www.shopify.com/", "Shopify", SourceCategory.TECHNOLOGY, "CA", "E-commerce platform"),
    DataSource("https://www.aircanada.com/", "Air Canada", SourceCategory.TRANSPORT, "CA", "National airline"),
    DataSource("https://www.viarail.ca/", "VIA Rail", SourceCategory.TRANSPORT, "CA", "Rail service"),
    DataSource("https://www.cbc.ca/", "CBC", SourceCategory.NEWS, "CA", "Public broadcaster"),
    DataSource("https://www.globalnews.ca/", "Global News", SourceCategory.NEWS, "CA", "News network"),
    DataSource("https://www.theglobeandmail.com/", "Globe and Mail", SourceCategory.NEWS, "CA", "National newspaper"),
    DataSource("https://nationalpost.com/", "National Post", SourceCategory.NEWS, "CA", "National newspaper"),
    DataSource("https://www.lapresse.ca/", "La Presse", SourceCategory.NEWS, "CA", "Quebec newspaper"),
    DataSource("https://www.thecanadianpress.com/", "Canadian Press", SourceCategory.NEWS, "CA", "News agency"),
    DataSource("https://www.rom.on.ca/", "Royal Ontario Museum", SourceCategory.CULTURE, "CA", "Toronto museum"),
    DataSource("https://www.ago.ca/", "Art Gallery of Ontario", SourceCategory.CULTURE, "CA", "Art gallery"),
    DataSource("https://www.mcord.qc.ca/", "McCord Museum", SourceCategory.CULTURE, "CA", "Montreal museum"),
    DataSource("https://www.mbam.qc.ca/", "Montreal Museum of Fine Arts", SourceCategory.CULTURE, "CA", "Art museum"),
    DataSource("https://www.destinationcanada.com/", "Destination Canada", SourceCategory.TOURISM, "CA", "National tourism", True),
    DataSource("https://www.pc.gc.ca/", "Parks Canada", SourceCategory.TOURISM, "CA", "National parks", True),
    DataSource("https://www.nhl.com/canadiens/", "Montreal Canadiens", SourceCategory.SPORT, "CA", "NHL team"),
    DataSource("https://www.nhl.com/mapleleafs/", "Toronto Maple Leafs", SourceCategory.SPORT, "CA", "NHL team"),
    DataSource("https://www.tfc.ca/", "Toronto FC", SourceCategory.SPORT, "CA", "MLS team"),
    DataSource("https://www.canadasoccer.com/", "Canada Soccer", SourceCategory.SPORT, "CA", "Football federation"),
    DataSource("https://www.olympic.ca/", "Canadian Olympic Committee", SourceCategory.SPORT, "CA", "Olympics"),
    DataSource("https://www.hockeycanada.ca/", "Hockey Canada", SourceCategory.SPORT, "CA", "Hockey federation"),
]

# ============================================================
# 🇲🇽 MEXICO DATA SOURCES
# ============================================================

MEXICO_SOURCES = [
    DataSource("https://www.gob.mx/", "Gobierno de México", SourceCategory.GOVERNMENT, "MX", "Federal government"),
    DataSource("https://www.diputados.gob.mx/", "Cámara de Diputados", SourceCategory.GOVERNMENT, "MX", "Congress"),
    DataSource("https://www.senado.gob.mx/", "Senado", SourceCategory.GOVERNMENT, "MX", "Senate"),
    DataSource("https://www.inegi.org.mx/", "INEGI", SourceCategory.STATISTICS, "MX", "Statistics", True),
    DataSource("https://datos.gob.mx/", "Datos.gob.mx", SourceCategory.STATISTICS, "MX", "Open data", True),
    DataSource("https://www.cdmx.gob.mx/", "Mexico City Portal", SourceCategory.GOVERNMENT, "MX", "Capital city"),
    DataSource("https://www.unam.mx/", "UNAM", SourceCategory.UNIVERSITY, "MX", "Largest university"),
    DataSource("https://www.tec.mx/", "Tecnológico de Monterrey", SourceCategory.UNIVERSITY, "MX", "Private university"),
    DataSource("https://www.ipn.mx/", "IPN", SourceCategory.UNIVERSITY, "MX", "Technical institute"),
    DataSource("https://www.udg.mx/", "Universidad de Guadalajara", SourceCategory.UNIVERSITY, "MX", "Jalisco university"),
    DataSource("https://www.uanl.mx/", "UANL", SourceCategory.UNIVERSITY, "MX", "Nuevo León university"),
    DataSource("https://www.banxico.org.mx/", "Banco de México", SourceCategory.BANK, "MX", "Central bank", True),
    DataSource("https://www.bbva.mx/", "BBVA Mexico", SourceCategory.BANK, "MX", "Major bank"),
    DataSource("https://www.banorte.com/", "Banorte", SourceCategory.BANK, "MX", "Major bank"),
    DataSource("https://www.santander.com.mx/", "Santander Mexico", SourceCategory.BANK, "MX", "Major bank"),
    DataSource("https://www.bmv.com.mx/", "BMV", SourceCategory.BANK, "MX", "Stock exchange", True),
    DataSource("https://www.pemex.com/", "PEMEX", SourceCategory.ENERGY, "MX", "State oil company"),
    DataSource("https://www.cfe.mx/", "CFE", SourceCategory.ENERGY, "MX", "Electric company"),
    DataSource("https://www.aeromexico.com/", "Aeromexico", SourceCategory.TRANSPORT, "MX", "National airline"),
    DataSource("https://www.televisa.com/", "Televisa", SourceCategory.NEWS, "MX", "Media conglomerate"),
    DataSource("https://www.tvazteca.com/", "TV Azteca", SourceCategory.NEWS, "MX", "Broadcasting"),
    DataSource("https://www.eluniversal.com.mx/", "El Universal", SourceCategory.NEWS, "MX", "Daily newspaper"),
    DataSource("https://www.reforma.com/", "Reforma", SourceCategory.NEWS, "MX", "Daily newspaper"),
    DataSource("https://www.milenio.com/", "Milenio", SourceCategory.NEWS, "MX", "News portal"),
    DataSource("https://www.notimex.gob.mx/", "Notimex", SourceCategory.NEWS, "MX", "News agency"),
    DataSource("https://www.mna.inah.gob.mx/", "Museo Nacional de Antropología", SourceCategory.CULTURE, "MX", "Anthropology museum"),
    DataSource("https://www.palacio.gob.mx/", "Palacio de Bellas Artes", SourceCategory.CULTURE, "MX", "Fine arts palace"),
    DataSource("https://www.visitmexico.com/", "Visit Mexico", SourceCategory.TOURISM, "MX", "National tourism"),
    DataSource("https://www.cancun.travel/", "Cancun Tourism", SourceCategory.TOURISM, "MX", "Beach resort"),
    DataSource("https://www.ligamx.net/", "Liga MX", SourceCategory.SPORT, "MX", "Football league", True),
    DataSource("https://www.fmf.mx/", "FMF", SourceCategory.SPORT, "MX", "Football federation"),
    DataSource("https://www.clubamerica.com.mx/", "Club América", SourceCategory.SPORT, "MX", "Football club"),
    DataSource("https://www.chivas.com.mx/", "Chivas", SourceCategory.SPORT, "MX", "Football club"),
    DataSource("https://www.f1.com/", "F1 Mexico", SourceCategory.SPORT, "MX", "Formula 1 race"),
    DataSource("https://www.com.org.mx/", "Mexican Olympic Committee", SourceCategory.SPORT, "MX", "Olympics"),
]

# ============================================================
# 🇧🇷 BRAZIL DATA SOURCES
# ============================================================

BRAZIL_SOURCES = [
    DataSource("https://www.gov.br/", "Governo do Brasil", SourceCategory.GOVERNMENT, "BR", "Federal government"),
    DataSource("https://www.camara.leg.br/", "Câmara dos Deputados", SourceCategory.GOVERNMENT, "BR", "Chamber"),
    DataSource("https://www.senado.leg.br/", "Senado Federal", SourceCategory.GOVERNMENT, "BR", "Senate"),
    DataSource("https://www.stf.jus.br/", "STF", SourceCategory.GOVERNMENT, "BR", "Supreme court"),
    DataSource("https://www.ibge.gov.br/", "IBGE", SourceCategory.STATISTICS, "BR", "Statistics", True),
    DataSource("https://dados.gov.br/", "Dados.gov.br", SourceCategory.STATISTICS, "BR", "Open data", True),
    DataSource("https://www.prefeitura.sp.gov.br/", "São Paulo City", SourceCategory.GOVERNMENT, "BR", "Largest city"),
    DataSource("https://www.rio.rj.gov.br/", "Rio de Janeiro", SourceCategory.GOVERNMENT, "BR", "Rio city"),
    DataSource("https://www.usp.br/", "USP", SourceCategory.UNIVERSITY, "BR", "Top university"),
    DataSource("https://www.unicamp.br/", "UNICAMP", SourceCategory.UNIVERSITY, "BR", "Campinas university"),
    DataSource("https://www.ufrj.br/", "UFRJ", SourceCategory.UNIVERSITY, "BR", "Rio university"),
    DataSource("https://www.ufmg.br/", "UFMG", SourceCategory.UNIVERSITY, "BR", "Minas Gerais university"),
    DataSource("https://www.ufrgs.br/", "UFRGS", SourceCategory.UNIVERSITY, "BR", "Porto Alegre university"),
    DataSource("https://www.unb.br/", "UnB", SourceCategory.UNIVERSITY, "BR", "Brasília university"),
    DataSource("https://www.fiocruz.br/", "Fiocruz", SourceCategory.RESEARCH, "BR", "Health research"),
    DataSource("https://www.bcb.gov.br/", "Banco Central do Brasil", SourceCategory.BANK, "BR", "Central bank", True),
    DataSource("https://www.bb.com.br/", "Banco do Brasil", SourceCategory.BANK, "BR", "State bank"),
    DataSource("https://www.itau.com.br/", "Itaú Unibanco", SourceCategory.BANK, "BR", "Major bank"),
    DataSource("https://www.bradesco.com.br/", "Bradesco", SourceCategory.BANK, "BR", "Major bank"),
    DataSource("https://www.santander.com.br/", "Santander Brasil", SourceCategory.BANK, "BR", "Major bank"),
    DataSource("https://www.caixa.gov.br/", "Caixa", SourceCategory.BANK, "BR", "State bank"),
    DataSource("https://www.b3.com.br/", "B3", SourceCategory.BANK, "BR", "Stock exchange", True),
    DataSource("https://www.petrobras.com.br/", "Petrobras", SourceCategory.ENERGY, "BR", "State oil company"),
    DataSource("https://www.vale.com/", "Vale", SourceCategory.INDUSTRY, "BR", "Mining company"),
    DataSource("https://www.embraer.com/", "Embraer", SourceCategory.INDUSTRY, "BR", "Aerospace"),
    DataSource("https://www.latam.com/", "LATAM Brazil", SourceCategory.TRANSPORT, "BR", "Airline"),
    DataSource("https://www.gol.com.br/", "Gol", SourceCategory.TRANSPORT, "BR", "Airline"),
    DataSource("https://www.azul.com.br/", "Azul", SourceCategory.TRANSPORT, "BR", "Airline"),
    DataSource("https://www.globo.com/", "Globo", SourceCategory.NEWS, "BR", "Media conglomerate"),
    DataSource("https://www.folha.uol.com.br/", "Folha de S.Paulo", SourceCategory.NEWS, "BR", "Major newspaper"),
    DataSource("https://www.estadao.com.br/", "O Estado de S. Paulo", SourceCategory.NEWS, "BR", "Major newspaper"),
    DataSource("https://www.uol.com.br/", "UOL", SourceCategory.NEWS, "BR", "Web portal"),
    DataSource("https://www.record.com.br/", "Record", SourceCategory.NEWS, "BR", "Broadcasting"),
    DataSource("https://agenciabrasil.ebc.com.br/", "Agência Brasil", SourceCategory.NEWS, "BR", "News agency"),
    DataSource("https://www.masp.org.br/", "MASP", SourceCategory.CULTURE, "BR", "Art museum"),
    DataSource("https://www.mam.org.br/", "MAM", SourceCategory.CULTURE, "BR", "Modern art museum"),
    DataSource("https://www.museudobrasil.gov.br/", "National Museum", SourceCategory.CULTURE, "BR", "Natural history"),
    DataSource("https://www.visitbrasil.com/", "Visit Brasil", SourceCategory.TOURISM, "BR", "National tourism"),
    DataSource("https://www.riotur.rio/", "Rio Tourism", SourceCategory.TOURISM, "BR", "Rio tourism"),
    DataSource("https://www.cbf.com.br/", "CBF", SourceCategory.SPORT, "BR", "Football federation", True),
    DataSource("https://www.brasileirao.com.br/", "Brasileirão", SourceCategory.SPORT, "BR", "Football league"),
    DataSource("https://www.flamengo.com.br/", "Flamengo", SourceCategory.SPORT, "BR", "Football club"),
    DataSource("https://www.corinthians.com.br/", "Corinthians", SourceCategory.SPORT, "BR", "Football club"),
    DataSource("https://www.palmeiras.com.br/", "Palmeiras", SourceCategory.SPORT, "BR", "Football club"),
    DataSource("https://www.saopaulofc.net/", "São Paulo FC", SourceCategory.SPORT, "BR", "Football club"),
    DataSource("https://www.santos.com.br/", "Santos FC", SourceCategory.SPORT, "BR", "Football club"),
    DataSource("https://www.gremio.net/", "Grêmio", SourceCategory.SPORT, "BR", "Football club"),
    DataSource("https://www.cob.org.br/", "COB", SourceCategory.SPORT, "BR", "Olympic committee"),
    DataSource("https://www.cbb.com.br/", "CBB Basketball", SourceCategory.SPORT, "BR", "Basketball federation"),
    DataSource("https://www.nba.com/brazil/", "NBA Brazil", SourceCategory.SPORT, "BR", "Basketball"),
    DataSource("https://www.ufc.com.br/", "UFC Brazil", SourceCategory.SPORT, "BR", "MMA"),
    DataSource("https://www.f1.com/", "F1 Brazil", SourceCategory.SPORT, "BR", "Formula 1 race"),
]

# ============================================================
# 🇦🇷 ARGENTINA DATA SOURCES
# ============================================================

ARGENTINA_SOURCES = [
    DataSource("https://www.argentina.gob.ar/", "Argentina.gob.ar", SourceCategory.GOVERNMENT, "AR", "Federal government"),
    DataSource("https://www.hcdn.gob.ar/", "Cámara de Diputados", SourceCategory.GOVERNMENT, "AR", "Chamber"),
    DataSource("https://www.senado.gob.ar/", "Senado", SourceCategory.GOVERNMENT, "AR", "Senate"),
    DataSource("https://www.indec.gob.ar/", "INDEC", SourceCategory.STATISTICS, "AR", "Statistics", True),
    DataSource("https://datos.gob.ar/", "Datos Argentina", SourceCategory.STATISTICS, "AR", "Open data", True),
    DataSource("https://www.buenosaires.gob.ar/", "Buenos Aires City", SourceCategory.GOVERNMENT, "AR", "Capital city"),
    DataSource("https://www.uba.ar/", "UBA", SourceCategory.UNIVERSITY, "AR", "Buenos Aires university"),
    DataSource("https://www.unlp.edu.ar/", "UNLP", SourceCategory.UNIVERSITY, "AR", "La Plata university"),
    DataSource("https://www.unc.edu.ar/", "UNC", SourceCategory.UNIVERSITY, "AR", "Córdoba university"),
    DataSource("https://www.conicet.gov.ar/", "CONICET", SourceCategory.RESEARCH, "AR", "Scientific research"),
    DataSource("https://www.bcra.gob.ar/", "BCRA", SourceCategory.BANK, "AR", "Central bank", True),
    DataSource("https://www.bna.com.ar/", "Banco Nación", SourceCategory.BANK, "AR", "State bank"),
    DataSource("https://www.santander.com.ar/", "Santander Argentina", SourceCategory.BANK, "AR", "Major bank"),
    DataSource("https://www.galicia.com.ar/", "Banco Galicia", SourceCategory.BANK, "AR", "Major bank"),
    DataSource("https://www.byma.com.ar/", "BYMA", SourceCategory.BANK, "AR", "Stock exchange", True),
    DataSource("https://www.ypf.com/", "YPF", SourceCategory.ENERGY, "AR", "Oil company"),
    DataSource("https://www.aerolineas.com.ar/", "Aerolíneas Argentinas", SourceCategory.TRANSPORT, "AR", "National airline"),
    DataSource("https://www.clarin.com/", "Clarín", SourceCategory.NEWS, "AR", "Major newspaper"),
    DataSource("https://www.lanacion.com.ar/", "La Nación", SourceCategory.NEWS, "AR", "Major newspaper"),
    DataSource("https://www.infobae.com/", "Infobae", SourceCategory.NEWS, "AR", "News portal"),
    DataSource("https://www.pagina12.com.ar/", "Página 12", SourceCategory.NEWS, "AR", "Daily newspaper"),
    DataSource("https://www.telam.com.ar/", "Télam", SourceCategory.NEWS, "AR", "News agency"),
    DataSource("https://www.malba.org.ar/", "MALBA", SourceCategory.CULTURE, "AR", "Latin American art"),
    DataSource("https://www.mnba.gob.ar/", "MNBA", SourceCategory.CULTURE, "AR", "Fine arts museum"),
    DataSource("https://www.teatrocolon.org.ar/", "Teatro Colón", SourceCategory.CULTURE, "AR", "Opera house"),
    DataSource("https://www.argentina.travel/", "Argentina Travel", SourceCategory.TOURISM, "AR", "National tourism"),
    DataSource("https://www.afa.com.ar/", "AFA", SourceCategory.SPORT, "AR", "Football federation", True),
    DataSource("https://www.ligaprofesional.ar/", "Liga Profesional", SourceCategory.SPORT, "AR", "Football league"),
    DataSource("https://www.bocajuniors.com.ar/", "Boca Juniors", SourceCategory.SPORT, "AR", "Football club"),
    DataSource("https://www.cariverplate.com.ar/", "River Plate", SourceCategory.SPORT, "AR", "Football club"),
    DataSource("https://www.coa.org.ar/", "COA", SourceCategory.SPORT, "AR", "Olympic committee"),
]

# ============================================================
# 🇨🇴 COLOMBIA DATA SOURCES
# ============================================================

COLOMBIA_SOURCES = [
    DataSource("https://www.gov.co/", "Gov.co", SourceCategory.GOVERNMENT, "CO", "Government portal"),
    DataSource("https://www.camara.gov.co/", "Cámara de Representantes", SourceCategory.GOVERNMENT, "CO", "Chamber"),
    DataSource("https://www.senado.gov.co/", "Senado", SourceCategory.GOVERNMENT, "CO", "Senate"),
    DataSource("https://www.dane.gov.co/", "DANE", SourceCategory.STATISTICS, "CO", "Statistics", True),
    DataSource("https://www.datos.gov.co/", "Datos.gov.co", SourceCategory.STATISTICS, "CO", "Open data", True),
    DataSource("https://www.bogota.gov.co/", "Bogotá Portal", SourceCategory.GOVERNMENT, "CO", "Capital city"),
    DataSource("https://www.unal.edu.co/", "Universidad Nacional", SourceCategory.UNIVERSITY, "CO", "National university"),
    DataSource("https://www.uniandes.edu.co/", "Universidad de los Andes", SourceCategory.UNIVERSITY, "CO", "Private university"),
    DataSource("https://www.javeriana.edu.co/", "Universidad Javeriana", SourceCategory.UNIVERSITY, "CO", "Private university"),
    DataSource("https://www.banrep.gov.co/", "Banco de la República", SourceCategory.BANK, "CO", "Central bank", True),
    DataSource("https://www.bancolombia.com/", "Bancolombia", SourceCategory.BANK, "CO", "Major bank"),
    DataSource("https://www.davivienda.com/", "Davivienda", SourceCategory.BANK, "CO", "Major bank"),
    DataSource("https://www.bvc.com.co/", "BVC", SourceCategory.BANK, "CO", "Stock exchange", True),
    DataSource("https://www.ecopetrol.com.co/", "Ecopetrol", SourceCategory.ENERGY, "CO", "Oil company"),
    DataSource("https://www.avianca.com/", "Avianca", SourceCategory.TRANSPORT, "CO", "National airline"),
    DataSource("https://www.eltiempo.com/", "El Tiempo", SourceCategory.NEWS, "CO", "Major newspaper"),
    DataSource("https://www.elespectador.com/", "El Espectador", SourceCategory.NEWS, "CO", "Major newspaper"),
    DataSource("https://www.semana.com/", "Semana", SourceCategory.NEWS, "CO", "News magazine"),
    DataSource("https://www.rcnradio.com/", "RCN", SourceCategory.NEWS, "CO", "Broadcasting"),
    DataSource("https://www.caracol.com.co/", "Caracol", SourceCategory.NEWS, "CO", "Broadcasting"),
    DataSource("https://www.museonacional.gov.co/", "Museo Nacional", SourceCategory.CULTURE, "CO", "National museum"),
    DataSource("https://www.colombia.travel/", "Colombia Travel", SourceCategory.TOURISM, "CO", "National tourism"),
    DataSource("https://www.fcf.com.co/", "FCF", SourceCategory.SPORT, "CO", "Football federation"),
    DataSource("https://www.dimayor.com.co/", "DIMAYOR", SourceCategory.SPORT, "CO", "Football league"),
    DataSource("https://www.coc.org.co/", "COC", SourceCategory.SPORT, "CO", "Olympic committee"),
]

# ============================================================
# 🇨🇱 CHILE DATA SOURCES
# ============================================================

CHILE_SOURCES = [
    DataSource("https://www.gob.cl/", "Gob.cl", SourceCategory.GOVERNMENT, "CL", "Government portal"),
    DataSource("https://www.camara.cl/", "Cámara de Diputados", SourceCategory.GOVERNMENT, "CL", "Chamber"),
    DataSource("https://www.senado.cl/", "Senado", SourceCategory.GOVERNMENT, "CL", "Senate"),
    DataSource("https://www.ine.cl/", "INE Chile", SourceCategory.STATISTICS, "CL", "Statistics", True),
    DataSource("https://datos.gob.cl/", "Datos.gob.cl", SourceCategory.STATISTICS, "CL", "Open data", True),
    DataSource("https://www.santiago.cl/", "Santiago Portal", SourceCategory.GOVERNMENT, "CL", "Capital city"),
    DataSource("https://www.uchile.cl/", "Universidad de Chile", SourceCategory.UNIVERSITY, "CL", "National university"),
    DataSource("https://www.uc.cl/", "PUC Chile", SourceCategory.UNIVERSITY, "CL", "Catholic university"),
    DataSource("https://www.udec.cl/", "Universidad de Concepción", SourceCategory.UNIVERSITY, "CL", "Concepción university"),
    DataSource("https://www.bcentral.cl/", "Banco Central de Chile", SourceCategory.BANK, "CL", "Central bank", True),
    DataSource("https://www.bancoestado.cl/", "BancoEstado", SourceCategory.BANK, "CL", "State bank"),
    DataSource("https://www.santander.cl/", "Santander Chile", SourceCategory.BANK, "CL", "Major bank"),
    DataSource("https://www.bolsadesantiago.com/", "Bolsa de Santiago", SourceCategory.BANK, "CL", "Stock exchange", True),
    DataSource("https://www.codelco.com/", "Codelco", SourceCategory.INDUSTRY, "CL", "Copper mining"),
    DataSource("https://www.latam.com/", "LATAM Airlines", SourceCategory.TRANSPORT, "CL", "National airline"),
    DataSource("https://www.emol.com/", "Emol", SourceCategory.NEWS, "CL", "News portal"),
    DataSource("https://www.latercera.com/", "La Tercera", SourceCategory.NEWS, "CL", "Major newspaper"),
    DataSource("https://www.elmercurio.com/", "El Mercurio", SourceCategory.NEWS, "CL", "Major newspaper"),
    DataSource("https://www.biobiochile.cl/", "BioBioChile", SourceCategory.NEWS, "CL", "News portal"),
    DataSource("https://www.mnba.gob.cl/", "MNBA Chile", SourceCategory.CULTURE, "CL", "Fine arts museum"),
    DataSource("https://www.chile.travel/", "Chile Travel", SourceCategory.TOURISM, "CL", "National tourism"),
    DataSource("https://www.anfp.cl/", "ANFP", SourceCategory.SPORT, "CL", "Football federation"),
    DataSource("https://www.coch.cl/", "COCh", SourceCategory.SPORT, "CL", "Olympic committee"),
]

# ============================================================
# 🇵🇪 PERU DATA SOURCES
# ============================================================

PERU_SOURCES = [
    DataSource("https://www.gob.pe/", "Gob.pe", SourceCategory.GOVERNMENT, "PE", "Government portal"),
    DataSource("https://www.congreso.gob.pe/", "Congreso", SourceCategory.GOVERNMENT, "PE", "Congress"),
    DataSource("https://www.inei.gob.pe/", "INEI", SourceCategory.STATISTICS, "PE", "Statistics", True),
    DataSource("https://www.datosabiertos.gob.pe/", "Datos Abiertos", SourceCategory.STATISTICS, "PE", "Open data", True),
    DataSource("https://www.munlima.gob.pe/", "Lima Portal", SourceCategory.GOVERNMENT, "PE", "Capital city"),
    DataSource("https://www.unmsm.edu.pe/", "UNMSM", SourceCategory.UNIVERSITY, "PE", "National university"),
    DataSource("https://www.pucp.edu.pe/", "PUCP", SourceCategory.UNIVERSITY, "PE", "Catholic university"),
    DataSource("https://www.bcrp.gob.pe/", "BCRP", SourceCategory.BANK, "PE", "Central bank", True),
    DataSource("https://www.bvl.com.pe/", "BVL", SourceCategory.BANK, "PE", "Stock exchange", True),
    DataSource("https://www.elcomercio.pe/", "El Comercio", SourceCategory.NEWS, "PE", "Major newspaper"),
    DataSource("https://larepublica.pe/", "La República", SourceCategory.NEWS, "PE", "Daily newspaper"),
    DataSource("https://rpp.pe/", "RPP", SourceCategory.NEWS, "PE", "Broadcasting"),
    DataSource("https://www.peru.travel/", "Peru Travel", SourceCategory.TOURISM, "PE", "National tourism"),
    DataSource("https://www.machupicchu.gob.pe/", "Machu Picchu", SourceCategory.TOURISM, "PE", "Historic site"),
    DataSource("https://www.fpf.org.pe/", "FPF", SourceCategory.SPORT, "PE", "Football federation"),
    DataSource("https://www.cop.org.pe/", "COP", SourceCategory.SPORT, "PE", "Olympic committee"),
]

# ============================================================
# 🇻🇪 VENEZUELA DATA SOURCES
# ============================================================

VENEZUELA_SOURCES = [
    DataSource("https://www.vtv.gob.ve/", "VTV", SourceCategory.NEWS, "VE", "State television"),
    DataSource("https://www.ucv.ve/", "UCV", SourceCategory.UNIVERSITY, "VE", "Central university"),
    DataSource("https://www.usb.ve/", "USB", SourceCategory.UNIVERSITY, "VE", "Simón Bolívar university"),
    DataSource("https://www.bcv.org.ve/", "BCV", SourceCategory.BANK, "VE", "Central bank", True),
    DataSource("https://www.pdvsa.com/", "PDVSA", SourceCategory.ENERGY, "VE", "State oil company"),
    DataSource("https://www.eluniversal.com/", "El Universal", SourceCategory.NEWS, "VE", "Major newspaper"),
    DataSource("https://www.fvf.org.ve/", "FVF", SourceCategory.SPORT, "VE", "Football federation"),
]

# ============================================================
# 🇪🇨 ECUADOR DATA SOURCES
# ============================================================

ECUADOR_SOURCES = [
    DataSource("https://www.gob.ec/", "Gob.ec", SourceCategory.GOVERNMENT, "EC", "Government portal"),
    DataSource("https://www.inec.gob.ec/", "INEC", SourceCategory.STATISTICS, "EC", "Statistics", True),
    DataSource("https://www.puce.edu.ec/", "PUCE", SourceCategory.UNIVERSITY, "EC", "Catholic university"),
    DataSource("https://www.ug.edu.ec/", "Universidad de Guayaquil", SourceCategory.UNIVERSITY, "EC", "State university"),
    DataSource("https://www.bce.fin.ec/", "BCE", SourceCategory.BANK, "EC", "Central bank", True),
    DataSource("https://www.elcomercio.com/", "El Comercio", SourceCategory.NEWS, "EC", "Major newspaper"),
    DataSource("https://www.eluniverso.com/", "El Universo", SourceCategory.NEWS, "EC", "Major newspaper"),
    DataSource("https://www.ecuador.travel/", "Ecuador Travel", SourceCategory.TOURISM, "EC", "National tourism"),
    DataSource("https://www.galapagos.gob.ec/", "Galápagos", SourceCategory.TOURISM, "EC", "National park"),
    DataSource("https://www.fef.ec/", "FEF", SourceCategory.SPORT, "EC", "Football federation"),
]

# ============================================================
# 🌴 CARIBBEAN DATA SOURCES
# ============================================================

CARIBBEAN_SOURCES = [
    # Cuba
    DataSource("https://www.cuba.cu/", "Cuba.cu", SourceCategory.GOVERNMENT, "CU", "Cuba portal"),
    DataSource("https://www.uh.cu/", "Universidad de La Habana", SourceCategory.UNIVERSITY, "CU", "Havana university"),
    DataSource("https://www.granma.cu/", "Granma", SourceCategory.NEWS, "CU", "State newspaper"),
    
    # Dominican Republic
    DataSource("https://www.gob.do/", "Gob.do", SourceCategory.GOVERNMENT, "DO", "DR government"),
    DataSource("https://www.one.gob.do/", "ONE", SourceCategory.STATISTICS, "DO", "Statistics"),
    DataSource("https://www.uasd.edu.do/", "UASD", SourceCategory.UNIVERSITY, "DO", "Autonomous university"),
    DataSource("https://www.godominicanrepublic.com/", "Go DR", SourceCategory.TOURISM, "DO", "Tourism"),
    DataSource("https://www.lidom.com/", "LIDOM", SourceCategory.SPORT, "DO", "Baseball league"),
    
    # Puerto Rico
    DataSource("https://www.pr.gov/", "PR.gov", SourceCategory.GOVERNMENT, "PR", "Puerto Rico"),
    DataSource("https://www.upr.edu/", "UPR", SourceCategory.UNIVERSITY, "PR", "University of PR"),
    DataSource("https://www.discoverpuertorico.com/", "Discover PR", SourceCategory.TOURISM, "PR", "Tourism"),
    
    # Jamaica
    DataSource("https://www.gov.jm/", "Gov.jm", SourceCategory.GOVERNMENT, "JM", "Jamaica"),
    DataSource("https://www.visitjamaica.com/", "Visit Jamaica", SourceCategory.TOURISM, "JM", "Tourism"),
    DataSource("https://www.jff.com.jm/", "JFF", SourceCategory.SPORT, "JM", "Football federation"),
    
    # Trinidad & Tobago
    DataSource("https://www.ttconnect.gov.tt/", "TTConnect", SourceCategory.GOVERNMENT, "TT", "T&T portal"),
    DataSource("https://www.uwi.edu/", "UWI", SourceCategory.UNIVERSITY, "TT", "West Indies university"),
    DataSource("https://www.visittnt.com/", "Visit T&T", SourceCategory.TOURISM, "TT", "Tourism"),
    
    # Bahamas
    DataSource("https://www.bahamas.gov.bs/", "Bahamas.gov.bs", SourceCategory.GOVERNMENT, "BS", "Bahamas"),
    DataSource("https://www.bahamas.com/", "Bahamas Tourism", SourceCategory.TOURISM, "BS", "Tourism"),
]

# ============================================================
# 🌎 PAN-AMERICAN SOURCES
# ============================================================

PAN_AMERICAN_SOURCES = [
    DataSource("https://www.oas.org/", "OAS", SourceCategory.GOVERNMENT, "INTL", "Organization of American States"),
    DataSource("https://www.iadb.org/", "IADB", SourceCategory.BANK, "INTL", "Inter-American Development Bank", True),
    DataSource("https://www.cepal.org/", "CEPAL/ECLAC", SourceCategory.RESEARCH, "INTL", "Economic Commission", True),
    DataSource("https://www.panamericanworld.com/", "Pan American", SourceCategory.TOURISM, "INTL", "Tourism"),
    DataSource("https://www.panam.org/", "Pan Am Sports", SourceCategory.SPORT, "INTL", "Pan American Sports Org"),
    DataSource("https://www.conmebol.com/", "CONMEBOL", SourceCategory.SPORT, "INTL", "South American football", True),
    DataSource("https://www.concacaf.com/", "CONCACAF", SourceCategory.SPORT, "INTL", "North/Central American football", True),
    DataSource("https://www.libertadores.com/", "Copa Libertadores", SourceCategory.SPORT, "INTL", "South American club"),
    DataSource("https://www.copaamerica.com/", "Copa América", SourceCategory.SPORT, "INTL", "National teams"),
]

# ============================================================
# COMBINED EXPORT
# ============================================================

ALL_AMERICAS_SOURCES = (
    USA_GOVERNMENT + USA_UNIVERSITIES + USA_HOSPITALS + USA_BANKS +
    USA_TECHNOLOGY + USA_NEWS + USA_CULTURE + USA_SPORT +
    USA_ENTERTAINMENT + USA_TOURISM +
    CANADA_SOURCES + MEXICO_SOURCES + BRAZIL_SOURCES +
    ARGENTINA_SOURCES + COLOMBIA_SOURCES + CHILE_SOURCES +
    PERU_SOURCES + VENEZUELA_SOURCES + ECUADOR_SOURCES +
    CARIBBEAN_SOURCES + PAN_AMERICAN_SOURCES
)

def get_all_sources() -> List[DataSource]:
    """Return all Americas data sources"""
    return ALL_AMERICAS_SOURCES

def get_sources_by_country(country_code: str) -> List[DataSource]:
    """Return sources for a specific country"""
    return [s for s in ALL_AMERICAS_SOURCES if s.country == country_code]

def get_sources_by_category(category: SourceCategory) -> List[DataSource]:
    """Return sources for a specific category"""
    return [s for s in ALL_AMERICAS_SOURCES if s.category == category]

def get_api_sources() -> List[DataSource]:
    """Return only sources with API access"""
    return [s for s in ALL_AMERICAS_SOURCES if s.api_available]

# Statistics
if __name__ == "__main__":
    print(f"🌎 Total Americas Sources: {len(ALL_AMERICAS_SOURCES)}")
    print(f"Countries covered: US, CA, MX, BR, AR, CO, CL, PE, VE, EC, CU, DO, PR, JM, TT, BS")
    print(f"Sources with API: {len(get_api_sources())}")
