# Install
1. 
`sudo apt install python3-pip python3-venv` 
2. 
`git clone https://github.com/luxonis/depthai.git` 
3. 
`cd depthai` 
4. 
`python3 -m venv myvenv`
5. 
`source myvenv/bin/activate`
6. 
`pip install -U pip`
7. 
`echo 'SUBSYSTEM=="usb", ATTRS{idVendor}=="03e7", MODE="0666"' | sudo tee /etc/udev/rules.d/80-movidius.rules`
8. 
`sudo udevadm control --reload-rules && sudo udevadm trigger`
9. 
`python3 install_requirements.py`







# Running
`cd depthai/depthai_sdk/examples/recording
python record_all.py --rgbResolution 1920x1080 --recordStream`