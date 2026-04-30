import subprocess
from flask import Flask, render_template, send_file, request
from jenkins_fetch import fetch_build_data
from reports import save_reports

app = Flask(__name__)


# Home Page
@app.route("/")
def home():
    return render_template("index.html", error=None)


# Report Generator
def generate_report(branch_name=None):
    results = fetch_build_data(branch_name)
    if isinstance(results, dict) and results.get("error"):
        return results
    return save_reports(results, branch_name)


# Generate & View
@app.route("/generate")
def generate():
    branch = request.args.get("branch")
    latest = generate_report(branch)
    if isinstance(latest, dict) and latest.get("error"):
        return render_template("index.html", error="Invalid branch")

    return send_file(latest, mimetype="text/html")


# Generate & Download PDF
@app.route("/download")
def download():
    branch = request.args.get("branch")
    html_file = generate_report(branch)

    if isinstance(html_file, dict) and html_file.get("error"):
        return render_template("index.html", error="Invalid branch")

    if not html_file:
        return "Report generation failed."

    pdf_file = html_file.replace(".html", ".pdf")

    try:
        subprocess.run([
            "/usr/local/bin/wkhtmltopdf",
            "--enable-local-file-access",
            html_file,
            pdf_file
        ], check=True)
    except Exception as e:
        return f"PDF generation failed: {str(e)}"

    return send_file(pdf_file, as_attachment=True, mimetype="application/pdf")
