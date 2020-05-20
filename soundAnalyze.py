import receive2
import parseData

def audioAnalysis(time, path):
    ans = receive2.data_request(duration=time, path=path)

    if ans == True:
        name1 = 'tempdata'

        file1 = open(path + name1 + '.txt', 'r')
        comb1 = parseData.parse(file1, 'comb')

        mean_magnitude1 = parseData.calc_mean_magnitude(comb1, 128, path)
        max_val1 = parseData.calc_max_val(comb1, 128, path)
        min_val1 = parseData.calc_min_val(comb1, 128, path)


if __name__ == '__main__':
    audioAnalysis(time = 5, path = "/home/pi/Documents/SoundAnalyze/web/")