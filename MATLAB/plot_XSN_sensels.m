function plot_XSN_sensels(XSNData)

% plot Senel maps
figure;
set(gcf,'Position',[161.6667 347.6667 778.6667 918.0000]);
subplot(1,2,1);
im1 = imagesc(XSNData.S_L(:,:,1));
set(gca,'XTickLabelMode','manual');
set(gca,'YTickLabelMode','manual');
xlim([0.5,11.5]); ylim([0.5,31.5]);
set(gca,'XTick',0.5:11.5);
set(gca,'YTick',0.5:31.5);
set(gca,'Linewidth',1.5);
grid on;
set(gca, 'xlimmode','manual',...
           'ylimmode','manual',...
           'zlimmode','manual',...
           'climmode','auto',...
           'alimmode','manual');
set(gca,'NextPlot','replacechildren');

subplot(1,2,2);
im2 = imagesc(XSNData.S_R(:,:,1));
set(gca,'XTickLabelMode','manual');
set(gca,'YTickLabelMode','manual');
xlim([0.5,11.5]); ylim([0.5,31.5]);
set(gca,'XTick',0.5:11.5);
set(gca,'YTick',0.5:31.5);
set(gca,'Linewidth',1.5);
grid on;
set(gca, 'xlimmode','manual',...
           'ylimmode','manual',...
           'zlimmode','manual',...
           'climmode','auto',...
           'alimmode','manual');
set(gca,'NextPlot','replacechildren');

set(gcf,'doublebuffer','off');

L = size(XSNData.S_L,3);
for i=1:L
    set(im1,'CData',XSNData.S_L(:,:,i));
    set(im2,'CData',XSNData.S_R(:,:,i));
    pause(0.001)
end

return