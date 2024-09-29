# Licensed under the WTFPL License

import os
import aiohttp
import asyncio
from urllib.parse import urlparse

url = 'https://storage.googleapis.com/panels-api/data/20240916/media-1a-i-p~s'

# Asynchronous delay function
async def delay(ms):
    await asyncio.sleep(ms / 1000)

# Download image asynchronously with retry support
async def download_image(session, image_url, file_path, retries=3):
    try:
        for attempt in range(retries):
            try:
                async with session.get(image_url) as response:
                    if response.status == 200:
                        content = await response.read()
                        with open(file_path, 'wb') as f:
                            f.write(content)
                        return  # Success, exit the function
                    else:
                        raise Exception(f"Failed to download image: {response.status}")
            except Exception as e:
                if attempt < retries - 1:
                    print(f"⚠️ Error downloading image (Attempt {attempt+1}/{retries}): {e}. Retrying...")
                    await delay(1000)  # Wait 1 second before retrying
                else:
                    print(f"⛔ Final error downloading image after {retries} attempts: {e}")
    except Exception as e:
        print(f"Error downloading image: {str(e)}")

# Main function to download all images
async def main():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"⛔ Failed to fetch JSON file: {response.status}")
                
                json_data = await response.json()
                data = json_data.get('data')
                
                if not data:
                    raise Exception('⛔ JSON does not have a "data" property at its root.')

                # Create a 'downloads' directory if it doesn't exist
                download_dir = os.path.join(os.getcwd(), 'downloads')
                if not os.path.exists(download_dir):
                    os.makedirs(download_dir)
                    print(f"📁 Created directory: {download_dir}")

                # Iterate over the JSON data and download images
                file_index = 1
                for key, subproperty in data.items():
                    if subproperty and subproperty.get('dhd'):
                        image_url = subproperty['dhd']
                        print(f"🔍 Found image URL!")
                        parsed_url = urlparse(image_url)
                        ext = os.path.splitext(parsed_url.path)[-1] or '.jpg'
                        filename = f"{file_index}{ext}"
                        file_path = os.path.join(download_dir, filename)

                        # Download the image
                        await download_image(session, image_url, file_path)
                        print(f"🖼️ Saved image to {file_path}")

                        file_index += 1
                        await delay(250)  # Delay between image downloads

    except Exception as e:
        print(f"Error: {str(e)}")

# ASCII art for some fun intro
def ascii_art():
    print("""
 /$$      /$$ /$$   /$$ /$$$$$$$   /$$$$$$  /$$$$$$$
| $$$    /$$$| $$  /$$/| $$__  $$ /$$__  $$| $$__  $$
| $$$$  /$$$$| $$ /$$/ | $$  \\ $$| $$  \\__/| $$  \\ $$
| $$ $$/$$ $$| $$$$$/  | $$$$$$$ |  $$$$$$ | $$  | $$
| $$  $$$| $$| $$  $$  | $$__  $$ \\____  $$| $$  | $$
| $$\\  $ | $$| $$\\  $$ | $$  \\ $$ /$$  \\ $$| $$  | $$
| $$ \\/  | $$| $$ \\  $$| $$$$$$$/|  $$$$$$/| $$$$$$$/
|__/     |__/|__/  \\__/|_______/  \\______/ |_______/""")
    print("")
    print("🤑 Starting downloads from your favorite sellout grifter's wallpaper app...")

# Safe handling for event loop management
if __name__ == "__main__":
    ascii_art()
    
    # Check if an event loop is already running (for environments like Jupyter)
    try:
        loop = asyncio.get_running_loop()
        print("⚠️ Event loop already running, using alternative method.")
        # Directly schedule the task using the existing event loop
        task = loop.create_task(main())  # Create the task
        loop.run_until_complete(task)    # Only use this if you're outside an async function
    except RuntimeError:
        # If no loop is running, use asyncio.run()
        print("No event loop running, starting a new one.")
        asyncio.run(main())
