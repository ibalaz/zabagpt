from flask import Flask, render_template, request
import requests
import gitlab
import openai

# Set the GitLab project URL and API token
api_token = 'glpat-S1cAUFXxzoK4qNgRsnag'
openai.api_key = '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'

app = Flask(__name__)
output_text = ''
project_id = ''


@app.route('/', methods=['GET', 'POST'])
def index():
    merge_links = []
    if request.method == 'POST':
        global project_id
        project_id = request.form['input-text']
        print('Project id: ', project_id)

        # Set the GitLab API endpoint for merge requests
        endpoint = f'https://gitlab.com/api/v4/projects/{project_id}/merge_requests?scope=all'

        # Set the headers for the API request
        headers = {
            'Authorization': f'Bearer {api_token}'
        }

        # Send a GET request to the API endpoint
        response = requests.get(endpoint, headers=headers)
        print('Response: ', response)

        # Check if the request was successful
        if response.status_code == 200:
            # Get the JSON data from the response
            merge_requests = response.json()

            # Print the merge request information
            for mr in merge_requests:
                merge_links.append({'label': mr["title"], 'value': mr["iid"]})
            print('Merge links: ', merge_links)
        else:
            print('Failed to retrieve merge requests.')

    return render_template('index.html', merge_links=merge_links)


@app.route('/gpt_endpoint', methods=['GET', 'POST'])
def gpt_endpoint():
    value = request.args.get('value')
    print('Value: ', value)

    # Set the GitLab API endpoint for merge requests
    endpoint = f'https://gitlab.com/api/v4/projects/{project_id}/merge_requests/{value}'
    print('Endpoint: ', endpoint)

    # Set the headers for the API request
    headers = {
        'Authorization': f'Bearer {api_token}'
    }

    # Send a GET request to the API endpoint
    response = requests.get(endpoint, headers=headers)
    print('Response: ', response.json())
    head_sha = response.json()["diff_refs"]["head_sha"]
    base_sha = response.json()["diff_refs"]["base_sha"]
    print('Head_sha: ', head_sha)
    print('Base_sha: ', base_sha)

    gl = gitlab.Gitlab('https://gitlab.com', private_token=api_token)
    diff = gl.projects.get(project_id).repository_compare(base_sha, head_sha)['diffs']

    print("diff: ", diff)
    global output_text

    prompt = f"Create changelog file for this diff {diff}"
    response2 = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=1,
        n=1,
        stop=None,
        temperature=0.5,
    )
    output_text += response2.choices[0].text

    return render_template('index.html', output_text=output_text)


if __name__ == '__main__':
    app.run(debug=True)
