import csv

class DataPager(object):
    """Wrapper for CSV file"""
    def __init__(self, _settings):
        print('Starting DataPager')
        self.rows = []
        self.current = 0
        self.previous = 0
        with open(_settings.filename) as csvfile:
            readCSV = csv.reader(csvfile, delimiter=',')
            for row in readCSV:
                self.rows.insert(0, row)
        csvfile.close()
        # TODO verify csv structure

    def next(self):
        self.current += 1
        self.previous += 1
        return self.rows[self.current]

    def first(self):
        return self.rows[0]

    def bydate(self):
        return "bydate"

    def byindex(self, ind):
        return self.rows[ind]
