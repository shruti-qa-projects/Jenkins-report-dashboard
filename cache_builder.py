import json
import requests
from requests.auth import HTTPBasicAuth
from config import JENKINS_URL, USERNAME, PASSWORD, REPOS

auth = HTTPBasicAuth(USERNAME, PASSWORD)

CACHE_FILE = "jenkins_build_data.json"


def load_cache():
    try:
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    except Exception:
        print("No existing cache, starting fresh")
        return {}


def save_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=4)
    print(f"\n Cache updated at {CACHE_FILE}")


def update_cache():
    cache = load_cache()

    for repo, rings in REPOS.items():
        for ring in rings:
            print(f"\nProcessing {ring}...")

            if ring not in cache:
                cache[ring] = {}

            url = f"{JENKINS_URL}/job/{ring}/api/json?tree=builds[number]{{,10}}"
            res = requests.get(url, auth=auth)
            res.raise_for_status()

            builds = res.json().get("builds", [])

            for b in builds:
                build_no = b["number"]

                build_api = f"{JENKINS_URL}/job/{ring}/{build_no}/api/json"
                build_res = requests.get(build_api, auth=auth)

                if build_res.status_code != 200:
                    print(f" X Failed build #{build_no}")
                    continue

                build_data = build_res.json()

                found_branch = False

                for action in build_data.get("actions", []):
                    if not action:
                        continue

                    if action.get("_class") == "hudson.plugins.git.util.BuildData":
                        branch_map = action.get("buildsByBranchName", {})

                        for branch, data in branch_map.items():
                            branch_name = branch.split("/")[-1]

                            if data.get("buildNumber") != build_no:
                                print(f" --> Skipping {branch_name}: {build_no}")
                                continue

                            print(f" >> {branch_name} → #{build_no}")

                            existing = cache[ring].get(branch_name)

                            if not existing or build_no > existing:
                                cache[ring][branch_name] = build_no

                            found_branch = True

                if not found_branch:
                    print(f" <> No branch found for build #{build_no}")

    save_cache(cache)


if __name__ == "__main__":
    update_cache()
