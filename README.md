# Treadmill of Science

This is the repository for the TOS. There are 3 peices to this project: Labview data acquistion for the sensors mounted in the treadmill, python data acquisition for the XSensors, and Matlab for data processing.

LABVIEW
To launch the labview program go to the LabView Data Logger folder and launch the Tradmill_Of_Science labview project file. This will open the full project, Open the Main VI and run the program from there. The VI has instructions in it for running it. The Main VI has every sensor in it, acquiring data idependantly. Ending the program will stop them all at once. Individual sensors can be toggled on/off for troulbeshooting or acquiring a subset of the sensor data.

PYTHON
To launch the XSensor acquisition navigate to XSensor/ToS and open the XSENSOR_data_collect file in an IDE such as Pycharm. Depending on the laptop used to run this you may need to change the file paths at the top of the file to match the locations on the laptop being used. Make sure the XSensor are on and paired with the laptop's bluetooth, then run the file. The program will aquire and log the XSensor data to the X_log.XSN. One the program is interrupted via keystroke it will end aquisition and begin to parse the XSN file into a CSV file called XSensor_output.csv.

optional python files:
Delete Data - This will delete all the labview data files. This is usful if you've just been doing some debugging and have a lot of files you don't care about. You can run this before a real Data Acquisition run to avoid dealing with multiple versions of the data files and to allow you to use the Move Data script

Move Data - This only works if the data you want to move is the only version in the folder, otherwise it will move an older version of the file. Run Delete Data before a Data Acquisition so you can use this afterward to quickly and easily group the data into a folder. Warning!! if the filepaths and/or file names are incorrect you can delete data using this.

MATLAB
This contains the matlab scripts used to process the data files collected using the Labview and python files. There is a folder named Bike V3 brake analysis which contains some linear regressions used on the Bike V3 project. While no longer relevant to the project, this script could be a good starting place for writing linear regression processing on large datasets
