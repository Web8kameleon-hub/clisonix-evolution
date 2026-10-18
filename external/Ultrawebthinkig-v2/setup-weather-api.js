/**
 * 🔑 OPENWEATHER API KEY SETUP HELPER
 * Helper script to configure your real OpenWeatherMap API key
 */

console.log("🌍 ULTRA INDUSTRIAL WEATHER API SETUP");
console.log("=====================================");

console.log("\n📋 STEP 1: Get your OpenWeatherMap API Key");
console.log("1. Go to: https://openweathermap.org/api");
console.log("2. Sign up or login to your account");
console.log("3. Go to API Keys section");
console.log("4. Copy your API key");

console.log("\n🔧 STEP 2: Test your API key");
console.log("Replace 'YOUR_API_KEY_HERE' with your real API key:");
console.log("curl \"https://api.openweathermap.org/data/2.5/weather?q=London&appid=YOUR_API_KEY_HERE\"");

console.log("\n⚡ STEP 3: Update .env.local file");
console.log("Open .env.local and replace the OPENWEATHER_API_KEY with your real key");

console.log("\n🚀 STEP 4: Restart development server");
console.log("npm run dev");

// Test function to validate API key
async function testApiKey(apiKey) {
    try {
        const response = await fetch(`https://api.openweathermap.org/data/2.5/weather?q=London&appid=${apiKey}`);
        const data = await response.json();
        
        if (response.ok) {
            console.log("✅ API Key is VALID!");
            console.log(`🌤️ Test data: ${data.name}, ${Math.round(data.main.temp - 273.15)}°C`);
            return true;
        } else {
            console.log("❌ API Key is INVALID!");
            console.log(`Error: ${data.message}`);
            return false;
        }
    } catch (error) {
        console.log("❌ Network error:", error.message);
        return false;
    }
}

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { testApiKey };
}

console.log("\n💡 TIP: After you get your API key, run:");
console.log("node setup-weather-api.js YOUR_API_KEY_HERE");
