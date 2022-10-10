function DopplerData = load_DopplerData(fullfname_tdms)

%fullfname_tdms = fullfile('C:\', 'Users' , 'cooper', 'Documents', 'MATLAB', 'XSensorIMU Test', 'Belt_Speed.tdms')


[Dname,fname,~] = fileparts(fullfname_tdms);
fullfname_mat = fullfile(Dname,[fname '.mat']);

if ~exist(fullfname_mat,'file')
    Data = convertTDMS(0,fullfname_tdms);

    DopplerData.t = Data.Data.MeasuredData(3).Data;
    DopplerData.t = datetime(DopplerData.t,'ConvertFrom','datenum','TimeZone','local');
    DopplerData.t.TimeZone = 'America/Los_Angeles';

    DopplerData.Doppler = Data.Data.MeasuredData(4).Data;

    % preprocess to calculate velocity
    % Edge to edge 

    save(fullfname_mat,'DopplerData');
else
    load(fullfname_mat,'DopplerData');
end

return