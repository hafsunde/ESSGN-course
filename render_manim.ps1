$env:Path += ";C:\Program Files\MiKTeX\miktex\bin\x64"
py -m manim --format=mp4 --fps 30 -r 1280,720 manim/behavioral_genetics_bias.py BehavioralGeneticsBiasScene
