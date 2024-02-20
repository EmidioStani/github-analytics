import csv
import time
from pathlib import Path
from queue import Empty

import requests
import yaml
from tqdm import tqdm


def get_config():
    my_path = Path(__file__).resolve()  # resolve to get rid of any symlinks
    config_path = my_path.parent / 'config.yaml'
    with config_path.open() as config_file:
        config = yaml.load(config_file, Loader=yaml.FullLoader)
    return config


def get_all_issues(per_page, sort_by, base_url, issue_state, token, headers):
    listdict = []
    
    # Dictionary of params for the request
    params = {
        'page': 1,
        'per_page': per_page,
        'sort': sort_by,
        'state': issue_state
    }

    # add endpoint
    endpoint_url = '/issues'
    url = base_url + endpoint_url
    # print(url)
    response = requests.get(base_url + endpoint_url, headers=headers, params=params)
    # print(response.json())
    # go to the next page until the json response of the page is empty
    while response.json():
        listdict.append(response.json())
        params['page'] = params['page'] + 1
        # print(params['page'])
        response = requests.get(base_url + endpoint_url, headers=headers, params=params)
        # print(response.json())
    return listdict

def main():
    config = get_config()
    api = config['api']
    repo_list = config['repo']
    waitingtime = config['waitingtime']
    token = config['token']
    accept = config['mediatype']
    output = config['output']
    issues_per_page = config['issuesperpage']
    issues_state = config['issuesstate']
    issues_sort_by = config['issuessortby']
    csv_header = config['header']
    csv_delimiter = config['delimiter']
    csv_encoding = config['encoding']
    csv_total = config['totallabel']
    bar_repos_desc = config['bars']['repos']['description']
    bar_repos_colour = config['bars']['repos']['colour']
    bar_repos_leave= config['bars']['repos']['leave']
    bar_pages_desc = config['bars']['pages']['description']
    bar_pages_colour = config['bars']['pages']['colour']
    bar_pages_leave= config['bars']['pages']['leave']
    bar_issues_desc = config['bars']['issues']['description']
    bar_issues_colour = config['bars']['issues']['colour']
    bar_issues_leave= config['bars']['issues']['leave']
    bar_comments_desc = config['bars']['comments']['description']
    bar_comments_colour = config['bars']['comments']['colour']
    bar_comments_leave= config['bars']['comments']['leave']
    
    headers = {'Authorization': 'token ' + token, 'Accept' : accept}
    lines = []
    total_count_issue = 0
    total_count_issue_open = 0
    total_count_issue_closed = 0
    total_count_comments = 0
    total_users = []
    total_locations = []
    repo_bar = tqdm(repo_list, desc=bar_repos_desc, colour=bar_repos_colour, leave=bar_repos_leave)
    for repo in repo_bar:
        repo_bar.set_description(repo)
        repo_url = api + "/repos/" + repo
        time.sleep(waitingtime)
        repo_response = requests.get(repo_url, headers=headers)
        if (repo_response.status_code == 200):
            repo_json = repo_response.json()
            created_at = repo_json["created_at"]
            issuelist = get_all_issues(issues_per_page, issues_sort_by, repo_url, issues_state, token, headers)
            count_issue = 0
            count_issues_open = 0
            count_issues_closed = 0
            list_creator = []
            list_creator_location = []
            count_comment = 0
            list_comments_creator = []
            list_comments_creator_location = []
    
            for page in tqdm(issuelist, desc=bar_pages_desc, colour=bar_pages_colour, leave=bar_pages_leave):
                for issue in tqdm(page, desc=bar_issues_desc, colour=bar_issues_colour, leave=bar_issues_leave):
                    count_issue += 1
                    # print(issue["url"])
                    # print(issue["created_at"])
                    # print(issue["user"]["login"])
                    if(issue['state'] == "open"):
                        count_issues_open += 1
                    else:
                        count_issues_closed += 1
                    issue_creator = issue["user"]["login"]

                    if(issue_creator not in list_creator):
                        list_creator.append(issue_creator)
                        profile_url = api + "/users/" + issue_creator
                        time.sleep(waitingtime)
                        profile_response = requests.get(profile_url, headers=headers)
                        profile = profile_response.json()
                        if(profile["location"]):
                            # print(profile["location"])
                            list_creator_location.append(profile["location"])
                    # print(issue["comments"])
                    comments = issue["comments"]
                    count_comment += comments
                    if(comments > 0):
                        comments_url = issue["comments_url"]
                        time.sleep(waitingtime)
                        comments_response = requests.get(comments_url, headers=headers)
                        comments_list = comments_response.json()
                        # print(comments_list)
                        if (len(comments_list) > 0): # in case of pull requests
                            for i in tqdm(range(len((comments_list))), desc=bar_comments_desc, colour=bar_comments_colour, leave=bar_comments_leave):
                                # print(comments_list[i]["url"])
                                # print(comments_list[i]["user"]["login"])
                                #print(comments_list[i])
                                
                                comment_creator = comments_list[i]["user"]["login"]
                                if(comment_creator not in list_comments_creator):
                                    list_comments_creator.append(comment_creator)
                                    # print(comments_list[i]["created_at"])
                                    comment_profile_url = api + "/users/" + comment_creator
                                    time.sleep(waitingtime)
                                    comment_profile_response = requests.get(comment_profile_url, headers=headers)
                                    comment_profile = comment_profile_response.json()
                                    if(comment_profile["location"]):
                                        # print(comment_profile["location"])
                                        list_comments_creator_location.append(comment_profile["location"])
                    #if(issue["url"] == "https://api.github.com/repos/SEMICeu/Core-Person-Vocabulary/issues/13"):
                    #    print(issue)

            # print("Repo name: %s" % repo)
            # print("Number of issues: %s" % count_issue)
            # print("Number of comments: %s" % count_comment)
            list_creator = list(set(list_creator))
            # print("Number of unique creators: %s" % len(list_creator))
            list_creator_location = list(set(list_creator_location))
            # print("Creator locations: %s" % list_creator_location)
            list_comments_creator = list(set(list_comments_creator))
            # print("Number of unique commenters: %s" % len(list_comments_creator))
            list_comments_creator_location = list(set(list_comments_creator_location))
            # print("Commenters location: %s" % list_comments_creator_location)
            joined_list_creator =  list(set(list_creator + list_comments_creator))
            # print("Number of joined creators: %s" % len(joined_list_creator))
            joined_list_location =  list(set(list_creator_location + list_comments_creator_location))
            # print("Joined locations: %s" % joined_list_location)
            
            total_count_issue += count_issue
            total_count_issue_open += count_issues_open
            total_count_issue_closed += count_issues_closed
            total_count_comments += count_comment
            for user in joined_list_creator:
                total_users.append(user)
            for location in joined_list_location:
                total_locations.append(location)
            lines.append([repo, created_at, count_issue, count_issues_open, count_issues_closed, count_comment, len(joined_list_creator),  joined_list_creator, joined_list_location])
        else:
            print("error " + str(repo_response.status_code))
            print("message " + str(repo_response.content))
    total_users = list(set(total_users))
    total_locations = list(set(total_locations))
    lines.append([csv_total, '' , total_count_issue, total_count_issue_open, total_count_issue_closed, total_count_comments, len(total_users), total_users, total_locations])
    with open(output, "w", newline='', encoding=csv_encoding) as f:
        writer = csv.writer(f, delimiter=csv_delimiter)
        # csv_header = ['Repo name', 'created', '#issues', '#comments', '#users', "locations"]
        writer.writerow(csv_header) # write the header
        # write the actual content line by line
        for l in lines:
            writer.writerow(l)
    
if __name__ == "__main__":
    main()
