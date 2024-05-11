import csv

class CSVData:
    def __init__(self, file_path, has_header=True):
        self.data = {}
        self.load_data(file_path, has_header)

    def load_data(self, file_path, has_header=True):
        with open(file_path, 'r', newline='') as file:
            if has_header:
                next(file)  # Saltar la primera fila si hay un encabezado
            reader = csv.reader(file)
            for row in reader:
                for item in row:
                    self.data[item] = True

    def exists(self, element):
        return element in self.data

    def __str__(self):
        return "\n".join(self.data.keys())