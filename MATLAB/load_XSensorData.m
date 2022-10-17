function XSNData = load_XSensorData(fullfname)


% read header, parse start time
fid = fopen(fullfname);
tline = fgetl(fid);
fclose(fid);

if strncmp(tline,'LogFileVersion',14)
    % file is our internal format
    [Time,S_L,S_R,SenselArea] = readfile_fromInternalSW(fullfname);
elseif strncmp(tline(3:7),'File:',5)
    % file is XSensor SW export format
    [Time,S_L,S_R,SenselArea] = readfile_fromXsensorSW(fullfname);
else
    error('unknown xsn file format');
end

% feature extraction
load FootMapsLogical.mat
FootMap_L = FootMaps.LeftToe | FootMaps.LeftMetatarsal | FootMaps.LeftMid | FootMaps.LeftHeel;
FootMap_R = FootMaps.RightToe | FootMaps.RightMetatarsal | FootMaps.RightMid | FootMaps.RightHeel;
N_FootMap = sum(FootMap_L,'all'); % right is the same, mirrored
N_ToeMap = sum(FootMaps.LeftToe,'all'); % right is the same, mirrored
N_MetMap = sum(FootMaps.LeftMetatarsal,'all'); % right is the same, mirrored
N_MidMap = sum(FootMaps.LeftMid,'all'); % right is the same, mirrored
N_HelMap = sum(FootMaps.LeftHeel,'all'); % right is the same, mirrored

L = size(S_L,3);
AvgP_L = zeros(L,1);
AvgP_R = zeros(L,1);
ContactPercent_L = zeros(L,1);
ContactPercent_R = zeros(L,1);
AvgP_Toe_L = zeros(L,1);
AvgP_Met_L = zeros(L,1);
AvgP_Mid_L = zeros(L,1);
AvgP_Hel_L = zeros(L,1);
AvgP_Toe_R = zeros(L,1);
AvgP_Met_R = zeros(L,1);
AvgP_Mid_R = zeros(L,1);
AvgP_Hel_R = zeros(L,1);

