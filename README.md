RecSyncNG is a video recording app with sub-millisecond synchronization accuracy for multiple Android smartphones,
useful for creating affordable and easy-to-setup multi-view camera systems for robotics, SLAM, 3D-reconstruction, panorama stitching.

RecSynchNG is a fork of the original [RecSynch-android](https://github.com/MobileRoboticsSkoltech/RecSync-android) project. Here is the [original README](README-orig.md).

The original project has been improved with a remote GUI allowing for remote control of the android devices, centralized video download capability,
 and a revised post-processing stage for the deployment of perfectly synchronized videos.


## Installation and setup

(Use img from the slides)


### Requirements

* A set of Android devices, _all of the same hardware type_, with Android version 10+. (We were able to compile and run on Android 8, but not tested since a while)
* Elect a _Leader_ android device:
  * must have an adaptor for Ethernet connection;
  * must be able to configure the ethernet with static IP address;
  * must be able to configure Hotspot (share Ethernet via WiFi):
    * not all devices can by default enable Hotspot without a SIM card. To circumvent some limited GUIs, we are using the `VPNHotspot` app.
* A laptop/PC with Python 3.9 and an ethernet adaptor

### Android devices installation and setup

* Install the RecSynchNG apk on all devices
* Select one device as _Leader_:
  * configure its Ethernet adaptor with:
    * Static IP: 192.168.5.2
    * Mask: 255.255.255.0
    * Gateway 192.168.5.1
  * Start a Wi-Fi hotspot, sharing the Ethernet connection.
* Connect all other android devices to the Hotspot WiFi network.


The master app should display now the connected clients and buttons for recording control

### Remote controlling PC installation and setup

Configure the ethernet adaptor of your PC as: 
* Static IP: 192.168.5.1
* Mask: 255.255.255.0
* Gateway 192.168.5.1

Cable connect the PC and the Master device.

Verify the Ethernet connection with Ping. E.g., from the PC, in a terminal

```
ping 192.168.5.2

64 bytes from 192.168.5.2: icmp_seq=347 ttl=125 time=2.425 ms
64 bytes from 192.168.5.2: icmp_seq=348 ttl=125 time=2.233 ms
64 bytes from 192.168.5.2: icmp_seq=349 ttl=125 time=7.560 ms
64 bytes from 192.168.5.2: icmp_seq=350 ttl=125 time=2.288 ms
```


Setup a python environment using Python 3.9+.

```
cd PythonTools
python3 -m venv p3env-RecSynchNG
source p3env-RecSynchNG/bin/activate
pip install -r requirements.txt
```

For the post-processing of the videos, you need to install ffmpeg executable. E.g.:
* On Linux: `apt install ffmpeg`
* On Mac: `brew install ffmpeg`


## Usage

### Run the software

(Android) First, start the app on all Android devices:
* Wait a few seconds for synchronization;
* on client devices you should see the client ID and info about the connection status; 
* on the leader device you should see the list of connected clients.

Second, start the software on the controlling PC.

On one terminal **start the http file server**. It starts a small http server ready to receive the recorded files from the android devices:

```
cd PythonTools
source p3env-RecSynchNG/bin/activate
python FileServer.py
```

TODO -- pic of the server console

On another terminal, **start the remote controlling GUI** :

```
cd PythonTools
source p3env-RecSynchNG/bin/activate
python RemoteController.py
```

TODO -- pic of the GUI


### Recording video

1.  [Optional step] Press the ```calculate period``` button. The app will analyze frame stream and use the calculated frame period in further synchronization steps.
2.  Adjust exposure and ISO to your needs.
3.  Press the ```phase align``` button.
4.  Press the ```record video``` button to start synchronized video recording.
5.  Get videos from RecSync folder in smartphone root directory.

### Extraction and matching of the frames



## Citations / Credits

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

This work is based on "Wireless Software Synchronization of Multiple Distributed Cameras"

Reference code for the paper
[Wireless Software Synchronization of Multiple Distributed Cameras](https://arxiv.org/abs/1812.09366).
_Sameer Ansari, Neal Wadhwa, Rahul Garg, Jiawen Chen_, ICCP 2019.
