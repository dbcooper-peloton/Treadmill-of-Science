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
    % (change in time)/(change in pulse rate)
    % change in time = timenow - timeprev
    % change in pulse rate = pulseratenow - pulserateprev
    % pulseratenow = pulse count now/time in minutes now
    % pulserateprev = pulse count prev/time in minutes prev

    
    

    %calc time 
    %timesec = second(DopplerData.t);
    time = second(DopplerData.t);
    %disp(time)
    %disp(time);
    pulse = DopplerData.Doppler;
    %disp(pulse);
    %calc pulse rate
    pulserate = [0;(pulse)/(65535)];
    %disp(pulserate)

    %calc change in pulse rate
    changeinpulserate = [0;diff(pulserate)];
    changeinpulserate(1) = [];
    %disp(changeinpulserate)
    %calc change in time 
    changeintime = [0;diff(time)];


    % change in time/ change in pulse rate
    velocity = [0;(changeinpulserate)./(changeintime)];
    velocity(1) = [];

    DopplerData.velocity = velocity*60;
    DopplerData.mph = velocity/1.46666667;
    %disp(DopplerData.velocity)
    %disp(DopplerData.velocity)

    %DopplerData.t = timemin;
    DopplerData.sec = time;
    %disp(DopplerData.sec)

    save(fullfname_mat,'DopplerData');
else
    load(fullfname_mat,'DopplerData');
end

return