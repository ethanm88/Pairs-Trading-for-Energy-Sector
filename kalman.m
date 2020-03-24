% p value < 0.1%
% E and EQNR
% COP and PBR
% CEO and EQNR

% plot E and EQNR

%{
plot(dates, Eprice);
hold on
plot(dates, EQNRprice);
title('E and EQNR');
xlabel('Date');
ylabel('Price');
legend('E', 'EQNR');
hold off
figure;
ratio = Eprice ./ EQNRprice;
plot(dates, ratio);
title('E/EQNR');
xlabel('Date');
ylabel('E/EQNR');
%}

% 2001-2003: days 1:637
% 2004-2006: days 638:1392
% 2007-2009: days 1393:2149
% 2010-2012: days 2150:2903
% 2013-2015: days 2904:3659
% 2016-2018: days 3660:4413
% 2019-2020: days 4414:4696
% enter two timetables of the securities 

times = days(1:637);
x=array2timetable(table2array(StockData(1:637,13)),'RowTimes',times); % set security 1
y=array2timetable(table2array(StockData(1:637,16)),'RowTimes',times); % set security 2

% Augment x with ones to  accomodate possible offset in the regression
% between y vs x.

x=[table2array(x) ones(size(table2array(x)))];

delta=0.0001; % delta=1 gives fastest change in beta, delta=0.000....1 allows no change (like traditional linear regression).

yhat=NaN(size(y)); % measurement prediction
e=NaN(size(y)); % measurement prediction error
Q=NaN(size(y)); % measurement prediction error variance

% initialize R, P and beta.
R=zeros(2);
P=zeros(2);
beta=NaN(2, size(x, 1));
Vw=delta/(1-delta)*eye(2);
Ve=0.001;


% Initialize beta(:, 1) to zero
beta(:, 1)=0;

% Given initial beta and R (and P), run kalman filter for hedge ratio
for t=1:size(y)
    if (t > 1)
        beta(:, t)=beta(:, t-1); % state prediction. Equation 3.7
        R=P+Vw; % state covariance prediction. Equation 3.8
    end
    
    yhat=x(t, :)*beta(:, t); % measurement prediction. Equation 3.9

    Q(t)=x(t, :)*R*x(t, :)'+Ve; % measurement variance prediction. Equation 3.10
    
    
    % Observe y(t)
    e=table2array(y)-yhat; % measurement prediction error
    
    K=R*x(t, :)'/Q(t); % Kalman gain
    
    beta(:, t)=beta(:, t)+K*e(t); % State update. Equation 3.11
    P=R-K*x(t, :)*R; % State covariance update. Equation 3.12
    
end

% plot(beta(1, :)');

%{
figure;

plot(beta(2, :)');
%}

%{
figure;

plot(e(3:end), 'r');
%}

%{
hold on;
plot(sqrt(Q(3:end)));
%}

y2=[x(:, 1) table2array(y)];

longsEntry=e < -sqrt(Q); % a long position means we should buy
longsExit=e > -sqrt(Q);

shortsEntry=e > sqrt(Q);
shortsExit=e < sqrt(Q);

numUnitsLong=NaN(length(y2), 1);
numUnitsShort=NaN(length(y2), 1);

numUnitsLong(1)=0;
numUnitsLong(longsEntry)=1; 
numUnitsLong(longsExit)=0;

numUnitsShort(1)=0;
numUnitsShort(shortsEntry)=-1; 
numUnitsShort(shortsExit)=0;

numUnits=numUnitsLong+numUnitsShort;
positions=repmat(numUnits, [1 size(y2, 2)]).*[-beta(1, :)' ones(size(beta(1, :)'))].*y2; % [hedgeRatio -ones(size(hedgeRatio))] is the shares allocation, [hedgeRatio -ones(size(hedgeRatio))].*y2 is the dollar capital allocation, while positions is the dollar capital in each ETF.
positions = array2timetable(positions, 'RowTimes',times);
y2 = array2timetable(y2, 'RowTimes',times);

pnl=sum(table2array(lag(positions, 1)).*(table2array(y2)-table2array(lag(y2, 1)))./table2array(lag(y2, 1)), 2); % daily P&L of the strategy
ret=pnl./sum(abs(table2array(lag(positions, 1))), 2); % return is P&L divided by gross market value of portfolio
ret(isnan(ret))=0;

figure;

plot(cumprod(1+ret)-1); % Cumulative compounded return
title('EQNR/CEO Kalman Filter Cumulative Compounded Return (2001-2003)');
fprintf(1, 'APR=%f Sharpe=%f\n', prod(1+ret).^(252/length(ret))-1, sqrt(252)*mean(ret)/std(ret));

