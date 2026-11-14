#!/bin/sh
cd "$(dirname "$0")"
python3 make_audio_elevenlabs.py --check || exit 1
printf "Which grade do you want to make? (3, 4, 5, 6 or ALL): "; read G
if [ "$G" = "ALL" ] || [ "$G" = "all" ]; then python3 make_audio_elevenlabs.py; else python3 make_audio_elevenlabs.py --grade "$G"; fi
