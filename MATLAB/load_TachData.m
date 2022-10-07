function TachData = load_TachData(fullfname_tdms)

%fullfname_tdms = fullfile('C:\', 'Users' , 'cooper', 'Documents', 'MATLAB', 'XSensorIMU Test', 'Tach_Data.tdms')


[Dname,fname,~] = fileparts(fullfname_tdms);
fullfname_mat = fullfile(Dname,[fname '.mat']);

if ~exist(fullfname_mat,'file')
    Data = convertTDMS(0,fullfname_tdms);

    TachData.t = Data.Data.MeasuredData(3).Data;
    TachData.t = datetime(TachData.t,'ConvertFrom','datenum','TimeZone','local');
    TachData.t.TimeZone = 'America/Los_Angeles';

    TachData.Tach = Data.Data.MeasuredData(4).Data;

    % preprocess to calcualte velocity
    dTach = [0;diff(TachData.Tach)];
    i = find(dTach>0.5);

    PPR = 24; % pulses per revolution
    intTach = cumsum(TachData.Tach(i))/PPR;
    intTach = interp1(TachData.t(i),intTach,TachData.t,'linear',NaN);

    tsec = second(TachData.t);
    vel = [0;diff(intTach)./diff(tsec)];
    vel(isnan(vel))=0;
    TachData.vel = vel * (2*pi); % [rad/s]

    save(fullfname_mat,'TachData');
else
    load(fullfname_mat,'TachData');
end

return