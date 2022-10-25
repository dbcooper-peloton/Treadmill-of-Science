function ForceData = load_ForceData(fullfname_tdms)
fullfname_tdms = fullfile('C:\', 'Users' , 'cooper', 'Documents', 'MATLAB', 'Mic Test 9_30', 'load_cells_Data.tdms')
[Dname,fname,~] = fileparts(fullfname_tdms);
fullfname_mat = fullfile(Dname,[fname '.mat']);
if ~exist(fullfname_mat,'file')
    Data = convertTDMS(0,fullfname_tdms);
    ForceData.t = Data.Data.MeasuredData(3).Data;
    ForceData.t = datetime(ForceData.t,'ConvertFrom','datenum','TimeZone','local');
    ForceData.t.TimeZone = 'America/Los_Angeles';
    % from Dee, Vout = 0.005(lbs force)
    G = 1/0.005; % Volts to [lbf]
    ForceData.Frnt_L = Data.Data.MeasuredData( 5).Data * G; % ch 1
    ForceData.FMid_L = Data.Data.MeasuredData(11).Data * G; % ch 7
    ForceData.BMid_L = Data.Data.MeasuredData( 8).Data * G; % ch 4
    ForceData.Back_L = Data.Data.MeasuredData(10).Data * G; % ch 6
    ForceData.Frnt_R = Data.Data.MeasuredData( 4).Data * G; % ch 0
    ForceData.FMid_R = Data.Data.MeasuredData( 6).Data * G; % ch 2
    ForceData.BMid_R = Data.Data.MeasuredData( 7).Data * G; % ch 3
    ForceData.Back_R = Data.Data.MeasuredData( 9).Data * G; % ch 5
    % smooth data
    %FL_smooth = smoothdata(ForceData.Frnt_L);
    %FML_smooth = smoothdata(ForceData.FMid_L);
    %BML_smooth = smoothdata(ForceData.BMid_L);
    %BL_smooth = smoothdata(ForceData.Back_L);
    %FR_smooth = smoothdata(ForceData.Frnt_R);
    %FMR_smooth = smoothdata(ForceData.FMid_R);
    %BMR_smooth = smoothdata(ForceData.BMid_R);
    %BR_smooth = smoothdata(ForceData.Back_R);
    % don't smooth data
    FL_smooth = ForceData.Frnt_L;
    FML_smooth = ForceData.FMid_L;
    BML_smooth = ForceData.BMid_L;
    BL_smooth = ForceData.Back_L;
    FR_smooth = ForceData.Frnt_R;
    FMR_smooth = ForceData.FMid_R;
    BMR_smooth = ForceData.BMid_R;
    BR_smooth = ForceData.Back_R;
    % 2khz = 2,000 cycles/second
    % 1 sec =  2,000 data points
    FL_short = FL_smooth(1:2000);
    FML_short = FML_smooth(1:2000);
    BML_short = BML_smooth(1:2000);
    BL_short = BL_smooth(1:2000);
    FR_short = FR_smooth(1:2000);
    FMR_short = FMR_smooth(1:2000);
    BMR_short = BMR_smooth(1:2000);
    BR_short = BR_smooth(1:2000);
    % find average of each shortened data point using mean()
    % ForceData.average = mean(ForceData.sum);
    FL_av = mean(FL_short);
    FML_av = mean(FML_short);
    BML_av = mean(BML_short);
    BL_av = mean(BL_short);
    FR_av = mean(FR_short);
    FMR_av = mean(FMR_short);
    BMR_av = mean(BMR_short);
    BR_av = mean(BR_short);
    % zero out forces by subtracting mean from each data point
    FL_zero = FL_smooth - FL_av;
    FML_zero = FML_smooth - FML_av;
    BML_zero = BML_smooth - BML_av;
    BL_zero = BL_smooth - BL_av;
    FR_zero = FR_smooth - FR_av;
    FMR_zero = FMR_smooth - FMR_av;
    BMR_zero = BMR_smooth - BMR_av;
    BR_zero = BR_smooth - BR_av;
    % test
    %display(ForceData.Frnt_L)
    %display(FL_short)
    %display(FL_av)
    %display(FL_zero)
    % sum forces after being zeroed
    ForceData.sum = FL_zero+...
         FML_zero+...
         BML_zero+...
         BL_zero+...
         FR_zero+...
         FMR_zero+...
         BMR_zero+...
         BR_zero;
    % TODO: create Snapshot algo
    % if above data point is above 20 lbs and less than 0.35 seconds, record until data point is no longer above 20 lbs
    % line this up with accel and mic data (compare time)
    % if weight is above 20 lbs, store in an array until weight drops below
    % 20 lbs
    temp = [];
    mat = zeros(1,4000);
    %create snap shots using non-empty data points
    for i=60000:length(ForceData.sum)
        %display(mat);
        % if the data point is not empty, add to temp vector
        if ForceData.sum(i) > 20;
            %x = ForceData.sum;
            item = ForceData.sum(i);
            temp = [temp, [item]];
            %display(temp);
            %ForceData.mat(i,:) = temp;
        % if data point is empty, store temp vector as a structure
        else
            %if length(temp) > 40000;
            %    temp = [];
            %    continue;
            %elseif isempty(temp);
            %    continue;
            %end
            if isempty(temp);
                continue;
            end
            %display(temp);
            temp(end+1:4000) = -1;
            %display(temp);
            mat(i, :) = temp;
            temp = [];
            %ForceData.s(i).temp=temp(i);
        end
    end

    ForceData.mat = mat;
    display(mat);
    %save(fullfname_mat,'ForceData');
else
    load(fullfname_mat,'ForceData');
end
return









