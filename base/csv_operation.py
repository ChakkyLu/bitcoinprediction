import csv
#-------------Explanation--------------
'''
    write_to_csv: write message to csv file
        tag_dict :  dictionary
        filename : string
        fieldnames: list

    read_to_dict: read message from csv file to variable with dict form
    filename: string
    return: dictionary
'''


def write_to_csv(tag_dict, filename, fieldnames):
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        data = [dict(zip(fieldnames, [k, v])) for k, v in tag_dict.items()]
        writer.writerows(data)


def write_test_data(tag_dict, filename, fieldnames):
    with open(filename, 'a+', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        data = [dict(zip(fieldnames, [k, v])) for k, v in tag_dict.items()]
        writer.writerows(data)


def read_to_dict(filename):
    dicts = {}
    with open(filename) as csvfile:
        Reader = csv.DictReader(csvfile)
        head = Reader.fieldnames
        for row in Reader:
            dicts[row[head[0]]] = row[head[1]]
    return dicts
