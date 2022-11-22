function DynoData = load_RawDynoV3(fullfname)

%fullfname = fullfile('C:\', 'Bike V3', 'drive-download-20221114T234942Z-001', 'Raw Log File 2022-11-11T10.12.47 P0.11_140rpm_5mm_B2_v2.csv')

[Dname,fname,~] = fileparts(fullfname);
fullfname_mat = fullfile(Dname,[fname '.mat']);

if ~exist(fullfname_mat,'file')
    
Data = readtable(fullfname, "VariableNamingRule","preserve");

DynoData.timestamp = Data.Timestamp
DynoData.step = Data.('Step Number')

DynoData.power = Data.('Power - Bike');
DynoData.resistance = Data.('L-value / Resistance');
DynoData.BrakePos = Data.('Brake Position');
DynoData.BrakeDisp = Data.('Brake_Disp(mm)');

DynoData.R3_x = Data.('R3-x');
DynoData.R3_y = Data.('R3-y');
DynoData.R3_z = Data.('R3-z');
DynoData.R3_T = Data.('R3-T');

DynoData.R4_x = Data.('R4-x');
DynoData.R4_y = Data.('R4-y');
DynoData.R4_z = Data.('R4-z');
DynoData.R4_T = Data.('R4-T');

DynoData.R5_x = Data.('R5-x');
DynoData.R5_y = Data.('R5-y');
DynoData.R5_z = Data.('R5-z');
DynoData.R5_T = Data.('R5-T');

DynoData.L3_x = Data.('R3-x');
DynoData.L3_y = Data.('R3-y');
DynoData.L3_z = Data.('R3-z');
DynoData.L3_T = Data.('R3-T');

DynoData.L4_x = Data.('R4-x');
DynoData.L4_y = Data.('R4-y');
DynoData.L4_z = Data.('R4-z');
DynoData.L4_T = Data.('R4-T');

DynoData.L5_x = Data.('R5-x');
DynoData.L5_y = Data.('R5-y');
DynoData.L5_z = Data.('R5-z');
DynoData.L5_T = Data.('R5-T');

    save(fullfname_mat,'DynoData');
else
    load(fullfname_mat,'DynoData');
end

return