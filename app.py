import os
import requests
from requests.auth import HTTPBasicAuth
import json

from env import API, BASE_URL, EMAIL, SPACEKEY

confluence_url = BASE_URL
username = EMAIL
api_token = API
space_key = SPACEKEY
page_title = "Test"

new_data = {
    "Column_1": os.getenv("Column_1", "Data 1"),
    "Column_2": os.getenv("Column_2", "Data 2"),
    "Column_3": os.getenv("Column_3", "Data 3"),
}

def confluenceapi(new_data):
    # Step 1: Check if the page already exists with expand parameters
    search_url = f"{confluence_url}?spaceKey={space_key}&title={page_title}&expand=version,body.storage"
    search_response = requests.get(
        search_url,
        auth=HTTPBasicAuth(username, api_token)
    )

    if search_response.status_code == 200:
        results = search_response.json().get("results")
        if results:
            # Page exists, retrieve page ID, current version, and content
            page_id = results[0].get("id")
            page_version = results[0].get("version", {}).get("number")
            page_content = results[0].get("body", {}).get("storage", {}).get("value")

            if page_version is None or page_content is None:
                print("Error: Could not retrieve page version or content.")
                return

            new_row_html = f"""
            <tr>
                <td>{new_data['Column_1']}</td>
                <td>{new_data['Column_2']}</td>
                <td>{new_data['Column_3']}</td>
            </tr>
            """

            updated_content = page_content.replace("</tbody>", f"{new_row_html}</tbody>")

            update_data = {
                "version": {
                    "number": page_version + 1
                },
                "title": page_title,
                "type": "page",
                "body": {
                    "storage": {
                        "value": updated_content,
                        "representation": "storage"
                    }
                }
            }

            update_response = requests.put(
                f"{confluence_url}/{page_id}",
                data=json.dumps(update_data),
                auth=HTTPBasicAuth(username, api_token),
                headers={
                    "Content-Type": "application/json"
                }
            )

            if update_response.status_code == 200:
                print("Page updated successfully!")
                print("Page URL:", update_response.json().get("_links").get("webui"))
            else:
                print("Failed to update page:", update_response.status_code)
                print(update_response.json())
        else:
            print("Page does not exist. Creating a new page...")

            new_page_content = f"""
            <table>
                <thead>
                    <tr>
                        <th>Column 1</th>
                        <th>Column 2</th>
                        <th>Column 3</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>{new_data['Column_1']}</td>
                        <td>{new_data['Column_2']}</td>
                        <td>{new_data['Column_3']}</td>
                    </tr>
                </tbody>
            </table>
            """

            create_data = {
                "type": "page",
                "title": page_title,
                "space": {
                    "key": space_key
                },
                "body": {
                    "storage": {
                        "value": new_page_content,
                        "representation": "storage"
                    }
                }
            }

            create_response = requests.post(
                confluence_url,
                data=json.dumps(create_data),
                auth=HTTPBasicAuth(username, api_token),
                headers={
                    "Content-Type": "application/json"
                }
            )

            if create_response.status_code == 200:
                print("Page created successfully!")
                print("Page URL:", create_response.json().get("_links").get("webui"))
            else:
                print("Failed to create page:", create_response.status_code)
                print(create_response.json())
    else:
        print("Failed to search for page:", search_response.status_code)
        print("Response content:", search_response.json())

confluenceapi(new_data)
