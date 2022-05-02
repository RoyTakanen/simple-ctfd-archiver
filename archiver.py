import requests
import sys
import os
import wget

# ctfd archiver

def check_if_auth_required(domain):
    text = requests.get("https://" + domain + "/api/v1/challenges/1").text
    if "You don't have the permission to access the requested resource. It is either read-protected or not readable by the server." in text:
        return True
    return False

def get_task_list(domain, session):
    return session.get("https://" + domain + "/api/v1/challenges").json()

def get_challenge_data(domain, session, challenge_id):
    return session.get("https://" + domain + "/api/v1/challenges/" + str(challenge_id)).json()

def get_solves(domain, session, challenge_id):
    return session.get("https://" + domain + "/api/v1/challenges/" + str(challenge_id) + "/solves").json()

def get_hint(domain, session, hint_id):
    return session.get("https://" + domain + "/api/v1/hints/" + str(hint_id)).json()

def download_file(link, dir):
    return wget.download(link, out=dir)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        domain = input("Enter domain: ")
    else:
        domain = sys.argv[1]

    if check_if_auth_required(domain):
        print("Auth required")
        if len(sys.argv) < 3:
            cookie = input("Enter session cookie: ")
        else:
            cookie = sys.argv[2]

        session = requests.Session()
        session.cookies.set("session",cookie,domain=domain)

        print("Getting task list...")

        print("Tasks:")
        print()

        for task in get_task_list(domain, session)["data"]:
            print("[*] " + task["name"])

        print()

        print("Starting save operation...")
        print()

        for task in get_task_list(domain, session)["data"]:
            print("[*] Getting challenge data for " + task["name"], end="\n\n")

            # TODO: archive account data

            os.makedirs("out/" + task["name"], exist_ok=True)

            challenge_data = get_challenge_data(domain, session, task["id"])

            # write description to file
            with open("out/" + task["name"] + "/README.md", "w") as f:
                f.write("# " + task["name"] + "\n\n")

                # tags
                if len(challenge_data["data"]["tags"]) > 0:
                    f.write("**Tags**\n\n")
                    for tag in challenge_data["data"]["tags"]:
                        f.write("* " + tag + "\n")

                # files
                if len(challenge_data["data"]["files"]) > 0:
                    f.write("**Files**\n\n")
                    for file in challenge_data["data"]["files"]:
                        os.makedirs("out/" + task["name"] + "/files", exist_ok=True)
                        name = download_file("https://" + domain + file, "out/" + task["name"] + "/files/")
                        f.write("* [" + name + "](files/" + name + ")\n")

                # challenge link
                if "connection_info" in challenge_data["data"] and challenge_data["data"]["connection_info"] != None:
                    f.write("\n**Challenge link:**\n\n")
                    f.write("[" + challenge_data["data"]["connection_info"] + "](" + challenge_data["data"]["connection_info"] + ")\n\n")

                # description
                f.write("\n**Description**\n\n")
                f.write(challenge_data["data"]["description"])

                # create hint list
                f.write("\n## Hints\n\n")
                for hint in challenge_data["data"]["hints"]:
                    f.write("* " + get_hint(domain, session, hint["id"])["data"]["content"])

                # create table of solvers
                f.write("\n\n## Solvers\n\n")
                f.write("| Username | Date |\n")
                f.write("|----------|--------|\n")
                for solver in get_solves(domain, session, task["id"])["data"]:                    
                    f.write("| " + solver["name"] + " | " + solver["date"]  + " |\n")
