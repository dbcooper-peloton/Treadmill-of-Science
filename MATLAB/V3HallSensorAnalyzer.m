function newTable = V3HallSensorAnalyzer(fnameVector, plt)
    
    %comment these if calling from another script
    close all;clear;clc;
    fullfname = fullfile('C:\', 'Bike V3', 'Summary Report File 2022-11-10T11.33.56 P0.11_140rpm_5mm_sweep.csv');
    fullfname2 = fullfile('C:\', 'Bike V3', 'Summary Report File 2022-11-11T10.12.47 P0.11_140rpm_5mm_B2_v2.csv');
    fnameVector = [string(fullfname) string(fullfname2)];
    plt = false;

    %!!!!!!!!change these 2 variables to change sensor number/axis
    activeSensor = 5; % 4, 5, or 6
    activeAxis = 'x'; % 'x', 'y', 'z', or 'T'

    %some constants
    SnCell = 'B3:B3'; %SN cell
    PositionCategories = {'2mm', '7mm', '12mm', '17mm', '22mm', '27mm', '32mm'}; %Brake positions
    
    %get board SNs
    SnVector = {};
    for sn= 1:length(fnameVector)
        [~,bsn,~] = xlsread(fnameVector(sn), 1, SnCell);
        SnVector{sn} = cell2mat(bsn);
    end

    %Get linear regression coefficents and create the models
    RsquareVector = zeros([length(PositionCategories), 1]);
    regressionVector = zeros([length(PositionCategories), 1]);
    for lr=1:length(SnVector)
        model = pltVsTorque(activeSensor, activeAxis, fnameVector(lr), plt);
        regressionVector(:, lr) = model(:, 1);
        RsquareVector(:, lr) = model(:, 2);
       
    end
    
    %create an output table
    tHeader = ["Position in MM"; "Board Sn"; "Slope"; "R Squared"; "Std"];
    tTypes = ["string", "string", "double", "double", "double"];
    tSize = [length(SnVector) * length(PositionCategories), length(tHeader)];
    newTable = table('Size', tSize,'VariableTypes', tTypes, 'VariableNames', tHeader);
    posCounter = 1;

    for z = 1:length(PositionCategories)
        newReg = regressionVector(z, :);
        newRS = RsquareVector(z, :);
        Std = std(newReg);
        for ez = 1:length(SnVector)
            newTable(posCounter, :) = [PositionCategories(z) SnVector(ez) newReg(ez) newRS(ez) Std];
            posCounter = posCounter + 1;
        end
    end
    newTable.('Position in MM') = append(string(newTable.('Position in MM')), "mm"); %Func returns this

    %func to group data by target brake position, normalize, plot, and
    %return a linear regression coefficent
    function SandR2 = pltVsTorque(sensorNum, sensorAxis, FileName, plotData)
        Data = readtable(FileName, "VariableNamingRule","preserve", NumHeaderLines=5);
        posCat = unique(Data.('Target Resistance'));
        poscatNames = strcat(num2str(posCat), 'mm');
        ResVector = Data.('Target Resistance');
        sensor = strcat('R', num2str(sensorNum), '-', string(sensorAxis));
        tName = strcat('Combined Hall Sensor',{' '}, string(sensorNum));
        linRegVector = zeros(size(posCat));
        Rsquare = zeros(size(posCat));
        if plotData
            figure
        end
        for i = 1:length(posCat)
            pos_df = Data(ResVector == posCat(i), :);
            H = mean([pos_df.(sensor), pos_df.(sensor)], 2);
            NormalizedH = -(H - H(1));
            linRegVector(i) = pos_df.('Torque Dyno')\NormalizedH;
            mdl = fitlm(pos_df.('Torque Dyno'), NormalizedH);
            Rsquare(i) = mdl.Rsquared.Ordinary;
            if plotData
                hold on
                plot(pos_df.('Torque Dyno'), NormalizedH, '-o',...
                   'MarkerSize',3)
            end
        end
        SandR2 = [linRegVector(:), Rsquare(:)];
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