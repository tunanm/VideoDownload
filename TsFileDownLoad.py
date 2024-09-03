import requests
import os
from urllib.parse import urljoin
import time
import os
import subprocess

def download_ts_files(m3u8_url, output_dir, max_retries=3, retry_delay=5):
    # Make the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # File to log failed downloads
    failed_log = os.path.join(output_dir, "failed_downloads.txt")

    # Download the .m3u8 playlist file
    response = requests.get(m3u8_url)
    response.raise_for_status()

    # Parse the .m3u8 file
    m3u8_content = response.text
    ts_urls = []

    base_url = m3u8_url.rsplit('/', 1)[0]

    for line in m3u8_content.splitlines():
        if line and not line.startswith("#"):
            ts_url = urljoin(base_url + '/', line)
            ts_urls.append(ts_url)

    # Function to attempt downloading a .ts file
    def attempt_download(ts_url, ts_filename, index):
        retries = 0
        while retries < max_retries:
            try:
                ts_response = requests.get(ts_url)
                ts_response.raise_for_status()

                with open(ts_filename, 'wb') as ts_file:
                    ts_file.write(ts_response.content)

                print(f"Successfully downloaded {ts_filename}")
                return True  # Success

            except requests.exceptions.RequestException as e:
                print(f"Failed to download {ts_url}: {e}")
                retries += 1
                if retries < max_retries:
                    print(f"Retrying ({retries}/{max_retries})...")
                    time.sleep(retry_delay)  # Wait before retrying

        # Log the failed URL and index if maximum retries reached
        with open(failed_log, 'a') as fail_file:
            fail_file.write(f"{ts_url}\nIndex: {index}\n")
        return False  # Failed after retries

    # Retry failed downloads
    for i, ts_url in enumerate(ts_urls):
        ts_filename = os.path.join(output_dir, f"segment_{i}.ts")
        if not attempt_download(ts_url, ts_filename, i):
            print(f"Failed to download {ts_url} after {max_retries} attempts.")

    print(f"Process completed.")


def merge_ts_files(input_dir, output_file):
    # Get list of all .ts files in the directory and sort them by index
    ts_files = [f for f in os.listdir(input_dir) if f.endswith(".ts")]

    if not ts_files:
        print("No .ts files found in the directory.")
        return

    # Sort files by their index extracted from the filename
    ts_files.sort(key=lambda f: int(f.split('_')[1].split('.')[0]))

    # Create a temporary text file to list all .ts files
    list_file_path = os.path.join(input_dir, "file_list.txt")
    with open(list_file_path, "w") as list_file:
        for ts_file in ts_files:
            list_file.write(f"file '{os.path.join(input_dir, ts_file).replace(os.sep, '/')}'\n")

    # Full path to ffmpeg executable
    ffmpeg_path = "C:/ffmpeg/ffmpeg.exe"

    # Run ffmpeg to merge the .ts files
    command = [
        ffmpeg_path,
        "-f", "concat",
        "-safe", "0",
        "-i", list_file_path,
        "-c", "copy",
        output_file
    ]

    print(f"Running command: {' '.join(command)}")
    try:
        subprocess.run(command, check=True)
        print(f"Video successfully saved as {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error during ffmpeg execution: {e}")

    # Cleanup: remove the temporary file list
    os.remove(list_file_path)


# # Download all part of video, retry if it fail
# # Example usage:
# m3u8_url = "https://vip.opstream11.com/20230106/41022_7d8dc19c/3000k/hls/mixed.m3u8"  # Replace with the correct .m3u8 URL
# output_directory = "D:/Film/Down and merge ts file/VideoDownload/ts_files"  # Directory to save .ts files
#
# download_ts_files(m3u8_url, output_directory)

# Merge the file into one video
# Example usage:
input_directory = "D:/Film/Down and merge ts file/VideoDownload/ts_files"  # Directory where .ts files are stored
output_video = "output.mp4"  # Name of the final output video file
merge_ts_files(input_directory, output_video)
