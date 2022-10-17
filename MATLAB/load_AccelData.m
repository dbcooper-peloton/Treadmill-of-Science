
function AccelData = load_AccelData1(fullfname_tdms)

%fullfname_tdms = fullfile('C:\', 'Users' , 'cooper', 'Documents', 'MATLAB', 'XSensorIMU Test', 'accel_and_power_data.tdms')

[Dname,fname,~] = fileparts(fullfname_tdms);
fullfname_mat = fullfile(Dname,[fname '.mat']);

if ~exist(fullfname_mat,'file')
    Data = convertTDMS(0,fullfname_tdms);

    AccelData.t = Data.Data.MeasuredData(3).Data;
    AccelData.t = datetime(AccelData.t,'ConvertFrom','datenum','TimeZone','local');
    AccelData.t.TimeZone = 'America/Los_Angeles';

    %AccelData.Left = Data.Data.MeasuredData(4).Data;
    %AccelData.Right = Data.Data.MeasuredData(5).Data;
    AccelData.Center_X = Data.Data.MeasuredData(4).Data;
    AccelData.Center_Y = Data.Data.MeasuredData(5).Data;
    AccelData.Current_Time = Data.Data.MeasuredData(6).Data;

    save(fullfname_mat,'AccelData');
else
    load(fullfname_mat,'AccelData');
end

return

end