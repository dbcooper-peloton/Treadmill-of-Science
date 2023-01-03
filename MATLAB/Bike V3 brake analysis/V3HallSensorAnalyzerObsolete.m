function newTable = V3HallSensorAnalyzer(~)
    
    close all;clear;clc;
    
    %find all csv files in the dirPath and load the names into the fnameVector
    dirPath = 'C:\Bike V3';
    fnameVector = ["temp"]; % init the vector as string
    fileList = dir(fullfile(dirPath, '*.csv'));
    for f = 1:length(fileList)
        fnameVector(f) = fullfile(dirPath, fileList(f).name);
    end

    %plot option
    plt = true;

    %This script needs each file to have the same number of Position
    %Categories. The categorie names don't have to match between files.
    %To compare files that have differ num of categories, save truncated versions
    PositionCategories = {'0mm', '5mm', '10mm', '15mm', '20mm', '25mm', '30mm'};
    activeSensor = [4, 5];
    activeAxis = {'x', 'y', 'z'};
    SnCell = 'B3:B3';
    fout = 'RheaHallSensorAnalysisObsolete.xlsx';
    
    %get board SNs
    SnVector = {};
    for sn= 1:length(fnameVector)
        [~,bsn,~] = xlsread(fnameVector(sn), 1, SnCell); %#ok<XLSRD> 
        SnVector{sn} = cell2mat(bsn); %#ok<AGROW> 
    end

    %create an output table
    tHeader = ["Position Category"; "Real Target Position"; "Board Sn"; "Sensor Number"; "Sensor Axis"; "Slope"; "R Squared"; "Std"];
    tTypes = ["string", "string", "string", "string", "string", "double", "double", "double",];
    tSize = [length(SnVector) * length(PositionCategories), length(tHeader)];
    newTable = table('Size', tSize,'VariableTypes', tTypes, 'VariableNames', tHeader);
    posCounter = 1;

    %!!!loop through sensor/axis combo.3x, 3y, 3z, 4x, 4y, 4z, 5x, 5y, 5z
    %Get linear regression coefficents and create the models

    model = pltVsTorque(activeSensor(1), activeAxis(1), fnameVector(1), plt, SnVector(1))

%     for senseNum = 1:length(activeSensor)
%         for senseAxis = 1:length(activeAxis)
%             %Get linear regression coefficents and create the models
%             RsquareVector = zeros([length(PositionCategories), 1]);
%             regressionVector = zeros([length(PositionCategories), 1]);
%             trueTargetPos = zeros([length(PositionCategories), 1]);
% 
%             for lr=1:length(SnVector)
%                 model = pltVsTorque(activeSensor(senseNum), activeAxis(senseAxis), fnameVector(lr), plt, lr);
%                 regressionVector(:, lr) = model(:, 1);
%                 RsquareVector(:, lr) = model(:, 2);
%                 trueTargetPos(:, lr) = model(:,3);
%             end
% 
%             for z = 1:length(PositionCategories)
%                 newReg = regressionVector(z, :);
%                 newRS = RsquareVector(z, :);
%                 Std = std(newReg);
% 
%                 for ez = 1:length(SnVector)
%                     newTable(posCounter, :) = [PositionCategories(z) trueTargetPos(z, ez) SnVector(ez) activeSensor(senseNum) activeAxis(senseAxis) newReg(ez) newRS(ez) Std];
%                     posCounter = posCounter + 1;
%                 end
%             end
%         end
%     end
%     %!!!End interation

   %newTable.('Real Target Position') = append(string(newTable.('Real Target Position')), "mm");
   %writetable(newTable, fout); %write to file

    %func to group data by target brake position, normalize, plot, and
    %return a linear regression coefficent. plotData is a bool for plotting
    function SandR2 = pltVsTorque(sensorNum, sensorAxis, FileName, plotData, SN)
        Data = readtable(FileName, "VariableNamingRule","preserve", NumHeaderLines=5);
        posCat = unique(Data.('Target Resistance'));
        poscatNames = strcat(num2str(posCat), 'mm');
        ResVector = Data.('Target Resistance');
        sensorR = strcat('R', num2str(sensorNum), '-', string(sensorAxis));
        sensorL = strcat('L', num2str(sensorNum), '-', string(sensorAxis));
        pTitle = strcat(num2str(sensorNum), '-', string(sensorAxis));
        tName = strcat('Combined Hall Sensor',{' '}, string(pTitle), {' '}, {'Board'}, {' '}, string(SN));
        linRegVector = zeros(size(posCat));
        Rsquare = zeros(size(posCat));
        if plotData
            figure
        end
        for i = 1:length(posCat)
            pos_df = Data(ResVector == posCat(i), :);
            H = mean([pos_df.(sensorR), pos_df.(sensorL)], 2);
            NormalizedH = -(H - H(1));
            linRegVector(i) = pos_df.('Torque Dyno')\NormalizedH;
            mdl = fitlm(pos_df.('Torque Dyno'), H);
            Rsquare(i) = mdl.Rsquared.Ordinary;
            if plotData
                hold on
                plot(pos_df.('Torque Dyno'), H, '-o',...
                   'MarkerSize',3)
            end
        end
        SandR2 = [linRegVector(:), Rsquare(:), posCat(:)];
        if plotData
            grid on
            title(tName)
            xlabel('Dyno Torque')
            ylabel('Magnetic Field uT') 
            legend(poscatNames,...
               'location', 'northwest', NumColumns=1)
        end
    end
end