Fest_Toe_L = zeros(L,1);
Fest_Met_L = zeros(L,1);
Fest_Mid_L = zeros(L,1);
Fest_Hel_L = zeros(L,1);
Fest_Toe_R = zeros(L,1);
Fest_Met_R = zeros(L,1);
Fest_Mid_R = zeros(L,1);
Fest_Hel_R = zeros(L,1);
for i=1:L
    S_R_frame = S_R(:,:,i);
    S_L_frame = S_L(:,:,i);
    
    ContactPercent_L(i) = max(N_FootMap - sum(S_L_frame(FootMap_L)==0),1)/N_FootMap;
    ContactPercent_R(i) = max(N_FootMap - sum(S_R_frame(FootMap_R)==0),1)/N_FootMap;

    AvgP_L(i) = sum( S_L_frame(FootMap_L), 'all' ) / (N_FootMap*ContactPercent_L(i));
    AvgP_R(i) = sum( S_R_frame(FootMap_R), 'all' ) / (N_FootMap*ContactPercent_R(i));

    AvgP_Toe_L(i) = sum( S_L_frame(FootMaps.LeftToe), 'all' ) / max(N_ToeMap - sum(S_L_frame(FootMaps.LeftToe)==0),1);
    AvgP_Met_L(i) = sum( S_L_frame(FootMaps.LeftMetatarsal), 'all' ) / max(N_MetMap - sum(S_L_frame(FootMaps.LeftMetatarsal)==0),1);
    AvgP_Mid_L(i) = sum( S_L_frame(FootMaps.LeftMid), 'all' ) / max(N_MidMap - sum(S_L_frame(FootMaps.LeftMid)==0),1);
    AvgP_Hel_L(i) = sum( S_L_frame(FootMaps.LeftHeel), 'all' ) / max(N_HelMap - sum(S_L_frame(FootMaps.LeftHeel)==0),1);
    
    AvgP_Toe_R(i) = sum( S_R_frame(FootMaps.RightToe), 'all' ) / max(N_ToeMap - sum(S_R_frame(FootMaps.RightToe)==0),1);
    AvgP_Met_R(i) = sum( S_R_frame(FootMaps.RightMetatarsal), 'all' ) / max(N_MetMap - sum(S_R_frame(FootMaps.RightMetatarsal)==0),1);
    AvgP_Mid_R(i) = sum( S_R_frame(FootMaps.RightMid), 'all' ) / max(N_MidMap - sum(S_R_frame(FootMaps.RightMid)==0),1);
    AvgP_Hel_R(i) = sum( S_R_frame(FootMaps.RightHeel), 'all' ) / max(N_HelMap - sum(S_R_frame(FootMaps.RightHeel)==0),1);

    % scale to Force from Pressure
    CP = max(N_ToeMap - sum(S_L_frame(FootMaps.LeftToe)==0),1)/N_ToeMap;
    Fest_Toe_L(i) = AvgP_Toe_L(i) * N_ToeMap * CP * SenselArea;
    CP = max(N_MetMap - sum(S_L_frame(FootMaps.LeftMetatarsal)==0),1)/N_MetMap;
    Fest_Met_L(i) = AvgP_Met_L(i) * N_MetMap * CP * SenselArea;
    CP = max(N_MidMap - sum(S_L_frame(FootMaps.LeftMid)==0),1)/N_MidMap;
    Fest_Mid_L(i) = AvgP_Mid_L(i) * N_MidMap * CP * SenselArea;
    CP = max(N_HelMap - sum(S_L_frame(FootMaps.LeftHeel)==0),1)/N_HelMap;
    Fest_Hel_L(i) = AvgP_Hel_L(i) * N_HelMap * CP * SenselArea;
    CP = max(N_ToeMap - sum(S_R_frame(FootMaps.RightToe)==0),1)/N_ToeMap;
    Fest_Toe_R(i) = AvgP_Toe_R(i) * N_ToeMap * CP * SenselArea;
    CP = max(N_MetMap - sum(S_R_frame(FootMaps.RightMetatarsal)==0),1)/N_MetMap;
    Fest_Met_R(i) = AvgP_Met_R(i) * N_MetMap * CP * SenselArea;
    CP = max(N_MidMap - sum(S_R_frame(FootMaps.RightMid)==0),1)/N_MidMap;
    Fest_Mid_R(i) = AvgP_Mid_R(i) * N_MidMap * CP * SenselArea;
    CP = max(N_HelMap - sum(S_R_frame(FootMaps.RightHeel)==0),1)/N_HelMap;
    Fest_Hel_R(i) = AvgP_Hel_R(i) * N_HelMap * CP * SenselArea;
end

% figure
% subplot 211;hold all;
% plot(AvgP_Toe_L)
% plot(AvgP_Met_L)
% plot(AvgP_Mid_L)
% plot(AvgP_Hel_L)
% legend('Toe','Meta','Mid','Heel')
% subplot 212;hold all;
% plot(AvgP_Toe_R)
% plot(AvgP_Met_R)
% plot(AvgP_Mid_R)
% plot(AvgP_Hel_R)
% legend('Toe','Meta','Mid','Heel')

% figure;hold all;
% plot(AvgP_L)
% plot(AvgP_R)
% legend('L','R')

% figure
% plot(AvgP_L)
% figure
% plot(AvgP_R)

Fest_L = AvgP_L * N_FootMap .* ContactPercent_L * SenselArea;
Fest_R = AvgP_R * N_FootMap .* ContactPercent_R * SenselArea;

% figure;
% subplot 211;hold all;
% plot(Fest_L)
% plot(Fest_R)
% subplot 212
% plot(Fest_L+Fest_R)

% set output struct
XSNData.t = Time;
XSNData.S_L = S_L;
XSNData.S_R = S_R;
XSNData.AvgP_L = AvgP_L;
XSNData.AvgP_R = AvgP_R;
XSNData.ContactPer_L = ContactPercent_L;
XSNData.ContactPer_R = ContactPercent_R;
XSNData.Fest_L = Fest_L;
XSNData.Fest_R = Fest_R;

