# github-analytics

This python script retrieves number of issues, comments, unique users (creators and commenters) and user locations (where explictly indicated), given the repositories specified in the config.yaml file and store it in an output file.

In order to execute the script, you need to get the personal access token in GitHub and put it in the config.yaml file

## Requirements

The script has been executed on Python 3.9.8, dependencies can be installed via the requirements.txt file

## How to execute the script

Provide the information needed in the config.yaml file like repositories and token and just run:

python github-analytics.py

The script will contact GitHub REST API in cascade, getting for each repostitory the list of issues (paginated), then for each issue get the creator and the number of comments, and for each creator and commenters retrieve, where possible, their locations.

During the execution, the script will use progress bar to show that the execution is on going, see ![Alt text](/screenshot.jpg?raw=true "screenshot")

## TO DO:

1) Use the link in the response header to progress with the issues pages, instead of using a counter:
https://stackoverflow.com/questions/33878019/how-to-get-data-from-all-pages-in-github-api-with-python/33878531#33878531
https://docs.github.com/en/rest/overview/resources-in-the-rest-api#link-header

2) look at multi processing to speed-up the script