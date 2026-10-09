"""
LABORATORIES MODULE
===================
Manages 23 specialized laboratories with their specific functions.

Each laboratory has:
- Unique ID and name
- Domain-specific function
- Geographic location
- Laboratory type
- Performance metrics
- Data services
"""

from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger("laboratories")


@dataclass
class Laboratory:
    """Represents a specialized laboratory with specific function"""
    lab_id: str
    name: str
    function: str
    location: str
    lab_type: str
    status: str = "operational"
    uptime_percentage: float = 99.5
    staff_count: int = 25
    active_projects: int = 5
    data_quality_score: float = 0.95
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert laboratory to dictionary"""
        return asdict(self)
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Get status summary of laboratory"""
        return {
            "lab_id": self.lab_id,
            "name": self.name,
            "location": self.location,
            "function": self.function,
            "status": self.status,
            "uptime": f"{self.uptime_percentage}%",
            "staff": self.staff_count,
            "projects": self.active_projects,
            "data_quality": self.data_quality_score
        }


class LaboratoryNetwork:
    """Manages network of 23 specialized laboratories"""
    
    # 23 Laboratories with specific functions
    LABORATORIES = {
        "Elbasan_AI": Laboratory(
            lab_id="Elbasan_AI",
            name="Elbasan AI Lab",
            function="Artificial Intelligence & Machine Learning",
            location="Elbasan, Albania",
            lab_type="AI",
            staff_count=30,
            active_projects=8
        ),
        "Tirana_Medical": Laboratory(
            lab_id="Tirana_Medical",
            name="Tirana Medical Lab",
            function="Medical Research & Bioscience",
            location="Tirana, Albania",
            lab_type="Medical",
            staff_count=35,
            active_projects=12
        ),
        "Durres_IoT": Laboratory(
            lab_id="Durres_IoT",
            name="Durrës IoT Lab",
            function="Internet of Things & Sensor Networks",
            location="Durrës, Albania",
            lab_type="IoT",
            staff_count=22,
            active_projects=7
        ),
        "Shkoder_Marine": Laboratory(
            lab_id="Shkoder_Marine",
            name="Shkodër Marine Lab",
            function="Marine Biology & Oceanography",
            location="Shkodër, Albania",
            lab_type="Marine",
            staff_count=28,
            active_projects=6
        ),
        "Vlore_Environmental": Laboratory(
            lab_id="Vlore_Environmental",
            name="Vlorë Environmental Lab",
            function="Environmental Monitoring & Ecology",
            location="Vlorë, Albania",
            lab_type="Environmental",
            staff_count=20,
            active_projects=5
        ),
        "Korce_Agricultural": Laboratory(
            lab_id="Korce_Agricultural",
            name="Korça Agricultural Lab",
            function="Agricultural Sciences & Crop Analysis",
            location="Korça, Albania",
            lab_type="Agricultural",
            staff_count=25,
            active_projects=9
        ),
        "Sarrande_Underwater": Laboratory(
            lab_id="Sarrande_Underwater",
            name="Sarandë Underwater Lab",
            function="Underwater Exploration & Deep Sea Research",
            location="Sarandë, Albania",
            lab_type="Underwater",
            staff_count=18,
            active_projects=4
        ),
        "Prishtina_Security": Laboratory(
            lab_id="Prishtina_Security",
            name="Prishtina Security Lab",
            function="Cybersecurity & Network Protection",
            location="Prishtina, Kosovo",
            lab_type="Security",
            staff_count=32,
            active_projects=10
        ),
        "Kostur_Energy": Laboratory(
            lab_id="Kostur_Energy",
            name="Kostur Energy Lab",
            function="Renewable Energy & Power Systems",
            location="Kostur, North Macedonia",
            lab_type="Energy",
            staff_count=26,
            active_projects=8
        ),
        "Athens_Classical": Laboratory(
            lab_id="Athens_Classical",
            name="Athens Classical Lab",
            function="Classical Studies & Historical Research",
            location="Athens, Greece",
            lab_type="Academic",
            staff_count=24,
            active_projects=6
        ),
        "Rome_Architecture": Laboratory(
            lab_id="Rome_Architecture",
            name="Rome Architecture Lab",
            function="Architectural Engineering & Design",
            location="Rome, Italy",
            lab_type="Architecture",
            staff_count=29,
            active_projects=7
        ),
        "Zurich_Finance": Laboratory(
            lab_id="Zurich_Finance",
            name="Zurich Finance Lab",
            function="Financial Analysis & Blockchain",
            location="Zurich, Switzerland",
            lab_type="Finance",
            staff_count=31,
            active_projects=11
        ),
        "Beograd_Industrial": Laboratory(
            lab_id="Beograd_Industrial",
            name="Beograd Industrial Lab",
            function="Industrial Process Optimization",
            location="Beograd, Serbia",
            lab_type="Industrial",
            staff_count=27,
            active_projects=9
        ),
        "Sofia_Chemistry": Laboratory(
            lab_id="Sofia_Chemistry",
            name="Sofia Chemistry Lab",
            function="Chemical Research & Material Science",
            location="Sofia, Bulgaria",
            lab_type="Chemistry",
            staff_count=28,
            active_projects=8
        ),
        "Zagreb_Biotech": Laboratory(
            lab_id="Zagreb_Biotech",
            name="Zagreb Biotech Lab",
            function="Biotechnology & Genetic Engineering",
            location="Zagreb, Croatia",
            lab_type="Biotech",
            staff_count=30,
            active_projects=7
        ),
        "Ljubljana_Quantum": Laboratory(
            lab_id="Ljubljana_Quantum",
            name="Ljubljana Quantum Lab",
            function="Quantum Computing & Physics",
            location="Ljubljana, Slovenia",
            lab_type="Quantum",
            staff_count=26,
            active_projects=6
        ),
        "Vienna_Neuroscience": Laboratory(
            lab_id="Vienna_Neuroscience",
            name="Vienna Neuroscience Lab",
            function="Neuroscience & Brain Research",
            location="Vienna, Austria",
            lab_type="Neuroscience",
            staff_count=33,
            active_projects=10
        ),
        "Prague_Robotics": Laboratory(
            lab_id="Prague_Robotics",
            name="Prague Robotics Lab",
            function="Robotics & Automation Systems",
            location="Prague, Czech Republic",
            lab_type="Robotics",
            staff_count=25,
            active_projects=8
        ),
        "Budapest_Data": Laboratory(
            lab_id="Budapest_Data",
            name="Budapest Data Lab",
            function="Big Data Analytics & Visualization",
            location="Budapest, Hungary",
            lab_type="Data",
            staff_count=28,
            active_projects=9
        ),
        "Bucharest_Nanotechnology": Laboratory(
            lab_id="Bucharest_Nanotechnology",
            name="Bucharest Nanotechnology Lab",
            function="Nanotechnology & Nanomaterials",
            location="Bucharest, Romania",
            lab_type="Nanotechnology",
            staff_count=29,
            active_projects=7
        ),
        "Istanbul_Trade": Laboratory(
            lab_id="Istanbul_Trade",
            name="Istanbul Trade Lab",
            function="International Trade & Logistics",
            location="Istanbul, Turkey",
            lab_type="Trade",
            staff_count=24,
            active_projects=6
        ),
        "Cairo_Archeology": Laboratory(
            lab_id="Cairo_Archeology",
            name="Cairo Archeology Lab",
            function="Archeological Research & Preservation",
            location="Cairo, Egypt",
            lab_type="Archeology",
            staff_count=22,
            active_projects=5
        ),
        "Jerusalem_Heritage": Laboratory(
            lab_id="Jerusalem_Heritage",
            name="Jerusalem Heritage Lab",
            function="Cultural Heritage & Restoration",
            location="Jerusalem, Palestine",
            lab_type="Heritage",
            staff_count=21,
            active_projects=4
        ),
    }
    
    def __init__(self):
        """Initialize laboratory network"""
        self.labs = self.LABORATORIES
        logger.info(f"✅ Laboratory Network initialized with {len(self.labs)} labs")
    
    def get_all_labs(self) -> List[Dict[str, Any]]:
        """Get all laboratories"""
        return [lab.to_dict() for lab in self.labs.values()]
    
    def get_all_labs_summary(self) -> Dict[str, Any]:
        """Get summary of all laboratories"""
        return {
            "total_labs": len(self.labs),
            "laboratories": [lab.get_status_summary() for lab in self.labs.values()],
            "timestamp": datetime.now().isoformat()
        }
    
    def get_lab_by_id(self, lab_id: str) -> Optional[Laboratory]:
        """Get laboratory by ID"""
        return self.labs.get(lab_id)
    
    def get_labs_by_type(self, lab_type: str) -> List[Laboratory]:
        """Get laboratories by type"""
        return [lab for lab in self.labs.values() if lab.lab_type.lower() == lab_type.lower()]
    
    def get_labs_by_location(self, location: str) -> List[Laboratory]:
        """Get laboratories by location"""
        return [lab for lab in self.labs.values() if location.lower() in lab.location.lower()]
    
    def get_labs_by_function_keyword(self, keyword: str) -> List[Laboratory]:
        """Get laboratories by function keyword"""
        keyword_lower = keyword.lower()
        return [lab for lab in self.labs.values() if keyword_lower in lab.function.lower()]
    
    def get_lab_types(self) -> List[str]:
        """Get all unique laboratory types"""
        return list(set(lab.lab_type for lab in self.labs.values()))
    
    def get_total_staff(self) -> int:
        """Get total staff across all labs"""
        return sum(lab.staff_count for lab in self.labs.values())
    
    def get_total_projects(self) -> int:
        """Get total active projects across all labs"""
        return sum(lab.active_projects for lab in self.labs.values())
    
    def get_avg_uptime(self) -> float:
        """Get average uptime across all labs"""
        if not self.labs:
            return 0
        return sum(lab.uptime_percentage for lab in self.labs.values()) / len(self.labs)
    
    def get_network_stats(self) -> Dict[str, Any]:
        """Get network statistics"""
        return {
            "total_laboratories": len(self.labs),
            "total_staff": self.get_total_staff(),
            "total_projects": self.get_total_projects(),
            "average_uptime": f"{self.get_avg_uptime():.1f}%",
            "lab_types": len(self.get_lab_types()),
            "timestamp": datetime.now().isoformat()
        }


# Singleton instance
_laboratory_network = None


def get_laboratory_network() -> LaboratoryNetwork:
    """Get or create laboratory network singleton"""
    global _laboratory_network
    if _laboratory_network is None:
        _laboratory_network = LaboratoryNetwork()
    return _laboratory_network


async def get_all_labs_data() -> Dict[str, Any]:
    """Get all laboratories data"""
    network = get_laboratory_network()
    return network.get_all_labs_summary()
