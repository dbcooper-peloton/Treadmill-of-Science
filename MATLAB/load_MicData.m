function MicData = load_MicData(fullfname_tdms)

%fullfname_tdms = fullfile('C:\', 'Users' , 'cooper', 'Documents', 'MATLAB', 'XSensorIMU Test', 'mic_data.tdms')

[Dname,fname,~] = fileparts(fullfname_tdms);
fullfname_mat = fullfile(Dname,[fname '.mat']);

if ~exist(fullfname_mat,'file')
    Data = convertTDMS(0,fullfname_tdms);

    MicData.t = Data.Data.MeasuredData(3).Data;
    MicData.t = datetime(MicData.t,'ConvertFrom','datenum','TimeZone','local');
    MicData.t.TimeZone = 'America/Los_Angeles';

    G = 1/(3.3/2); % [unknown]
    Bias = 3.3/2;
    MicData.Frnt_L = (Data.Data.MeasuredData(4).Data-Bias) * G;
    MicData.Back_L = (Data.Data.MeasuredData(5).Data-Bias) * G;
    MicData.Frnt_R = (Data.Data.MeasuredData(7).Data-Bias) * G;
    MicData.Back_R = (Data.Data.MeasuredData(6).Data-Bias) * G;

    %MicData.Frnt_L = MicData.Frnt_L - mean(MicData.Frnt_L);
    %MicData.Back_L = MicData.Back_L - mean(MicData.Back_L);
    %MicData.Frnt_R = MicData.Frnt_R - mean(MicData.Frnt_R);
    %MicData.Back_R = MicData.Back_R - mean(MicData.Back_R);

    %Ts = mean(seconds(diff(t_Mic)));
    %Fs = 1/Ts;
    %Fc = 1000;
    %Mic_LeftFront = lopass(Mic_LeftFront,Fs,Fc);
    %Mic_LeftBack = lopass(Mic_LeftBack,Fs,Fc);
    %Mic_RightBack = lopass(Mic_RightBack,Fs,Fc);
    %Mic_RightFront = lopass(Mic_RightFront,Fs,Fc);

    save(fullfname_mat,'MicData');
else
    load(fullfname_mat,'MicData');
end

return