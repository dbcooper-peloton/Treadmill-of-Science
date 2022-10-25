import os
import shutil
Destination = input("Enter the name of the new folder")
Destination = f"C:\TOS_Data\TOS_User_Data\{Destination}"
os.mkdir(Destination)

shutil.move(r"C:\TOS_Data\Accels\accel_data.tdms",Destination + r"\accel_data.tdms")
shutil.move(r"C:\TOS_Data\Accels\accel_data.tdms_index",Destination + r"\accel_data.tdms_index")
shutil.move(r"C:\TOS_Data\LoadCells\load_cells_Data.tdms",Destination + r"\load_cells_Data.tdms")
shutil.move(r"C:\TOS_Data\LoadCells\load_cells_Data.tdms_index",Destination + r"\load_cells_Data.tdms_index")
shutil.move(r"C:\TOS_Data\Mics\mic_data.tdms",Destination + r"\mic_data.tdms")
shutil.move(r"C:\TOS_Data\Mics\mic_data.tdms_index",Destination + r"\mic_data.tdms_index")
shutil.move(r"C:\TOS_Data\Tach Sensor\Tach_Data.tdms", Destination + "\Tach_Data.tdms")
shutil.move(r"C:\TOS_Data\Tach Sensor\Tach_Data.tdms_index",Destination + "\Tach_Data.tdms_index")
shutil.move(r"C:\TOS_Data\Torque\Torque_and_Power_Data.tdms", Destination + "\Torque_and_Power_Data.tdms")
shutil.move(r"C:\TOS_Data\Torque\Torque_and_Power_Data.tdms_index",Destination + "\Torque_and_Power_Data.tdms_index")
shutil.move(r"C:\TOS_Data\Torque\Torque_Position.tdms", Destination + "\Torque_Position.tdms")
shutil.move(r"C:\TOS_Data\Torque\Torque_Position.tdms_index",Destination + "\Torque_Position.tdms_index")
#shutil.move(r"C:\TOS_Data\Belt Speed\Belt_Speed.tdms", Destination + "\Belt_Speed.tdms")
#shutil.move(r"C:\TOS_Data\Belt Speed\Belt_Speed.tdms_index", Destination + "\Belt_Speed.tdms_index")
shutil.move(r"C:\TOS_Data\XSensor\XSensor_output.csv",Destination + "\XSensor_output.csv")
shutil.move(r"C:\TOS_Data\XSensor\IMU_output.csv",Destination + "\IMU_output.csv")
shutil.move(r"C:\TOS_Data\XSensor\X_log.xsn",Destination + "\X_log.xsn")
