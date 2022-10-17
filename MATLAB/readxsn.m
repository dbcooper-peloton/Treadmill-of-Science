% Read into Matlab XSensor session log file 
% 
% [Time,S_L,S_R] = readxsn(fname)
% returns a Time vector and the raw Left and Right Sensel matricies
% 
% ver: 2022-07-27

function [Time,S_L,S_R] = readxsn(fname)

h = waitbar(0,'Reading XSN file, please wait...');
fid = fopen(fname,'rt');
% read full file into cell array
C = textscan(fid,'%s','whitespace', '','delimiter','\n'); C = C{1};
fclose(fid);
waitbar(1,h);drawnow;

% Find all FRAMEs in file
I_frame = strmatch('"FRAME"',C);
% Find all SENSELS sets in file
I_sensels = strmatch('"SENSELS"',C);

L = numel(I_frame);
% allocate output variables
Time = zeros(L,1);
S_L = zeros(31,11,L);
S_R = zeros(31,11,L);

% loop through all frames and parse the chosen fields
waitbar(0,h,'Parsing XSN file, please wait...');
for i=1:L
    % Parse time value from current frame
    a = I_frame(i);
    Time(i) = sscanf(C{a+2},'"Time","%f"');

    % Grab indecies for Left and Right Sensels matricies from current frame
    A = find(I_sensels > I_frame(i),2,'first');
    
    % Parse Left Sensels maxtix from 31 lines of data
    a = I_sensels(A(1));
    for j=1:31
        S_L(j,:,i) = sscanf(C{a+j},'"%f","%f","%f","%f","%f","%f","%f","%f","%f","%f","%f')';
    end
    
    % Parse Right Sensels maxtix from 31 lines of data
    a = I_sensels(A(2));
    for j=1:31
        S_R(j,:,i) = sscanf(C{a+j},'"%f","%f","%f","%f","%f","%f","%f","%f","%f","%f","%f')';
    end

    waitbar(i/L,h)
end
close(h);

% dont flip, keep them so print to console is the correct orientation
% S_L = flipud(S_L);
% S_R = flipud(S_R);

return