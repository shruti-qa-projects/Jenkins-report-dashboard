from datetime import datetime
import os

from config import REPORT_FOLDER
from generate_dashboard import generate_dashboard


def save_reports(results, branch_name=None):
    os.makedirs(REPORT_FOLDER, exist_ok=True)
    html_content = generate_dashboard(results)

    if branch_name:
        branch = branch_name.replace("/", "_").replace(" ", "_")
        filename = f"{branch}_report.html"
    else:
        filename = f"Latest_Consolidated_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

    filepath = os.path.join(REPORT_FOLDER, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"Dashboard generated: {filepath}")

    return filepath
