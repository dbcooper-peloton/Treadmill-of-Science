close all;clear;clc;

%DataRootDir is the parent path of the dataset folder
%Dname is the folder that the dataset file is in

DataRootDir = 'C:\Users\cooper\Documents\MATLAB';

Dname = 'Sana_11.4.22';
%Dname = 'Andy-11.1.22';
%Dname = 'Chris_11.3.22';
%Dname = 'Emily_11.3.22';

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

row = 18;
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
if 1
%row = 17;
figure
hold all
plot(ForceData.footStrikeTime(row,:),ForceData.footStrike(row,:));title('single strike load cell');ylabel('Pounds (lbs)');xlabel('Time (Datetime)')
plot(ForceData.footStrikeTime(row,:), ForceData.footStrikeZone1(row,:));
plot(ForceData.footStrikeTime(row,:), ForceData.footStrikeZone2(row,:));
plot(ForceData.footStrikeTime(row,:), ForceData.footStrikeZone3(row,:));
plot(ForceData.footStrikeTime(row,:), ForceData.footStrikeZone4(row,:));
%hold off


%display(ForceData.max)
%display(ForceData.maxTime)

% calculate the max
[xmax, ymax] = max(ForceData.footStrike(row,:));
maxStrike = xmax;
maxTime = ForceData.footStrikeTime(row,ymax);

%display(maxStrike)
%display(maxTime)
plot(maxTime, maxStrike,'x',color='red');

% calculate the percentages
zone1_percent = ForceData.footStrikeZone1(row,ymax)/maxStrike * 100;
zone2_percent = ForceData.footStrikeZone2(row,ymax)/maxStrike * 100;
zone3_percent = ForceData.footStrikeZone3(row,ymax)/maxStrike * 100;
zone4_percent = ForceData.footStrikeZone4(row,ymax)/maxStrike * 100;

% find the value of the zones at the max value
zone1_value = ForceData.footStrikeZone1(row,ymax);
zone2_value = ForceData.footStrikeZone2(row,ymax);
zone3_value = ForceData.footStrikeZone3(row,ymax);
zone4_value = ForceData.footStrikeZone4(row,ymax);

% create vectors
zonevectorpercentage = [zone1_percent,zone2_percent,zone3_percent,zone4_percent];
zonevectorvalue = [zone1_value, zone2_value, zone3_value, zone4_value];
deckvector = [8.3, 26.7, 28.3, 26.7, 10];

%figure
% plot the max
%hold on
plot(ForceData.footStrikeTime(row,ymax), zone1_value,'x',color='magenta');
plot(ForceData.footStrikeTime(row,ymax), zone2_value,'x',color='blue');
plot(ForceData.footStrikeTime(row,ymax), zone3_value,'x',color='green');
plot(ForceData.footStrikeTime(row,ymax), zone4_value,'x',color='black');

% algo time
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

%display(zonevectorvalue(ii))
%display(zonevectorvalue(ii-1))
%display(sum2)
%display(rise)
%display(run)

% calculate slope
m = rise/run;

% find x
x = fact(m,b);

% find distance travelled
distance = ((x + sum2)/100) * 60;

display(m)
display(b)
display(x)
display(distance)


%legend('Front Percentage: '+ zone1_percent, 'Front Middle Percentage: '+zone2_percent,'Back Middle Percentage: '+zone3_percent,'Back Percentage: '+zone4_percent);
stringpercentage1 = 'Front: ' + string(zone1_percent);
stringpercentage2 = 'Front Middle: ' + string(zone2_percent);
stringpercentage3 = 'Back Middle: ' + string(zone3_percent);
stringpercentage4 = 'Back: ' + string(zone4_percent);
legend('Sum', 'Front Zone', 'Front Middle Zone', 'Back Middle Zone', 'Back Zone', stringpercentage1, stringpercentage2, stringpercentage3, stringpercentage4);


figure
hold on
plot([0,distance,60], [0,12.5,25],'x',color='red');
plot(12, 0:25,'.',color='blue');


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
if 0
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

if 0
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

% function to find x in y = mx+b
function f = fact(m,b)
    f = (50-b)/m;
end


