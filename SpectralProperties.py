import numpy
import scipy
import librosa

def features(signal, rate):
    # Extract MFCCs, MFCC deltas, MFCC double deltas
    mfcc        = librosa.feature.mfcc(signal, n_mfcc=13)
    delta_mfcc  = librosa.feature.delta(mfcc)
    delta2_mfcc = librosa.feature.delta(mfcc, order=2)
    plp         = librosa.beat.plp(signal,rate)
    
def spectral_properties(file):
    """
    - meanfreq : mean frequency (in kHz)
    - sd       : standard deviation of frequency
    - median   : median frequency (in kHz)
    - Q25      : first quantile (in kHz)
    - Q75      : third quantile (in kHz)
    - IQR      : interquantile range (in kHz)
    - skew     : skewness (see note in specprop description)
    - kurt     : kurtosis (see note in specprop description)
    - sp.ent   : spectral entropy
    - sfm      : spectral flatness
    - mode     : mode frequency
    - centroid : frequency centroid (see specprop)
    - peakf    : peak frequency (frequency with highest energy)
    - meanfun  : average of fundamental frequency measured across acoustic signal
    - minfun   : minimum fundamental frequency measured across acoustic signal
    - maxfun   : maximum fundamental frequency measured across acoustic signal
    - meandom  : average of dominant frequency measured across acoustic signal
    - mindom   : minimum of dominant frequency measured across acoustic signal
    - maxdom   : maximum of dominant frequency measured across acoustic signal
    - dfrange  : range of dominant frequency measured across acoustic signal
    - modindx  : modulation index. Calculated as the accumulated absolute difference between adjacent measurements of fundamental frequencies divided by the frequency range
    - label    : male or female
    """
    signal, rate = librosa.load(file)
    
    #F, f_names = audioFeatureExtraction.stFeatureExtraction(signal, rate, 0.050*rate, 0.025*rate);
    spectrum                       = numpy.abs(numpy.fft.rfft(signal))
    frequencies                    = numpy.fft.rfftfreq(len(signal), d=1. / rate)
    amplitudes                     = spectrum / spectrum.sum()  
    mean_frequency                 = (frequencies * amplitudes).sum() 
    peak_frequency                 = frequencies[numpy.argmax(amplitudes)] 
    frequencies_standard_deviation = frequencies.std()
    amplitudes_cumulative_sum      = numpy.cumsum(amplitudes)
    median_frequency               = frequencies[len(amplitudes_cumulative_sum[amplitudes_cumulative_sum <= 0.5]) + 1]
    mode_frequency                 = frequencies[amplitudes.argmax()]
    frequencies_q25                = frequencies[len(amplitudes_cumulative_sum[amplitudes_cumulative_sum <= 0.25]) + 1]
    frequencies_q75                = frequencies[len(amplitudes_cumulative_sum[amplitudes_cumulative_sum <= 0.75]) + 1]
    frequencies_iqr                = frequencies_q75 - frequencies_q25
    frequencies_skewness           = scipy.stats.skew(frequencies)
    frequencies_kurtosis           = scipy.stats.kurtosis(frequencies)
    spectral_entropy               = scipy.stats.entropy(amplitudes)
    
    # Spectral features 
    chroma_stft        = librosa.feature.chroma_stft(signal, rate)                     # Compute a chromagram from a waveform or power spectrogram.
    chroma_cqt         = librosa.feature.chroma_cqt(signal,  rate)                     # Constant-Q chromagram
    chroma_cens        = librosa.feature.chroma_cens(signal, rate)                     # Computes the chroma variant “Chroma Energy Normalized” (CENS), following [R674badebce0d-1].
#    melspectrogram     = librosa.feature.melspectrogram(librosa.stft(signal), rate) 	 # Compute a mel-scaled spectrogram.
    mfcc               = librosa.feature.mfcc(signal, rate, n_mfcc=13, dct_type=3)     # Mel-frequency cepstral coefficients (MFCCs)
    rms                = librosa.feature.rms(signal)                                   # Compute root-mean-square (RMS) value for each frame, either from the audio samples y or from a spectrogram S.
    spectral_centroid  = librosa.feature.spectral_centroid(signal,  rate)              # Compute the spectral centroid.
    spectral_bandwidth = librosa.feature.spectral_bandwidth(signal, rate)              # Compute p’th-order spectral bandwidth.
