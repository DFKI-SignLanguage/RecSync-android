![Logo](https://imgur.com/YtJA0E2.png)

If you use this application, please cite [Sub-millisecond Video Synchronization of Multiple Android Smartphones](https://arxiv.org/abs/2107.00987):
```
@misc{akhmetyanov2021submillisecond,
      title={Sub-millisecond Video Synchronization of Multiple Android Smartphones}, 
      author={Azat Akhmetyanov and Anastasiia Kornilova and Marsel Faizullin and David Pozo and Gonzalo Ferrer},
      year={2021},
      eprint={2107.00987},
      archivePrefix={arXiv},
      primaryClass={cs.CV}
}
```
## Usage:

### Network setup

(Use img from the slides)

Cable connect the PC and the Master device

* Configure the ethernet adaptor of your PC 
  * Static IP: 192.168.5.1
  * Mask: 255.255.255.0
  * Gateway 192.168.5.1

* Configure the Master with an Ethernet adaptor and set it to:
  * Static IP: 192.168.5.2
  * Mask: 255.255.255.0
  * Gateway 192.168.5.1

Check the Ethernet connection with Ping.
E.g., from the PC, in a terminal

```
ping 192.168.5.2

64 bytes from 192.168.5.2: icmp_seq=347 ttl=125 time=2.425 ms
64 bytes from 192.168.5.2: icmp_seq=348 ttl=125 time=2.233 ms
64 bytes from 192.168.5.2: icmp_seq=349 ttl=125 time=7.560 ms
64 bytes from 192.168.5.2: icmp_seq=350 ttl=125 time=2.288 ms
```

### Leader smartphone setup

1.  Start a Wi-Fi hotspot.
2.  Start tha app

### Clients smartphones setup

1. Enable WiFi and connect to the Wi-Fi hotspot.
2. Start the app

The master app should display now the connected clients and buttons for recording control


#### Remote Controller on the connected PC

If not done yet, setup a python environment using Python 3.7+ (This is needed only the first time)

```
cd Remote Controller
python3 -m venv p3env-RecSynchNG
source p3env-RecSynchNG/bin/activate
pip install -r requirements.txt
```

To use it, activate the environment and run the remote controller (App must be already running on the _master_ Android device)

```
cd RemoteController
source p3env-RecSynchNG/bin/activate
python remote_controller.py
```



#### Recording video

1.  [Optional step] Press the ```calculate period``` button. The app will analyze frame stream and use the calculated frame period in further synchronization steps.
2.  Adjust exposure and ISO to your needs.
3.  Press the ```phase align``` button.
4.  Press the ```record video``` button to start synchronized video recording.
5.  Get videos from RecSync folder in smartphone root directory.

#### Extraction and matching of the frames

```
Requirements:

- Python
- ffmpeg
```

1. Navigate to ```utils``` directory in the repository.
2. Run ```./match.sh <VIDEO_1> <VIDEO_2>```.
3. Frames will be extracted to directories ```output/1``` and ```output/2``` with timestamps in filenames, output directory will also contain ```match.csv``` file in the following format:
    ```
    timestamp_1(ns) timestamp_2(ns)
    ```

### Our contribution:

- Integrated **synchronized video recording**
- Scripts for extraction, alignment and processing of video frames
- Experiment with flash blinking to evaluate video frames synchronization accuracy
- Panoramic video demo with automated Hugin stitching

### Panoramic video stitching demo

### [Link to youtube demo video](https://youtu.be/W6iANtCuQ-o)

- We provide scripts to **stitch 2 syncronized smatphone videos** with Hujin panorama CLI tools
- Usage:
    - Run ```./make_demo.sh {VIDEO_LEFT} {VIDEO_RIGHT}```

### This work is based on "Wireless Software Synchronization of Multiple Distributed Cameras"

Reference code for the paper
[Wireless Software Synchronization of Multiple Distributed Cameras](https://arxiv.org/abs/1812.09366).
_Sameer Ansari, Neal Wadhwa, Rahul Garg, Jiawen Chen_, ICCP 2019.
