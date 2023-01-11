function newTable = V3HallSensorAnalyzerMultiRL(~)

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
plt = false; %toggle plot
invertAxis = true; %invert the x/y axis

%This script needs each file to have the same number of Position
%Categories. The categorie names don't have to match between files.
%To compare files that have differ num of categories, save truncated versions
PositionCategories = {'0', '5', '10', '15', '20', '25', '30'};
activeSensor = 4;
activeAxis = 'x';
activeSide = ['R', 'L'];
SnCell = 'B3:B3';

fout = 'RheaHallSensorAnalysis_AllRL.xlsx';

%get board SNs
SnVector = {};
for sn= 1:length(fnameVector)
    [~,bsn,~] = xlsread(fnameVector(sn), 1, SnCell); %#ok<XLSRD>
    SnVector{sn} = cell2mat(bsn); %#ok<AGROW>
end

%create an output table
tHeader = ["Position Category"; "Real Target Position"; "Board Sn"; "Sensor Number"; "Sensor Axis"; "Sensor side"; "Slope"; "Constant"; "R Squared"; "Std"];
tTypes = ["string", "string", "string", "string", "string", "string", "double", "double", "double", "double"];
tSize = [length(SnVector) * length(PositionCategories), length(tHeader)];
newTable = table('Size', tSize,'VariableTypes', tTypes, 'VariableNames', tHeader);

%Get linear regression coefficents and create the models
RsquareVector = zeros([length(PositionCategories), 1]);
regressionVector = zeros([length(PositionCategories), 1]);
trueTargetPos = zeros([length(PositionCategories), 1]);
constantVector = zeros([length(PositionCategories), 1]);

pCounter = 1;
for lr=1:length(SnVector)
    for s = 1:length(activeSide)
        model = regmodel(activeSensor, activeAxis, fnameVector(lr), plt, SnVector(lr), invertAxis, activeSide(s));
        regressionVector(:, pCounter) = model(:, 1);
        RsquareVector(:, pCounter) = model(:, 2);
        trueTargetPos(:, pCounter) = model(:, 3);
        constantVector(:, pCounter) = model(:, 4);
        pCounter = pCounter + 1;
    end
end

%Write the Slope, Rsquared, and Standard Deviation to output file
rCounter = 1;
for pos = 1:length(PositionCategories)
    posCounter = 1;
    newReg = regressionVector(pos, :);
    stdR = std(newReg(1:2:end));
    stdL = std(newReg(2:2:end));
    Std = [stdR, stdL];
    newRS = RsquareVector(pos, :);
    newconstant = constantVector(pos, :); 
    for SN = 1:length(SnVector) 
        for ss = 1:length(activeSide)
            newTable(rCounter, :) = [PositionCategories(pos) trueTargetPos(pos, SN) SnVector(SN) activeSensor activeAxis activeSide(ss) newReg(posCounter) newconstant(posCounter) newRS(posCounter) Std(ss)];
            posCounter = posCounter + 1;
            rCounter = rCounter + 1;
        end
    end
end

%newTable.('Real Target Position') = append(string(newTable.('Real Target Position')), "mm");
writetable(newTable, fout); %write to file

%func to group data by target brake position, normalize, plot, and
%return a linear regression coefficent. plotData is a bool for plotting
    function RegressionModel = regmodel(sensorNum, sensorAxis, FileName, plotData, SN, inAx, side)
        Data = readtable(FileName, "VariableNamingRule","preserve", NumHeaderLines=5);
        posCat = unique(Data.('Target Resistance'));
        ResVector = Data.('Target Resistance');
        sensor = strcat(string(side), num2str(sensorNum), '-', string(sensorAxis));
        pTitle = strcat(string(side), num2str(sensorNum), '-', string(sensorAxis));
        linRegVector = zeros(size(posCat));
        Rsquare = zeros(size(posCat));
        constantsVector = zeros(size(posCat));
        if plotData
           figure
        end

        tName = strcat('Hall Sensor',{' '}, string(pTitle), {' '}, {'Board'}, {' '}, string(SN));

        Data.H = Data.(sensor);
        Data.NormalizedH = -(Data.H - Data.H(1));

        for i = 1:length(posCat)
            pos_df = Data(ResVector == posCat(i), :);
            x = pos_df.('Torque Dyno');
            y = pos_df.NormalizedH;
            if inAx
                tempTbl = table(y, x);
            else
                tempTbl = table(x, y);
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