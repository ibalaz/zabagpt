import openai
import requests
from flask import Flask, render_template, request
import markdown


# Set the GitLab project URL and API token
api_token = 'glpat-S1cAUFXxzoK4qNgRsnag'
openai.api_key = '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'

app = Flask(__name__)
output_text = ''
project_id = ''


def extract_project_path(url):
    # Remove the protocol (http:// or https://) from the URL
    url = url.replace('http://', '').replace('https://', '')

    # Find the index of the first occurrence of '/'
    first_slash_index = url.index('/')

    # Find the index of the second occurrence of '/'
    second_slash_index = url.index('/', first_slash_index + 1)

    # Extract the project path
    project_path = url[second_slash_index + 1:]

    return project_path


def extract_added_lines(diff):
    # Split diff into lines
    diff_lines = diff.split('\n')

    # Keep only added lines
    added_lines = [line for line in diff_lines if line.startswith('+')]

    # Exclude lines that start with '+++'
    added_lines = [line for line in added_lines if not line.startswith('+++')]

    return added_lines


@app.route('/', methods=['GET', 'POST'])
def index():
    commit_links = []
    if request.method == 'POST':
        # Set the headers for the API request
        headers = {
            'Authorization': f'Bearer {api_token}'
        }
        global project_id
        project_url = request.form['input-text']
        print('Project url: ', project_url)
        project_path = extract_project_path(project_url)
        print('Project path: ', project_path)

        url = f'https://gitlab.com/api/v4/projects?search={project_path}'
        response_project_id = requests.get(url, headers=headers)

        if response_project_id.status_code == 200:
            projects = response_project_id.json()
            if len(projects) > 0:
                project_id = projects[0]['id']
            else:
                print('No project found with specified path.')
        else:
            print("Error getting project information")

        print('Project id: ', project_id)

        # Set the GitLab API endpoint for merge requests
        endpoint = f'https://gitlab.com/api/v4/projects/{project_id}/repository/commits'

        # Send a GET request to the API endpoint
        response = requests.get(endpoint, headers=headers)
        print('Response: ', response)

        # Check if the request was successful
        if response.status_code == 200:
            # Get the JSON data from the response
            commits = response.json()

            # Print the merge request information
            for com in commits:
                commit_links.append({'label': com["title"], 'value': com["id"]})
            print('Commits: ', commit_links)
        else:
            print('Failed to retrieve commits.')

    return render_template('index.html', commit_links=commit_links)


@app.route('/gpt_endpoint', methods=['GET', 'POST'])
def gpt_endpoint():
    value = request.args.get('value')
    print('Value: ', value)

    # Set the GitLab API endpoint for merge requests
    endpoint = f'https://gitlab.com/api/v4/projects/{project_id}/repository/commits/{value}/diff'
    print('Endpoint: ', endpoint)

    # Set the headers for the API request
    headers = {
        'Authorization': f'Bearer {api_token}'
    }

    # Send a GET request to the API endpoint
    response = requests.get(endpoint, headers=headers)
    print('Response: ', response.json())
    global output_text

    for commit in response.json():
        added_lines = extract_added_lines(commit['diff'])
        print("Added lines: ", added_lines)

        prompt = f"Optimize this added lines in commit {added_lines} and explain"
        response2 = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=2300,
            n=1,
            stop=None,
            temperature=0.7,
        )
        print('response2: ', response2.choices[0].text)
        output_text += 'Added lines: ' + str(added_lines) + '\n Optimization: ' + response2.choices[0].text + '\n'
        print('Output: ', output_text)

    return output_text


if __name__ == '__main__':
    app.run(debug=True)
