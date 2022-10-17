function MotorData = load_MotorData(fullfname_tdms)

%fullfname_tdms = fullfile('C:\', 'Users' , 'cooper', 'Documents', 'MATLAB', 'XSensorIMU Test', 'Torque_Data.tdms')


[Dname,fname,~] = fileparts(fullfname_tdms);
fullfname_mat = fullfile(Dname,[fname '.mat']);

if ~exist(fullfname_mat,'file')
    Data = convertTDMS(0,fullfname_tdms);

    MotorData.t = Data.Data.MeasuredData(3).Data;
    MotorData.t = datetime(MotorData.t,'ConvertFrom','datenum','TimeZone','local');
    MotorData.t.TimeZone = 'America/Los_Angeles';

    % from Dee, Vout = 0.005(lbs force)
    Gt = 3.9123; % [Nm]
    Gi = (-1/0.0125); % [amps]
    Gv = 15; % [V]

    MotorData.Torque = Data.Data.MeasuredData(4).Data * Gt;
    %MotorData.Current = Data.Data.MeasuredData(5).Data * Gi;
    %MotorData.Voltage = Data.Data.MeasuredData(6).Data * Gv;

    save(fullfname_mat,'MotorData');
else
    load(fullfname_mat,'MotorData');
end

return