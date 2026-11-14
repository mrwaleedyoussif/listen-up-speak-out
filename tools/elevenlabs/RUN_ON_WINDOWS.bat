@echo off
cd /d "%~dp0"
echo ============================================
echo  Listen Up! Speak Out! - ElevenLabs voices
echo ============================================
where python >nul 2>nul || (echo Python is not installed. Get it from https://www.python.org/downloads/ ^(tick "Add Python to PATH"^). & pause & exit /b)
if not exist ".env" (
  echo.
  echo First time? Create a file named .env in this folder with one line:
  echo ELEVENLABS_API_KEY=your_key_here
  echo.
  pause & exit /b
)
python make_audio_elevenlabs.py --check
echo.
set /p G=Which grade do you want to make? (3, 4, 5, 6 or ALL): 
if /I "%G%"=="ALL" (python make_audio_elevenlabs.py) else (python make_audio_elevenlabs.py --grade %G%)
pause
