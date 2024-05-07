[cA, cD] = dwt(signal, 'db3');
[cA2, cD2] = dwt(cA, 'db3');
[cA3, cD3] = dwt(cA2, 'db3');
[cA4, cD4] = dwt(cA3, 'db3');
[cA5, cD5] = dwt(cA4, 'db3');