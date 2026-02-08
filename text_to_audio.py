
from kokoro import KPipeline
from IPython.display import display, Audio
import soundfile as sf
import torch
import shutil
import os
import glob

# Constants for file paths
INPUT_FOLDER = os.path.join('..', 'clio-out')  # Go up one directory
INPUT_FILE = 'extracted_text.txt'
INPUT_PATH = os.path.join(INPUT_FOLDER, INPUT_FILE)
OUTPUT_FOLDER = 'hermes-text-to-audio-out'

# Clear the output folder before generating new files
if os.path.exists(OUTPUT_FOLDER):
    shutil.rmtree(OUTPUT_FOLDER)
os.makedirs(OUTPUT_FOLDER)

with open(INPUT_PATH, 'r', encoding='utf-8') as f:
    text = f.read()

pipeline = KPipeline(lang_code='a')
generator = pipeline(text, voice='af_heart')
for i, (gs, ps, audio) in enumerate(generator):
    print(i, gs, ps)
    display(Audio(data=audio, rate=24000, autoplay=i==0))
    sf.write(os.path.join(OUTPUT_FOLDER, f'{i}.wav'), audio, 24000)
