function EncoderData = load_EncoderData(fullfname_tdms)

fullfname_tdms = fullfile('C:\', 'Users' , 'cooper', 'Documents', 'MATLAB', 'NoRunner_2MPH_800K', 'Torque_Position.tdms');


[Dname,fname,~] = fileparts(fullfname_tdms);
fullfname_mat = fullfile(Dname,[fname '.mat']);


if ~exist(fullfname_mat,'file')
    Data = convertTDMS(0,fullfname_tdms);

    EncoderData.t = Data.Data.MeasuredData(3).Data;
    EncoderData.t = datetime(EncoderData.t,'ConvertFrom','datenum','TimeZone','local');
    EncoderData.t.TimeZone = 'America/Los_Angeles';

    EncoderData.Encoder = Data.Data.MeasuredData(4).Data;

    %EncoderData.vel = EncoderData.Encoder/EncoderData.t;

    % preprocess to calculate RPM
    % RPM = pulses/360
    %diff1 = [0;(diff(EncoderData.Encoder))];
    %disp(diff1)
    %plot(diff1);
    
    %velocity = [0;(diff(EncoderData.Encoder))/360];
    velocity = [0;((EncoderData.Encoder).*60)/360];
    velocity(isnan(velocity))=0;
    % remove first element so that its the same lenght as time
    velocity(1) = [];

    EncoderData.vel = velocity;
    

    save(fullfname_mat,'EncoderData');
else
    load(fullfname_mat,'EncoderData');
end

return