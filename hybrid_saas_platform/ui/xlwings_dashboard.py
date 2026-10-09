"""
Live Excel Dashboard with Pop-up Alerts using xlwings
Opens Excel visibly and shows Windows message box alerts for critical events.

REQUIRES: xlwings library and Microsoft Excel installed
Install: pip install xlwings
"""

import json
import time
import os

try:
    import xlwings as xw
    XLWINGS_AVAILABLE = True
except ImportError:
    XLWINGS_AVAILABLE = False
    print("WARNING: xlwings not installed. Run: pip install xlwings")

# Paths
excel_file = 'canonical_table_dashboard.xlsx'
json_file = 'pipeline_output.json'

# Threshold for ML anomaly alert
ML_ANOMALY_THRESHOLD = 0.7
ALERT_STATUS = 'FAIL'


def run_xlwings_dashboard(excel_path: str = None, 
                           json_path: str = None,
                           anomaly_threshold: float = None):
    """
    Run live Excel dashboard with Windows pop-up alerts.
    
    Uses xlwings to open Excel application visibly and
    display MsgBox alerts for FAIL status and ML anomalies.
    
    Args:
        excel_path: Path to Excel dashboard file
        json_path: Path to JSON output file
        anomaly_threshold: Threshold for ML anomaly alerts
    """
    if not XLWINGS_AVAILABLE:
        print("ERROR: xlwings is required for pop-up alerts.")
        print("Install with: pip install xlwings")
        return
    
    excel_path = excel_path or excel_file
    json_path = json_path or json_file
    threshold = anomaly_threshold or ML_ANOMALY_THRESHOLD
    
    print("=" * 60)
    print("LIVE EXCEL DASHBOARD WITH POP-UP ALERTS")
    print("=" * 60)
    print(f"Watching: {json_path}")
    print(f"Opening: {excel_path}")
    print("Press Ctrl+C to stop.")
    print("=" * 60)
    
    # Open Excel workbook with xlwings (visible)
    app = xw.App(visible=True)
    wb = xw.Book(excel_path)
    ws = wb.sheets['Canonical Table']
    
    # Get headers from first row
    headers_range = ws.range('1:1').value
    headers = [h for h in headers_range if h is not None]
    
    # Track last modified time
    last_mtime = 0
    
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
                        # Find next empty row in Excel
                        last_row = ws.range('A' + str(ws.cells.last_cell.row)).end('up').row
                        next_row = last_row + 1
                        
                        # Write row data
                        col_idx = 1
                        for key in headers:
                            value = row_data.get(key, '')
                            ws.cells(next_row, col_idx).value = value
                            col_idx += 1
                        
                        # Check for alerts
                        status_val = row_data.get('Status', '')
                        ml_anomaly_val = row_data.get('ML_Anomaly_Prob', 0)
                        
                        try:
                            ml_anomaly_val = float(ml_anomaly_val)
                        except (ValueError, TypeError):
                            ml_anomaly_val = 0
                        
                        # Pop-up alerts
                        if status_val == ALERT_STATUS:
                            try:
                                xw.apps.active.api.MsgBox(
                                    f"ALERT: Row {next_row} Status = FAIL!\n\n"
                                    f"Row ID: {row_data.get('Row_ID', 'Unknown')}\n"
                                    f"Source: {row_data.get('Source', 'Unknown')}",
                                    0,  # OK button only
                                    "Pipeline Alert - FAIL"
                                )
                            except Exception as e:
                                print(f"MsgBox error: {e}")
                        
                        elif ml_anomaly_val >= threshold:
                            try:
                                xw.apps.active.api.MsgBox(
                                    f"ALERT: Row {next_row} ML Anomaly Detected!\n\n"
                                    f"Probability: {ml_anomaly_val:.3f}\n"
                                    f"Threshold: {threshold}\n"
                                    f"Row ID: {row_data.get('Row_ID', 'Unknown')}",
                                    0,  # OK button only
                                    "ML Alert - Anomaly"
                                )
                            except Exception as e:
                                print(f"MsgBox error: {e}")
                    
                    # Save workbook
                    wb.save()
                    print(f"Updated Excel dashboard with {len(data)} new row(s) and alerts.")
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nLive Excel dashboard stopped.")
        wb.close()
        app.quit()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Live Excel Dashboard with Pop-up Alerts')
    parser.add_argument('--excel', type=str, default=excel_file,
                        help='Path to Excel file')
    parser.add_argument('--json', type=str, default=json_file,
                        help='Path to JSON output file')
    parser.add_argument('--threshold', type=float, default=ML_ANOMALY_THRESHOLD,
                        help='ML anomaly probability threshold')
    
    args = parser.parse_args()
    run_xlwings_dashboard(args.excel, args.json, args.threshold)
