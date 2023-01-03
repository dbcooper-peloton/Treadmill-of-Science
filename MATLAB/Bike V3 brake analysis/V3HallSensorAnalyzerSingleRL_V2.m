function outTable = V3HallSensorAnalyzerSingleRL_V2(~)

%----------------------------------------------------------------------
%                           Setup
%----------------------------------------------------------------------
    close all;clear;clc;
    
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
    
    fout = 'RheaHallSensorAnalysis_SingleRL_V2.xlsx';
    
    %get board SNs
    SnVector = {};
    for sn= 1:length(fnameVector)
        [~,bsn,~] = xlsread(fnameVector(sn), 1, SnCell); %#ok<XLSRD>
        SnVector{sn} = cell2mat(bsn); %#ok<AGROW>
    end
    
    %create an output table
    tHeader = ["Position Category"; "Board Sn"; "Sensor Number"; "Sensor Axis"; "Sensor side"; "Slope"; "Constant"; "R Squared"];
    tTypes = ["string", "string", "string", "string", "string", "double", "double", "double"];
    tSize = [length(SnVector) * length(PositionCategories), length(tHeader)];
    outTable = table('Size', tSize,'VariableTypes', tTypes, 'VariableNames', tHeader);

%--------------------------------------------------------------------------
%                           Main Loop
%--------------------------------------------------------------------------  
    pCounter = 1;
    for lr=1:length(SnVector)
        for s = 1:length(activeSide)
            outTable = DS(activeSensor, activeAxis, activeSide(s), fnameVector(lr), SnVector(lr), invertAxis, outTable, pCounter);
            pCounter = pCounter + length(PositionCategories);
        end
     end

    writetable(outTable, fout); %write to file

%-------------------------------------------------------------------------
%                           Functions
%-------------------------------------------------------------------------

    function DataScience = DS(sensorNum, sensorAxis, sensorSide, FileName, SN, invertAx, tbl, tblPos)
        Data = readtable(FileName, "VariableNamingRule","preserve", NumHeaderLines=5); %Full file table
        posCat = unique(Data.('Target Resistance')); %Target position categories (Target Resistance)
        ResVector = Data.('Target Resistance'); %full Target Resistance column
        sensor = strcat(string(sensorSide), num2str(sensorNum), '-', string(sensorAxis)); %name of the sensor column
        Data.H = Data.(sensor); %data column for the input sensor
        Data.NormalizedH = -(Data.H - Data.H(1)); %normalize the data so 0 rpm is 0
        DataScience = tbl;

        for i = 1:length(posCat) % for each position category
            pos_df = Data(ResVector == posCat(i), :); %get all the data for only that category
            x = pos_df.('Torque Dyno'); % linreg model
            y = pos_df.NormalizedH; % linreg model
            if invertAx
                tempTbl = table(y, x);
            else
                tempTbl = table(x, y);
            end
            mdl = fitlm(tempTbl);
            linReg = mdl.Coefficients.Estimate(2);
            constant = mdl.Coefficients.Estimate(1);
            Rsquare = mdl.Rsquared.Ordinary;
            DataScience(tblPos + i - 1, :) = [posCat(i) SN sensorNum sensorAxis sensorSide linReg constant Rsquare];
        end
    end
end
