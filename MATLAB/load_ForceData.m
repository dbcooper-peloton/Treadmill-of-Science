
function ForceData = load_ForceData(fullfname_tdms)

%fullfname_tdms = fullfile('C:\', 'Users' , 'cooper', 'Documents', 'MATLAB', 'ChrisP Dataset', 'load_cells_Data.tdms')

[Dname,fname,~] = fileparts(fullfname_tdms);
fullfname_mat = fullfile(Dname,[fname '.mat']);

if ~exist(fullfname_mat,'file')
    Data = convertTDMS(0,fullfname_tdms);

    ForceData.t = Data.Data.MeasuredData(3).Data;
    ForceData.t = datetime(ForceData.t,'ConvertFrom','datenum','TimeZone','local');
    ForceData.t.TimeZone = 'America/Los_Angeles';
    ForceData.t.Format = 'HH:mm:ss.SSS';

    % from Dee, Vout = 0.005(lbs force)
    G = 1/0.02; % Volts to [lbf]

    ForceData.Frnt_L = Data.Data.MeasuredData( 5).Data * G; % ch 1
    ForceData.FMid_L = Data.Data.MeasuredData(11).Data * G; % ch 7
    ForceData.BMid_L = Data.Data.MeasuredData( 8).Data * G; % ch 4
    ForceData.Back_L = Data.Data.MeasuredData(10).Data * G; % ch 6

    ForceData.Frnt_R = Data.Data.MeasuredData( 4).Data * G; % ch 0
    ForceData.FMid_R = Data.Data.MeasuredData( 6).Data * G; % ch 2
    ForceData.BMid_R = Data.Data.MeasuredData( 7).Data * G; % ch 3
    ForceData.Back_R = Data.Data.MeasuredData( 9).Data * G; % ch 5

    % butterworth filter 
    fc = 1000;
    fs = 3000;
    [b,a] = butter(6,fc/(fs/2));
    %freqz(b,a,[],fs)
    %subplot(2,1,1)
    %ylim([-100 20])

    dataInFL = ForceData.Frnt_L;
    dataInFML = ForceData.FMid_L;
    dataInBML = ForceData.BMid_L;
    dataInBL = ForceData.Back_L;
    dataInFR = ForceData.Frnt_R;
    dataInFMR = ForceData.FMid_R;
    dataInBMR = ForceData.BMid_R;
    dataInBR = ForceData.Back_R;

    dataOutFL = filter(b,a,dataInFL);
    dataOutFML = filter(b,a,dataInFML);
    dataOutBML = filter(b,a,dataInBML);
    dataOutBL = filter(b,a,dataInBL);
    dataOutFR = filter(b,a,dataInFR);
    dataOutFMR = filter(b,a,dataInFMR);
    dataOutBMR = filter(b,a,dataInBMR);
    dataOutBR = filter(b,a,dataInBR);
    
    FL_smooth = dataOutFL;
    FML_smooth = dataOutFML;
    BML_smooth = dataOutBML;
    BL_smooth = dataOutBL;
    FR_smooth = dataOutFR;
    FMR_smooth = dataOutFMR;
    BMR_smooth = dataOutBMR;
    BR_smooth = dataOutBR;

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
    %FL_smooth = ForceData.Frnt_L;
    %FML_smooth = ForceData.FMid_L;
    %BML_smooth = ForceData.BMid_L;
    %BL_smooth = ForceData.Back_L;
    %FR_smooth = ForceData.Frnt_R;
    %FMR_smooth = ForceData.FMid_R;
    %BMR_smooth = ForceData.BMid_R;
    %BR_smooth = ForceData.Back_R;


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

    ForceData.zone1 = FR_zero + FL_zero;
    ForceData.zone2 = FML_zero + FMR_zero;
    ForceData.zone3 = BMR_zero + BML_zero;
    ForceData.zone4 = BR_zero + BL_zero;

    % Snapshot Algorithm
    % if above data point is above 30 lbs, record until data point is no longer above 30 lbs
    % TODO: line this up with accel and mic data (compare time)

    % create empty vectors and matrices
    temp = [];
    timeTemp = [];

    mat = zeros(1,4000);
    timeMat = NaT(1,4000);

    tempzone1 = [];
    tempzone2 = [];
    tempzone3 = [];
    tempzone4 = [];

    matzone1 = zeros(1,4000);
    matzone2 = zeros(1,4000);
    matzone3 = zeros(1,4000);
    matzone4 = zeros(1,4000);

    endTime = [];

    % same timezone as time data
    timeMat.TimeZone = 'America/Los_Angeles';
    
    %create snap shots using non-empty data points
    for i=1:length(ForceData.sum)
        % if the data point is above 30 lbs, add to temp vector
        if ForceData.sum(i) > 30
            % create matrix for force sum
            item = ForceData.sum(i);
            temp = [temp, [item]];
            itemTime = ForceData.t(i);
            timeTemp = [timeTemp, [itemTime]];

            % create matrix for each zone
            tempzone1 = [tempzone1, [ForceData.zone1(i)]];
            tempzone2 = [tempzone2, [ForceData.zone2(i)]];
            tempzone3 = [tempzone3, [ForceData.zone3(i)]];
            tempzone4 = [tempzone4, [ForceData.zone4(i)]];

        % if data point is below 30 lbs, store temp vector as a matrix
        else
            % if the vector is longer than 2 seconds, then remove
            if length(temp) > 4000
                temp = [];
                tempzone1 = [];
                tempzone2 = [];
                tempzone3 = [];
                tempzone4 = [];
                timeTemp = [];
                continue;
            % if vector is shorter than 20 data points, then remove
            elseif length(temp) < 20
                temp = [];
                tempzone1 = [];
                tempzone2 = [];
                tempzone3 = [];
                tempzone4 = [];
                timeTemp = [];
                continue;
            % if the vector is empty, then start loop again
            elseif isempty(temp)
                continue;
            end
            
            % add data vector to data matrix
            % make the vector into a 2 second window if its not already so
            % that we are concatenating the right size vector to the matrix
            % each time
            temp(end+1:4000) = -1;
            mat = [mat; temp];

            %display(length(tempzone1));
            %display(lenght(temp));

            tempzone1(end+1:4000) = -1;
            matzone1 = [matzone1; tempzone1];

            tempzone2(end+1:4000) = -1;
            matzone2 = [matzone2; tempzone2];

            tempzone3(end+1:4000) = -1;
            matzone3 = [matzone3; tempzone3];

            tempzone4(end+1:4000) = -1;
            matzone4 = [matzone4; tempzone4];

            %grab end time
            endTime = [endTime, timeTemp(end)];

            % add time vector to time matrix
            timeTemp(end+1:4000) = NaT;
            timeMat = [timeMat; timeTemp]; 
            
    
            temp = []; 
            tempzone1 = [];
            tempzone2 = [];
            tempzone3 = [];
            tempzone4 = [];
            timeTemp = [];
        end
    end

    % create workspace vectors
    ForceData.footStrike = mat;
    ForceData.footStrikeTime = timeMat; 

    ForceData.footStrikeZone1 = matzone1;
    ForceData.footStrikeZone2 = matzone2;
    ForceData.footStrikeZone3 = matzone3;
    ForceData.footStrikeZone4 = matzone4;
    
    
    % create endtime workspace vector
    % endTime = second(endTime);
    ForceData.endTime = endTime';
   

    save(fullfname_mat,'ForceData');
else
    load(fullfname_mat,'ForceData');
end

return