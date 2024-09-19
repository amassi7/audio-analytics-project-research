import os
import azure.cognitiveservices.speech as speechsdk

def synthesize_speech_with_azure(ssml_text):
    # Retrieve Azure Speech key and region from environment variables
    speech_key = os.getenv("AZURE_SPEECH_KEY")
    speech_region = os.getenv("AZURE_SPEECH_REGION")

    # Check if the environment variables are set
    if not speech_key or not speech_region:
        print("Azure Speech Key or Region not set. Please configure your environment variables.")
        return None

    # Set up the Speech SDK using the credentials from environment variables
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)

    # Configure the audio output to save to a WAV file instead of using the default speaker
    audio_config = speechsdk.audio.AudioOutputConfig(filename="output.wav")

    # Create a synthesizer with the given configurations
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

    # Synthesize the speech using SSML
    result = synthesizer.speak_ssml_async(ssml_text).get()

    # Check the result of the synthesis
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("Speech synthesized successfully and saved to output.wav.")
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print(f"Speech synthesis canceled: {cancellation_details.reason}")
        if cancellation_details.error_details:
            print(f"Error details: {cancellation_details.error_details}")

# Full dialogue SSML with alternating voices and 1000ms break time, wrapped in <s> tags
ssml = '''
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis"
       xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="en-US">
    <voice name="en-US-AriaNeural">
        <mstts:express-as style="happy">
            <s>Good morning. Thank you for calling ITdesk. This is Aline Rebeck, ID 64523. Can I please get your name and ID?</s>
        </mstts:express-as>
    </voice>
</speak>
'''

# Synthesize speech with Azure
synthesize_speech_with_azure(ssml)