#    spectral_contrast  = librosa.feature.spectral_contrast(librosa.stft(signal), rate) # Compute spectral contrast [R6ffcc01153df-1]
    spectral_flatness  = librosa.feature.spectral_flatness(signal)                     # Compute spectral flatness
    spectral_rolloff   = librosa.feature.spectral_rolloff(signal, rate)                # Compute roll-off frequency.
    poly_features      = librosa.feature.poly_features(signal, order=2)                # Get coefficients of fitting an nth-order polynomial to the columns of a spectrogram.
    tonnetz            = librosa.feature.tonnetz(signal, rate) 	 	                   # Computes the tonal centroid features (tonnetz), following the method of [Recf246e5a035-1].
    zero_crossing_rate = librosa.feature.zero_crossing_rate(signal)                    # Compute the zero-crossing rate of an audio time series

    d = {
                'mean_frequency'                 : mean_frequency / 1000,
                'frequencies_standard_deviation' : frequencies_standard_deviation / 1000,
                'median_frequency'               : median_frequency/ 1000,
                'frequencies_q25'                : frequencies_q25 / 1000,
                'frequencies_q75'                : frequencies_q75 / 1000,
                'frequencies_iqr'                : frequencies_iqr / 1000,
                'frequencies_skewness'           : frequencies_skewness,
                'frequencies_kurtosis'           : frequencies_kurtosis,
                'spectral_entropy'               : spectral_entropy,
                'mean_spectral_flatness'         : spectral_flatness.mean() /1000,
                'mode_frequency'                 : mode_frequency / 1000,
                'mean_spectral_centroid'         : spectral_centroid.mean() / 1000,
               } 
    
    # fundamental frequencies calculations   
    from FundFreqs import FundamentalFrequencies
    fundamental_frequencies_extractor = FundamentalFrequencies()
    fundamental_frequencies, harmonic_rates, argmins, times, duration  = fundamental_frequencies_extractor.main(rate, signal)

    # dominant frequencies calculations   
    from DomFreqs import DominantFrequenciesExtractor    
    dominant_frequencies_extractor = DominantFrequenciesExtractor()
    dominant_frequencies           = dominant_frequencies_extractor.main("sample2.wav")
 
    # modulation index calculation  
    changes = numpy.abs(dominant_frequencies[:-1] - dominant_frequencies[1:])
    dfrange = dominant_frequencies.max() - dominant_frequencies.min()
    if dominant_frequencies.min() == dominant_frequencies.max():
        modulation_index = 0
    else: 
        modulation_index = changes.mean() / dfrange
        
    result_d = {
                "meanfreq" : mean_frequency / 1000,
                "sd"       : frequencies_standard_deviation / 1000,
                "median"   : median_frequency / 1000,
                "Q25"      : frequencies_q25  / 1000,
                "Q75"      : frequencies_q75  / 1000,
                "IQR"      : frequencies_iqr  / 1000,
                "skew"     : frequencies_skewness,
                "kurt"     : frequencies_kurtosis,
                "sp.ent"   : spectral_entropy,
                "sfm"      : spectral_flatness.mean() /1000,
                "mode"     : mode_frequency / 1000,
                "centroid" : spectral_centroid.mean() / 1000,
                "peakf"    : peak_frequency / 1000,
                "meanfun"  : fundamental_frequencies.mean() / 1000,
                "minfun"   : fundamental_frequencies.min()  / 1000,
                "maxfun"   : fundamental_frequencies.max()  / 1000,
                "meandom"  : dominant_frequencies.mean() / 1000,    
                "mindom"   : dominant_frequencies.min()  / 1000,    
                "maxdom"   : dominant_frequencies.max()  / 1000,   
                "dfrange"  : dfrange / 1000,                        
                "modindx"  : modulation_index,                      
                "label"    : 1,
               }     
    
    return result_d


results = spectral_properties("sample2.wav")
for k, v in results.items(): 
    print("%50s : %10f" % (k, round(v, 3)))



# subprocess.call ("/usr/bin/Rscript --vanilla /pathto/MyrScript.r", shell=True)