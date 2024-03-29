close all;clear;clc;

%DataRootDir is the parent path of the dataset folder
%Dname is the folder that the dataset file is in

% WINDOWS
DataRootDir = 'C:\Users\cooper\Documents\MATLAB';

% LINUX
%DataRootDir = '/home/daniel/Documents/MATLAB';

%Dname = 'Sana_11.4.22';
%Dname = 'Chris_11.3.22';
Dname = 'Emily_11.3.22';
%Dname = 'Andy-11.1.22';
%Dname = 'ChrisP_12_6_2022';

Dname = fullfile(DataRootDir,Dname);
disp(Dname)

% select which footstrike to analyze
row = 20;

%% NOTES

% relate runner sound pitch to speed
% use footfall picture
    % take the second half of the snapshot, after peak ground reaction
    % force
    % then run an FFT on that (mic channels)
    % tag each footstep with speed
        % tack on speed on to the end of each vector
    % lay two different FFTs on top of each other and look for shifts in
    % peaks

    % modify snapshot algo to have a speed variable added on to footstrike
    % vector
    % use tach sensor to find speed inside the snapshot


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

%% FOOTSTRIKE FINDING MAX

% remove the zero padding in the footsrike to the end and to find the index of the end
endvalue = rmmissing(ForceData.footStrikeTime(row,:));
endvaluenum = numel(endvalue);

% calculate the max
[xmax, ymax] = max(ForceData.footStrike(row,:));
maxStrike = xmax;
maxTime = ForceData.footStrikeTime(row,ymax);

% why is the scale 20?
ymaxAccel = ymax*20;

%% READ TACH DATA
if 0
TachData = load_TachData(fullfile(Dname,'Tach_Data.tdms'));

vel = TachData.vel;
M_vel = vel * 2.6; % [rad/s]
B_r = 0.050/2; % [m]
B_vel = vel/(2*pi) * (2*pi*B_r); % roller vel in [rad/s] to belt vel in [m/s]

B_vel_avg = mean(TachData.footStrikeVel(row,1:endvaluenum), "all");

end

%% GRAPH TACH DATA 

if 0
% B_vel is in mph

%figure
%subplot 311
%plot(TachData.t,TachData.Tach);title('Tach')
%ylim([-0.25 1.25])
%subplot 312
%plot(TachData.t,vel);title('Velocity m/s')
%subplot 313
%plot(TachData.t,B_vel);title('Velocity mph') % [m/s] to [mph] *2.23694

plot(TachData.footStrikeTime(row,:), TachData.footStrikeVel(row,:));

end


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
%plot(ForceData.footStrikeTime, ForceData.footStrike);
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
arrayX = [];
arrayY = [];

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
    distanceX = 60 - (60*FRONT_percentnextstrike);
    distanceY = LEFT_percentnextstrike * 25;

    arrayX = [arrayX, distanceX];
    arrayY = [arrayY, distanceY];
    %display(distanceX)
    %display(distanceY)

    % plot the footstrikes on a treadmill deck
    hold on
    plot([0,distance,60], [0,12.5,25],'x',color='white');
    %plot(distanceFront,right_left_placement, 'x', color='blue');
    plot(distanceX,distanceY, 'x', color='red');
    plot(12, 0:25,'.',color='blue');
end

averageXdist = mean(arrayX);
averageYdist = mean(arrayY);

end

%% FIND AND PLOT LOAD CELL DERIVATIVE

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
% plot(ForceData.t,ForceData.Frnt_L);hold all;title('Load Cells lbs')
% plot(ForceData.t,ForceData.FMid_L);
% plot(ForceData.t,ForceData.BMid_L);
% plot(ForceData.t,ForceData.Back_L);
% plot(ForceData.t,ForceData.Frnt_R);
% plot(ForceData.t,ForceData.FMid_R);
% plot(ForceData.t,ForceData.BMid_R);
% plot(ForceData.t,ForceData.Back_R);
% legend('Frnt L','FMid L','BMid L','Back L','Frnt R','FMid R','BMid R','Back R')

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

