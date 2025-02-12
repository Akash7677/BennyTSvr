import requests
import base64
import numpy as np
import sounddevice as sd
from typing import Optional, Dict
import json
import threading
import queue
from pydub import AudioSegment
from io import BytesIO


class AudioStreamClient:
    def __init__(self, server_url: str = "http://localhost:8000"):
        self.server_url = server_url
        self.audio_queue = queue.Queue()
        self.is_playing = False

    def _convert_mp3_to_pcm(self, mp3_data: bytes) -> np.ndarray:
        """Convert MP3 data to PCM format"""
        # Load MP3 data
        audio = AudioSegment.from_mp3(BytesIO(mp3_data))

        # Convert to numpy array
        samples = np.array(audio.get_array_of_samples())

        # Convert to float32 between -1 and 1
        samples = samples.astype(np.float32) / (2 ** 15 if audio.sample_width == 2 else 2 ** 7)

        # Convert to stereo if mono
        if audio.channels == 1:
            samples = np.column_stack((samples, samples))

        return samples, audio.frame_rate

    def _play_audio_worker(self):
        """Worker thread to continuously play audio chunks"""
        while self.is_playing:
            try:
                audio_chunk = self.audio_queue.get(timeout=1)
                if audio_chunk is not None:
                    # Convert MP3 to PCM
                    samples, frame_rate = self._convert_mp3_to_pcm(audio_chunk)

                    # Play the audio
                    sd.play(samples, frame_rate)
                    sd.wait()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error playing audio chunk: {e}")
                break

    def generate_response(self,
                          text: str,
                          profanity_level: int = 3,
                          voice_id: Optional[str] = "542jzeOaLKbcpZhWfJDa",
                          stability: float = 1,
                          similarity_boost: float = 0.5,
                          style: float = 0.7,
                          use_speaker_boost: bool = True) -> Dict:
        """
        Send request to server and handle the response
        """
        request_data = {
            "text": text,
            "profanity_level": profanity_level,
            "voice_id": voice_id,
            "stability": stability,
            "similarity_boost": similarity_boost,
            "style": style,
            "use_speaker_boost": use_speaker_boost
        }

        try:
            # Make request to server
            response = requests.post(
                f"{self.server_url}/generate",
                json=request_data,
                stream=True
            )
            response.raise_for_status()
            print()

            # Start audio playback thread
            self.is_playing = True
            play_thread = threading.Thread(target=self._play_audio_worker)
            play_thread.start()

            # Process the streaming response
            buffer = b""
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    buffer += chunk
                    try:
                        # Try to parse the current buffer as JSON
                        response_data = json.loads(buffer.decode('utf-8'))

                        # Extract audio data and feed to player
                        audio_data = base64.b64decode(response_data['audio_base64'])
                        self.audio_queue.put(audio_data)

                        # Return the complete response data
                        return {
                            'text_response': response_data['text_response'],
                            'words': response_data['words'],
                            'word_start_times_seconds': response_data['word_start_times_seconds'],
                            'word_end_times_seconds': response_data['word_end_times_seconds']
                        }
                    except json.JSONDecodeError:
                        # If we can't parse as JSON yet, continue accumulating data
                        continue

        except Exception as e:
            print(f"Error during request: {e}")
            return None
        finally:
            self.is_playing = False
            play_thread.join()

    def stop_playback(self):
        """Stop the audio playback"""
        self.is_playing = False
        sd.stop()
        with self.audio_queue.mutex:
            self.audio_queue.queue.clear()


# Example usage
if __name__ == "__main__":
    client = AudioStreamClient()

    # Test the client
    response = client.generate_response(
        text="Tell me a joke!",
        profanity_level=1,
        stability=0.5,
        similarity_boost=0.5
    )

    if response:
        print("Text Response:", response['text_response'])
        print("\nCharacter Timings:")
        for word, start, end in zip(
                response['words'],
                response['word_start_times_seconds'],
                response['word_end_times_seconds']
        ):
            print(f"Word: {word}, Start: {start:.2f}s, End: {end:.2f}s")