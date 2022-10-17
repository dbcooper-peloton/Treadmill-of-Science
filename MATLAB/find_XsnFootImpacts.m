function FootImpacts = find_XsnFootImpacts(XSNData,leftright)

plotflag = 0;

if isequal(upper(leftright),'LEFT')
    Toe = XSNData.Fest_Toe_L;
    Met = XSNData.Fest_Met_L;
    Mid = XSNData.Fest_Mid_L;
    Hel = XSNData.Fest_Hel_L;
    Fest = XSNData.Fest_L;

    if plotflag
    f1=figure; hold all;
    plot(XSNData.t,XSNData.Fest_Toe_L)
    plot(XSNData.t,XSNData.Fest_Met_L)
    plot(XSNData.t,XSNData.Fest_Mid_L)
    plot(XSNData.t,XSNData.Fest_Hel_L)
    legend('Toe','Meta','Mid','Heel')
    end
else
    Toe = XSNData.Fest_Toe_R;
    Met = XSNData.Fest_Met_R;
    Mid = XSNData.Fest_Mid_R;
    Hel = XSNData.Fest_Hel_R;
    Fest = XSNData.Fest_R;

    if plotflag
    f1=figure; hold all;
    plot(XSNData.t,XSNData.Fest_Toe_R)
    plot(XSNData.t,XSNData.Fest_Met_R)
    plot(XSNData.t,XSNData.Fest_Mid_R)
    plot(XSNData.t,XSNData.Fest_Hel_R)
    legend('Toe','Meta','Mid','Heel')
    end
end

ang = atan(Met./Hel);
ang = ang - atan(1); % offset around zero for in sync Heel / Metatarsal

ang2 = atan(Met./Mid);
ang2 = ang2 - atan(1); % offset around zero for in sync Mid / Metatarsal

% scale angle with signal amplitude to mask out noise
k = Fest;

% use derivative of k to increase the gain at the edges of the steps
% k_diff = [0;diff(k)];
% k_diff = abs(k_diff);
% k_diff = k_diff/max(k_diff);
% k = k + k_diff;

k = k-min(k);
k = k/max(k);

ang = ang .* k * (180/pi);
ang2 = ang2 .* k * (180/pi);

th = mean(k)/2; % known min(k)==0
kk = zeros(size(k));
kk(k>th) = 1;

if plotflag
ff = gcf;
f3 = figure;
plot(XSNData.t,k,'b');hold on;
plot(XSNData.t,ones(size(k))*th,'k');
plot(XSNData.t,kk,'r')
figure(ff);
end

ndx_impact = find(diff(kk)>0);
ndx_liftoff = find(diff(kk)<0);
% sync
if ~(ndx_impact(1) < ndx_liftoff(1))
    ndx_liftoff(1)=[];
end
if length(ndx_impact) > length(ndx_liftoff)
    ndx_impact(end)=[];
end

type_impact = zeros(size(ndx_impact));
for i=1:numel(ndx_impact)
    % find end of ground contact
    a = ndx_impact(i);
    b = ndx_liftoff(i);
    p_win = 0.10; % Percent into the phase
    c = round( a + p_win*(b-a) );
    ang_avg = sum(ang(a:c)) * p_win;
    Toe_avg = sum(Toe(a:c)) * p_win;
    Met_avg = sum(Met(a:c)) * p_win;
    Mid_avg = sum(Mid(a:c)) * p_win;
    Hel_avg = sum(Hel(a:c)) * p_win;
    tot_avg = Toe_avg+Met_avg+Mid_avg+Hel_avg;

    if (Met_avg) > (0.6*tot_avg)
        type_impact(i) = 3; %forefoot
    elseif Hel_avg > (0.5*tot_avg)
        type_impact(i) = 1; % heel
    else
        type_impact(i) = 2; % midfoot
    end
    
    if 0 % manually step through each phase for debug
    figure(77);clf
    x = linspace(0,100,(b-a)+1);
    subplot 211;hold all;
    plot(x,Toe(a:b))
    plot(x,Met(a:b))
    plot(x,Mid(a:b))
    plot(x,Hel(a:b))
    m = max([Toe(a:b);Met(a:b);Mid(a:b);Hel(a:b)]);
    plot(p_win*100*ones(2,1),[0;m],'-.k','LineWidth',2)
    subplot 212;hold all;
    plot(x,ang(a:b))
    plot(x,ang2(a:b))
    plot(p_win*100*ones(2,1),[min(ang(a:b));max(ang(a:b))],'-.k','LineWidth',2)
    keyboard
    end
end

ndx_foreimpact = ndx_impact(type_impact==3);
ndx_midimpact = ndx_impact(type_impact==2);
ndx_heelimpact = ndx_impact(type_impact==1);

if plotflag
plot(XSNData.t(ndx_impact(type_impact==3)),kk(ndx_impact(type_impact==3)),'ob','linewidth',2)
plot(XSNData.t(ndx_impact(type_impact==2)),kk(ndx_impact(type_impact==2)),'ok','linewidth',2)
plot(XSNData.t(ndx_impact(type_impact==1)),kk(ndx_impact(type_impact==1)),'or','linewidth',2)
legend('Toe','Meta','Mid','Heel','Forefoot Impact','Midfoot Impact','Heel Impact')

f5=figure;
plot(XSNData.t(ndx_impact),type_impact,'o','LineWidth',2);
ylim([0 4])
yticks([1,2,3])
yticklabels({'Heel','Mid','Fore'})
legend('Impact Type')
end

FootImpacts.i_all = ndx_impact;
FootImpacts.i_all_lift = ndx_liftoff;
FootImpacts.type = type_impact;
FootImpacts.typenamemap = {'Heel','Mid','Fore'};


return