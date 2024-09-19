from pyannote.audio import Pipeline
from transformers import AutoModelForAudioClassification, Wav2Vec2FeatureExtractor
import torch
import librosa
import numpy as np

# Load the pre-trained models
# Replace "YOUR_HUGGINGFACE_TOKEN" with your actual Hugging Face access token if the pipeline requires authentication
pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization", use_auth_token="YOUR TOKEN HERE")
model = AutoModelForAudioClassification.from_pretrained("superb/wav2vec2-large-superb-er", trust_remote_code=True)
feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained("superb/wav2vec2-large-superb-er")

# Define the audio path
audio_path = "./output.wav"  # Path to your local audio file

def load_audio(audio_path):
    # Load audio file and resample to 16 kHz
    audio, sr = librosa.load(audio_path, sr=16000)
    return audio, sr

def diarize_audio(audio_path):
    # Perform speaker diarization
    diarization = pipeline(audio_path)
    return diarization

def segment_audio(audio, sr, start, end):
    # Extract a segment of the audio based on start and end times
    return audio[int(start * sr):int(end * sr)]

def predict_sentiment(segment, model, feature_extractor):
    # Minimum length requirement to avoid convolution errors
    min_length = 320  # Adjust this based on the model's convolution requirements

    # Check if segment is too short
    if len(segment) < min_length:
        print(f"Segment too short: {len(segment)} samples. Skipping this segment.")
        return "Too Short", 0.0

    # Process the audio segment and convert it into the appropriate format
    inputs = feature_extractor(segment, sampling_rate=16000, return_tensors="pt", padding=True)

    # Perform inference
    with torch.no_grad():
        logits = model(**inputs).logits

    # Calculate probabilities using softmax
    probabilities = torch.nn.functional.softmax(logits, dim=-1)[0]

    # Get the predicted label and its confidence score
    predicted_id = torch.argmax(probabilities).item()
    predicted_label = model.config.id2label.get(predicted_id, f"Label for ID {predicted_id} not found")
    confidence = probabilities[predicted_id].item()

    return predicted_label, confidence


def analyze_sentiments(diarization, audio, sr):
    # Prepare sentiment results for both speakers
    sentiment_results = {
        'Agent': [],
        'Customer': []
    }

    # Loop through each speaker segment and predict sentiment
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        # Extract the audio segment for the current speaker
        segment = segment_audio(audio, sr, turn.start, turn.end)
        sentiment, confidence = predict_sentiment(segment, model, feature_extractor)

        # Assume SPEAKER_00 is the Agent and SPEAKER_01 is the Customer; adjust as needed
        if speaker == 'SPEAKER_00':
            sentiment_results['Agent'].append((sentiment, confidence))
        else:
            sentiment_results['Customer'].append((sentiment, confidence))

    # Aggregate results
    agent_sentiments = [s[0] for s in sentiment_results['Agent']]
    customer_sentiments = [s[0] for s in sentiment_results['Customer']]
    
    # Return the most frequent sentiment for each speaker
    overall_agent_sentiment = max(set(agent_sentiments), key=agent_sentiments.count) if agent_sentiments else "No data"
    overall_customer_sentiment = max(set(customer_sentiments), key=customer_sentiments.count) if customer_sentiments else "No data"

    return {
        'Agent Overall Sentiment': overall_agent_sentiment,
        'Customer Overall Sentiment': overall_customer_sentiment,
        'Agent Detailed Sentiments': sentiment_results['Agent'],
        'Customer Detailed Sentiments': sentiment_results['Customer']
    }

# Load the audio file
audio, sr = load_audio(audio_path)

# Perform diarization
diarization = diarize_audio(audio_path)

# Analyze sentiments for each speaker
sentiment_results = analyze_sentiments(diarization, audio, sr)

# Output the result
print("Sentiment Analysis Results:")
print(sentiment_results)
