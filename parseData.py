import numpy as np
import matplotlib.pyplot as plt
import os
import datetime
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level = logging.DEBUG)
logging.getLogger('matplotlib').setLevel(logging.ERROR)

class Parse_data:
    def __init__(self, file, path, num_bins):
        self.file = file
        self.path = path
        self.num_bins = num_bins
        
    def parse(self, return_option):
        magnitude = []
        bins = []
        ID_val = []
        for line in self.file:
            try:
                if line == '\n':
                    pass
                if line.split(';')[1].isdigit():
                    ID_val.append(int(line.split(';')[0]))
                    bins.append(int(line.split(';')[1]))
                    magnitude.append(int(line.split(';')[2]))
            except (IndexError, ValueError) as e:
                logger.error(e)
                pass
            
        while bins[len(bins)-1] != 127:
            bins = np.delete(bins, len(bins)-1)
            magnitude = np.delete(magnitude, len(magnitude)-1)
            ID_val = np.delete(ID_val, len(ID_val)-1)
            
        
        combined = np.vstack((bins, magnitude)).T
        
        if (len(ID_val) != ID_val[len(ID_val)-1]):
            logger.error("There is missing data")
            return "There is missing data"
        if return_option == 'mag':
            return magnitude
        elif return_option == 'comb':
            return combined
        elif return_option == 'ID':
            return ID_val
        
    def calc_mean_magnitude(self, input_array):
        mean_magnitude = np.zeros(self.num_bins)

        for i in range (0, len(input_array)):
            mean_magnitude[input_array[i][0]] += input_array[i][1]
        for i in range(0, len(mean_magnitude)):
            mean_magnitude[i] = mean_magnitude[i]/(len(input_array)/len(mean_magnitude))
        file = open(self.path + "mean_value_" + datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S") + ".txt","w")
        for i in range (0, len(mean_magnitude)):
            file.write(str(i+1) + ':' + str(round(mean_magnitude[i],1)) + '\n')
        file.close()
        return mean_magnitude

    def calc_max_val(self, input_array):
        max_val = np.zeros(self.num_bins)
        
        for i in range(0, len(input_array)):
            if input_array[i][1] > max_val[input_array[i][0]]:
                max_val[input_array[i][0]] = input_array[i][1]
        file = open(self.path + "max_value_" + datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S") + ".txt","w")
        for i in range (0, len(max_val)):
            file.write(str(i+1) + ':' + str(max_val[i]) + '\n')
        file.close()
        return max_val

    def calc_min_val(self, input_array):
        min_val = np.full(self.num_bins, 256)

        for i in range(0, len(input_array)):
            if input_array[i][1] < min_val[input_array[i][0]] and input_array[i][1] != 0:
                min_val[input_array[i][0]] = input_array[i][1]
        file = open(self.path + "min_value_" + datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S") + ".txt","w")
        for i in range (0, len(min_val)):
            file.write(str(i+1) + ':' + str(min_val[i]) + '\n')
        file.close()
        return min_val
    
    def plot(self, val1, val2, val3):
        freq_range = np.arange(0.0, 1000.0, 37.5)


        fig, axs = plt.subplots(1,3, sharex='col', sharey='row',
                                gridspec_kw={'hspace':0.2, 'wspace':0})

        (ax1, ax2, ax3) = axs
        


        ax1.plot(freq_range, val1[0:27])
        ax1.set_title('mean magnitude')

        ax1.text(3400,70, 'Date: 21.02.20')
        ax1.text(3400,60, 'Mic: Electret')
        ax1.text(3400,50, 'Motor: good(153986)')
        #ax1.text(3400,-40, 'Gyro: Bad')
        ax2.plot(freq_range, val2[0:27])
        ax2.set_title('min val')
        ax2.text(3400,70, 'Mic: Electret')
        ax2.text(3400,60, 'Motor: good(153986)')
        #ax2.text(3600,-40, 'Gyro: Bad')
        ax3.plot(freq_range, val3[0:27])
        ax3.set_title('max val')
        #ax3.set_title('Difference of max value between 20-30 and 30-40')
        ax3.text(3400,70, 'Mic: Electret')
        ax3.text(3400,60, 'Motor: good(153986)')
        #ax3.text(3600,-40, 'Gyro: Bad')


        for ax in axs.flat:
            ax.set(xlabel='Frequency [Hz]', ylabel='Magnitude')
            ax.set_yticks(np.arange(-50,90,10))



        for ax in axs.flat:
            ax.label_outer()
        plt.show()


if __name__ == '__main__':
    
    name = 'tempdata'
    num_bins = 128
    os.chdir("/home/pi/Documents/SoundAnalyze/web")
    path = "/home/pi/Documents/SoundAnalyze/web/"
    file = open(path + name + '.txt', 'r')
    
    parse_data = Parse_data(file, path, num_bins)
    comb = parse_data.parse('comb')
    

    mean_val = parse_data.calc_mean_magnitude(comb)
    max_val = parse_data.calc_max_val(comb)
    min_val= parse_data.calc_min_val(comb)
    parse_data.plot(mean_val, min_val, max_val)



  
