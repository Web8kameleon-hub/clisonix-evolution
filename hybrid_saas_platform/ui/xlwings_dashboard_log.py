"""
Live Excel Dashboard with Pop-up Alerts and Alert Log using xlwings
Opens Excel visibly, shows Windows message box alerts, and logs all alerts
to a separate Alert_Log sheet.

REQUIRES: xlwings library and Microsoft Excel installed
Install: pip install xlwings
"""

import json
import time
import os
from datetime import datetime

try:
    import xlwings as xw
    XLWINGS_AVAILABLE = True
except ImportError:
    XLWINGS_AVAILABLE = False
    print("WARNING: xlwings not installed. Run: pip install xlwings")

# Paths
excel_file = 'canonical_table_dashboard.xlsx'
json_file = 'pipeline_output.json'

# Alert configuration
ML_ANOMALY_THRESHOLD = 0.7
ALERT_STATUS = 'FAIL'


def ensure_alert_log_sheet(wb) -> object:
    """
    Ensure Alert_Log sheet exists, create if not.
    
    Args:
        wb: xlwings Workbook object
        
    Returns:
        Alert_Log sheet object
    """
    sheet_names = [s.name for s in wb.sheets]
    
    if 'Alert_Log' not in sheet_names:
        alert_sheet = wb.sheets.add('Alert_Log')
        # Set up headers
        alert_sheet.range('A1').value = ['Timestamp', 'Row', 'Alert_Type', 'Value', 'Row_ID', 'Source']
        # Format header row
        alert_sheet.range('A1:F1').api.Font.Bold = True
        alert_sheet.range('A1:F1').api.Interior.Color = 0xCCCCCC  # Light gray
        print("Created Alert_Log sheet")
    else:
        alert_sheet = wb.sheets['Alert_Log']
    
    return alert_sheet


def log_alert(alert_sheet, row_num: int, alert_type: str, 
              value: str, row_id: str = '', source: str = ''):
    """
    Log an alert to the Alert_Log sheet.
    
    Args:
        alert_sheet: xlwings Sheet object for Alert_Log
        row_num: Row number where alert occurred
        alert_type: Type of alert (FAIL, ML Anomaly, etc.)
        value: Alert value
        row_id: Row ID from data
        source: Source from data
    """
    # Find next empty row
    last_row = alert_sheet.range('A' + str(alert_sheet.cells.last_cell.row)).end('up').row
    next_row = last_row + 1
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    alert_sheet.range(f'A{next_row}').value = [
        timestamp, 
        row_num, 
        alert_type, 
        value,
        row_id,
        source
    ]
    
    # Color code by alert type
    if alert_type == 'FAIL':
        alert_sheet.range(f'A{next_row}:F{next_row}').api.Interior.Color = 0x6680FF  # Red
    elif alert_type == 'ML Anomaly':
        alert_sheet.range(f'A{next_row}:F{next_row}').api.Interior.Color = 0x00A5FF  # Orange


