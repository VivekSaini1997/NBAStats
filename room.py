# a class that holds the information for each of the rooms
# the info is the room number, the building it is in, 
# the capacity of the room and the cost of booking
import requests
from bs4 import BeautifulSoup as bs
import json
import datetime

class room(object):
    
    # constructs a room object which stores the info stored on above
    # dict_ specifies whether or not to fetch the info from the server 
    # or to use a dict that would have been generated from a json file
    # the file is used to cache the results
    def __init__(self, building_code = None, room_number = None, dict_ = None):
        # depending on whether or not a dict is specified
        # update from the server or from a dict if a dict is given
        
        if dict_ is None:
            self.building_code = building_code
            self.room_number = room_number
            self.fetch_info_from_server()
            # when you fetch from the server, in order to allow the room_list
            # class to store the results
            self.create_dict_from_room()
        elif building_code is None and room_number is None:
            # if the dict is specified, use it to generate the neccessary fields
            # for the struct
            self.room_dict = dict_
            self.building_code = dict_['building_code']
            self.capacity = dict_['capacity']
            self.cost = dict_['cost']
            self.room_number = dict_['room_number']
        else:
            # this should never occur
            # should probably raise an exception
            print('This is not good')
        # when you get here, specify that the room is occupied by default
        # change that when you find that the room is vacant in the 
        # get_booking_vacancy function
        self.vacant = False
        # also provide a url to get room information
        self.url = 'https://ace.utoronto.ca/ws/f?p=210:1:::::P1_BLDG,P1_ROOM:{},{}'.format(self.building_code, self.room_number)

    # fetch the info for the building in particular using 
    # a request to ace.utoronto.ca
    def fetch_info_from_server(self):  
        # this is the server page that has the information about the room
        request_str = "https://ace.utoronto.ca/ws/f?p=210:1:::::P1_BLDG,P1_ROOM:{},{}".format(self.building_code, self.room_number)
        request = requests.get(request_str)
        # use beautiful soup to parse the resultant html to gather 
        # information about the room 
        soup = bs(request.text, features="html.parser")
        self.capacity = int(fetch_parameter_from_html(soup, 'Capacity'))
        self.cost = fetch_parameter_from_html(soup, 'External Rental Rate')

    # convert the fields into a dict for use when writing to a json file
    def create_dict_from_room(self):
        # we just brute force it for now, there may be a more elegant solution
        self.room_dict = {}
        self.room_dict['building_code'] = self.building_code
        self.room_dict['room_number'] = self.room_number
        self.room_dict['capacity'] = self.capacity
        self.room_dict['cost'] = self.cost
        return self.room_dict

    # the function where a lot of the magic happens
    # given a string of a date formatted YYYYMMDD and two times formatted HH:MM,
    # return whether or not the room is vacant at the given day and in between the given times
    # fair warning, this function is fricked up lol
    # also you might want to look at a Calendar of Availability on the ace.utoronto.ca website
    # if you want more of a chance to follow along on this trainwreck
    # and make sure to look at the html if you want a bit more of an understanding
    #TODO: Add support for a range of times instead of just a singular time
    def get_booking_vacancy(self, date, time_of_day = '00:00', start_time = None, end_time = None):
        # this is the formatting to request the calendar availability
        # of this room for the given date and the subsequent request
        calendar_request_str = "https://ace.utoronto.ca/ws/f?p=200:3:::NO::P3_BLDG,P3_ROOM,P3_CALENDAR_DATE:{},{},{}".format(self.building_code, self.room_number, date)
        calendar_request = requests.get(calendar_request_str)
        # this is the soup used to parse the resulting html
        calendar_request_soup = bs(calendar_request.text, "html.parser")

        # get the day of the week that the date lies on
        # 0 is Monday, 6 is Sunday, and everything in between
        day_and_time = datetime.datetime(int(date[:4]), int(date[4:6]), int(date[6:8]))
        day_of_week = day_and_time.weekday()

        # day count is used to iterate through a subsection of the list once the correct time is found
        # time tracker is used to keep track of which time of day a given time slot in the calendar table refers to
        day_count = 0
        time_tracker = ''

        # a list of all of the hours the room needs to be vacant in order to satisfy requirements
        # created using the start and end times 
        valid_times = []
        if start_time is not None and end_time is not None:
            # create a range of valid times for the algorithm to check
            start_interval = int(start_time[:2])
            end_interval = int(end_time[:2])
            # if the time ends on the hour, no need to book the room the room for the next hour
            if '00' in end_time[3:5]:
                end_interval -= 1
            valid_times = range(start_interval, end_interval + 1)
        else:
            valid_times.append(int(time_of_day[:2]))

        # there probably is a cleaner way of doing this, this is just the first approach that came to mind tbh
        # go through all of the tags that either have a valign attribute (those would be elements of the table on the ace.utoronto website)
        # or those that have a class attribute equal to t3Hour (which tell us what hour of the day the next 7 table entries correspond,
        # one entry for each day of the week)
        for tag in calendar_request_soup.find_all(lambda x : (x.has_attr('valign') or 't3Hour' in x['class']) \
            if x.has_attr('class') else False):

            # if the tag has a class attribute equal to t3Hour, it is telling us what hour the next time slots refer to
            # so set the time_tracker value to whatever time the tage encompasses
            # catch the awkward exception where the first time slots don't have anything inside of them and move along
            if 't3Hour' in tag['class']:
                try:
                    time_tracker = str(tag.contents[0]).strip('\n')
                    # print 'lol'
                    day_count = 0
                except UnicodeEncodeError:
                    pass
            
            # if you have a valid time tracker value compare that with 
            # the desired time value range, find the time slot that corresponds to the right day,
            # and return whether or not that time slot is vacant or not i.e., the time slot has a valid hour for it
            elif len(time_tracker) > 0:    
                # check that the right times are being matched so that your looking through 
                # the right subsection of time slots
                if int(time_tracker[:2]) in valid_times:  
                    # if the time slot is the same day of the week as the date entered, return whether or not the room is vacant
                    # True for vacant, False for occupied
                    # if the string is empty, that means there is no text between the start and end tag so there is no booking in the time slot
                    # therefore it must be vacant, if the string has some text, there is a room booking so it is occupied
                    if day_count == day_of_week:
                        # print str(tag.contents[0]).strip('\n'), len(str(tag.contents[0]).strip('\n'))
                        occupier = str(tag.contents[0]).strip('\n')
                        # if it is vacant say so, if not specify who occupies the room
                        # print 'the date is {}, the hour is {}:00'.format(day_and_time.date(), time_tracker[:2])
                        if len(occupier) > 0:
                            # print '{} {} is occupied by {}'.format(self.building_code, self.room_number, occupier)
                            self.vacant = False
                            return False
                        #else:
                            # print '{} {} is vacant at this time'.format(self.building_code, self.room_number)
                    # otherwise increment the day counter and continue
                    # else:
                    day_count += 1

        # if you got here, return True because every time slot you required was vacant 
        # print '{} {} is vacant'.format(self.building_code, self.room_number)
        self.vacant = True
        return True

# given a parameter, fetches a parameter from a given soup
# this utilizes the manner in which parameters are
# stored in the html for ace.utoronto.ca
# this might not work in the future lmao
def fetch_parameter_from_html(soup, param):
    for tag in soup.descendants:
        for sibling_tag in tag.previous_siblings:
            if param in sibling_tag:
                # if the room can't be rented, there is a janky non ascii character instead of 
                # anything meaningful, as a result, catch that character and return something else
                try:
                    return str(tag.contents[0])
                except UnicodeEncodeError:
                    return "Not specified"