import pet2017 as pet
#import pywt

s = [*pet.data_by_month('2017-09-07')["PETH"],*pet.data_by_month('2017-09-08')["PETH"]]
#hA, hD = pywt.dwt(s,'db3')

#s = [6, 8, 4, 1, 5, 24, 23, 27, 15, 17, 19, 36, 38, 24, 25, 29, 13, 11, 5, 8, 9, 4, 3, 2, 6, 8, 9, 0, 4, 3, 14, 15, 16, 14, 13, 9, 6, 27, 39, 25, 24, 23, 16, 18, 26, 28, 37, 15, 14, 11]

s_mirror_start = s[:4][::-1]
s_mirror_end = s[len(s)-4::][::-1]

s = [*s_mirror_start, *s, *s_mirror_end]


#Коэффициенты низкочастотного фильтра db3 – LowDec
low = [0.035226, -0.085441, -0.13501, 0.45988, 0.80689, 0.33267] #db3 lowDec
#Коэффициенты высокочастотного фильтра db3 - HiDec
high = [-0.33267, 0.80689, -0.45988, -0.13501, 0.085441, 0.035226] #db3 highDec
#Чуи как вычислять
#Как вычисляются добеши "10 лекций по вейвлетам" добеши автор

def dwt(signal, low, high):

    
    s_mirror_start = signal[:4][::-1]
    s_mirror_end = signal[len(signal)-4::][::-1]

    signal = [*s_mirror_start, *signal, *s_mirror_end]

    A, D = ([0.] * (len(signal)-len(s_mirror_start)),[0.]*(len(signal)-len(s_mirror_start)))
    
    
    for i in range(0,(len(signal)- len(low)+1),2):
        for j in range(len(low)):
            A[i] += signal[i+j] * low[len(low) -1  - j]
            D[i] += signal[i+j] * high[len(high) -1  - j]

    return (A[::2],D[::2])
