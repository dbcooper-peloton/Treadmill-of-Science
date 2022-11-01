function MicData = load_MicData(fullfname_tdms)

%fullfname_tdms = fullfile('C:\', 'Users' , 'cooper', 'Documents', 'MATLAB', 'ChrisP Dataset', 'mic_data.tdms')

[Dname,fname,~] = fileparts(fullfname_tdms);
fullfname_mat = fullfile(Dname,[fname '.mat']);

% need this to use ForceData
ForceData = load_ForceData(fullfile(Dname,'load_cells_Data.tdms'));

% creating the end time vector
MicData.endTime = ForceData.endTime;
%display(length(MicData.endTime));

% create start time vector
startTime = ForceData.footStrikeTime(:,1);

% remove empty cells
startTime = rmmissing(startTime);
%display(startTime);

% converting datetime to seconds
MicData.startTimeSec = (startTime);
%MicData.startTimeSec = convertTo(startTime, '.net');

if ~exist(fullfname_mat,'file')
    Data = convertTDMS(0,fullfname_tdms);

    MicData.t = Data.Data.MeasuredData(3).Data;
    MicData.t = datetime(MicData.t,'ConvertFrom','datenum','TimeZone','local');
    MicData.t.TimeZone = 'America/Los_Angeles';
    MicData.t.Format = 'HH:mm:ss.SSS';

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

    % converting to seconds from datetime
    MicData.accelTime = (MicData.t);
    %display(AccelData.accelTime);

    % creating empty vectors
    tempTime = [];
    tempFrontL = [];
    tempBackL = [];
    tempFrontR = [];
    tempBackR = [];


    % create empty matrixes
    matFrontL = zeros(1,100000);
    matBackL = zeros(1,100000);
    matFrontR = zeros(1,100000);
    matBackR = zeros(1,100000);

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
                    tempFrontL = [tempFrontL, [MicData.Frnt_L(i)]]; 
                    tempBackL = [tempBackL, [MicData.Back_L(i)]]; 
                    tempFrontR = [tempFrontL, [MicData.Frnt_R(i)]]; 
                    tempBackR = [tempFrontL, [MicData.Back_R(i)]]; 

                    % continue loop
                    continue;
                % else if we hit the end time, stop logging
                else                 
                    % if we reach the end of the index
                    if j == length(MicData.endTime)
                        break;
                    % if the vector is empty, then start loop again
                    elseif isempty(tempTime)
                        continue;
                    end
                    % log vector into matrix
                    %display(length(tempFrontL));
                    tempFrontL(end+1:100000) = -1;
                    %display(length(tempFrontL));
                    matFrontL = [matFrontL; tempFrontL];
                    
                    tempBackL(end+1:100000) = -1;
                    matBackL = [matBackL; tempBackL];
                    
                    tempFrontR(end+1:100000) = -1;
                    matFrontR = [matFrontR; tempFrontR];
                    
                    tempBackR(end+1:100000) = -1;
                    matBackR = [matBackR; tempBackR];
                    
                    % log vector into matrix
                    tempTime(end+1:100000) = NaT;
                    timeMat = [timeMat; tempTime]; 

                    % flush
                    tempFrontL = []; 
                    tempBackL = [];
                    tempFrontR = [];
                    tempBackR = [];
                    tempTime = [];

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

    MicData.footStrikeTime = timeMat;
    

    save(fullfname_mat,'MicData');
else
    load(fullfname_mat,'MicData');
end

return