import json
import obd
from dictionary import dictionary_commands
from time import *
import pandas as pd


class ObdSensors(obd.OBD):

    def __init__(self, file_name='/dev/ttyUSB0'):
        self.file_name = file_name
        super().__init__(self.file_name)

    def is_connected(self):
        return super().is_connected()

    def get_value(self, command):
        sens_val = super().query(command)
        if not sens_val.is_null():
            try:
                return sens_val.value.magnitude
            except AttributeError:
                return sens_val.value
        return 'Nan'


def main():
    obd_object = ObdSensors()
    dict_commands = dictionary_commands.copy()
    x, start_time, num_reading_three_sec, speed_three_seconds = 0, 0, 0, []
    time_taken = 60*60*3
    time_start = time()

    time_end = time()
    # loop for 2500 times

    while (time_end-time_start) < time_taken:

        # if not connection keep checking until there is a connection
        # if not obd_object.is_connected():
        #     print("No connection")
        #     obd_object = ObdSensors()
        #     sleep(1)
        #     continue

        # method one for getting speed of last 3 seconds
        #
        if time() - start_time > 3:
            start_time = time()
            acceleration = [(int(speed_three_seconds[x+1]) - int(speed_three_seconds[x])) * (3600 / num_reading_three_sec)
                            for x in range(len(speed_three_seconds) - 1)]
            num_reading_three_sec = 0
            speed_three_seconds = []

        # the following dictionary is a single value for every key used in json file to send
        current_dict = dictionary_commands.copy()

        # loop through all sensors, put them in a dict with corresponding command
        for i in range(len(dictionary_commands.keys())):
            sensor_value = obd_object.get_value(obd.commands[1][i])
            dict_commands[str(obd.commands[1][i])].append(sensor_value)
            current_dict[str(obd.commands[1][i])].append(sensor_value)
            if str(obd.commands[1][i]) == "b'010D': Vehicle Speed" and sensor_value != 'Nan':
                speed_three_seconds.append(sensor_value)

        # num_reading_three_sec += 1
        time_end = time()

        '''
        send json file to server
        '''

        # as a file delete if not needed

        with open("data.json", 'w') as json_file:
            json.dump(current_dict, json_file)

        # serializing json delete if not needed

        json_object = json.dumps(current_dict, indent=4)
        print(json_object)

        # click so the laptop doesn't turn off and your data go missing

        x += 1
    # Convert dictionary to csv file
    df = pd.DataFrame(dict_commands)
    df.to_csv('data_car2.csv', index=False, header=True)


if __name__ == '__main__':
    main()
