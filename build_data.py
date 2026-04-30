import json

BUILD_FILE = "/jenkins_ring_support/jenkins_reports/jenkins_build_data.json"


def load_build_data():
    try:
        with open(BUILD_FILE, "r") as f:
            return json.load(f)
    except Exception:
        print("Build not found or invalid")
        return {}


def get_build_number(data, ring, branch_name):
    ring_data = data.get(ring, {})

    for branch, build_no in ring_data.items():
        if branch_name.lower() in branch.lower():
            return build_no

    return None