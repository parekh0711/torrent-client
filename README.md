# Project Description

A Bittorrent client for peer to peer sharing of files written in Python using multithreading. It works with any torrent file. It download as well as upload files.

# Supported Platforms
- Linux

# Requirements
- Python 3.5 or later
- bencodepy

# Compilation Instructions
- The most basic way to run the program is ` python3 main.py <path to torrent file> `
- The optional paramters are:

| Parameter      	| Syntax                    	| Definition                                                                                         	|
|----------------	|---------------------------	|----------------------------------------------------------------------------------------------------	|
| path           	| -path &lt;output-path&gt; 	| This is used to define output folder for the torrent. It must end with a /. The folder must exist. 	|
| download speed 	| -dk &lt;speed&gt;         	| This defines maximum download speed in kilobits per second.                                        	|
| download speed 	| -dm &lt;speed&gt;         	| This defines maximum download speed in megabits per second.                                        	|
| upload speed   	| -uk &lt;speed&gt;         	| This defines maximum upload speed in kilobits per second.                                          	|
| upload speed   	| -um &lt;speed&gt;         	| This defines maximum upload speed in megabits per second.                                          	|
| peers          	| -peers &lt;integer&gt;     	| This is the maximum number of peers that it can connect to. Default is 100.                        	| 


# Screenshots
