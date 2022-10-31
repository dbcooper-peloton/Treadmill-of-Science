
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
     
    % creating empty indices
    j = 1;
    jj = 1;

    %display(length(AccelData.endTime));
    
    % using the endtime and startime, create a snapshot of the accel data
    if 1 == 1
       for i=1:length(AccelData.accelTime)
            % if we hit the startime, start logging
            if AccelData.startTimeSec(j) < AccelData.accelTime(i)
                jj = jj+1;
                % if we hit end time, stop logging
                if AccelData.accelTime(i) < AccelData.endTime(j)
                    continue;
                end
                temp = [temp, [AccelData.accelTime(i)]];
                tempX = [tempX, [AccelData.Center_X(i)]];
                
                % increase index
                j = j+1;

                % if we reach the end of the index
                if j == 25
                    break;
                end
                
            end
        end
    end

    % create workspace vector
    AccelData.footStrike = tempX;
    AccelData.footStrikeTime = temp;

    % plot single rows
    %row = 4;
    %figure
    %plot(AccelData.footStrikeTime(row,:),AccelData.footStrike(row,:));title('single strike')


    %save(fullfname_mat,'AccelData');
else
    load(fullfname_mat,'AccelData');
end

return

end