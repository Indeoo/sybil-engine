import csv


def read_csv_rows(csv_file):
    # Replace 'file.csv' with the path to your CSV file
    with open(csv_file, mode='r') as file:
        csv_reader = csv.reader(file)

        # Optional: Read the first row as headers
        headers = next(csv_reader)

        rows = []

        # Loop through the rest of the rows
        for row in csv_reader:
            rows.append(row)

        return rows
