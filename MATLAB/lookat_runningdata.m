close all;clear;clc;

%DataRootDir is the parent path of the dataset folder
%Dname is the folder that the dataset file is in

%DataRootDir = 'C:\Users\Tony\Downloads\Tread AD Adv Metrics';
DataRootDir = 'C:\Users\cooper\Documents\MATLAB';

% Dname = 'Real Data 8_3_22\Andrea';
% Dname = 'Real Data 8_3_22\Data Sync drop test2';

% Dname = 'Dataset_20220822\Andrea';
% Dname = 'Dataset_20220822\Andy'; % Heel
% Dname = 'Dataset_20220822\Daniel Cooper';
% Dname = 'Dataset_20220822\Harrison'; % Heel
% Dname = 'Dataset_20220822\Sana'; % bug
% Dname = 'Dataset_20220822\Sarah';

% Dname = 'Dataset_20220823\ChrisP'; % Midfoot
% Dname = 'Dataset_20220823\Dee';
% Dname = 'Dataset_20220823\Joshua'; % Forefoot
% Dname = 'Dataset_20220823\Rene';
Dname = 'XSensorIMU Test'

Dname = fullfile(DataRootDir,Dname);


%% clear intermediate mat files from target directory
% D = dir(fullfile(Dname,'*.mat'));
% delete(fullfile(Dname,'*.mat'));
% return


%% READ ACCEL DATA
if 1
AccelData = load_AccelData(fullfile(Dname,'accel_and_power_data.tdms'));

figure
%plot(AccelData.t,AccelData.Left);
%plot(AccelData.t,AccelData.Right);
plot(AccelData.t,AccelData.Center_X);hold all;title('Accels')
plot(AccelData.t,AccelData.Center_Y);
end

%% READ TACH DATA
if 1
TachData = load_TachData(fullfile(Dname,'Tach_Data.tdms'));

vel = TachData.vel;
M_vel = vel * 2.6; % [rad/s]
B_r = 0.050/2; % [m]
B_vel = vel/(2*pi) * (2*pi*B_r); % roller vel in [rad/s] to belt vel in [m/s]

figure
subplot 311
plot(TachData.t,TachData.Tach);title('Tach')
ylim([-0.25 1.25])
subplot 312
plot(TachData.t,vel)
subplot 313
plot(TachData.t,B_vel) % [m/s] to [mph] *2.23694
end

%% READ ENCODER DATA

if 1
EncoderData = load_EncoderData(fullfile(Dname,'Torque_Position.tdms'));

figure 
%subplot 211
%plot(EncoderData.t, EncoderData.Encoder);title('Encoder')
%subplot 212
plot(EncoderData.t, EncoderData.vel);title('RPM')
end

%% READ DOPPLER DATA
if 1
DopplerData = load_DopplerData(fullfile(Dname,'Belt_Speed.tdms'));

figure
subplot(211)
plot(DopplerData.t, DopplerData.velocity);title('Doppler ft/min')
subplot(212)
plot(DopplerData.t, DopplerData.mph);title('Doppler MPH')
end

%% READ LOADCELL DATA
if 1
ForceData = load_ForceData(fullfile(Dname,'load_cells_Data.tdms'));

figure
plot(ForceData.t,ForceData.Frnt_L);hold all;title('Load Cells')
plot(ForceData.t,ForceData.FMid_L);
plot(ForceData.t,ForceData.BMid_L);
plot(ForceData.t,ForceData.Back_L);
plot(ForceData.t,ForceData.Frnt_R);
plot(ForceData.t,ForceData.FMid_R);
plot(ForceData.t,ForceData.BMid_R);
plot(ForceData.t,ForceData.Back_R);
legend('Frnt L','FMid L','BMid L','Back L','Frnt R','FMid R','BMid R','Back R')

figure
plot(ForceData.t,ForceData.Frnt_L+...
                 ForceData.FMid_L+...
                 ForceData.BMid_L+...
                 ForceData.BMid_L+...
                 ForceData.Frnt_R+...
                 ForceData.FMid_R+...
                 ForceData.BMid_R+...
                 ForceData.BMid_R)
