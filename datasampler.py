import csv
from datetime import datetime
import time

class DataSampler(object):
    """Wrapper for CSV file"""
    def __init__(self, _infile):
        print('Starting DataPager')
        self.rows = []
        self.current = 0
        self.previous = 0
        self.yearlist = {}
        self.years = {}
        self.min = 9999
        self.max = 0
        with open(_infile + '.csv') as csvfile:
            readCSV = csv.reader(csvfile, delimiter=',')
            for row in readCSV:
                if row[4] == "" or row[4] == 0 or row[4] == None:
                    continue
                if row[0] == "APPROVED" or "PROVISIONAL":
                    reading = float(row[4])
                    if reading > self.max:
                        self.max = reading
                    if reading < self.min:
                        self.min = reading
                    try:
                        datetime_object = datetime.strptime(row[2], '%m/%d/%Y %H:%M')
                        if not datetime_object.year in self.yearlist:
                            self.yearlist[datetime_object.year] = 1
                            self.years[str(datetime_object.year) + "rowlist"] = []
                            self.years[str(datetime_object.year) + "rowlist"].append([row[2], reading])
                        else:
                            self.yearlist[datetime_object.year] += 1
                            self.years[str(datetime_object.year) + "rowlist"].append([row[2], reading])
                        pass
                    except ValueError:
                        continue
        csvfile.close()
        print(self.yearlist)
        for x in self.years:
            self.years[x] = self.downsampleBresenham(self.years[x], x, 300)

    def downsampleBresenham(self, list, listname, desired_size):
        # TODO given a list of x size, return a list of y size that has been evenly downsampled.
        if len(list) < desired_size:
            return
        f = lambda m, n: [i*n//m + n//(2*m) for i in range(m)]
        keepmap = f(desired_size, len(list))
        print("Bresenham returns items for " + listname + ": " +str(len(keepmap)))
        print(keepmap[0])
        print(keepmap[int(len(keepmap)/2)])
        print(keepmap[-1])
        print("---")
        new = []
        for ind in keepmap:
            new.append(list[ind])
        return new
        
    def writeFinal(self):
        # TODO verify csv structure
        with open('sampled.csv', 'w', newline='') as writeFile:
            writer = csv.writer(writeFile)
            writer.writerow([self.min, self.max])
            for x in self.years:
                writer.writerows(self.years[x])
            print("Done")
        
        writeFile.close()


thing = DataSampler("csg-593579")
thing.writeFinal()