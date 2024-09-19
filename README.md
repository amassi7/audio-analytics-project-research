# audio-analytics-project-research
This repository contains research on the audio analytics AI platform made for HawkVoice. The code in this repository can serve as the skeleton for building and deploying the audio-analytics tool made for the application. Although more code is needed to extract more specific information about the specific sentiment-- the current model outputs only whether the sentiment was positive, neutral, or negative without much accuracy. The research also includes using a speaker diarization model to split audio files into two.

This repository includes:
#### 1. Text to Speech research
This folder includes a couple of experiments to generate audio from text in order to possibly train or fine-tune a sentiment recognition model with pre-labeled data (when you generate the audio with Google Cloud TTS or Azure, you can specify the sentiment-- this specification we can then use as a label for the voice data). The finding is that Azure allows us to specify many more sentiments in comparison to Google Cloud TTS.

#### 2. Audio Sentiment Analysis with speaker diarization
This folder includes code that outputs an overall sentiment per speaker using the superb/wav2vec2-large-superb-er (customer service agent vs customer) as well as sentiment per line, which is diarized using the pyannote/speaker-diarization model. The second piece of code adds some padding to each audio segment after the diarization is performed, then saves each segment separately, which yields better results.