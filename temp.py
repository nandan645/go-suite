import requests
import os
from tqdm import tqdm # Optional, for a nice progress bar

def download_file(url, destination_folder):
    # Make the request to get the file
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))  # Get total file size

    # Open a file to write the downloaded content
    filename = os.path.join(destination_folder, url.split('/')[-1])
    with open(filename, 'wb') as file:
        # Create a progress bar if you have tqdm installed
        progress_bar = tqdm(total=total_size, unit='B', unit_scale=True, unit_divisor=1024, desc=filename)

        # Read the file in chunks
        for chunk in response.iter_content(chunk_size=8192):  # Adjust chunk_size as needed
            if chunk:  # Filter out keep-alive new chunks
                file.write(chunk)
                progress_bar.update(len(chunk))  # Update the progress bar

        progress_bar.close()

    print(f"Download completed: {filename}")

# Usage
url = 'https://archive.org/download/fluxus-official_202403/Fluxus%20Official.apk'
destination_folder = '.'
download_file(url, destination_folder)
