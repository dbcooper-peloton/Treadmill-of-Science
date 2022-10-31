
function AccelData = load_AccelData(fullfname_tdms)

fullfname_tdms = fullfile('C:\', 'Users' , 'cooper', 'Documents', 'MATLAB', 'Andy_10.24.22', 'accel_data.tdms')

% need this to use ForceData
DataRootDir = 'C:\Users\cooper\Documents\MATLAB';
Dname = 'Andy_10.24.22';
Dname = fullfile(DataRootDir,Dname);
ForceData = load_ForceData(fullfile(Dname,'load_cells_Data.tdms'));
%ForceData = load_ForceData(fullfile(fullfname_tdms));

% creating the end time vector
AccelData.endTime = ForceData.endTime;

startTime = [];
% create start time vector
for i=1:length(ForceData.footStrikeTime)
    startTime = [startTime, ForceData.footStrikeTime(:,i)];

% remove empty cells
startTime = rmmissing(startTime);
%display(startTime);

% converting datetime to seconds
AccelData.startTimeSec = second(startTime);
%display(AccelData.startTimeSec)

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
    %AccelData.Current_Time = Data.Data.MeasuredData(6).Data;
    
    % converting to seconds from datetime
    AccelData.accelTime = second(AccelData.t);
    %display(AccelData.accelTime);

    % creating empty vectors
    temp = [];
    tempX = [];

    % create empty matrixes
    mat = zeros(1,4000);
    timeMat = NaT(1,4000);

    % same timezone as time data
    timeMat.TimeZone = 'America/Los_Angeles';
     
    % creating empty indices
    j = 1;
    
    % using the endtime and startime, create a snapshot of the accel data
    if 1 == 1
       for i=1:length(AccelData.accelTime)
            % if we hit the startime, start logging
            if AccelData.startTimeSec(j) <= AccelData.accelTime(i)
                % if we're less than end time, keep logging
                if AccelData.accelTime(i) <= AccelData.endTime(j)
                    % log into vector
                    temp = [temp, [AccelData.t(i)]];
                    tempX = [tempX, [AccelData.Center_X(i)]]; 
                    % continue loop
                    continue;
                % else if we hit the end time, stop logging
                else
                    % increase index
                    j = j+1;
                    % if we reach the end of the index
                    if j == 25
                        break;
                    end
                    % log vector into matrix
                    tempX(end+1:4000) = -1;
                    mat = [mat; tempX];
                    
                    % log vector into matrix
                    temp(end+1:4000) = NaT;
                    timeMat = [timeMat; temp]; 

                    % flush
                    tempX = []; 
                    temp = [];

                end                               
            end
        end
    end

    % create workspace vector
    AccelData.footStrike = mat;
    AccelData.footStrikeTime = timeMat;

    % plot single rows
    row = 4;
    figure
    subplot 211
    plot(AccelData.footStrikeTime(row,:),AccelData.footStrike(row,:));title('single strike accel')
    subplot 212
    plot(ForceData.footStrikeTime(row,:),ForceData.footStrike(row,:));title('single strike load cell')



    %save(fullfname_mat,'AccelData');
else
    load(fullfname_mat,'AccelData');
end

return

end