XSNData.AvgP_Toe_L = AvgP_Toe_L;
XSNData.AvgP_Met_L = AvgP_Met_L;
XSNData.AvgP_Mid_L = AvgP_Mid_L;
XSNData.AvgP_Hel_L = AvgP_Hel_L;
XSNData.AvgP_Toe_R = AvgP_Toe_R;
XSNData.AvgP_Met_R = AvgP_Met_R;
XSNData.AvgP_Mid_R = AvgP_Mid_R;
XSNData.AvgP_Hel_R = AvgP_Hel_R;

XSNData.Fest_Toe_L = Fest_Toe_L;
XSNData.Fest_Met_L = Fest_Met_L;
XSNData.Fest_Mid_L = Fest_Mid_L;
XSNData.Fest_Hel_L = Fest_Hel_L;
XSNData.Fest_Toe_R = Fest_Toe_R;
XSNData.Fest_Met_R = Fest_Met_R;
XSNData.Fest_Mid_R = Fest_Mid_R;
XSNData.Fest_Hel_R = Fest_Hel_R;

return

function [Time,S_L,S_R,SenselArea] = readfile_fromInternalSW(fname)

opts = detectImportOptions(fname);
% read header, parse start time
fid = fopen(fname);
C = textscan(fid,'%s',opts.VariableNamesLine,'delimiter','\n');C = C{1};
fclose(fid);
% Tstart = textscan(C{4},'DATE:,%{yyyy-MM-dd HH:mm:ss}D','whitespace', '','delimiter','\n');
% Tstart = Tstart{1};
% ignore the header time stamp, only grab the date
Dstart = textscan(C{4},'DATE:,%{yyyy-MM-dd}D','delimiter',' ');
Dstart = Dstart{1};
% grab the Sensel dimensions and compute area
tmp = textscan(C{5},'%s %s %f %s %f','delimiter',',');
SenselArrayWidth_cm = tmp{3};
SenselArrayLength_cm = tmp{5};
SenselArea = (SenselArrayWidth_cm/11) * (SenselArrayLength_cm/31);
SenselArea = SenselArea / 2.54^2; % [in^2]

% temp scale from [bar] to [psi]
Gsensel = 14.5038;

% --- Hardcode for now, move to header parsed
MinP_R = 1.00; % [psi]
MinP_L = 1.01; % [psi]
% ----

% read data
Data = readtable(fname);

% trim data if L/R samples not in sync
Tstamps = unique(Data.Time_Stamp(1:22));
if numel(Tstamps)>1
    % need to trim start
    Data(1:11,:) = [];
end
Tstamps = unique(Data.Time_Stamp(end-21:end));
if numel(Tstamps)>1
    % need to trim end
    Data(end-10:end,:) = [];
end

% establish time vector
T = Data.Time_Stamp;
Time = Dstart + seconds(T); % + hours(3);
Time = unique(Time);
Time.TimeZone = 'America/Los_Angeles';

% find which sensors are being used, and their ID for Right and Left
Data.ID = uint8(char(Data.ID));
SensorID_Right = uint8('R');
SensorID_Left = uint8('L');

% ndx = strmatch('RIGHT',Data.ID);
ndx = find(Data.ID == SensorID_Right);
z_R = [ Data.col0(ndx)  Data.col1(ndx)...
        Data.col2(ndx)  Data.col3(ndx)...
        Data.col4(ndx)  Data.col5(ndx)...
        Data.col6(ndx)  Data.col7(ndx)...
        Data.col8(ndx)  Data.col9(ndx)...
        Data.col10(ndx) Data.col11(ndx)...
        Data.col12(ndx) Data.col13(ndx)...
        Data.col14(ndx) Data.col15(ndx)...
        Data.col16(ndx) Data.col17(ndx)...
        Data.col18(ndx) Data.col19(ndx)...
        Data.col20(ndx) Data.col21(ndx)...
        Data.col22(ndx) Data.col23(ndx)...
        Data.col24(ndx) Data.col25(ndx)...
        Data.col26(ndx) Data.col27(ndx)...
        Data.col28(ndx) Data.col29(ndx)...
        Data.col30(ndx)];

