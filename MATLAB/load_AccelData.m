
function AccelData = load_AccelData(fullfname_tdms)

%fullfname_tdms = fullfile('C:\', 'Users' , 'cooper', 'Documents', 'MATLAB', 'ChrisP Dataset', 'accel_data.tdms')

[Dname,fname,~] = fileparts(fullfname_tdms);
fullfname_mat = fullfile(Dname,[fname '.mat']);

% need this to use ForceData
ForceData = load_ForceData(fullfile(Dname,'load_cells_Data.tdms'));

% creating the end time vector
AccelData.endTime = ForceData.endTime;

% startTime = [];
% create start time vector
startTime = ForceData.footStrikeTime(:,1);

% remove empty cells
startTime = rmmissing(startTime);
%display(startTime);

%display(startTime);

AccelData.startTimeSec = startTime;

% converting datetime to seconds
%AccelData.startTimeSec = second(startTime);
%AccelData.startTimeSec = datenum(startTime, 'HH:MM:SS.SSS');

%display(AccelData.startTimeSec)


if ~exist(fullfname_mat,'file')
    Data = convertTDMS(0,fullfname_tdms);

    AccelData.t = Data.Data.MeasuredData(3).Data;
    AccelData.t = datetime(AccelData.t,'ConvertFrom','datenum','TimeZone','local');
    AccelData.t.TimeZone = 'America/Los_Angeles';
    AccelData.t.Format = 'HH:mm:ss.SSS';

    %AccelData.Left = Data.Data.MeasuredData(4).Data;
    %AccelData.Right = Data.Data.MeasuredData(5).Data;
    AccelData.Center_X = Data.Data.MeasuredData(4).Data;
    AccelData.Center_Y = Data.Data.MeasuredData(5).Data;
    %AccelData.Current_Time = Data.Data.MeasuredData(6).Data;

    %Butterworth Filter on sum of X
    fc = 1000;
    fs = 3000;
    
    [b,a] = butter(6,fc/(fs/2));
    freqz(b,a,[],fs)
    
    %subplot(2,1,1)
    %ylim([-100 20])
    
    % Filter X data
    XdataIn = AccelData.Center_X;
    XdataOut = filter(b,a,XdataIn);
    AccelData.Center_X_BW = XdataOut;

    % Filter Y data
    YdataIn = AccelData.Center_Y;
    YdataOut = filter(b,a,YdataIn);
    AccelData.Center_Y_BW = YdataOut;
    
    % converting to seconds from datetime
    AccelData.accelTime = AccelData.t;
    %display(AccelData.accelTime);

    % creating empty vectors
    temp = [];
    tempX = [];
    tempY = [];

    % create empty matrixes
    matX = zeros(1,10000);
    matY = zeros(1,10000);
    timeMat = NaT(1,10000);

    % same timezone as time data
    timeMat.TimeZone = 'America/Los_Angeles';
     
    % creating empty indices
    j = 1;
    
    % using the endtime and startime, create a snapshot of the accel data
    if 1 == 1
       for i=1:length(AccelData.accelTime)
            % if we hit the startime, start logging
            if AccelData.startTimeSec(j) <= AccelData.accelTime(i)
                %display(i);
                % if we're less than end time, keep logging
                if AccelData.accelTime(i) <= AccelData.endTime(j)
                    % log into vector
                    temp = [temp, [AccelData.t(i)]];
                    tempX = [tempX, [AccelData.Center_X_BW(i)]]; 
                    tempY = [tempY, [AccelData.Center_Y_BW(i)]];
                    % continue loop
                    % continue;
                % else if we hit the end time, stop logging
                else
                    % if we reach the end of the index
                    if j == length(AccelData.endTime)
                        break;
                    % if the vector is empty, then start loop again
                    elseif isempty(temp)
                        continue;
                    end
                    % log vector into X matrix
                    tempX(end+1:10000) = -1;
                    matX = [matX; tempX];

                    % log vector into Y matrix
                    tempY(end+1:10000) = -1;
                    matY = [matY; tempY];
                    
                    % log vector into matrix
                    %display(temp);
                    temp(end+1:10000) = NaT;
                    timeMat = [timeMat; temp]; 

                    % flush
                    tempX = []; 
                    tempY = [];
                    temp = [];

                    % increase index
                    j = j+1;

                end                               
            end
        end
    end

    %display(AccelData.accelTime(126000));
    %display(length(AccelData.endTime));
    %display(j);

    % create workspace vector
    AccelData.footStrikeX = matX;
    AccelData.footStrikeY = matY;
    AccelData.footStrikeTime = timeMat;

    save(fullfname_mat,'AccelData');
else
    load(fullfname_mat,'AccelData');
end

return