# DeskFormerUI

## Install

> apt install -y libmtdev-dev libxss1 libpangocairo-1.0-0 libatk1.0-0 libffi-dev make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev liblzma-dev libgtk2.0-0
> curl https://pyenv.run | bash

## Dev

> curl https://pyenv.run | bash
> pyenv install 3.7.12

Add to ~/.bashrc:

> export PATH="/home/anton/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
> eval "$(pyenv virtualenv-init -)"
> pyenv virtualenvs

> env PYTHON_CONFIGURE_OPTS="--enable-shared" pyenv install 3.7.12
> pyenv virtualenv 3.7.12 deskformer_ui
> source ~/.pyenv/versions/deskformer_ui/bin/activate
> pip install -r requirements.txt

sudo apt install libsdl2-dev
pip install PySDL2

Running a script:

> DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0 python3 <COMMAND>

sudo apt-get install build-essential git ffmpeg libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev zlib1g-dev
USE_SDL2=1 pip install https://github.com/Flid/kivy/archive/refs/heads/master.zip
