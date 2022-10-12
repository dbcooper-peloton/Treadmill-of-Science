function VoltsData = load_VoltsData(fullfname_tdms)

[Dname,fname,~] = fileparts(fullfname_tdms);
fullfname_mat = fullfile(Dname,[fname '.mat']);

if ~exist(fullfname_mat,'file')
    Data = convertTDMS(0,fullfname_tdms);

    VoltsData.t = Data.Data.MeasuredData(3).Data;
    VoltsData.t = datetime(VoltsData.t,'ConvertFrom','datenum','TimeZone','local');
    VoltsData.t.TimeZone = 'America/Los_Angeles';

    voltage = Data.Data.MeasuredData(4).Data*100;
    VoltsData.Voltage = voltage;


    save(fullfname_mat,'VoltsData');
else
    load(fullfname_mat,'VoltsData');
end

return