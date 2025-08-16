
from kokoro import KPipeline
from IPython.display import display, Audio
import soundfile as sf
import torch
import argparse
import shutil

import os
import glob

parser = argparse.ArgumentParser(description="Generate audio from text file.")
parser.add_argument("filepath", type=str, help="Path to the text file")
args = parser.parse_args()

# Clear the audio folder before generating new files
audio_folder = 'audio'
if os.path.exists(audio_folder):
    shutil.rmtree(audio_folder)
os.makedirs(audio_folder)

with open(args.filepath, 'r', encoding='utf-8') as f:
    text = f.read()

pipeline = KPipeline(lang_code='a')
generator = pipeline(text, voice='af_heart')
for i, (gs, ps, audio) in enumerate(generator):
    print(i, gs, ps)
    display(Audio(data=audio, rate=24000, autoplay=i==0))
    sf.write(f'audio/{i}.wav', audio, 24000)
