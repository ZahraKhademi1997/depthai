# Install
`sudo apt install python3-pip python3-venv` 
`git clone https://github.com/luxonis/depthai.git` 
`cd depthai` 
`python3 -m venv myvenv`
`source myvenv/bin/activate`
`pip install -U pip`
`echo 'SUBSYSTEM=="usb", ATTRS{idVendor}=="03e7", MODE="0666"' | sudo tee /etc/udev/rules.d/80-movidius.rules`
`sudo udevadm control --reload-rules && sudo udevadm trigger`
`python3 install_requirements.py`







# Running
`cd depthai/depthai_sdk/examples/recording
python record_all.py --rgbResolution 1920x1080 --recordStream`