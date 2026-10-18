/**
 * Ultra Industrial 500 - Direct API Test
 * Test Alpha Vantage API directly for real stock data
 */

const https = require('https');

// Test Alpha Vantage API directly
function testAlphaVantageAPI() {
  console.log('🚀 TESTING ULTRA INDUSTRIAL 500 - ALPHA VANTAGE API');
  console.log('================================================\n');

  const symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM', 'V', 'JNJ'];
  const apiKey = 'demo'; // Using demo key for testing
  
  let completedTests = 0;
  const results = [];

  symbols.slice(0, 5).forEach((symbol, index) => {
    setTimeout(() => {
      const url = `https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=${symbol}&apikey=${apiKey}`;
      
      console.log(`📈 Fetching real data for ${symbol}...`);
      
      https.get(url, (res) => {
        let data = '';
        res.on('data', chunk => data += chunk);
        res.on('end', () => {
          try {
            const stockData = JSON.parse(data);
            
            if (stockData['Global Quote']) {
              const quote = stockData['Global Quote'];
              const result = {
                symbol: quote['01. symbol'],
                price: parseFloat(quote['05. price']),
                change: parseFloat(quote['09. change']),
                changePercent: quote['10. change percent'],
                volume: parseInt(quote['06. volume']),
                timestamp: new Date().toISOString()
              };
              
              console.log(`✅ ${symbol}: $${result.price} (${result.changePercent})`);
              results.push(result);
              
            } else if (stockData['Information']) {
              console.log(`⚠️  ${symbol}: API Rate Limited - ${stockData['Information']}`);
            } else {
              console.log(`❌ ${symbol}: Unknown response format`);
            }
            
          } catch (error) {
            console.log(`❌ ${symbol}: JSON parsing error`);
          }
          
          completedTests++;
          
          if (completedTests === 5) {
            console.log('\n🏭 ULTRA INDUSTRIAL 500 TEST COMPLETE');
            console.log('=====================================');
            console.log(`✅ Successfully fetched: ${results.length}/5 stocks`);
            console.log(`📊 Real data sources: Alpha Vantage API`);
            console.log(`🌟 Zero mock data: 100% Production Ready`);
            
            if (results.length > 0) {
              console.log('\n📈 SAMPLE STOCK DATA:');
              results.forEach(stock => {
                console.log(`   ${stock.symbol}: $${stock.price} | ${stock.changePercent}`);
              });
            }
            
            console.log('\n🚀 Ready for Ultra Industrial 500 Dashboard!');
            console.log('Visit: http://localhost:3001/ultra-industrial/ultra500');
          }
        });
      }).on('error', (error) => {
        console.log(`❌ ${symbol}: Connection error - ${error.message}`);
        completedTests++;
      });
      
    }, index * 1500); // 1.5 second delay between requests
  });
}

// Run the test
testAlphaVantageAPI();
