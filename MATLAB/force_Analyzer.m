close all;clear;clc;

%DataRootDir is the parent path of the dataset folder
%Dname is the folder that the dataset file is in

DataRootDir = 'C:\Users\cooper\Documents\MATLAB';

%Dname = 'Sana_11.4.22';
%Dname = 'Andy-11.1.22';
%Dname = 'Chris_11.3.22';
Dname = 'Emily_11.3.22';

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
endvalue = rmmissing(ForceData.footStrikeTime(row,:));
endvaluenum = numel(endvalue);

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
if 0
%row = 17;
figure
plot(ForceData.footStrikeTime(row,:),ForceData.footStrike(row,:));title('single strike load cell')
end

% LOAD CELL Derivative
if 0
figure
%Calcuate derivative of filtered and combined GRF data
GRF_Derivative = diff(ForceData.footStrike(row,(1:endvaluenum)));
%GRF_2ndDerivative = diff(ForceData.GRF_Derivative);

%display(length(GRF_Derivative));
%display((endvaluenum));

XValues = numel(GRF_Derivative);
plot([1:endvaluenum-1],GRF_Derivative);hold all;title(Dname,'GRF Derivative')
end

% SINGLE ACCEL
if 0
figure
%subplot 211
%plot(AccelData.footStrikeTime(row,:),AccelData.footStrikeX(row,:));title('single strike accel X')
%subplot 212
plot(AccelData.footStrikeTime(row,:),AccelData.footStrikeZ(row,:));title('single strike accel Z')
end

% INTEGRAL of ACCEL
if 0
figure
dataAccel = cumtrapz(AccelData.footStrikeY(row,:));
plot(AccelData.footStrikeTime(row,:),dataAccel);
end


% SINGEL MIC
if 0
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
if 0
figure
subplot 311
plot(AccelData.t,AccelData.Center_X);title('Accels')
subplot 312
plot(AccelData.t,AccelData.Center_Y);
subplot 313
plot(AccelData.t, AccelData.Center_Z);
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

%% ACCEL FFT

% ACCEL
if 01
% Z
%FFT_ACCELZ = fft(AccelData.Center_Z);
FFT_ACCELZ = fft(AccelData.footStrikeZ(row, (1:endvaluenum)));
FFTValuesZ = numel(FFT_ACCELZ);

figure
plot(1:FFTValuesZ, FFT_ACCELZ);title('Z AXIS ACCEL FFT')

% X
%FFT_ACCELX = fft(AccelData.Center_X);
%FFT_ACCELX = fft(AccelData.footStrikeX(row, (1:endvaluenum)));
%FFTValuesX = numel(FFT_ACCELX);

% Y
%FFT_ACCELY = fft(AccelData.Center_Y);
%FFT_ACCELY = fft(AccelData.footStrikeY(row, (1:endvaluenum)));
%FFTValuesY = numel(FFT_ACCELY);
end

%% MIC FFT

if 01
% MIC
FFT_MIC_FL = fft(MicData.footStrikeFL(row, (1:endvaluenum)));
FFTValues_FL = numel(FFT_MIC_FL);

figure
plot(1:FFTValuesZ, FFT_MIC_FL);title('FRONT LEFT MIC FFT')


%plot([1:endvaluenum], FFT_ACCEL);
end


%% clear intermediate mat files from target directory
%D = dir(fullfile(Dname,'*.mat'));
%delete(fullfile(Dname,'*.mat'));
%return



