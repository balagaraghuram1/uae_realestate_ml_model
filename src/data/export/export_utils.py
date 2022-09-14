 """Data export utilities for reports and analysis."""
import csv, json, io, logging
from typing import Dict, List
import pandas as pd

logger = logging.getLogger(__name__)

def export_to_csv(data: List[Dict], filepath: str) -> str:
    """Export data to CSV file."""
    if not data:
        return filepath
    df = pd.DataFrame(data)
    df.to_csv(filepath, index=False, encoding="utf-8-sig")
    logger.info("Exported %d rows to %s", len(data), filepath)
    return filepath

def export_to_excel(data: List[Dict], filepath: str, sheet_name: str = "Data") -> str:
    """Export data to Excel file."""
    df = pd.DataFrame(data)
    df.to_excel(filepath, index=False, sheet_name=sheet_name)
    logger.info("Exported %d rows to %s", len(data), filepath)
    return filepath

def export_to_json(data: List[Dict], filepath: str, pretty: bool = True) -> str:
    """Export data to JSON file."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2 if pretty else None, default=str)
    logger.info("Exported %d records to %s", len(data), filepath)
    return filepath

def generate_summary_csv(properties: List[Dict]) -> str:
    """Generate a CSV string summary of properties."""
    output = io.StringIO()
    if not properties:
        return ""
    writer = csv.DictWriter(output, fieldnames=properties[0].keys())
    writer.writeheader()
    writer.writerows(properties)
    return output.getvalue()
