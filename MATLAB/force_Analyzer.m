%close all;clear;clc;

%DataRootDir is the parent path of the dataset folder
%Dname is the folder that the dataset file is in

DataRootDir = 'C:\Users\cooper\Documents\MATLAB';

Dname = 'Andy_10.24.22';
%Dname = 'ChrisP_10.24.22';
%Dname = 'Sana_10_26_22';
%Dname = 'Andy_toe_10_26_22';
%Dname = 'Emily10_27_22';

Dname = fullfile(DataRootDir,Dname);

%% READ LOADCELL DATA
if 1
ForceData = load_ForceData(fullfile(Dname,'load_cells_Data.tdms'));
end

%% READ ACCEL DATA
if 1
AccelData = load_AccelData(fullfile(Dname,'accel_data.tdms'));
end

%% READ MIC DATA
if 1
MicData = load_MicData(fullfile(Dname,'mic_data.tdms'));
end


%% PLOT

row = 15;

% PLOT SINGLE STRIKES
if 0
%row = 17;
figure
subplot 611
plot(AccelData.footStrikeTime(row,:),AccelData.footStrike(row,:));title('single strike accel')
subplot 612
plot(ForceData.footStrikeTime(row,:),ForceData.footStrike(row,:));title('single strike load cell')
subplot 613
plot(MicData.footStrikeTime(row,:),MicData.footStrikeFL(row,:));title('single strike front left mic')
subplot 614
plot(MicData.footStrikeTime(row,:),MicData.footStrikeBL(row,:));title('single strike back left mic')
subplot 615
plot(MicData.footStrikeTime(row,:),MicData.footStrikeFR(row,:));title('single strike front right mic')
subplot 616
plot(MicData.footStrikeTime(row,:),MicData.footStrikeBR(row,:));title('single strike back right mic')
end

% SINGLE FORCE 
if 1
%row = 17;
figure
plot(ForceData.footStrikeTime(row,:),ForceData.footStrike(row,:));title('single strike load cell')
end

% SINGLE ACCEL
if 1
figure
%subplot 211
%plot(AccelData.footStrikeTime(row,:),AccelData.footStrikeX(row,:));title('single strike accel X')
%subplot 212
plot(AccelData.footStrikeTime(row,:),AccelData.footStrikeY(row,:));title('single strike accel Y')
end

% SINGEL MIC
if 1
figure
%subplot 411
plot(MicData.footStrikeTime(row,:),MicData.footStrikeFL(row,:));title('single strike front left mic')
%subplot 412
%plot(MicData.footStrikeTime(row,:),MicData.footStrikeBL(row,:));title('single strike back left mic')
%subplot 413
%plot(MicData.footStrikeTime(row,:),MicData.footStrikeFR(row,:));title('single strike front right mic')
%subplot 414
%plot(MicData.footStrikeTime(row,:),MicData.footStrikeBR(row,:));title('single strike back right mic')
end

% PLOT ACCEL DATA
if 1
figure
plot(AccelData.t,AccelData.Center_X);hold all;title('Accels')
plot(AccelData.t,AccelData.Center_Y);
end

% PLOT LOAD CELL DATA
if 0
%plot forces individually
%figure
%plot(ForceData.t,ForceData.Frnt_L);hold all;title('Load Cells lbs')
%plot(ForceData.t,ForceData.FMid_L);
%plot(ForceData.t,ForceData.BMid_L);
%plot(ForceData.t,ForceData.Back_L);
%plot(ForceData.t,ForceData.Frnt_R);
%plot(ForceData.t,ForceData.FMid_R);
%plot(ForceData.t,ForceData.BMid_R);
%plot(ForceData.t,ForceData.Back_R);
%legend('Frnt L','FMid L','BMid L','Back L','Frnt R','FMid R','BMid R','Back R')

%plot of the summed up forces
figure
plot(ForceData.t, ForceData.sum);title('Combined Force lbs')
%plot(ForceData.newTime, ForceData.newSum);title('Combined Force lbs')

%figure
%plot(ForceData.t,ForceData.Frnt_L+...
                 %ForceData.FMid_L+...
                 %ForceData.BMid_L+...
                 %ForceData.BMid_L+...
                 %ForceData.Frnt_R+...
                 %ForceData.FMid_R+...
                 %ForceData.BMid_R+...
                 %ForceData.BMid_R);title('Combined Force 2')
end

% PLOT MIC DATA
if 0
MicData = load_MicData(fullfile(Dname,'mic_data.tdms'));

figure;
plot(MicData.t,MicData.Frnt_L);hold all;title('Mics')
plot(MicData.t,MicData.Back_L);
plot(MicData.t,MicData.Frnt_R);
plot(MicData.t,MicData.Back_R);
legend('Frnt L','Back L','Frnt R','Back R')
end



