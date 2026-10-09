/**
 * 🔌 CLISONIX POWER AUTOMATE CONNECTOR
 * Ky script thirret nga Power Automate për të bërë HTTP requests të vërteta
 * 
 * FLOW NË POWER AUTOMATE:
 * 1. Recurrence (trigger) → çdo 5 minuta
 * 2. Run script (Office Scripts) → ky script
 * 3. HTTP connector → thirr API
 * 4. Update Excel → shkruan rezultatin
 * 
 * KOLONAT:
 * D (3): Endpoint
 * F (5): Status_Testimi
 * R (17): Response_Sample
 * S (18): Last_Check
 */

// Versioni i thjeshtë për Excel Online
export async function main(workbook: ExcelScript.Workbook): Promise<EndpointData[]> {
    const SHEET_NAME = "API_Endpoints";
    
    let sheet = workbook.getWorksheet(SHEET_NAME);
    if (!sheet) {
        return [];
    }
    
    let usedRange = sheet.getUsedRange();
    let values = usedRange.getValues();
    let endpoints: EndpointData[] = [];
    
    // Kolekto të gjitha endpoints për Power Automate
    for (let i = 1; i < values.length; i++) {
        let endpoint = values[i][3];  // D - Endpoint
        let method = values[i][2];    // C - Method
        
        if (endpoint && typeof endpoint === 'string') {
            endpoints.push({
                row: i,
                endpoint: String(endpoint),
                method: String(method)
            });
        }
    }
    
    return endpoints;
}

// Interface për të dhënat
interface EndpointData {
    row: number;
    endpoint: string;
    method: string;
}

/**
 * SCRIPT I DYTË: Përditëson rezultatin pas HTTP request
 * Thirret nga Power Automate pas çdo HTTP response
 */
async function updateResult(
    workbook: ExcelScript.Workbook,
    row: number,
    status: string,
    response: string,
    latency: number
) {
    const SHEET_NAME = "API_Endpoints";
    let sheet = workbook.getWorksheet(SHEET_NAME);
    
    if (!sheet) return;
    
    let timestamp = new Date().toISOString();
    
    // Përditëso kolonat
    sheet.getCell(row, 5).setValue(status);           // F - Status Testimi
    sheet.getCell(row, 17).setValue(response);        // R - Response Sample
    sheet.getCell(row, 18).setValue(timestamp);       // S - Last Check
    
    // Nëse latency > 1000ms, shëno si i ngadalshëm
    if (latency > 1000) {
        sheet.getCell(row, 14).setValue(`⚠️ Slow: ${latency}ms`);  // O - Komente
    }
}
