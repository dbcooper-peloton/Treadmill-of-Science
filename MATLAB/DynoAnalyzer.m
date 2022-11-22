DataRootDir = 'C:\Bike V3'
%Dname = 'Raw Log File 2022-11-11T10.12.47 P0.11_140rpm_5mm_B2_v2.csv'
Dname = 'Summary Report File 2022-11-10T11.33.56 P0.11_140rpm_5mm_sweep.csv'

Dname = fullfile(DataRootDir,Dname);

%DynoData = load_RawDynoV3(Dname);
DynoData = load_SummaryDynoV3(Dname)


%figure('Name','Power vs R3')
%plot(DynoData.R3_x, DynoData.power)
