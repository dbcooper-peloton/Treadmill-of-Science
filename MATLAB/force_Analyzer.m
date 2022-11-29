close all;clear;clc;

%DataRootDir is the parent path of the dataset folder
%Dname is the folder that the dataset file is in

%DataRootDir = 'C:\Users\cooper\Documents\MATLAB';
DataRootDir = '/home/daniel/Documents/MATLAB';

%Dname = 'Sana_11.4.22';
%Dname = 'Andy-11.1.22';
%Dname = 'Chris_11.3.22';
Dname = 'Emily_11.3.22';

Dname = fullfile(DataRootDir,Dname);
disp(Dname)

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

%% FOOTSTRIKE ROW SELCTION AND FINDING MAX

% select which footstrike to analyze
row = 2;

% remove the zero padding in the footsrike to the end and to find the index of the end
endvalue = rmmissing(ForceData.footStrikeTime(row,:));
endvaluenum = numel(endvalue);

% calculate the max
[xmax, ymax] = max(ForceData.footStrike(row,:));
maxStrike = xmax;
maxTime = ForceData.footStrikeTime(row,ymax);

% why is the scale 20?
ymaxAccel = ymax*20;


%% PLOT SINGLE STRIKES FOR ACCEL, 
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

%% PLOT SINGLE FORCE FOOTSRIKE 
if 0
plot(ForceData.footStrikeTime(row,:),ForceData.footStrike(row,:));title('single strike load cell');ylabel('Pounds (lbs)');xlabel('Time (Datetime)')
end

%% FORCE FOOTSRIKE ANALYZER
if 01

% plot the foot strike of each zone on a single graph
% this plot also shows the sum of all the forces and the sum of the LEFT
% and RIGHT forces
figure
hold on
plot(ForceData.footStrikeTime(row,:),ForceData.footStrike(row,:));title('single strike load cell');ylabel('Pounds (lbs)');xlabel('Time (Datetime)')
plot(ForceData.footStrikeTime(row,:), ForceData.footStrikeZone1(row,:));
plot(ForceData.footStrikeTime(row,:), ForceData.footStrikeZone2(row,:));
plot(ForceData.footStrikeTime(row,:), ForceData.footStrikeZone3(row,:));
plot(ForceData.footStrikeTime(row,:), ForceData.footStrikeZone4(row,:));
plot(ForceData.footStrikeTime(row,:), ForceData.RIGHT(row,:));
plot(ForceData.footStrikeTime(row,:), ForceData.LEFT(row,:));

% calculate the percentages
zone1_percent = ForceData.footStrikeZone1(row,ymax)/maxStrike * 100;
zone2_percent = ForceData.footStrikeZone2(row,ymax)/maxStrike * 100;
zone3_percent = ForceData.footStrikeZone3(row,ymax)/maxStrike * 100;
zone4_percent = ForceData.footStrikeZone4(row,ymax)/maxStrike * 100;
RIGHT_percent = ForceData.RIGHT(row,ymax)/maxStrike;
LEFT_percent = ForceData.LEFT(row,ymax)/maxStrike;

FRONT_percent = (zone1_percent + zone2_percent)/100;

% find the value of the zones at the max value
zone1_value = ForceData.footStrikeZone1(row,ymax);
zone2_value = ForceData.footStrikeZone2(row,ymax);
zone3_value = ForceData.footStrikeZone3(row,ymax);
zone4_value = ForceData.footStrikeZone4(row,ymax);
RIGHT_value = ForceData.RIGHT(row,ymax);
LEFT_value = ForceData.LEFT(row,ymax);

right_left_placement = LEFT_percent * 25;

% create vectors
zonevectorpercentage = [zone1_percent,zone2_percent,zone3_percent,zone4_percent];
zonevectorvalue = [zone1_value, zone2_value, zone3_value, zone4_value];
deckvector = [8.3, 26.7, 28.3, 26.7, 10];

