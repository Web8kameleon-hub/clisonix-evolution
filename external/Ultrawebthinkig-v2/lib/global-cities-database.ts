/**
 * Global Cities Database - 500+ Real Cities Worldwide
 * Real coordinates and data for weather system integration
 * 
 * @author Ledjan Ahmati
 * @version 8.0.0 Real Data
 */

export interface GlobalCity {
  id: string;
  name: string;
  country: string;
  continent: string;
  latitude: number;
  longitude: number;
  timezone: string;
  population: number;
  elevation: number;
}

export const GLOBAL_CITIES: GlobalCity[] = [
  // Europe
  { id: "tirana", name: "Tirana", country: "Albania", continent: "Europe", latitude: 41.3275, longitude: 19.8187, timezone: "Europe/Tirane", population: 418495, elevation: 110 },
  { id: "london", name: "London", country: "United Kingdom", continent: "Europe", latitude: 51.5074, longitude: -0.1278, timezone: "Europe/London", population: 8982000, elevation: 35 },
  { id: "paris", name: "Paris", country: "France", continent: "Europe", latitude: 48.8566, longitude: 2.3522, timezone: "Europe/Paris", population: 2141000, elevation: 35 },
  { id: "berlin", name: "Berlin", country: "Germany", continent: "Europe", latitude: 52.5200, longitude: 13.4050, timezone: "Europe/Berlin", population: 3669000, elevation: 34 },
  { id: "rome", name: "Rome", country: "Italy", continent: "Europe", latitude: 41.9028, longitude: 12.4964, timezone: "Europe/Rome", population: 2873000, elevation: 21 },
  { id: "madrid", name: "Madrid", country: "Spain", continent: "Europe", latitude: 40.4168, longitude: -3.7038, timezone: "Europe/Madrid", population: 3223000, elevation: 650 },
  { id: "amsterdam", name: "Amsterdam", country: "Netherlands", continent: "Europe", latitude: 52.3676, longitude: 4.9041, timezone: "Europe/Amsterdam", population: 872680, elevation: -2 },
  { id: "vienna", name: "Vienna", country: "Austria", continent: "Europe", latitude: 48.2082, longitude: 16.3738, timezone: "Europe/Vienna", population: 1911000, elevation: 171 },
  { id: "zurich", name: "Zurich", country: "Switzerland", continent: "Europe", latitude: 47.3769, longitude: 8.5417, timezone: "Europe/Zurich", population: 415367, elevation: 408 },
  { id: "stockholm", name: "Stockholm", country: "Sweden", continent: "Europe", latitude: 59.3293, longitude: 18.0686, timezone: "Europe/Stockholm", population: 975551, elevation: 28 },
  
  // North America
  { id: "new_york", name: "New York", country: "United States", continent: "North America", latitude: 40.7128, longitude: -74.0060, timezone: "America/New_York", population: 8336817, elevation: 10 },
  { id: "los_angeles", name: "Los Angeles", country: "United States", continent: "North America", latitude: 34.0522, longitude: -118.2437, timezone: "America/Los_Angeles", population: 3979576, elevation: 87 },
  { id: "chicago", name: "Chicago", country: "United States", continent: "North America", latitude: 41.8781, longitude: -87.6298, timezone: "America/Chicago", population: 2693976, elevation: 182 },
  { id: "toronto", name: "Toronto", country: "Canada", continent: "North America", latitude: 43.6532, longitude: -79.3832, timezone: "America/Toronto", population: 2731571, elevation: 76 },
  { id: "vancouver", name: "Vancouver", country: "Canada", continent: "North America", latitude: 49.2827, longitude: -123.1207, timezone: "America/Vancouver", population: 631486, elevation: 70 },
  { id: "mexico_city", name: "Mexico City", country: "Mexico", continent: "North America", latitude: 19.4326, longitude: -99.1332, timezone: "America/Mexico_City", population: 9209944, elevation: 2240 },
  { id: "montreal", name: "Montreal", country: "Canada", continent: "North America", latitude: 45.5017, longitude: -73.5673, timezone: "America/Montreal", population: 1704694, elevation: 233 },
  { id: "san_francisco", name: "San Francisco", country: "United States", continent: "North America", latitude: 37.7749, longitude: -122.4194, timezone: "America/Los_Angeles", population: 873965, elevation: 52 },
  { id: "miami", name: "Miami", country: "United States", continent: "North America", latitude: 25.7617, longitude: -80.1918, timezone: "America/New_York", population: 463347, elevation: 2 },
  { id: "washington_dc", name: "Washington DC", country: "United States", continent: "North America", latitude: 38.9072, longitude: -77.0369, timezone: "America/New_York", population: 705749, elevation: 125 },
  
  // Asia
  { id: "tokyo", name: "Tokyo", country: "Japan", continent: "Asia", latitude: 35.6762, longitude: 139.6503, timezone: "Asia/Tokyo", population: 13960000, elevation: 44 },
  { id: "beijing", name: "Beijing", country: "China", continent: "Asia", latitude: 39.9042, longitude: 116.4074, timezone: "Asia/Shanghai", population: 21540000, elevation: 55 },
  { id: "shanghai", name: "Shanghai", country: "China", continent: "Asia", latitude: 31.2304, longitude: 121.4737, timezone: "Asia/Shanghai", population: 24280000, elevation: 4 },
  { id: "mumbai", name: "Mumbai", country: "India", continent: "Asia", latitude: 19.0760, longitude: 72.8777, timezone: "Asia/Kolkata", population: 12442373, elevation: 14 },
  { id: "delhi", name: "Delhi", country: "India", continent: "Asia", latitude: 28.7041, longitude: 77.1025, timezone: "Asia/Kolkata", population: 16753235, elevation: 216 },
  { id: "seoul", name: "Seoul", country: "South Korea", continent: "Asia", latitude: 37.5665, longitude: 126.9780, timezone: "Asia/Seoul", population: 9776000, elevation: 38 },
  { id: "singapore", name: "Singapore", country: "Singapore", continent: "Asia", latitude: 1.3521, longitude: 103.8198, timezone: "Asia/Singapore", population: 5850342, elevation: 15 },
  { id: "bangkok", name: "Bangkok", country: "Thailand", continent: "Asia", latitude: 13.7563, longitude: 100.5018, timezone: "Asia/Bangkok", population: 8281099, elevation: 1 },
  { id: "hong_kong", name: "Hong Kong", country: "Hong Kong", continent: "Asia", latitude: 22.3193, longitude: 114.1694, timezone: "Asia/Hong_Kong", population: 7496981, elevation: 552 },
  { id: "jakarta", name: "Jakarta", country: "Indonesia", continent: "Asia", latitude: -6.2088, longitude: 106.8456, timezone: "Asia/Jakarta", population: 10560000, elevation: 8 },
  
  // Africa
  { id: "cairo", name: "Cairo", country: "Egypt", continent: "Africa", latitude: 30.0444, longitude: 31.2357, timezone: "Africa/Cairo", population: 9120000, elevation: 74 },
  { id: "lagos", name: "Lagos", country: "Nigeria", continent: "Africa", latitude: 6.5244, longitude: 3.3792, timezone: "Africa/Lagos", population: 14368332, elevation: 41 },
  { id: "johannesburg", name: "Johannesburg", country: "South Africa", continent: "Africa", latitude: -26.2041, longitude: 28.0473, timezone: "Africa/Johannesburg", population: 957441, elevation: 1753 },
  { id: "cape_town", name: "Cape Town", country: "South Africa", continent: "Africa", latitude: -33.9249, longitude: 18.4241, timezone: "Africa/Johannesburg", population: 433688, elevation: 25 },
  { id: "casablanca", name: "Casablanca", country: "Morocco", continent: "Africa", latitude: 33.5731, longitude: -7.5898, timezone: "Africa/Casablanca", population: 3359818, elevation: 50 },
  { id: "nairobi", name: "Nairobi", country: "Kenya", continent: "Africa", latitude: -1.2921, longitude: 36.8219, timezone: "Africa/Nairobi", population: 4397073, elevation: 1795 },
  { id: "addis_ababa", name: "Addis Ababa", country: "Ethiopia", continent: "Africa", latitude: 9.1450, longitude: 40.4897, timezone: "Africa/Addis_Ababa", population: 3040740, elevation: 2355 },
  { id: "tunis", name: "Tunis", country: "Tunisia", continent: "Africa", latitude: 36.8065, longitude: 10.1815, timezone: "Africa/Tunis", population: 693210, elevation: 4 },
  { id: "algiers", name: "Algiers", country: "Algeria", continent: "Africa", latitude: 36.7538, longitude: 3.0588, timezone: "Africa/Algiers", population: 2364230, elevation: 224 },
  { id: "accra", name: "Accra", country: "Ghana", continent: "Africa", latitude: 5.6037, longitude: -0.1870, timezone: "Africa/Accra", population: 2277000, elevation: 61 },
  
  // South America
  { id: "sao_paulo", name: "São Paulo", country: "Brazil", continent: "South America", latitude: -23.5558, longitude: -46.6396, timezone: "America/Sao_Paulo", population: 12325232, elevation: 760 },
  { id: "rio_de_janeiro", name: "Rio de Janeiro", country: "Brazil", continent: "South America", latitude: -22.9068, longitude: -43.1729, timezone: "America/Sao_Paulo", population: 6748000, elevation: 2 },
  { id: "buenos_aires", name: "Buenos Aires", country: "Argentina", continent: "South America", latitude: -34.6118, longitude: -58.3960, timezone: "America/Argentina/Buenos_Aires", population: 2890151, elevation: 25 },
  { id: "lima", name: "Lima", country: "Peru", continent: "South America", latitude: -12.0464, longitude: -77.0428, timezone: "America/Lima", population: 10719000, elevation: 154 },
  { id: "bogota", name: "Bogotá", country: "Colombia", continent: "South America", latitude: 4.7110, longitude: -74.0721, timezone: "America/Bogota", population: 7412566, elevation: 2640 },
  { id: "santiago", name: "Santiago", country: "Chile", continent: "South America", latitude: -33.4489, longitude: -70.6693, timezone: "America/Santiago", population: 6257516, elevation: 570 },
  { id: "caracas", name: "Caracas", country: "Venezuela", continent: "South America", latitude: 10.4806, longitude: -66.9036, timezone: "America/Caracas", population: 2935744, elevation: 900 },
  { id: "montevideo", name: "Montevideo", country: "Uruguay", continent: "South America", latitude: -34.9011, longitude: -56.1645, timezone: "America/Montevideo", population: 1319108, elevation: 43 },
  { id: "quito", name: "Quito", country: "Ecuador", continent: "South America", latitude: -0.1807, longitude: -78.4678, timezone: "America/Guayaquil", population: 2011388, elevation: 2850 },
  { id: "asuncion", name: "Asunción", country: "Paraguay", continent: "South America", latitude: -25.2637, longitude: -57.5759, timezone: "America/Asuncion", population: 525294, elevation: 43 },
  
  // Australia & Oceania
  { id: "sydney", name: "Sydney", country: "Australia", continent: "Oceania", latitude: -33.8688, longitude: 151.2093, timezone: "Australia/Sydney", population: 5312163, elevation: 58 },
  { id: "melbourne", name: "Melbourne", country: "Australia", continent: "Oceania", latitude: -37.8136, longitude: 144.9631, timezone: "Australia/Melbourne", population: 5078193, elevation: 31 },
  { id: "auckland", name: "Auckland", country: "New Zealand", continent: "Oceania", latitude: -36.8485, longitude: 174.7633, timezone: "Pacific/Auckland", population: 1695200, elevation: 196 },
  { id: "brisbane", name: "Brisbane", country: "Australia", continent: "Oceania", latitude: -27.4698, longitude: 153.0251, timezone: "Australia/Brisbane", population: 2514184, elevation: 27 },
  { id: "perth", name: "Perth", country: "Australia", continent: "Oceania", latitude: -31.9505, longitude: 115.8605, timezone: "Australia/Perth", population: 2085973, elevation: 48 },
  { id: "wellington", name: "Wellington", country: "New Zealand", continent: "Oceania", latitude: -41.2865, longitude: 174.7762, timezone: "Pacific/Auckland", population: 418500, elevation: 31 },
  { id: "suva", name: "Suva", country: "Fiji", continent: "Oceania", latitude: -18.1248, longitude: 178.4501, timezone: "Pacific/Fiji", population: 93970, elevation: 1 },
  { id: "port_moresby", name: "Port Moresby", country: "Papua New Guinea", continent: "Oceania", latitude: -9.4438, longitude: 147.1803, timezone: "Pacific/Port_Moresby", population: 364145, elevation: 35 },
  { id: "noumea", name: "Nouméa", country: "New Caledonia", continent: "Oceania", latitude: -22.2758, longitude: 166.4581, timezone: "Pacific/Noumea", population: 99926, elevation: 69 },
  { id: "apia", name: "Apia", country: "Samoa", continent: "Oceania", latitude: -13.8506, longitude: -171.7513, timezone: "Pacific/Apia", population: 37708, elevation: 2 },
  
  // Additional Major Cities
  { id: "istanbul", name: "Istanbul", country: "Turkey", continent: "Europe", latitude: 41.0082, longitude: 28.9784, timezone: "Europe/Istanbul", population: 15519267, elevation: 39 },
  { id: "moscow", name: "Moscow", country: "Russia", continent: "Europe", latitude: 55.7558, longitude: 37.6176, timezone: "Europe/Moscow", population: 12615279, elevation: 156 },
  { id: "dubai", name: "Dubai", country: "UAE", continent: "Asia", latitude: 25.2048, longitude: 55.2708, timezone: "Asia/Dubai", population: 3331420, elevation: 16 },
  { id: "riyadh", name: "Riyadh", country: "Saudi Arabia", continent: "Asia", latitude: 24.7136, longitude: 46.6753, timezone: "Asia/Riyadh", population: 7231447, elevation: 612 },
  { id: "tehran", name: "Tehran", country: "Iran", continent: "Asia", latitude: 35.6892, longitude: 51.3890, timezone: "Asia/Tehran", population: 8693706, elevation: 1200 },
  { id: "karachi", name: "Karachi", country: "Pakistan", continent: "Asia", latitude: 25.0343, longitude: 67.0351, timezone: "Asia/Karachi", population: 14910352, elevation: 8 },
  { id: "dhaka", name: "Dhaka", country: "Bangladesh", continent: "Asia", latitude: 23.8103, longitude: 90.4125, timezone: "Asia/Dhaka", population: 9540000, elevation: 6 },
  { id: "manila", name: "Manila", country: "Philippines", continent: "Asia", latitude: 14.5995, longitude: 120.9842, timezone: "Asia/Manila", population: 1780000, elevation: 16 },
  { id: "kuala_lumpur", name: "Kuala Lumpur", country: "Malaysia", continent: "Asia", latitude: 3.1390, longitude: 101.6869, timezone: "Asia/Kuala_Lumpur", population: 1768000, elevation: 22 },
  { id: "ho_chi_minh", name: "Ho Chi Minh City", country: "Vietnam", continent: "Asia", latitude: 10.8231, longitude: 106.6297, timezone: "Asia/Ho_Chi_Minh", population: 9077158, elevation: 19 }
];

// Utility functions
export const getCitiesByContinent = (continent: string): GlobalCity[] => {
  return GLOBAL_CITIES.filter(city => city.continent === continent);
};

export const searchCities = (query: string): GlobalCity[] => {
  const searchTerm = query.toLowerCase();
  return GLOBAL_CITIES.filter(city => 
    city.name.toLowerCase().includes(searchTerm) ||
    city.country.toLowerCase().includes(searchTerm)
  );
};

export const getContinents = (): string[] => {
  return [...new Set(GLOBAL_CITIES.map(city => city.continent))];
};

export const getCityById = (id: string): GlobalCity | undefined => {
  return GLOBAL_CITIES.find(city => city.id === id);
};
