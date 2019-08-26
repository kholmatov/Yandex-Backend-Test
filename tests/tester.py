import unittest
import random
import os
from app import *

cur_dir = os.getcwd()
def generate_dict_for_json(citizen_count, error_line=None, relatives=None) -> dict:
    """
    Generates test data
    :param citizen_count: number of people to generate
    :param error_line: number of erroneous rows
    :param relatives: number of links to generate
    :return: the data dictionary
    """

    with open(cur_dir+'/data/cities.json', 'r') as cities_file, open(cur_dir+'/data/streets.json', 'r') as streets_file, \
            open(cur_dir+'/data/names.json', 'r') as names_file, open(cur_dir+'/data/birth_date.json',
                                                                   'r') as birth_date_file:
        cities = json.load(cities_file)
        streets = json.load(streets_file)
        names = json.load(names_file)
        birth_date = json.load(birth_date_file)

    citizens_dict = {}
    for i in range(1, citizen_count + 1):
        citizens_dict[i] = dict(citizen_id=i, town=random.choice(cities), street=random.choice(streets),
             building = str(random.randint(1, 10000)), apartment=random.randint(1, 10000),
             name=random.choice(names), birth_date=random.choice(birth_date),
             gender=random.choice(['male', 'female']),
             relatives=[])

    for i in range(random.randint((citizen_count-1) // 2,
                                  ((citizen_count-1) // 2 * random.randint(2, 4)) * 5) if relatives is None else relatives):
        number_one, number_two = random.randint(1, citizen_count-1), random.randint(1, citizen_count-1)

        if number_one not in citizens_dict[number_two]['relatives'] and number_two != citizens_dict[number_one]['citizen_id']:
            citizens_dict[number_one]['relatives'].append(number_two)
            citizens_dict[number_two]['relatives'].append(number_one)

    citizens = [v for k, v in citizens_dict.items()]
    if error_line and len(citizens) > 1:
        if error_line == "town":
            citizens[0]["town"] = ""
        elif error_line == "street":
            citizens[0]["street"] = ""
        elif error_line == "building":
            citizens[0]["building"] = ""
        elif error_line == "apartment":
            citizens[0]["apartment"] = ""
        elif error_line == "name":
            citizens[0]["name"] = ""
        elif error_line == "birth_date":
            citizens[0]["birth_date"] = "31.02.2019"
        elif error_line == "gender":
            citizens[0]["gender"] = "???"
        elif error_line == "relatives":
            citizens[0]["relatives"] = [2]
            citizens[1]["relatives"] = []

    return {"citizens": citizens}


class MyTestCase(unittest.TestCase):

    def test_task_one(self) -> None:
        """
        The test first method of the API
        :return:
        """
        result = json.dumps(generate_dict_for_json(10000, relatives=1000))
        response = self.app.post("/imports",
                                 data=result,
                                 content_type='application/json')
        self.assertEqual(response.status_code, 201)

if __name__ == '__main__':
    unittest.main()