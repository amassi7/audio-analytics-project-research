from pyannote.audio import Pipeline
from transformers import AutoModelForAudioClassification, Wav2Vec2FeatureExtractor
import torch
import librosa
import numpy as np

# Load the pre-trained models
pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization", use_auth_token="YOUR TOKEN HERE")
#model = AutoModelForAudioClassification.from_pretrained("superb/wav2vec2-large-superb-er", trust_remote_code=True)
#feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained("superb/wav2vec2-large-superb-er")

#pipe = pipeline("audio-classification", model="Hatman/audio-emotion-detection")   
model = AutoModelForAudioClassification.from_pretrained("Hatman/audio-emotion-detection") 
feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained("Hatman/audio-emotion-detection")


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

def concatenate_segments(segment, previous_segment, min_length=320):
    # Concatenate with previous segment if too short
    if len(segment) < min_length and previous_segment is not None:
        combined_segment = np.concatenate((previous_segment, segment))
        if len(combined_segment) >= min_length:
            return combined_segment
    return segment

def pad_segment_with_context(segment, min_length=320):
    # Contextual padding with repetition to reach minimum length
    if len(segment) < min_length:
        padded_segment = np.tile(segment, int(np.ceil(min_length / len(segment))))[:min_length]
        return padded_segment
    return segment

def predict_sentiment_with_aggregation(segment, model, feature_extractor):
    # Apply padding or skip segment based on length
    segment = pad_segment_with_context(segment)

    # Process the audio segment and convert it into the appropriate format
    inputs = feature_extractor(segment, sampling_rate=16000, return_tensors="pt", padding=True)

    # Perform inference
    with torch.no_grad():
        logits = model(**inputs).logits

    # Calculate probabilities using softmax
    probabilities = torch.nn.functional.softmax(logits, dim=-1)[0]
    
    # Get top 3 predictions to aggregate sentiment
    top_indices = torch.argsort(probabilities, descending=True)[:3]

    # Combine sentiments with weights based on confidence scores
    combined_label = np.mean([probabilities[idx].item() for idx in top_indices])
    predicted_label = model.config.id2label[top_indices[0].item()]

    return predicted_label, combined_label

def analyze_sentiments_with_context(diarization, audio, sr):
    # Prepare sentiment results for both speakers
    sentiment_results = {
        'Agent': [],
        'Customer': []
    }

    previous_segment = None  # Keep track of the previous segment to concatenate if needed

    # Loop through each speaker segment and predict sentiment
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        # Extract the audio segment for the current speaker
        segment = segment_audio(audio, sr, turn.start, turn.end)

        # Handle short segments by concatenating with the previous segment
        segment = concatenate_segments(segment, previous_segment)

        # Skip if the segment is still too short
        if len(segment) < 320:
            print(f"Segment too short after concatenation: {len(segment)} samples. Skipping this segment.")
            continue

        # Predict sentiment for the current segment
        sentiment, confidence = predict_sentiment_with_aggregation(segment, model, feature_extractor)

        # Update the previous segment tracker
        previous_segment = segment

        # Assume SPEAKER_00 is the Agent and SPEAKER_01 is the Customer; adjust as needed
        if speaker == 'SPEAKER_00':
            sentiment_results['Agent'].append((sentiment, confidence))
        else:
            sentiment_results['Customer'].append((sentiment, confidence))

    # Aggregate overall sentiment
    overall_agent_sentiment = max(set([s[0] for s in sentiment_results['Agent']]), key=[s[0] for s in sentiment_results['Agent']].count) if sentiment_results['Agent'] else "No data"
    overall_customer_sentiment = max(set([s[0] for s in sentiment_results['Customer']]), key=[s[0] for s in sentiment_results['Customer']].count) if sentiment_results['Customer'] else "No data"

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
sentiment_results = analyze_sentiments_with_context(diarization, audio, sr)

# Output the result
print("Sentiment Analysis Results:")
print(sentiment_results)
