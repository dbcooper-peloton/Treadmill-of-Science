function MicData = load_MicData(fullfname_tdms)

%fullfname_tdms = fullfile('C:\', 'Users' , 'cooper', 'Documents', 'MATLAB', 'ChrisP Dataset', 'mic_data.tdms')

[Dname,fname,~] = fileparts(fullfname_tdms);
fullfname_mat = fullfile(Dname,[fname '.mat']);

% creating the end and start time vector from ForceData
ForceData = load_ForceData(fullfile(Dname,'load_cells_Data.tdms'));
MicData.endTime = ForceData.endTime;
startTime = ForceData.footStrikeTime(:,1);

% remove empty cells
startTime = rmmissing(startTime);

% assign mic start time vector to force start time vector
MicData.startTimeSec = (startTime);

% check first if MATLAB converted TDMS file exists, if not then convert
% TDMS into MATLAB file
if ~exist(fullfname_mat,'file')
    Data = convertTDMS(0,fullfname_tdms);

    MicData.t = Data.Data.MeasuredData(3).Data;
    MicData.t = datetime(MicData.t,'ConvertFrom','datenum','TimeZone','local');
    MicData.t.TimeZone = 'America/Los_Angeles';
    MicData.t.Format = 'HH:mm:ss.SSS';

    % TODO: figure out scaling
    G = 1/(3.3/2); % [unknown]
    Bias = 3.3/2;
    MicData.Frnt_L = (Data.Data.MeasuredData(4).Data-Bias) * G;
    MicData.Back_L = (Data.Data.MeasuredData(5).Data-Bias) * G;
    MicData.Frnt_R = (Data.Data.MeasuredData(7).Data-Bias) * G;
    MicData.Back_R = (Data.Data.MeasuredData(6).Data-Bias) * G;

    MicData.sum = MicData.Frnt_L+MicData.Back_L+MicData.Frnt_R+MicData.Back_R;

    %Ts = mean(seconds(diff(t_Mic)));
    %Fs = 1/Ts;
    %Fc = 1000;
    %Mic_LeftFront = lopass(Mic_LeftFront,Fs,Fc);
    %Mic_LeftBack = lopass(Mic_LeftBack,Fs,Fc);
    %Mic_RightBack = lopass(Mic_RightBack,Fs,Fc);
    %Mic_RightFront = lopass(Mic_RightFront,Fs,Fc);

    %Butterworth Filter on sum of X
    fc = 50;
    fs = 40000;
    [b,a] = butter(6,fc/(fs/2));
    %freqz(b,a,[],fs)

    % Filter FL data
    FLdataIn = MicData.Frnt_L;
    FLdataOut = filter(b,a,FLdataIn);
    MicData.Frnt_L_BW = FLdataOut;

    % Filter BL data
    BLdataIn = MicData.Back_L;
    BLdataOut = filter(b,a,BLdataIn);
    MicData.Back_L_BW = BLdataOut;

    % Filter FR data
    FRdataIn = MicData.Frnt_R;
    FRdataOut = filter(b,a,FRdataIn);
    MicData.Frnt_R_BW = FRdataOut;

    % Filter BR data
    BRdataIn = MicData.Back_R;
    BRdataOut = filter(b,a,BRdataIn);
    MicData.Back_R_BW = BRdataOut;

    % ZERO OUT DATA

    % 40khz = 40,000 cycles/second
    % 1 sec =  40,000 data points 
    % find average of each shortened data point using mean()
    % ForceData.average = mean(ForceData.sum);
    FL_av = mean(MicData.Frnt_L_BW(1:40000));
    BL_av = mean(MicData.Back_L_BW(1:40000));
    FR_av = mean(MicData.Frnt_R_BW(1:40000));
    BR_av = mean(MicData.Back_R_BW(1:40000));
    % zero out forces by subtracting mean from each data point
    FL_zero = MicData.Frnt_L_BW - FL_av;
    BL_zero = MicData.Back_L_BW - BL_av;
    FR_zero = MicData.Frnt_R_BW - FR_av; 
    BR_zero = MicData.Back_R_BW - BR_av; 

    % converting to seconds from datetime
    MicData.accelTime = (MicData.t);

    % creating empty vectors
    tempTime = [];
    tempFrontL = [];
    tempBackL = [];
    tempFrontR = [];
    tempBackR = [];
    tempSum = [];

    % create empty matrixes
    matFrontL = zeros(1,100000);
    matBackL = zeros(1,100000);
    matFrontR = zeros(1,100000);
    matBackR = zeros(1,100000);
    matSum = zeros(1,100000);
    timeMat = NaT(1,100000);

    % same timezone as time data
    timeMat.TimeZone = 'America/Los_Angeles';
     
    % creating empty indices
    j = 1;
    
    % using the endtime and startime, create a snapshot of the FRONT LEFT mic data
    if 1 == 1
       for i=1:length(MicData.accelTime)
            % if we hit the startime, start logging
            if MicData.startTimeSec(j) <= MicData.accelTime(i)
                % if we're less than end time, keep logging
                if MicData.accelTime(i) <= MicData.endTime(j)
                    % log into vector
                    tempTime = [tempTime, [MicData.t(i)]];
                    tempFrontL = [tempFrontL, [FL_zero(i)]]; 
                    tempBackL = [tempBackL, [BL_zero(i)]]; 
                    tempFrontR = [tempFrontR, [FR_zero(i)]]; 
                    tempBackR = [tempBackR, [BR_zero(i)]]; 
                    tempSum = [tempSum, [MicData.sum(i)]]; 

                    % continue loop
                    continue;
                % else if we hit the end time, stop logging
                else                 
                    % if we reach the end of the index, stop logging
                    if j == length(MicData.endTime)
                        break;
                    % if the vector is empty, then start loop again
                    elseif isempty(tempTime)
                        continue;
                    end
                    % log vectors into corresponding matrices
                    tempFrontL(end+1:100000) = -1;
                    matFrontL = [matFrontL; tempFrontL];
                    
                    tempBackL(end+1:100000) = -1;
                    matBackL = [matBackL; tempBackL];
                    
                    tempFrontR(end+1:100000) = -1;
                    matFrontR = [matFrontR; tempFrontR];
                    
                    tempBackR(end+1:100000) = -1;
                    matBackR = [matBackR; tempBackR];

                    tempSum(end+1:100000) = -1;
                    matSum = [matSum; tempSum];
                    
                    % log vector into matrix
                    tempTime(end+1:100000) = NaT;
                    timeMat = [timeMat; tempTime]; 

                    % flush
                    tempFrontL = []; 
                    tempBackL = [];
                    tempFrontR = [];
                    tempBackR = [];
                    tempTime = [];
                    tempSum = [];

                    % increase index
                    j = j+1;

                end                               
            end
        end
    end

    % create workspace vector
    MicData.footStrikeFL = matFrontL;
    MicData.footStrikeBL = matBackL;
    MicData.footStrikeFR = matFrontR;
    MicData.footStrikeBR = matBackR;

    MicData.footStrikeSum = matSum;

    MicData.footStrikeTime = timeMat;
    
    save(fullfname_mat,'MicData');
else
    load(fullfname_mat,'MicData');
end

return