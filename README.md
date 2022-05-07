# LANMan (Local Area Network Manager)

### Supervisor: Professor Nathan Clarke

## Project Vision:

The vision of my project is help address the lack of awareness of devices in Local Area Networks (LAN) as well as the importance of updates to devices and provide a rough guidance on what the risks are by introducing unpatched / unconfigured devices to the network. 

 

The ideal consumer of this product would be inexperienced people (both home users and micro and small enterprises) who would just like to have an overview on their network which would include patching of systems and a reminder on each new network device if they have been configured to remove default passwords and so forth. 

 

Security within the network you are connected to is for everyone. Both the owner of the network and people who connect to it. The problem with it is that people with less technical backgrounds are often left overwhelmed with the number of tools and options to pick from.  

 

LANMan (Local Area Network Manager) will be a “Security Tool” which can be installed onto a Raspberry Pi or equivalent device. It will offer an interface for a user to be able to look at what is currently on the network and, where an agent (Windows & Linux devices) is installed, see the patching status of those devices, whether the device is up-to-date or if it is missing key updates. It will not be similar in fashion to other available tools such as “Nagios” which offers service monitoring / device monitoring, nor will it be like software such as “AdGuard” or “PiHole” which offer ad-blocking services. 

# Windows Set-Up

To get setup with LANMan on Windows, you need to perform the following steps:
1. Clone this GitHub repository using Git from the command-line **OR** click the above 'Code' button and then 'Download ZIP'.
2. Once downloaded, navigate to the download destination and extract if necessary. Within the 'Website' folder is a file named 'config.py', open this with your favourite text-editor and verify the settings:

- TESTING -- This line should be set to True if you're planning on developing features for LANMan.
- DEBUG -- This line should be set to True if you're planning on developing features for LANMan.
- FLASK_ENV -- This line shoud be set 'production'. If you're planning on developing features for LANMan, set this to 'development'.
- SECRET_KEY -- This should be a mix of 24 or more letters and numbers. 
- SQLALCHEMY_DATABASE_URI -- Unless you use a dedicated database server, leave this alone.
- SQLACLHEMY_TRACK_MODIFICATIONS -- Leave this as False as otherwise there will be excessive log output from LANMan.
- IP_RANGE -- Set this value to the correct range of your home address. Usually these are either 192.168.1.0/24 **OR** 192.168.0.0/24. If you see no devices within your network dashboard, you may have configured this incorrectly.
- DEFAULT_USERNAME -- This is used for the initial user creation on first start-up. Change this to something you are likely to rememeber.
- DEFALT_USERPASS -- This is the associated password for the DEFAULT_USERNAME field above.

3. Once you have configured the config.py file, right click on 'start.ps1' file and click *Run as Administrator* and then LANMan will start.

# Linux Set-Up

1. Follow Steps 1 and 2 from Windows Set-Up.
2. Once you have configured the config.py file, either using the terminal or by right clicking the 'start.sh' file, run this as sudo as it requires access to packet-capturing functions of the OS.
