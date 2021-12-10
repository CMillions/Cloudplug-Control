# Introduction
This is the Control Software for Team 1282's UT Dallas ECE capstone project for the Spring-Fall 2021 semesters. The team, known as "Team CloudPlug", consists of six EE majors and one CE major.

## Team Members
### Computer Engineering
- Connor DeCamp
### Electrical Engineering
- Brandon Bearden
- Elizabeth Estrada
- Eduardo Hervert
- Jason Kim
- Nguyen Nguyen
- DongHyun Seo


# Project Abstract
SFP+ modules can transmit data at high speeds using many different types of cables. There are hundreds of different SFP+ modules from different vendors, and, theoretically, most of them should follow a standard. On each module is an EEPROM chip that stores vendor and diagnostic information which is used by a host to identify the device. However, not every module works with every host system. This leads to customers asking system vendors to support different SFP+ modules, which leads to dozens of software variants, test cases, and combinations per host-system. The issue is that each qualification test requires a person to physically insert and remove the module. This limits testing to a small number of switches featuring the SFP+ modules under test. Thus, qualification testing requires physical access to a limited resource which is time consuming. 

The main goal of this project is to design and build a proof-of-concept device, known as the CloudPlug, to qualify the control aspect of programmable pluggable interfaces. In other words, the CloudPlug should be able to mimic specific SFP+ modules and be accepted as genuine by the network switch. In order to do this, a docking station is needed to read and save the internal memory of vendor SFP+ modules. The docking station also allows users to monitor critical parameters of SFP+ modules in order to create stress-cases to program into the CloudPlug, which the CloudPlug can feed to the network switch it’s inserted into. The docking station is controllable through ethernet/IP and the CloudPlug is wirelessly controllable, both through a control software designed by the team. CloudPlugs would allow scaling testing resources by replicating vendor specific logic in software and swapping modules by remote configuration rather than physical replacement.

# Dependencies
- Python 3.8.10
- PyQt5 5.15.2
- python-dotenv 0.19.0
- mysql-connector-python 8.0.26
- pyqtgraph 0.12.3
- binary-fractions 1.1.0
- fpdf 1.7.2
