# This is a sample Python script.
import os
import sys
from datetime import date
import yaml

import requests
import pandas as pd
from bs4 import BeautifulSoup
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

CONFIG_FILE = "config.yml"
PROPOSAL_LINK_PREFIX = "https://api.app.astrodao.com/api/v1/proposals/"
DAO_LINK_PREFIX = "https://api.app.astrodao.com/api/v1/daos/"
DAOs = [
    "news.sputnik-dao.near",
    "nearweek-news-contribution.sputnik-dao.near"
]
# DAO = "news.sputnik-dao.near"
DAO = "nearweek-news-contribution.sputnik-dao.near"
PROPOSAL_PREFIX = "https://app.astrodao.com/dao/news.sputnik-dao.near/proposals/" + DAO
FOLDER_RESULT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "result")
today = date.today()
today_str1 = today.strftime("%d/%m/%Y")
today_str2 = today.strftime("%d_%m_%Y")

def read_config(file, key):
    file = open('config.yml', 'r')
    config = yaml.safe_load(file)
    if key in config.keys():
        return config[key]
    else:
        return None

def write_config(file, key, value):
    config = {
        key: value
    }
    file = open('config.yml', 'w')
    yaml.dump(config, file)

def get_dao(dao):
    link_dao = DAO_LINK_PREFIX + dao
    # res = requests.get(link_proposal, allow_redirects=False, verify=False)
    res = requests.get(link_dao, allow_redirects=False)
    if res.status_code == 400:
        return None
    return res.json()

def get_proposal(id):
    proposal_id = "{}-{}".format(DAO, id)
    link_proposal = PROPOSAL_LINK_PREFIX + proposal_id
    # res = requests.get(link_proposal, allow_redirects=False, verify=False)
    res = requests.get(link_proposal, allow_redirects=False)
    if res.status_code == 400:
        return None
    proposal = res.json()
    proposer = proposal["proposer"]
    content = proposal["description"].split("$$$$")
    description, link = content[0], content[1]
    description = description.replace("\n", "").replace("\b", "").encode("ascii", "ignore").decode().strip()
    return {
        "id": id,
        "link_proposal": link_proposal,
        "proposer": proposer,
        "description": description,
        "link": link,
        "created_at": proposal["createdAt"]
    }


def main(args):
    start_id = read_config(CONFIG_FILE, "last_proposal")
    if start_id is not None:
        start_id += 1
    if len(args) > 0:
        start_id = int(args[0])
    if start_id == None:
        print("Missing config or start proposal")
        return
    id = start_id
    dao = get_dao(DAO)
    last_proposal_id = dao["lastProposalId"]
    write_config(CONFIG_FILE, "last_proposal", last_proposal_id)
    proposals = []
    while True:
        proposal = get_proposal(id)
        if proposal is None and id > last_proposal_id:
            break
        if proposal is not None:
            proposals.append(proposal)
        id += 1
    data = []
    for proposal in proposals:
        data.append({
            # "date": today_str1,
            "date": proposal["created_at"],
            "tags": "",
            "title": proposal["description"],
            "link": proposal["link"],
            "link_proposal": "{}-{}".format(PROPOSAL_PREFIX, proposal["id"]),
            "source": "x",
            "sputnik": proposal["id"],
            "collector": proposal["proposer"]
        })
    df = pd.DataFrame(data)

    print(df)
    if not os.path.isdir(FOLDER_RESULT):
        os.mkdir(FOLDER_RESULT)
    output_filename = "{}.xlsx".format(today_str2)
    output = os.path.join(FOLDER_RESULT, output_filename)
    df.to_excel(output, index=False)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main(sys.argv[1:])
     #main([4517])
    # write_config("config.yml", "abc", 1000)
    # a = read_config("config.yml", "abcd")
    # print(a)
    # a = get_proposal(5299)
    # print(a)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
