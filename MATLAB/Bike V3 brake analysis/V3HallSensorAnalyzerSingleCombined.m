function newTable = V3HallSensorAnalyzerSingleCombined(~)

close all;clear;clc;
%format long

%find all csv files in the dirPath and load the names into the fnameVector
dirPath = 'C:\Bike V3';
fnameVector = ["temp"]; % init the vector as string
fileList = dir(fullfile(dirPath, '*.csv'));
for f = 1:length(fileList)
    fnameVector(f) = fullfile(dirPath, fileList(f).name);
end

%options
plt = true; %toggle plot
invertAxis = true; %invert the x/y axis

%This script needs each file to have the same number of Position
%Categories. The categorie names don't have to match between files.
%To compare files that have differ num of categories, save truncated versions
PositionCategories = {'0mm', '5mm', '10mm', '15mm', '20mm', '25mm', '30mm'};
activeSensor = 4;
activeAxis = 'x';
SnCell = 'B3:B3';

fout = 'RheaHallSensorAnalysis_SingleCombined.xlsx';

%get board SNs
SnVector = {};
for sn= 1:length(fnameVector)
    [~,bsn,~] = xlsread(fnameVector(sn), 1, SnCell); %#ok<XLSRD>
    SnVector{sn} = cell2mat(bsn); %#ok<AGROW>
end

%create an output table
tHeader = ["Position Category"; "Real Target Position"; "Board Sn"; "Sensor Number"; "Sensor Axis"; "Slope"; "Constant"; "R Squared"; "Std"];
tTypes = ["string", "string", "string", "string", "string", "double", "double", "double", "double"];
tSize = [length(SnVector) * length(PositionCategories), length(tHeader)];
newTable = table('Size', tSize,'VariableTypes', tTypes, 'VariableNames', tHeader);
posCounter = 1;

%Get linear regression coefficents and create the models
RsquareVector = zeros([length(PositionCategories), 1]);
regressionVector = zeros([length(PositionCategories), 1]);
trueTargetPos = zeros([length(PositionCategories), 1]);
constantVector = zeros([length(PositionCategories), 1]);

for lr=1:length(SnVector)
    model = regmodel(activeSensor, activeAxis, fnameVector(lr), plt, lr, invertAxis);
    regressionVector(:, lr) = model(:, 1);
    RsquareVector(:, lr) = model(:, 2);
    trueTargetPos(:, lr) = model(:, 3);
    constantVector(:, lr) = model(:, 4);
end

%Write the Slope, Rsquared, and Standard Deviation to output file
for pos = 1:length(PositionCategories)
    newReg = regressionVector(pos, :);
    newRS = RsquareVector(pos, :);
    Std = std(newReg);
    newconstant = constantVector(pos, :);

    for SN = 1:length(SnVector)
        newTable(posCounter, :) = [PositionCategories(pos) trueTargetPos(pos, SN) SnVector(SN) activeSensor activeAxis newReg(SN) newconstant(SN) newRS(SN) Std];
        posCounter = posCounter + 1;
    end
end

newTable.('Real Target Position') = append(string(newTable.('Real Target Position')), "mm");
writetable(newTable, fout); %write to file

%func to group data by target brake position, normalize, plot, and
%return a linear regression coefficent. plotData is a bool for plotting
    function RegressionModel = regmodel(sensorNum, sensorAxis, FileName, plotData, SN, inAx)
        Data = readtable(FileName, "VariableNamingRule","preserve", NumHeaderLines=5);
        posCat = unique(Data.('Target Resistance'));
        %poscatNames = strcat(num2str(posCat), 'mm') % for plot
        ResVector = Data.('Target Resistance');
        sensorR = strcat('R', num2str(sensorNum), '-', string(sensorAxis));
        sensorL = strcat('L', num2str(sensorNum), '-', string(sensorAxis));
        pTitle = strcat(num2str(sensorNum), '-', string(sensorAxis));
        linRegVector = zeros(size(posCat));
        Rsquare = zeros(size(posCat));
        constantsVector = zeros(size(posCat));
        if plotData
           figure
        end

        tName = strcat('Combined Hall Sensor',{' '}, string(pTitle), {' '}, {'Board'}, {' '}, string(SN));

        Data.H = mean([Data.(sensorR), Data.(sensorL)], 2);
        Data.NormalizedH = -(Data.H - Data.H(1));

        for i = 1:length(posCat)
            pos_df = Data(ResVector == posCat(i), :);
            x = pos_df.('Torque Dyno');
            y = pos_df.NormalizedH;
            if inAx
                tempTbl = table(y, x);
                %mName = strcat("uT ~ Toque", {' '}, poscatNames(i));
            else
                tempTbl = table(x, y);
                %mName = strcat("Torque ~ uT", {' '}, poscatNames(i));
            end
            
            mdl = fitlm(tempTbl);
            linRegVector(i) = mdl.Coefficients.Estimate(2);
            constantsVector(i) = mdl.Coefficients.Estimate(1);
            Rsquare(i) = mdl.Rsquared.Ordinary;
            if plotData
                hold on
                p = plot(mdl);
                delete(p(3:4));
                delete(p(1));
                scatter(y, x);
            end
        end
        RegressionModel = [linRegVector(:), Rsquare(:), posCat(:), constantsVector(:)];
        if plotData
            grid on
            title(tName)
            if inAx
                ylabel('Dyno Torque')
                xlabel('Magnetic Field uT')
            else
                xlabel('Dyno Torque')
                ylabel('Magnetic Field uT')
            end
            l = get(gca,'Children');
            legend([l(1),l(3), l(5), l(7), l(9), l(11), l(13)],string(posCat));
            exportgraphics(gcf,strcat(tName, '.png'),'Resolution',300);
        end
    end
end