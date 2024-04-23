
%[ca2,cd2]=dwt(s, "db3");
%subplot(3,2,5); plot(ca2); title("Approx. coef. for db2");
%subplot(3,2,6); plot(cd2); title("Detail coef. for bd2");

[phi, psi, X] = wavefun('db3', 6);
signal_n = (signal - min(signal)) / ( max(signal) - min(signal));
[A, D] = dwt(signal, 'db3');
%freqs(X, psi)
z = zeros(722, 1)
dFreq = idwt(A, zeros(722,1), 'db3');
n1 = length(D);
nMax = length(signal);
D_lerp = interp1(1:n1, D, linspace(1, n1, nMax));
D_lerp = D_lerp.';


n1 = length(A);
nMax = length(signal);
A_lerp = interp1(1:n1, A, linspace(1, n1, nMax));
A_lerp = A_lerp.';



len = 32;
fb = dwtfilterbank('Wavelet','db3','SignalLength',len);
%freqz(fb)
%tfest
data = iddata(signal, dFreq , 1440*60);
sys = tfest(data, 2);
%[h,w] = freqz(sys);

bode(sys)
%plot(w/pi,20*log10(abs(h)))
%ax = gca;

%ax.XTick = 0:.5:2;
%xlabel('Normalized Frequency (\times\pi rad/sample)')
%ylabel('Magnitude (dB)')
%