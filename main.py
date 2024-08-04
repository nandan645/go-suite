import platform
import requests
import os
import zipfile
import io
from tqdm import tqdm
import stat

def get_download_url():
    system = platform.system().lower()
    architecture = platform.machine().lower()
    
    base_url = "https://downloads.rclone.org/"
    
    urls = {
        'linux': {
            'x86_64': 'rclone-current-linux-amd64.zip',
            'i386': 'rclone-current-linux-386.zip',
            'armv5': 'rclone-current-linux-arm.zip',
            'armv6': 'rclone-current-linux-arm-v6.zip',
            'armv7': 'rclone-current-linux-arm-v7.zip',
            'aarch64': 'rclone-current-linux-arm64.zip',
            'mips': 'rclone-current-linux-mips.zip',
            'mipsle': 'rclone-current-linux-mipsle.zip'
        },
        'windows': {
            'amd64': 'rclone-current-windows-amd64.zip',
            'x86': 'rclone-current-windows-386.zip',
            'arm64': 'rclone-current-windows-arm64.zip'
        },
        'darwin': {
            'x86_64': 'rclone-current-osx-amd64.zip',
            'arm64': 'rclone-current-osx-arm64.zip'
        },
        'freebsd': {
            'x86_64': 'rclone-current-freebsd-amd64.zip',
            'i386': 'rclone-current-freebsd-386.zip',
            'arm': 'rclone-current-freebsd-arm.zip',
            'armv6': 'rclone-current-freebsd-arm-v6.zip',
            'armv7': 'rclone-current-freebsd-arm-v7.zip'
        },
        'netbsd': {
            'x86_64': 'rclone-current-netbsd-amd64.zip',
            'i386': 'rclone-current-netbsd-386.zip',
            'arm': 'rclone-current-netbsd-arm.zip',
            'armv6': 'rclone-current-netbsd-arm-v6.zip',
            'armv7': 'rclone-current-netbsd-arm-v7.zip'
        },
        'openbsd': {
            'x86_64': 'rclone-current-openbsd-amd64.zip',
            'i386': 'rclone-current-openbsd-386.zip'
        },
        'plan9': {
            'amd64': 'rclone-current-plan9-amd64.zip',
            'x86': 'rclone-current-plan9-386.zip'
        },
        'solaris': {
            'amd64': 'rclone-current-solaris-amd64.zip'
        }
    }
    
    try:
        download_url = base_url + urls[system][architecture]
    except KeyError:
        raise Exception(f"No binary available for {system} on {architecture}")
    
    return download_url

def find_binary_in_zip(zip_ref, binary_name):
    for file_info in zip_ref.infolist():
        if file_info.filename.endswith(binary_name):
            return file_info.filename
    return None

def download_and_extract(url, dest_folder):
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)
    
    local_filename = url.split('/')[-1]
    binary_name = "rclone.exe" if platform.system().lower() == "windows" else "rclone"
    local_path = os.path.join(dest_folder, binary_name)

    # Streaming the request
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        total_size = int(r.headers.get('content-length', 0))
        block_size = 1024
        progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True)
        zip_buffer = io.BytesIO()
        
        for data in r.iter_content(block_size):
            progress_bar.update(len(data))
            zip_buffer.write(data)
        
        progress_bar.close()
        
        zip_buffer.seek(0)  # Rewind the buffer to the beginning

        with zipfile.ZipFile(zip_buffer, 'r') as zip_ref:
            binary_file_name = find_binary_in_zip(zip_ref, binary_name)
            if binary_file_name is None:
                raise Exception(f"No binary named '{binary_name}' found in the archive")
            with zip_ref.open(binary_file_name) as binary_file:
                with open(local_path, 'wb') as f:
                    f.write(binary_file.read())
    
    # Make the binary executable (non-Windows systems)
    if platform.system().lower() != "windows":
        os.chmod(local_path, os.stat(local_path).st_mode | stat.S_IEXEC)
    
    return local_path

def main():
    try:
        download_url = get_download_url()
        print(f"Downloading from: {download_url}")
        extracted_file = download_and_extract(download_url, './binaries')
        print(f"Extracted binary to: {extracted_file}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