% plot the max of each zone
plot(ForceData.footStrikeTime(row,ymax), zone1_value,'x',color='magenta');
plot(ForceData.footStrikeTime(row,ymax), zone2_value,'x',color='blue');
plot(ForceData.footStrikeTime(row,ymax), zone3_value,'x',color='green');
plot(ForceData.footStrikeTime(row,ymax), zone4_value,'x',color='black');

% algo time baby
sum = 0;
sum2 = 0;
rise = 0;
run = 0;
ii = 1;
b= 0;
while true
    % if zones add up to over 50, then we are done
    if sum + zonevectorpercentage(ii) > 50
        break;
    else
       % calculate b
       sum = sum + zonevectorpercentage(ii);       
       b = sum;
       % calculate deck percentages to find distance later
       sum2 = sum2 + deckvector(ii);
       % find rise and run
       rise = zonevectorpercentage(ii+1);
       run = deckvector(ii);
       
    end
    ii = ii+1;
end

% calculate slope
m = rise/run;

% find x
x = fact(m,b);

% find distance travelled
distance = ((x + sum2)/100) * 60;

%display(m)
%display(b)
%display(x)
%display(distance)

% creating labels for the plot legend
stringpercentage1 = 'Front: ' + string(zone1_percent);
stringpercentage2 = 'Front Middle: ' + string(zone2_percent);
stringpercentage3 = 'Back Middle: ' + string(zone3_percent);
stringpercentage4 = 'Back: ' + string(zone4_percent);
legend('Sum', 'Front Zone', 'Front Middle Zone', 'Back Middle Zone', 'Back Zone', 'RIGHT', 'LEFT', stringpercentage1, stringpercentage2, stringpercentage3, stringpercentage4);

% find the distance from the front of deck where the footstirkes occur
distanceFront = 60 -(60 * FRONT_percent);

% This for loop will go through the 
figure
for j = 1:length(ForceData.endTime)
    
    % find the percentages of the footstrikes in zone 1 and zone 2
    zone1_percentnextstrike = ForceData.footStrikeZone1(j,ymax)/maxStrike * 100;
    zone2_percentnextstrike = ForceData.footStrikeZone2(j,ymax)/maxStrike * 100;
    % using the percentages find the percentage of the front zones and the
    % left zones
    FRONT_percentnextstrike = (zone1_percentnextstrike + zone2_percentnextstrike)/100;
    LEFT_percentnextstrike = ForceData.LEFT(j,ymax)/maxStrike;
    
    % find the distance from the front of deck where the footstirkes occur
    distanceFrontnextstrike = 60 - (60*FRONT_percentnextstrike);
    right_left_placementnextstrike = LEFT_percentnextstrike * 25;

    % plot the footstrikes on a treadmill deck
    hold on
    plot([0,distance,60], [0,12.5,25],'x',color='white');
    %plot(distanceFront,right_left_placement, 'x', color='blue');
    plot(distanceFrontnextstrike,right_left_placementnextstrike, 'x', color='red');
    plot(12, 0:25,'.',color='blue');
end

end

%% FIND AND PLOT LOAD CELL DERIVATIVE
% this section finds the derivative of the filtered LOAD CELL strike

if 0
figure
%Calcuate derivative of filtered and combined GRF data
GRF_Derivative = diff(ForceData.footStrike(row,(1:endvaluenum)));
%GRF_2ndDerivative = diff(ForceData.GRF_Derivative);

% find the lenght of the derivate and plot it
XValues = numel(GRF_Derivative);
plot([1:endvaluenum-1],GRF_Derivative);hold all;title(Dname,'GRF Derivative')
end

%% PLOT SINGLE ACCEL FOOTSTRIKE

if 0
figure
%subplot 211
%plot(AccelData.footStrikeTime(row,:),AccelData.footStrikeX(row,:));title('single strike accel X')
%subplot 212
%plot(AccelData.footStrikeTime(row,:),AccelData.footStrikeZ(row,:));title('single strike accel Z')
plot(AccelData.footStrikeTime(row,1:ymaxAccel),AccelData.footStrikeZ(row,1:ymaxAccel));title('single strike accel Z')

