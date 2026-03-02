@echo off
cd /d "D:\hackathon 0"
:: Start the main Task Loop
start "Ralph Wiggum - Task Loop" python scripts/ralph_loop.py
:: Start the Autonomous Efficiency Loop
start "Ralph Wiggum - Autonomous Loop" python scripts/ralph_autonomous_loop.py
