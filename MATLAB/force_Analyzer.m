%close all;clear;clc;

%DataRootDir is the parent path of the dataset folder
%Dname is the folder that the dataset file is in

DataRootDir = 'C:\Users\cooper\Documents\MATLAB';

%Dname = 'XSensorIMU Test';
%Dname = 'NoRunner_2MPH_800K';
%Dname = 'Andy3MPH_900K';
Dname = 'Andy_10.24.22';
%Dname = '1MPH_NoRunner';


Dname = fullfile(DataRootDir,Dname);

%% READ LOADCELL DATA
if 1
ForceData = load_ForceData(fullfile(Dname,'load_cells_Data.tdms'));

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

%TODO: Subtract zero value from each force in summed up force plot

%plot of the summed up forces
figure
plot(ForceData.t, ForceData.sum);title('Combined Force lbs')
%plot(ForceData.newTime, ForceData.newSum);title('Combined Force lbs')

% plot single rows
row = 4;
figure
plot(footStrikeTime(row,:),footStrike(row,:));title('Combined Force lbs')

% plot each row
%figure
%hold on
%for i = 1:length(ForceData.mat)
%    plot(ForceData.timeMat(i,:), ForceData.mat(i,:))
%end


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


%% READ ACCEL DATA
if 1
AccelData = load_AccelData(fullfile(Dname,'accel_data.tdms'));

figure
%plot(AccelData.t,AccelData.Left);
%plot(AccelData.t,AccelData.Right);
plot(AccelData.t,AccelData.Center_X);hold all;title('Accels')
plot(AccelData.t,AccelData.Center_Y);
end


