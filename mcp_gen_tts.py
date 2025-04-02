from fastmcp import FastMCP
import requests
import base64
import os
import time
from pathlib import Path
import os
import subprocess

mcp = FastMCP("VseGPT tts gen")


@mcp.tool()
def generate_speech(text: str, voice_id: str, instructions: str) -> str:
    """
Generate speech via provided text.
Params:
- text - text to speech
- voice_id - one of voices [alloy, ash, ballad, coral, echo, fable, onyx, nova, sage, shimmer, verse]
- instructions - instructions of HOW generate speech. Examples of instructions:

(Instructions For Bedtime Story)
Affect: A gentle, curious narrator, guiding a magical, child-friendly adventure through a fairy tale world.

Tone: Magical, warm, and inviting, creating a sense of wonder and excitement for young listeners.

Pacing: Steady and measured, with slight pauses to emphasize magical moments and maintain the storytelling flow.

Emotion: Wonder, curiosity, and a sense of adventure, with a lighthearted and positive vibe throughout.

Pronunciation: Clear and precise, with an emphasis on storytelling, ensuring the words are easy to follow and enchanting to listen to.
-
(Instructions For Dramatic)
Voice Affect: Low, hushed, and suspenseful; convey tension and intrigue.

Tone: Deeply serious and mysterious, maintaining an undercurrent of unease throughout.

Pacing: Slow, deliberate, pausing slightly after suspenseful moments to heighten drama.

Emotion: Restrained yet intense—voice should subtly tremble or tighten at key suspenseful points.

Emphasis: Highlight sensory descriptions ("footsteps echoed," "heart hammering," "shadows melting into darkness") to amplify atmosphere.

Pronunciation: Slightly elongated vowels and softened consonants for an eerie, haunting effect.

Pauses: Insert meaningful pauses after phrases like "only shadows melting into darkness," and especially before the final line, to enhance suspense dramatically.
-
(Instructions For Mad Scientist character style)
Delivery: Exaggerated and theatrical, with dramatic pauses, sudden outbursts, and gleeful cackling.

Voice: High-energy, eccentric, and slightly unhinged, with a manic enthusiasm that rises and falls unpredictably.

Tone: Excited, chaotic, and grandiose, as if reveling in the brilliance of a mad experiment.

Pronunciation: Sharp and expressive, with elongated vowels, sudden inflections, and an emphasis on big words to sound more diabolical.
-
(Instructions For Emo teenager character style)
Tone: Sarcastic, disinterested, and melancholic, with a hint of passive-aggressiveness.

Emotion: Apathy mixed with reluctant engagement.

Delivery: Monotone with occasional sighs, drawn-out words, and subtle disdain, evoking a classic emo teenager attitude.
-
Tool returns URL path to file in format like "C:/Test/speech.mp3" (URL local path).
    """
    # Get API key from environment variable
    api_key = os.environ.get("VSEGPT_API_KEY")
    if not api_key:
        raise ValueError("VSEGPT_API_KEY environment variable is not set")

    # Create API session
    session = requests.Session()

    # Set up authorization headers
    session.headers.update({
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    })

    # VseGPT API endpoint for image generation
    url = "https://api.vsegpt.ru/v1/audio/speech"

    # Prepare payload as specified
    payload = {
        "model": "tts-openai/gpt-4o-mini-tts",
        "input": text,
        "voice": voice_id,
        "instructions": instructions
    }
    # Update headers with title
    session.headers.update({"X-Title": f"MCP TTS"})
    # Make the API request
    response = session.post(url, json=payload, timeout=600)
    # Check if request was successful
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Create tmp_images directory in the same folder as the script
    tmp_dir = Path(script_dir) / "tmp_images"
    tmp_dir.mkdir(exist_ok=True)

    if response.status_code == 200:


        # Generate filename with timestamp
        timestamp = int(time.time())
        filename = f"{timestamp}.mp3"
        filepath = tmp_dir / filename

        # Save to file MP3
        with open(filepath, 'wb') as f:
            f.write(response.content)

        # Предполагаемый путь к MPC-HC
        mpc_hc_path = r"C:\Program Files\MPC-HC\mpc-hc64.exe"

        # Получение абсолютного пути к файлу
        absolute_filepath = str(filepath.absolute())

        # Return absolute path to the file
        # Запуск воспроизведения в фоне с помощью MPC-HC
        try:
            # /play - начать воспроизведение сразу
            # /close - закрыть текущий экземпляр перед открытием нового
            subprocess.Popen([mpc_hc_path, "/play", absolute_filepath],
                             shell=False,
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL,
                             creationflags=subprocess.CREATE_NO_WINDOW)  # Это предотвратит открытие окна командной строки
            # print(f"Воспроизведение файла {absolute_filepath} запущено в фоне")
        except Exception as e:
            # print(f"Ошибка при запуске MPC-HC: {str(e)}")
            pass
        # Return absolute path to the file
        return absolute_filepath
    else:
        # with open(tmp_dir / 'log_tts.txt', 'wb') as f:
        #     f.write(f"{response.status_code}: {response.text}")
        raise ValueError(f"{response.status_code}: {response.text}")
