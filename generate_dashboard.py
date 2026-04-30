def generate_dashboard(results, output_file="global_dashboard.html"):

    html = """
    <html>
    <head>
    <title>Jenkins Consolidated Dashboard</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma; background: #f4f6f9; }
        h2 { text-align:center; color: #1E3A8A; margin-top:20px; }
        h3 { margin-left: 3%; color:#374151; }

        table {
            border-collapse: collapse;
            width: 94%;
            margin: 20px auto;
            background: white;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        }

        th, td {
            border: 1px solid #e5e7eb;
            padding: 10px;
            text-align: center;
            font-size: 13px;
            background-color: white;
        }

        th {
            background: linear-gradient(90deg, #1E3A8A, #2563EB);
            color: #efeeee;
        }

        tr:nth-child(even) { background-color: #f9fafb; }
        tr:hover { background-color: #eef2ff; }

        .status-badge {
            padding: 4px 10px;
            border-radius: 20px;
            color: white;
            font-weight: bold;
            font-size: 12px;
        }

        .success { background-color: #16a34a; }
        .failure { background-color: #dc2626; }
        .unstable { background-color: #F5D34D; color:black; }
        .aborted { background-color: #99ccff; color:black; }
        .running { background-color: #2563eb; }
        .error { background-color: #6b7280; }

        .date-column {
            min-width: 120px;
            white-space: nowrap;
        }

        a { text-decoration:none; color:#1E3A8A; font-family: monospace; }
    </style>
    </head>
    <body>
    <h2>Global Jenkins Consolidated Dashboard</h2>
    """

    # Group by repo
    grouped = {}
    for r in results:
        grouped.setdefault(r["repo"], []).append(r)

    for repo, repo_data in grouped.items():
        html += f"<h3>Repository: {repo}</h3>"

        html += """
        <table>
        <thead style="display: table-header-group;">
        <tr>
            <th>Ring</th>
            <th>Status</th>
            <th>Build</th>
            <th class="date-column">Date of Execution</th>
            <th>Total Tests</th>
            <th>Passed</th>
            <th>Failed</th>
            <th>Consolidated Report</th>
            <th>Duration</th>
        </tr>
        </thead>
        <tbody>
        """
        for r in repo_data:
            status_upper = r["status"].upper()
            build_link_html = f'<a href="{r["link"]}" target="_blank">{r["build"]}</a>'
            consolidated_report_html = (
                f'<a href="{r["consolidated_report_link"]}" target="_blank">{r["consolidated_report_link"]}</a>'
                if r["consolidated_report_link"] != "#"
                else "Not Available"
            )

            date_only = r['execution_date'].split()[0] if r['execution_date'] != "-" else "-"

            html += f"""
            <tr>
                <td>{r['ring']}</td>
                <td><span class="status-badge {status_upper.lower()}">{r['status']}</span></td>
                <td>{build_link_html}</td>
                <td class="date-column">{date_only}</td>
                <td>{r['total_tests']}</td>
                <td>{r['passed_cases']}</td>
                <td>{r['failed_tests']}</td>
                <td>{consolidated_report_html}</td>
                <td>{r['build_duration']}</td>
            </tr>
            """

        html += "</table>"

    html += """
    </body>
    </html>
    """

    with open(output_file, "w") as f:
        f.write(html)

    print(f"Dashboard generated: {output_file}")
    return html