end

%% FIND AND PLOT INTEGRAL of ACCEL FOOTSTRIKE

if 0
figure
dataAccel = cumtrapz(AccelData.footStrikeY(row,:));
plot(AccelData.footStrikeTime(row,:),dataAccel);
end

%% PLOT SINGLE MIC FOOTSTRIKE

if 0
figure
hold on
subplot 411
plot(MicData.footStrikeTime(row,1:ymaxAccel),MicData.footStrikeFL(row,1:ymaxAccel), color = 'red');title('single strike front left mic')
subplot 412
plot(MicData.footStrikeTime(row,1:ymaxAccel),MicData.footStrikeBL(row,1:ymaxAccel),color = 'green');title('single strike back left mic')
subplot 413
plot(MicData.footStrikeTime(row,1:ymaxAccel),MicData.footStrikeFR(row,1:ymaxAccel), color = 'blue');title('single strike front right mic')
subplot 414
plot(MicData.footStrikeTime(row,1:ymaxAccel),MicData.footStrikeBR(row,1:ymaxAccel),color = 'magenta');title('single strike back right mic')
end

%% FIND SUM of ABS of MIC

if 0
disp(ymaxAccel)
sum_Frnt_L = sum(abs(MicData.footStrikeFL(row,1:ymaxAccel)))
sum_Back_L = sum(abs(MicData.footStrikeBL(row,1:ymaxAccel)))
sum_Frnt_R = sum(abs(MicData.footStrikeFR(row,1:ymaxAccel)))
sum_Back_R = sum(abs(MicData.footStrikeBR(row,1:ymaxAccel)))
end


%% PLOT ACCEL DATA

if 0
figure
subplot 311
plot(AccelData.t,AccelData.Center_X);title('Accels')
subplot 312
plot(AccelData.t,AccelData.Center_Y);
subplot 313
plot(AccelData.t, AccelData.Center_Z);
end

%% PLOT LOAD CELL DATA
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

%% PLOT MIC DATA

if 0
figure
plot(MicData.t,MicData.Frnt_L);hold all;title('Mics')
plot(MicData.t,MicData.Back_L);
plot(MicData.t,MicData.Frnt_R);
plot(MicData.t,MicData.Back_R);
legend('Frnt L','Back L','Frnt R','Back R')
end

%% ACCEL FFT

if 01

% calculate the FFT of a single footstirke on the Z Accel Axis
FFT_ACCELZ = fft(AccelData.footStrikeZ(row, (1:endvaluenum)));
FFTValuesZ = numel(FFT_ACCELZ);

% frequency domain
frequencyZ = 5000*(0:(FFTValuesZ/2))/FFTValuesZ;

% single sided and two sided spectrum
P2 = abs(FFT_ACCELZ/FFTValuesZ);
P1 = P2(1:FFTValuesZ/2+1);
P1(2:end-1) = 2*P1(2:end-1);

figure
plot(frequencyZ,P1);title('P1 Z AXIS ACCEL FFT')
%plot(frequencyZ,P2);title('P2 Z AXIS ACCEL FFT')

end

%% MIC FFT

if 01

% calculate the FFT of a single footstrike on the sum of all Mic data
FFT_MIC_FL = fft(MicData.footStrikeSum(row, (1:endvaluenum)));
FFTValues_FL = numel(FFT_MIC_FL);

% frequency domain
frequencyMic = 40000*(0:(FFTValues_FL/2))/FFTValues_FL;

% single sided and two sided spectrum
P2 = abs(FFT_MIC_FL/FFTValues_FL);
P1 = P2(1:FFTValues_FL/2+1);
P1(2:end-1) = 2*P1(2:end-1);

figure
plot(frequencyMic,P1);title('P1 FRONT LEFT MIC FFT')

end

%% clear intermediate mat files from target directory

%D = dir(fullfile(Dname,'*.mat'));
%delete(fullfile(Dname,'*.mat'));
%return

%% function to find x in y = mx+b

function f = fact(m,b)
    f = (50-b)/m;
end
