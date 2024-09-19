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
        <mstts:express-as style="advertisement_upbeat">
            <s>Good morning. Thank you for calling ITdesk. This is Aline Rebeck, ID 64523. Can I please get your name and ID?</s>
        </mstts:express-as>
    </voice>
    <voice name="en-US-DavisNeural">
        <mstts:express-as style="sad">
            <s>Hi, this is Jacob Harper, ID number JD36894.</s>
        </mstts:express-as>
    </voice>
    <voice name="en-US-AriaNeural">
        <mstts:express-as style="customerservice">
            <s>Thank you for your information. I found your account. How can I help you today?</s>
        </mstts:express-as>
    </voice>
    <voice name="en-US-DavisNeural">
        <mstts:express-as style="angry">
            <s>Hi, I can't log in with my badge.</s>
        </mstts:express-as>
    </voice>
    <voice name="en-US-AriaNeural">
        <mstts:express-as style="customerservice">
            <s>Is your badge properly inserted into the card reader?</s>
        </mstts:express-as>
    </voice>
    <voice name="en-US-DavisNeural">
        <mstts:express-as style="unfriendly">
            <s>Yeah, it's properly inserted, but it keeps saying access denied.</s>
        </mstts:express-as>
    </voice>
    <voice name="en-US-AriaNeural">
        <mstts:express-as style="friendly">
            <s>Have you recently received a new badge or updated your credentials?</s>
        </mstts:express-as>
    </voice>
    <voice name="en-US-DavisNeural">
        <mstts:express-as style="chat">
            <s>No, it's the same badge I've been using.</s>
        </mstts:express-as>
    </voice>
    <voice name="en-US-AriaNeural">
        <mstts:express-as style="customerservice">
            <s>Okay, let me try resetting your badge credentials on our system. Please hold on for one moment.</s>
        </mstts:express-as>
    </voice>
    <voice name="en-US-DavisNeural">
        <mstts:express-as style="hopeful">
            <s>Okay.</s>
        </mstts:express-as>
    </voice>
    <voice name="en-US-AriaNeural">
        <mstts:express-as style="cheerful">
            <s>Okay, I've reset your credentials. Please try logging in again now.</s>
        </mstts:express-as>
    </voice>
    <voice name="en-US-DavisNeural">
        <mstts:express-as style="cheerful">
            <s>It worked. Thanks so much. Amazing.</s>
        </mstts:express-as>
    </voice>
    <voice name="en-US-AriaNeural">
        <mstts:express-as style="narration-professional">
            <s>You're welcome. If you encounter any other issues, please let us know. Also, for reference, your ticket number is DXV1234567. Have a great day.</s>
        </mstts:express-as>
    </voice>
</speak>
'''

# Synthesize speech with Azure
synthesize_speech_with_azure(ssml)
