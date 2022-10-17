close all;clear;clc;

fname = 'John W 7-11 Test.csv';

[Time,S_L,S_R] = readxsn(fname);

% figure
% plot(Time)
% xlabel('Frames')
% ylabel("Time [sec]")

[~,I] = min(Time);
L = numel(Time);
if I>1
    % non-monitonic time found, crop data
    Time = Time(I:L);
    S_L = S_L(:,:,I:L);
    S_R = S_R(:,:,I:L);
end

% plot the raw Sensel data frame by frame
figure
set(gcf,'Position',[161.6667 347.6667 778.6667 918.0000]);
for i=1:numel(Time)
    subplot 121
    contourf(S_L(:,:,i));grid on;
    set(gca,'XTick',[1:11]);
    set(gca,'YTick',[1:31]);
    set(gca,'Linewidth',1.5);
    subplot 122
    contourf(S_R(:,:,i));grid on;
    set(gca,'XTick',[1:11]);
    set(gca,'YTick',[1:31]);
    set(gca,'Linewidth',1.5);
    drawnow;
end