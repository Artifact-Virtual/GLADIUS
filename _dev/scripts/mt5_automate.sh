#!/bin/bash
set -eux

export HOME=/home/sirius
export USER=sirius
export DISPLAY=:1

# Start Xvfb if not running
if ! pgrep -f "Xvfb :1" >/dev/null 2>&1; then
  nohup Xvfb :1 -screen 0 1280x1024x24 > /home/sirius/xvfb.log 2>&1 &
  sleep 2
fi

# Start openbox if not running
if ! pgrep -f openbox >/dev/null 2>&1; then
  nohup openbox > /home/sirius/openbox.log 2>&1 &
  sleep 1
fi

# Start meta-trader installer (non-silent so GUI appears) in background
nohup env DISPLAY=$DISPLAY wine "/home/sirius/Downloads/mt5setup.exe" > /home/sirius/mt5_inst_stdout.log 2>&1 &
INST_PID=$!

# Wait for potential installer windows and attempt to drive them with xdotool
sleep 8

# function to send repeated keystrokes to try to progress typical installer dialogs
try_clicks() {
  local win
  win=$(DISPLAY=$DISPLAY xdotool search --name "MetaTrader" | head -n 1 || true)
  if [ -n "$win" ]; then
    DISPLAY=$DISPLAY xdotool windowactivate --sync $win
    sleep 1
    # try to press 'Next', 'I Agree', 'Install' by sending Return, Tab+Return sequences
    for i in 1 2 3 4 5; do
      DISPLAY=$DISPLAY xdotool key --clearmodifiers Return
      sleep 2
    done
    # try some Tabs + Return
    DISPLAY=$DISPLAY xdotool key --clearmodifiers Tab Tab Return
    sleep 2
  fi
}

# Try several times to auto-drive the installer
for i in {1..12}; do
  try_clicks || true
  sleep 3
done

# Wait for installer to finish
wait $INST_PID || true
sleep 5

# Attempt to locate installed terminal
TERMINAL_PATH=""
if [ -f "$HOME/.wine/drive_c/\"Program Files\"/MetaTrader 5/terminal64.exe" ]; then
  TERMINAL_PATH="$HOME/.wine/drive_c/\"Program Files\"/MetaTrader 5/terminal64.exe"
fi
if [ -z "$TERMINAL_PATH" ] && [ -f "$HOME/.wine/drive_c/\"Program Files (x86)\"/MetaTrader 5/terminal.exe" ]; then
  TERMINAL_PATH="$HOME/.wine/drive_c/\"Program Files (x86)\"/MetaTrader 5/terminal.exe"
fi

# If found, start it and attempt automated login
if [ -n "$TERMINAL_PATH" ]; then
  nohup env DISPLAY=$DISPLAY wine "$TERMINAL_PATH" > /home/sirius/mt5_terminal.log 2>&1 &
  sleep 10
  # find terminal window
  TERM_WIN=$(DISPLAY=$DISPLAY xdotool search --name "MetaTrader" | head -n1 || true)
  if [ -n "$TERM_WIN" ]; then
    DISPLAY=$DISPLAY xdotool windowactivate --sync $TERM_WIN
    sleep 1
    # open login dialog (Ctrl+L)
    DISPLAY=$DISPLAY xdotool key --clearmodifiers ctrl+l
    sleep 1
    # Type login, password and server: get them from .env
    LOGIN=$(grep -m1 '^MT5_LOGIN=' /home/sirius/herald/.env | cut -d'=' -f2-)
    PASS=$(grep -m1 '^MT5_PASSWORD=' /home/sirius/herald/.env | cut -d'=' -f2-)
    SERVER=$(grep -m1 '^MT5_SERVER=' /home/sirius/herald/.env | cut -d'=' -f2-)
    DISPLAY=$DISPLAY xdotool type --delay 50 --clearmodifiers "$LOGIN"
    DISPLAY=$DISPLAY xdotool key --clearmodifiers Tab
    DISPLAY=$DISPLAY xdotool type --delay 50 --clearmodifiers "$PASS"
    DISPLAY=$DISPLAY xdotool key --clearmodifiers Tab
    # Type server name; this might require selecting from dropdown - try direct typing
    DISPLAY=$DISPLAY xdotool type --delay 50 --clearmodifiers "$SERVER"
    sleep 1
    DISPLAY=$DISPLAY xdotool key --clearmodifiers Return
  fi
fi

# Wait and capture some logs
sleep 12
ls -lh /home/sirius/.wine/drive_c || true
ps aux | grep -i metatrader | grep -v grep || true

# Dump installer logs if available
if [ -f /home/sirius/mt5_install.log ]; then
  tail -n 200 /home/sirius/mt5_install.log || true
fi

echo done
