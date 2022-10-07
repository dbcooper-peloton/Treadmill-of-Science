function ForceData = load_ForceData(fullfname_tdms)

%fullfname_tdms = fullfile('C:\', 'Users' , 'cooper', 'Documents', 'MATLAB', 'XSensorIMU Test', 'load_cells_Data.tdms')


[Dname,fname,~] = fileparts(fullfname_tdms);
fullfname_mat = fullfile(Dname,[fname '.mat']);

if ~exist(fullfname_mat,'file')
    Data = convertTDMS(0,fullfname_tdms);

    ForceData.t = Data.Data.MeasuredData(3).Data;
    ForceData.t = datetime(ForceData.t,'ConvertFrom','datenum','TimeZone','local');
    ForceData.t.TimeZone = 'America/Los_Angeles';

    % from Dee, Vout = 0.005(lbs force)
    G = 1/0.005; % Volts to [lbf]

    ForceData.Frnt_L = Data.Data.MeasuredData( 5).Data * G; % ch 1
    ForceData.FMid_L = Data.Data.MeasuredData(11).Data * G; % ch 7
    ForceData.BMid_L = Data.Data.MeasuredData( 8).Data * G; % ch 4
    ForceData.Back_L = Data.Data.MeasuredData(10).Data * G; % ch 6

    ForceData.Frnt_R = Data.Data.MeasuredData( 4).Data * G; % ch 0
    ForceData.FMid_R = Data.Data.MeasuredData( 6).Data * G; % ch 2
    ForceData.BMid_R = Data.Data.MeasuredData( 7).Data * G; % ch 3
    ForceData.Back_R = Data.Data.MeasuredData( 9).Data * G; % ch 5
    
    save(fullfname_mat,'ForceData');
else
    load(fullfname_mat,'ForceData');
end

return