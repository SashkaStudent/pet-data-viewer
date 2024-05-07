len = 167;
fb = dwtfilterbank('Wavelet','db11','SignalLength',len);
freqz(fb)