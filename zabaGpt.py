from flask import Flask, render_template, request
import requests

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        output_text = ''
        input_text = request.form['input-text']
        print('URL: ', input_text)

        # Set the GitLab project URL and API token
        api_token = 'glpat-Rq7Rxqx1mJACcmuVhv3o'

        # Set the GitLab API endpoint for merge requests
        endpoint = f'{input_text}/merge_requests'

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
                output_text += f'Merge Request {mr["iid"]}: {mr["title"]} \n'
        else:
            print('Failed to retrieve merge requests.')
    else:
        output_text = ''
    return render_template('index.html', output_text=output_text)


if __name__ == '__main__':
    app.run(debug=True)
