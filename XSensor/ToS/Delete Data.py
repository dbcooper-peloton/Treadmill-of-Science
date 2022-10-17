import os, shutil
folder = [r'C:\TOS_Data\Tach Sensor', r'C:\TOS_Data\LoadCells', r'C:\TOS_Data\Belt Speed', r'C:\TOS_Data\Torque', r'C:\TOS_Data\Mics', r'C:\TOS_Data\Accels', 'C:\TOS_Data\Power']
for folder in folder:
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))
