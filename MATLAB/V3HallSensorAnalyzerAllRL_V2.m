function outTable = V3HallSensorAnalyzerAllRL_V2(~)

%----------------------------------------------------------------------
%                           Setup
%----------------------------------------------------------------------
    close all;clear;clc; 
    delete 'RheaHallSensorAnalysis_AllRL_V2.xlsx';
    %find all csv files in the dirPath and load the names into the fnameVector
    dirPath = 'C:\Bike V3';
    fnameVector = ["temp"]; % init the vector as string
    fileList = dir(fullfile(dirPath, '*.csv'));
    for f = 1:length(fileList)
        fnameVector(f) = fullfile(dirPath, fileList(f).name);
    end
    
    %options
    invertAxis = true; %invert the x/y axis
    pltD = false; %plot each board sensor and save the image. produces 12 images per board.
    
    %This script needs each file to have the same number of Position
    %Categories. The categorie names don't have to match between files.
    %To compare files that have differ num of categories, save truncated versions
    PositionCategories = [0, 5, 10, 15, 20, 25, 30];
    activeSensor = [4, 5];
    activeAxis = ['x', 'y', 'z'];
    activeSide = ['R' 'L'];
    SnCell = 'B3:B3';
    
    fout = 'RheaHallSensorAnalysis_AllRL_V2.xlsx';
    
    %get board SNs
    SnVector = {};
    for sn= 1:length(fnameVector)
        [~,bsn,~] = xlsread(fnameVector(sn), 1, SnCell); %#ok<XLSRD>
        SnVector{sn} = cell2mat(bsn); %#ok<AGROW>
    end
    
    %create an output table
    tHeader = ["Position Category"; "Board Sn"; "SensorName"; "Sensor Number"; "Sensor Axis"; "Sensor side"; "Slope"; "Constant"; "R Squared"; "StdDev"];
    tTypes = ["single", "string", "string", "string", "string", "string", "double", "double", "double", "double"];
    tSize = [length(SnVector) * length(PositionCategories), length(tHeader)];
    outTable = table('Size', tSize,'VariableTypes', tTypes, 'VariableNames', tHeader);

%--------------------------------------------------------------------------
%                           Main Loop
%-------------------------------------------------------------------------- 
    disp("Working...")
    pCounter = 1;
    for lr=1:length(SnVector) %for each Board
        for n = 1:length(activeSensor) % for each Board sensor
            for a = 1:length(activeAxis) % for each Board sensor Axis
                for s = 1:length(activeSide) % for each Board sensor Axis side combo
                    outTable = DS(activeSensor(n), activeAxis(a), activeSide(s), fnameVector(lr), SnVector(lr), invertAxis, pltD, outTable, pCounter);
                    pCounter = pCounter + length(PositionCategories);
                end
            end
        end
    end

    %calculate standard deviation for each position/sensor/axis/side combo
    sensorNames = unique(outTable.SensorName);
    for p = 1:length(PositionCategories) %for each position
        catData = outTable(outTable.('Position Category') == PositionCategories(p), :); %get all the data for only that category
        for sName = 1:length(sensorNames) %for each sensor number/axis/side combo
            pData = catData(catData.SensorName == sensorNames(sName), :); %get all the data for each sensor/category combo
            outTable.StdDev(outTable.SensorName == sensorNames(sName) & outTable.('Position Category') == PositionCategories(p), :) = std(pData.Slope);
        end
    end

    %Sanity check.  duplicates mean there is likely a problem
    if size(outTable.Slope) ~= size(unique(outTable.Slope))
        outTable(end + 1, 2) = {'Warning, duplicate slope values'};
    elseif size(outTable.Constant) ~= size(unique(outTable.Constant))
        outTable(end + 1, 3) = {'Warning, duplicate slope values'};
    elseif size(outTable.('R Squared')) ~= size(unique(outTable.('R Squared')))
        outTable(end + 1, 4) = {'Warning, duplicate slope values'};
    end
    writetable(outTable, fout); %write to file

%-------------------------------------------------------------------------
%                           Functions
%-------------------------------------------------------------------------
% This function takes in the sensor number, axis, and side; the filename
% for the board, the Board SN, the invert axis and plot options, the table, and the
% table row to start writting at. It will calculate the linear regression
% model for each position, write them to the table and return the table

    function DataScience = DS(sensorNum, sensorAxis, sensorSide, FileName, SN, invertAx, plt, tbl, tblPos)
        Data = readtable(FileName, "VariableNamingRule","preserve", NumHeaderLines=5); %Full file table
        posCat = unique(Data.('Target Resistance')); %Target position categories (Target Resistance)
        ResVector = Data.('Target Resistance'); %full Target Resistance column
        sensor = strcat(string(sensorSide), num2str(sensorNum), '-', string(sensorAxis)); %name of the sensor column
        Data.H = Data.(sensor); %data column from the input sensor
        Data.NormalizedH = -(Data.H - Data.H(1)); %normalize the data so 0 rpm value is 0 uT
        DataScience = tbl;
        if plt
            figure
        end
        for i = 1:length(posCat) % for each position category
            pos_df = Data(ResVector == posCat(i), :); %get all the data for only that category
            x = pos_df.('Torque Dyno'); % linreg model
            y = pos_df.NormalizedH; % linreg model
            if invertAx %invert the axis option
                tempTbl = table(y, x);
            else
                tempTbl = table(x, y);
            end
            mdl = fitlm(tempTbl); %the linear model for this position
            linReg = mdl.Coefficients.Estimate(2);
            constant = mdl.Coefficients.Estimate(1);
            Rsquare = mdl.Rsquared.Ordinary;
            DataScience(tblPos + i - 1, :) = [posCat(i) SN {sensor} sensorNum sensorAxis sensorSide linReg constant Rsquare, 0];
            if plt
                hold on
                pt = plot(mdl);
                delete(pt(3:4));
                delete(pt(1));
                if invertAx
                    scatter(y, x);
                else
                    scatter(x, y);
                end
            end
        end
        if plt
            grid on
            title(strcat(sensor, SN))
            if invertAx
                ylabel('Dyno Torque')
                xlabel('Magnetic Field uT')
            else
                xlabel('Dyno Torque')
                ylabel('Magnetic Field uT')
            end
            l = get(gca,'Children');
            legend([l(1),l(3), l(5), l(7), l(9), l(11), l(13)],string(posCat));
            exportgraphics(gcf,strcat(sensor, '.png'),'Resolution',300);
        end
    end
end