% ndx = strmatch('LEFT',Data.ID);
ndx = find(Data.ID == SensorID_Left);
z_L = [ Data.col0(ndx)  Data.col1(ndx)...
        Data.col2(ndx)  Data.col3(ndx)...
        Data.col4(ndx)  Data.col5(ndx)...
        Data.col6(ndx)  Data.col7(ndx)...
        Data.col8(ndx)  Data.col9(ndx)...
        Data.col10(ndx) Data.col11(ndx)...
        Data.col12(ndx) Data.col13(ndx)...
        Data.col14(ndx) Data.col15(ndx)...
        Data.col16(ndx) Data.col17(ndx)...
        Data.col18(ndx) Data.col19(ndx)...
        Data.col20(ndx) Data.col21(ndx)...
        Data.col22(ndx) Data.col23(ndx)...
        Data.col24(ndx) Data.col25(ndx)...
        Data.col26(ndx) Data.col27(ndx)...
        Data.col28(ndx) Data.col29(ndx)...
        Data.col30(ndx)];

Lseg = 11;
Larray = size(z_R,1);
N = Larray/Lseg;

S_R = zeros(11,31,N);
S_L = zeros(11,31,N);
for i=1:N
    j = (i-1)*11+1;
    S_R(:,:,i) = z_R(j:j+11-1,:);
    S_L(:,:,i) = z_L(j:j+11-1,:);
end
clear z_R z_L;

% rotate so its 31 rows by 11 columns
S_R = rot90(S_R);
S_L = rot90(S_L);
% flip it so the matrix printed to console matches the POV of a foot print
S_R = flipud(S_R);
S_L = flipud(S_L);


% scaling and zeroing
S_R(S_R==-1) = 0;
S_L(S_L==-1) = 0;

S_R = S_R * Gsensel; % output in [psi]
S_L = S_L * Gsensel;

S_R(S_R < MinP_R) = 0;
S_L(S_L < MinP_L) = 0;


return


%% this function reads the format exported from the XSensor software
function [Time,S_L,S_R,SenselArea] = readfile_fromXsensorSW(fname)

h = waitbar(0,'Reading XSN file, please wait...');
fid = fopen(fname,'rt');
% read full file into cell array
C = textscan(fid,'%s','whitespace', '','delimiter','\n'); C = C{1};
fclose(fid);
waitbar(1,h);drawnow;

% ---- hardcode for now but move to parsed from file
SenselArea = (0.8 / 2.54)^2;
% ----

% Find all FRAMEs in file
I_frame = strmatch('"FRAME"',C);
% Find all SENSELS sets in file
I_sensels = strmatch('"SENSELS"',C);

L = numel(I_frame);
% allocate output variables
Time = zeros(L,1);
S_L = zeros(31,11,L);
S_R = zeros(31,11,L);

% loop through all frames and parse the chosen fields
waitbar(0,h,'Parsing XSN file, please wait...');
for i=1:L
    % Parse time value from current frame
    a = I_frame(i);
    Time(i) = sscanf(C{a+2},'"Time","%f"');

    % Grab indecies for Left and Right Sensels matricies from current frame
    A = find(I_sensels > I_frame(i),2,'first');
    
    % Parse Left Sensels maxtix from 31 lines of data
    a = I_sensels(A(1));
    for j=1:31
        S_L(j,:,i) = sscanf(C{a+j},'"%f","%f","%f","%f","%f","%f","%f","%f","%f","%f","%f')';
    end
    
    % Parse Right Sensels maxtix from 31 lines of data
    a = I_sensels(A(2));
    for j=1:31
        S_R(j,:,i) = sscanf(C{a+j},'"%f","%f","%f","%f","%f","%f","%f","%f","%f","%f","%f')';
    end

    waitbar(i/L,h)
end
close(h);

% dont flip, keep them so print to console is the correct orientation
% S_L = flipud(S_L);
% S_R = flipud(S_R);

return