if 0

% calculate the FFT of a single footstirke on the Z Accel Axis
FFT_ACCELZ = fft(AccelData.footStrikeZ(row, (1:endvaluenum)));
FFTValuesZ = numel(FFT_ACCELZ);

% frequency domain
frequencyZ = 5000*(0:(FFTValuesZ/2))/FFTValuesZ;

P1 = FFT(FFT_MIC, FFTValues);

figure
plot(frequencyZ,P1);title('P1 Z AXIS ACCEL FFT')
%plot(frequencyZ,P2);title('P2 Z AXIS ACCEL FFT')

end

%% MIC FFT
filter = 0.0005;

% SINGLE 
if 0
 
% take the average of the B_vel vector
B_vel_avg = mean(TachData.footStrikeVel(row,1:endvaluenum), "all");

% calculate the FFT of a single footstrike on the sum of all Mic data
FFT_MIC = fft(MicData.footStrikeSum(row, (1:endvaluenum)));
FFTValues = numel(FFT_MIC);

% calculate the FFT of the FFT
FFT_MIC_PRIME = diff(FFT_MIC);
%disp(FFT_MIC_PRIME)
FFTValues_PRIME = numel(FFTValues);

% where 0, is a peak or trough
magnitude = abs(FFT_MIC_PRIME);

% find amplitude and frequency of the peaks 
[amp, freq] = findpeaks(real(FFT_MIC));
%disp(amp)

% filter peaks by choosing a threshold for the amplitude 
% output should be in format (magnitude, Hz, speed)
%filter = 0.0005;

% find where the amplitudes are below the filter
FFT_PRIME_filter = find(amp < filter);
FFTValues_filter = numel(FFT_PRIME_filter);

% set the values to zero where the amplitude is below the filter
amp(FFT_PRIME_filter) = [];
freq(FFT_PRIME_filter) = [];

%disp(FFT_PRIME_filter);

% frequency domain
frequencyMic = 40000*(0:(FFTValues/2))/FFTValues;
frequencyMic2 = 40000*(0:(FFTValues))/FFTValues;

P1 = FFT(FFT_MIC, FFTValues);

% convert B_vel_avg to a string for labelling purposes
averagespeed = 'Average Speed: ' + string(B_vel_avg);
filterstring = 'Filter: ' + string(filter);

figure
%hold on
plot(frequencyMic,P1);title('MIC SINGLE SIDED SPECTRUM FFT')
legend(averagespeed)

figure
plot(freq, amp);title('Filtered FFT')
legend(filterstring)
%plot(frequencyMic2,P2);title('MIC TWO SIDED SPECTRUM FFT')

end

% LOOP
if 0
% loop through all footstrikes and plot the FFTs of each one
figure()
hold on
startLoop = 27;
endLoop = 37;
%nLoops = length(ForceData.endTime);
for j = startLoop:endLoop
%for j = 1:length(ForceData.endTime)

    % take the average of the B_vel vector
    B_vel_avg = mean(TachData.footStrikeVel(j,1:endvaluenum), "all");
    
    % calculate the FFT of a single footstrike on the sum of all Mic data
    FFT_MIC = fft(MicData.footStrikeSum(j, (1:endvaluenum)));
    FFTValues = numel(FFT_MIC);

    % find amplitude and frequency of the peaks 
    [amp, freq] = findpeaks(real(FFT_MIC));
    
    % filter peaks by choosing a threshold for the amplitude 
    % output should be in format (magnitude, Hz, speed)
    %filter = 0.2;
    
    % find where the amplitudes are below the filter
    FFT_PRIME_filter = find(amp < filter);
    FFTValues_filter = numel(FFT_PRIME_filter);
    
    % set the values to zero where the amplitude is below the filter
    amp(FFT_PRIME_filter) = [];
    freq(FFT_PRIME_filter) = [];
    
    % frequency domain
    frequencyMic = 40000*(0:(FFTValues/2))/FFTValues;
    frequencyMic2 = 40000*(0:(FFTValues))/FFTValues;
    
    P1 = FFT(FFT_MIC, FFTValues);
    
    % convert B_vel_avg to a string for labelling purposes
    averagespeed = 'STRIKE ' + string(j) + ' Average Speed: ' + string(B_vel_avg);

    plot(frequencyMic,P1);title('MIC SINGLE SIDED SPECTRUM FFT COMPARISON');
    %plot(freq, amp);
    legends{j-(startLoop-1)} = sprintf(averagespeed);

