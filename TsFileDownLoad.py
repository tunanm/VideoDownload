import glob
import requests
import os
from urllib.parse import urljoin
import time
import os
import subprocess

def download_ts_files(m3u8_url, output_dir, max_retries=5, retry_delay=5):
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
        print(f"Video successfully saved as {output_file} at {os.path.dirname(input_dir)}")
    except subprocess.CalledProcessError as e:
        print(f"Error during ffmpeg execution: {e}")

    # Cleanup: remove the temporary file list
    os.remove(list_file_path)
def clear_ts_file(ts_dir):
    folder_path = ts_dir
    # Get all files in the folder
    files = glob.glob(os.path.join(folder_path, '*'))

    # Loop through and delete each file
    for file in files:
        try:
            os.remove(file)
            print(f"Deleted: {file}")
        except Exception as e:
            print(f"Failed to delete {file}. Reason: {e}")
def down_ts_file():
    m3u8_url = input("Enter m3u8 url: ").strip()  # Replace with the correct .m3u8 URL
    output_directory = "D:/Film/Down and merge ts file/VideoDownload/ts_files"  # Directory to save .ts files
    # default_output = int(input("Do you want to use default output or modify it? 1 for default 2 for modify"))
    # if default_output == 1:
    #     print(f"Default output is {output_directory}")
    # if default_output == 2:
    #     output_directory = input("Enter output directory for saving ts files:").strip()
    clear_ts_file(output_directory)
    download_ts_files(m3u8_url, output_directory)
def merge_video():
    input_directory = "D:/Film/Down and merge ts file/VideoDownload/ts_files"  # Directory where .ts files are stored
    # default_input = int(input("Do you want to use default output or modify it? 1 for default 2 for modify"))
    # if default_input == 1:
    #     print(f"Default input is {input_directory}")
    # if default_input == 2:
    #     input_directory = input("Enter output directory for saving ts files:").strip()
    output_name = input("Enter output files name: ").strip()
    output_video = f"{output_name}.mp4"  # Name of the final output video file
    merge_ts_files(input_directory, output_video)

while True:
    user_input = int(input("Enter a number \n"
                           "0 to exit, \n"
                           "1 to do get ts file from the url, \n"
                           "2 to do merge file to video, \n"
                           "3 to download video without modify ts files: "))
    if user_input == 0:
        print("Exiting the loop.")
        break
    if user_input == 1:
        # Download all part of video, retry if it fail Example usage:
        down_ts_file()
    if user_input == 2:
        # Merge the file into one video
        # Example usage:
        merge_video()
    if user_input == 3:
        down_ts_file()
        merge_video()

