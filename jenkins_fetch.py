import re
from config import JENKINS_URL, USERNAME, PASSWORD, REPOS
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta

from build_data import load_build_data, get_build_number

auth = HTTPBasicAuth(USERNAME, PASSWORD)


def get_build_details(ring, build_number):
    url = f"{JENKINS_URL}/job/{ring}/{build_number}/api/json"
    res = requests.get(url, auth=auth)
    res.raise_for_status()
    return res.json()


def get_latest_build(ring):
    url = f"{JENKINS_URL}/job/{ring}/lastBuild/api/json"
    res = requests.get(url, auth=auth)
    res.raise_for_status()
    return res.json()


def fetch_build_data(branch_name=None):
    results = []
    build_cache = load_build_data()

    branch_found_anywhere = False

    for repo_name, rings in REPOS.items():
        for ring in rings:
            build_duration = None

            try:
                build = None
                if branch_name:
                    build_no = get_build_number(build_cache, ring, branch_name)

                    if not build_no:
                        print(f"[{ring}] --> Branch not in cache")

                        results.append({
                            "repo": repo_name,
                            "ring": ring,
                            "status": "NO_DATA",
                            "build": "-",
                            "execution_date": "-",
                            "link": "#",
                            "total_tests": 0,
                            "failed_tests": 0,
                            "passed_cases": 0,
                            "build_duration": None,
                            "consolidated_report_link": "#"
                        })
                        continue
                    
                    branch_found_anywhere = True

                    print(f"[{ring}] : #{build_no}")
                    build = get_build_details(ring, build_no)

                else:
                    build = get_latest_build(ring)

                building = build.get("building", False)
                build_status = build.get("result")
                build_number = build.get("number")

                execution_date = datetime.fromtimestamp(
                    build.get("timestamp") / 1000
                ).strftime("%Y-%m-%d")

                build_url = build.get("url", "#")

                duration = build.get("duration", 0)
                build_duration = timedelta(seconds=duration / 1000)

                test_action = next(
                    (ta for ta in build.get("actions", [])
                     if ta.get("_class") == "hudson.tasks.junit.TestResultAction"),
                    None
                )

                if test_action:
                    total_cases = test_action.get("totalCount", 0)
                    failed_cases = test_action.get("failCount", 0)
                    passed_cases = total_cases - failed_cases
                else:
                    total_cases = failed_cases = passed_cases = 0

                status = "RUNNING" if building else (build_status or "UNKNOWN")

                consolidated_report_link = "#"

                if build_status in ("SUCCESS", "UNSTABLE"):
                    console_res = requests.get(f"{build_url}console", auth=auth)
                    match = re.search(
                        r'(http[s]?://\d+\.\d+\.\d+\.\d+:\d+/\d+_Consolidated_Test_Report\.html)',
                        console_res.text
                    )
                    if match:
                        consolidated_report_link = match.group(1)

                results.append({
                    "repo": repo_name,
                    "ring": ring,
                    "status": status,
                    "build": build_number,
                    "execution_date": execution_date,
                    "link": build_url,
                    "total_tests": total_cases,
                    "failed_tests": failed_cases,
                    "passed_cases": passed_cases,
                    "build_duration": build_duration,
                    "consolidated_report_link": consolidated_report_link
                })

            except Exception as e:
                print(f"[{ring}] ERROR: {e}")

                results.append({
                    "repo": repo_name,
                    "ring": ring,
                    "status": "ERROR",
                    "build": "-",
                    "execution_date": "-",
                    "link": "#",
                    "total_tests": 0,
                    "failed_tests": 0,
                    "passed_cases": 0,
                    "build_duration": build_duration,
                    "consolidated_report_link": "#"
                })

    if branch_name and not branch_found_anywhere:
        return {"error": "Invalid branch"}

    return results