end

%% READ MIC DATA
if 1
MicData = load_MicData(fullfile(Dname,'mic_data.tdms'));

figure;
plot(MicData.t,MicData.Frnt_L);hold all;title('Mics')
plot(MicData.t,MicData.Back_L);
plot(MicData.t,MicData.Frnt_R);
plot(MicData.t,MicData.Back_R);
legend('Frnt L','Back L','Frnt R','Back R')
end

%% READ TORQUE AND POWER DATA
if 1
MotorData = load_MotorData(fullfile(Dname,'Torque_Data.tdms'));
G_mtop = 2.6; % Motion ratio Motor shaft to drive roller

%M_EP = MotorData.Current.*MotorData.Voltage;

R_vel = interp1(TachData.t,TachData.vel,MotorData.t,'linear');
M_vel = R_vel*G_mtop * (1/60) * (2*pi); % roller vel in [rpm] to motor vel in [rad/s]

M_MP = M_vel .* MotorData.Torque;

figure
%plot(MotorData.t,M_EP);hold on
plot(MotorData.t,M_MP);legend('EP','MP')

% figure
% plot(M_vel/(2*pi) * 60,M_Voltage)

figure;
subplot 311
plot(MotorData.t,MotorData.Torque);hold all;title('Motor');legend('Torque')
subplot 312
%plot(MotorData.t,MotorData.Current);legend('Current')
%subplot 313
%plot(MotorData.t,MotorData.Voltage);legend('Voltage')
end


%% READ XSENSOR DATA

XSNData = load_XSensorData(fullfile(Dname,'XSensor_output.csv'));

% plot_XSN_sensels(XSNData);

% feature extraction
FootImpacts_L = find_XsnFootImpacts(XSNData,'left');
FootImpacts_R = find_XsnFootImpacts(XSNData,'right');

figure;
subplot 211;
plot(XSNData.t,XSNData.Fest_L);hold all
plot(XSNData.t,XSNData.Fest_R);
subplot 212;hold all;
plot(XSNData.t(FootImpacts_L.i_all),FootImpacts_L.type,'o','LineWidth',2);
plot(XSNData.t(FootImpacts_R.i_all),FootImpacts_R.type,'s','LineWidth',2);
ylim([0 4])
yticks([1,2,3])
yticklabels({'Heel','Mid','Fore'})
legend('Left Impact Type','Right Impact Type')

R_vel = interp1(TachData.t,TachData.vel,XSNData.t,'linear','extrap');
B_vel = R_vel/(2*pi) * (2*pi*0.050/2); % roller vel in [rad/s] to belt vel in [m/s]

tsec = second(XSNData.t);
dt = [0;diff(tsec)];
tmin = zeros(size(tsec));
tmin(dt<0)=60;
tsec = tsec + cumsum(tmin);
B_x = cumtrapz(tsec,B_vel);
figure
subplot 311
plot(XSNData.t,B_x);hold on
plot(XSNData.t(FootImpacts_L.i_all),B_x(FootImpacts_L.i_all),'ob')
plot(XSNData.t(FootImpacts_R.i_all),B_x(FootImpacts_R.i_all),'or')
legend('Belt Displacement','Left Impact','Right Impact')

StrideLen_L = [0;diff(B_x(FootImpacts_L.i_all))];
StrideLen_R = [0;diff(B_x(FootImpacts_R.i_all))];
FootImpacts_all = union(FootImpacts_L.i_all,FootImpacts_R.i_all);
StepLen = [0;diff(B_x(FootImpacts_all))];

subplot 312; hold on
plot(XSNData.t(FootImpacts_L.i_all),StrideLen_L)
plot(XSNData.t(FootImpacts_R.i_all),StrideLen_R)
plot(XSNData.t(FootImpacts_all),StepLen)
legend('Stride Len L','Stride Len R','Step Len')

Cadence = B_vel(FootImpacts_all) ./ (StepLen*2);
Cadence = Cadence * 60; % strides/sec to strides/min

subplot 313; hold on
plot(XSNData.t(FootImpacts_all),Cadence)
legend('Cadence')