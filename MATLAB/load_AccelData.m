
function AccelData = load_AccelData(fullfname_tdms)

fullfname_tdms = fullfile('C:\', 'Users' , 'cooper', 'Documents', 'MATLAB', 'Andy_10.24.22', 'accel_data.tdms')

% need this to use ForceData
DataRootDir = 'C:\Users\cooper\Documents\MATLAB';
Dname = 'Andy_10.24.22';
Dname = fullfile(DataRootDir,Dname);

ForceData = load_ForceData(fullfile(Dname,'load_cells_Data.tdms'));

%ForceData.mat
%ForceData.timeMat

AccelData.endTime = ForceData.endTime;

startTime = [];
% create start time vector
for i=1:length(ForceData.timeMat)
    startTime = [startTime, ForceData.timeMat(:,i)];

startTime = rmmissing(startTime);
%display(startTime);

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
    
    AccelData.accelTime = second(AccelData.t);
    %display(AccelData.accelTime);

    temp = [];
    tempX = [];
     
    j = 1;
    jj = 1;
    
    if 1 == 1
       for i=1:length(AccelData.accelTime)
            %if j > numel(AccelData.startTimeSec)
            %        break;
                %display(startTime(1))
                %display(AccelData.t(i))
                %display(AccelData.startTimeSec(j));
                %display(AccelData.accelTime(i));
                if AccelData.startTimeSec(j) < AccelData.accelTime(i) %&& AccelData.accelTime(i) < AccelData.endTime(j) 
                    jj = jj+1;
                    if AccelData.accelTime(i) < AccelData.endTime(j)
                        continue;
                    end
                    temp = [temp; AccelData.accelTime(i)];
                    tempX = [tempX; AccelData.Center_X(i)];
                    %display(tempX)
                    j = j+1;
                    if j == 25
                        break;
                    end
                end
            %end
        end
    end

    display(tempX);
    display(j);
    display(jj);

    plot(temp, tempX);


    %save(fullfname_mat,'AccelData');
else
    load(fullfname_mat,'AccelData');
end

return

end