end
%disp(legends)
legend(legends)

end

% DOUBLE 
if 0

row1 = 27;
row2 = 33;
 
% take the average of the B_vel vector
B_vel_avg1 = mean(TachData.footStrikeVel(row1,1:endvaluenum), "all");
B_vel_avg2 = mean(TachData.footStrikeVel(row2,1:endvaluenum), "all");

% calculate the FFT of a single footstrike on the sum of all Mic data
FFT_MIC1 = fft(MicData.footStrikeSum(row1, (1:endvaluenum)));
FFTValues1 = numel(FFT_MIC1);
FFT_MIC2 = fft(MicData.footStrikeSum(row2, (1:endvaluenum)));
FFTValues2 = numel(FFT_MIC2);

% find amplitude and frequency of the peaks 
[amp1, freq1] = findpeaks(real(FFT_MIC1));
[amp2, freq2] = findpeaks(real(FFT_MIC2));

% filter peaks by choosing a threshold for the amplitude 
% output should be in format (magnitude, Hz, speed)
%filter = 0.2;

% find where the amplitudes are below the filter
FFT_PRIME_filter1 = find(amp1 < filter);
FFTValues_filter1 = numel(FFT_PRIME_filter1);
FFT_PRIME_filter2 = find(amp2 < filter);
FFTValues_filter2 = numel(FFT_PRIME_filter2);

% set the values to zero where the amplitude is below the filter
amp1(FFT_PRIME_filter1) = [];
freq1(FFT_PRIME_filter1) = [];
amp2(FFT_PRIME_filter2) = [];
freq2(FFT_PRIME_filter2) = [];

% frequency domain
frequencyMic = 40000*(0:(FFTValues1/2))/FFTValues1;
filterstring = 'Filter: ' + string(filter);

P1_1 = FFT(FFT_MIC1, FFTValues1);
P1_2 = FFT(FFT_MIC2, FFTValues2);

% convert B_vel_avg to a string for labelling purposes
averagespeed1 = 'STRIKE ' + string(row1) + ' Average Speed: ' + string(B_vel_avg1);
averagespeed2 = 'STRIKE ' + string(row2) + ' Average Speed: ' + string(B_vel_avg2);

figure
hold on
plot(frequencyMic,P1_1);title('MIC SINGLE SIDED SPECTRUM FFT COMPARISON')
%figure
plot(frequencyMic,P1_2);

legend(averagespeed1, averagespeed2)

figure
hold on
plot(freq1, amp1);title('Filtered FFT');
plot(freq2, amp2);
legend(filterstring)


end


%% clear intermediate mat files from target directory

%D = dir(fullfile(Dname,'*.mat'));
%delete(fullfile(Dname,'*.mat'));
%return

%% FUNCTIONS

function f = fact(m,b)
    f = (50-b)/m;
end


function f = FFT(FFT_MIC,FFTValues)
    % single sided and two sided spectrum
    P2 = abs(FFT_MIC/FFTValues);
    P1 = P2(1:FFTValues/2+1);
    P1(2:end-1) = 2*P1(2:end-1);
    
    % not sure why but I had to add a zero to the end of the two sided spectrum
    % also first value is always higher than the rest, so I got rid of it for
    % now
    P2(end+1) = 0;
    P1(1) = 0;
    P2(1) = 0;

    f = P1;
end
    
