from google.cloud import texttospeech
from pydub import AudioSegment
import io

def synthesize_speech(ssml, voice_name, language_code, gender):
    client = texttospeech.TextToSpeechClient()

    # Set the SSML input
    synthesis_input = texttospeech.SynthesisInput(ssml=ssml)

    voice = texttospeech.VoiceSelectionParams(
        name=voice_name,
        language_code=language_code,
        ssml_gender=gender
    )

    # Use LINEAR16 for WAV format
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16
    )

    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )

    return response.audio_content

# Generate agent's response with a neutral style
agent_ssml = '''
<speak>
    <voice name="en-US-Wavenet-D">
        <prosody volume="default" rate="medium">
            Hello, how can I assist you today?
        </prosody>
    </voice>
</speak>
'''
agent_audio = synthesize_speech(
    ssml=agent_ssml,
    voice_name="en-US-Wavenet-D",  # Example voice for Agent
    language_code="en-US",
    gender=texttospeech.SsmlVoiceGender.MALE
)

# Generate customer's response with a sad style
customer_ssml = '''
<speak>
    <voice name="en-US-Wavenet-F" style="happy">
            I’m having trouble with my computer.
    </voice>
</speak>
'''
customer_audio = synthesize_speech(
    ssml=customer_ssml,
    voice_name="en-US-Wavenet-F",  # Example voice for Customer
    language_code="en-US",
    gender=texttospeech.SsmlVoiceGender.FEMALE
)

# Use BytesIO to handle the audio segments
agent_io = io.BytesIO(agent_audio)
customer_io = io.BytesIO(customer_audio)

# Load audio segments from BytesIO with WAV format
agent_segment = AudioSegment.from_file(agent_io, format="wav")
customer_segment = AudioSegment.from_file(customer_io, format="wav")

print(f"Agent audio length: {len(agent_segment)} bytes")
print(f"Customer audio length: {len(customer_segment)} bytes")


# Create a silent pause segment (e.g., 1 second)
pause = AudioSegment.silent(duration=1000)  # Duration is in milliseconds

# Combine the audio segments with the pause in between
combined_audio = agent_segment + pause + customer_segment

# Export the combined audio to a single output file
combined_audio.export("conversation.wav", format="wav")

print("Conversation audio with pause written to conversation.wav")
