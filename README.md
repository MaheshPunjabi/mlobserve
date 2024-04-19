# mlobserve
Plot system resource usage of your deep learning system resources like GPU, CPU, Disks

![image](https://github.com/MaheshPunjabi/mlobserve/assets/31258686/ca8c0bce-62a9-45ab-a50e-7469aa1ac331)

Collect data with: 

    python3 observe.py


Start model now

Optionally, terminate observe.py to stop data collection: 

    Ctrl+C

Plot resource usage: 

    python3 showplot.py

## Requirements:
Ubuntu's sysstat package:

    sudo apt install sysstat

### NOTE: Activate conda/venv prior to next steps.

NVIDIA nvidia-ml-py

    pip install nvidia-ml-py
    

Python dependencies:

    pip install matplotlib
    pip install pandas