def run_xlwings_dashboard_with_log(excel_path: str = None,
                                    json_path: str = None,
                                    anomaly_threshold: float = None):
    """
    Run live Excel dashboard with pop-up alerts and alert logging.
    
    Features:
    - Opens Excel visible
    - Pop-up alerts for FAIL and ML Anomaly
    - Logs all alerts to Alert_Log sheet with timestamp
    - Color-coded alert log entries
    
    Args:
        excel_path: Path to Excel dashboard file
        json_path: Path to JSON output file
        anomaly_threshold: Threshold for ML anomaly alerts
    """
    if not XLWINGS_AVAILABLE:
        print("ERROR: xlwings is required for this dashboard.")
        print("Install with: pip install xlwings")
        return
    
    excel_path = excel_path or excel_file
    json_path = json_path or json_file
    threshold = anomaly_threshold or ML_ANOMALY_THRESHOLD
    
    print("=" * 60)
    print("LIVE EXCEL DASHBOARD WITH POP-UP ALERTS AND LOGGING")
    print("=" * 60)
    print(f"Watching: {json_path}")
    print(f"Opening: {excel_path}")
    print(f"ML Anomaly Threshold: {threshold}")
    print("Press Ctrl+C to stop.")
    print("=" * 60)
    
    # Open Excel workbook with xlwings (visible)
    app = xw.App(visible=True)
    wb = xw.Book(excel_path)
    ws = wb.sheets['Canonical Table']
    
    # Ensure Alert_Log sheet exists
    alert_sheet = ensure_alert_log_sheet(wb)
    
    # Get headers from first row
    headers_range = ws.range('1:1').value
    headers = [h for h in headers_range if h is not None]
    
    # Track last modified time
    last_mtime = 0
    
    # Alert counters
    total_alerts = 0
    fail_alerts = 0
    anomaly_alerts = 0
    
    try:
        while True:
            if os.path.exists(json_path):
                mtime = os.path.getmtime(json_path)
                if mtime != last_mtime:
                    last_mtime = mtime
                    
                    with open(json_path) as f:
                        data = json.load(f)
                    
                    if isinstance(data, dict):
                        data = [data]
                    
                    for row_data in data:
                        # Find next empty row
                        last_row = ws.range('A' + str(ws.cells.last_cell.row)).end('up').row
                        next_row = last_row + 1
                        
                        # Write row data
                        col_idx = 1
                        for key in headers:
                            value = row_data.get(key, '')
                            ws.cells(next_row, col_idx).value = value
                            col_idx += 1
                        
                        # Extract alert-relevant values
                        status_val = row_data.get('Status', '')
                        row_id = row_data.get('Row_ID', 'Unknown')
                        source = row_data.get('Source', 'Unknown')
                        
                        ml_anomaly_val = row_data.get('ML_Anomaly_Prob', 0)
                        try:
                            ml_anomaly_val = float(ml_anomaly_val)
                        except (ValueError, TypeError):
                            ml_anomaly_val = 0
                        
                        alert_triggered = False
                        alert_type = ''
                        alert_value = ''
                        
                        # Check for FAIL status
                        if status_val == ALERT_STATUS:
                            alert_triggered = True
                            alert_type = 'FAIL'
                            alert_value = status_val
                            fail_alerts += 1
                            
                            try:
                                xw.apps.active.api.MsgBox(
                                    f"ALERT: Row {next_row} Status = FAIL!\n\n"
                                    f"Row ID: {row_id}\n"
                                    f"Source: {source}\n\n"
                                    f"This has been logged to Alert_Log sheet.",
                                    0,
                                    "Pipeline Alert - FAIL"
                                )
                            except Exception as e:
                                print(f"MsgBox error: {e}")
                        
                        # Check for ML Anomaly
                        elif ml_anomaly_val >= threshold:
                            alert_triggered = True
                            alert_type = 'ML Anomaly'
                            alert_value = f"{ml_anomaly_val:.3f}"
                            anomaly_alerts += 1
                            
                            try:
                                xw.apps.active.api.MsgBox(
                                    f"ALERT: Row {next_row} ML Anomaly Detected!\n\n"
                                    f"Probability: {ml_anomaly_val:.3f}\n"
                                    f"Threshold: {threshold}\n"
                                    f"Row ID: {row_id}\n\n"
                                    f"This has been logged to Alert_Log sheet.",
                                    0,
                                    "ML Alert - Anomaly"
                                )
                            except Exception as e:
                                print(f"MsgBox error: {e}")
                        
                        # Log alert if triggered
                        if alert_triggered:
                            total_alerts += 1
                            log_alert(
                                alert_sheet, 
                                next_row, 
                                alert_type, 
                                alert_value,
                                row_id,
                                source
                            )
                            print(f"Alert logged: {alert_type} at row {next_row}")
                    
                    # Save workbook
                    wb.save()
                    print(f"Updated Excel dashboard with {len(data)} new row(s) and alerts logged.")
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n" + "=" * 60)
        print("DASHBOARD SESSION SUMMARY")
        print("=" * 60)
        print(f"Total alerts triggered: {total_alerts}")
        print(f"  - FAIL alerts: {fail_alerts}")
        print(f"  - ML Anomaly alerts: {anomaly_alerts}")
        print(f"\nAll alerts have been logged to Alert_Log sheet.")
        print("Live Excel dashboard stopped.")
        
        # Save final state
        wb.save()
        wb.close()
        app.quit()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Live Excel Dashboard with Pop-up Alerts and Logging'
    )
    parser.add_argument('--excel', type=str, default=excel_file,
                        help='Path to Excel file')
    parser.add_argument('--json', type=str, default=json_file,
                        help='Path to JSON output file')
    parser.add_argument('--threshold', type=float, default=ML_ANOMALY_THRESHOLD,
                        help='ML anomaly probability threshold')
    
    args = parser.parse_args()
    run_xlwings_dashboard_with_log(args.excel, args.json, args.threshold)
