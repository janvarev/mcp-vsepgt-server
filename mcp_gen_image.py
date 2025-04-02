from fastmcp import FastMCP
import requests
import base64
import os
import time
from pathlib import Path
import os

mcp = FastMCP("VseGPT image gen")


@mcp.tool()
def generate_image(prompt_eng: str) -> str:
    """
    Using prompt, generate image via VseGPT api call. Prompt must be in English language!!
    :return URL path to file in format like "C:/Test/image_file.png" (URL local path). If user require markdown, local path can be rendered like this: ![image](/C:/Test/1c_integ1.png)
    """
    # Get API key from environment variable
    api_key = os.environ.get("VSEGPT_API_KEY")
    if not api_key:
        raise ValueError("VSEGPT_API_KEY environment variable is not set")

    img_model_id = os.environ.get("IMG_MODEL_ID", "img-dummy/image")
    img_size = os.environ.get("IMG_SIZE", "1024x1024")

    # Create API session
    session = requests.Session()

    # Set up authorization headers
    session.headers.update({
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    })

    # VseGPT API endpoint for image generation
    url = "https://api.vsegpt.ru/v1/images/generations"

    # Prepare payload as specified
    payload = {
        "model": img_model_id,
        "prompt": prompt_eng,
        "size": img_size,
        "n": 1,
        "response_format": "b64_json",
    }
    # Update headers with title
    session.headers.update({"X-Title": f"MCP image gen standard {img_size}"})
    # Make the API request
    response = session.post(url, json=payload)
    # Check if request was successful
    if response.status_code == 200:
        # Get base64 string from response
        response_json = response.json()
        b64_data = response_json["data"][0]["b64_json"]

        # Get the directory of the current script
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Create tmp_images directory in the same folder as the script
        tmp_dir = Path(script_dir) / "tmp_images"
        tmp_dir.mkdir(exist_ok=True)

        # Generate filename with timestamp
        timestamp = int(time.time())
        filename = f"{timestamp}.jpg"
        filepath = tmp_dir / filename

        # Decode base64 and save to file
        with open(filepath, "wb") as img_file:
            img_file.write(base64.b64decode(b64_data))

        # Return absolute path to the file
        return str(filepath.absolute())
    else:
        raise ValueError(f"{response.status_code}: {response.text}")
