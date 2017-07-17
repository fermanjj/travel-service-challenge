import re


def parse_flight_text(data):
    """Parses the text from the pnrs endpoint.

    :param str data: The payload from the Java pnrs request
    :return: A dict of the flight data parsed out.
    """
    # parse the ticket number using regex
    ticket_number = re.search(
        r'[1-9][0-9]*\. AS ([0-9]{13})', data).group(1)

    # parse the flight segments using regex
    segments = re.findall(r'[a-z]\.(.*)(?:\n|$)', data)

    # create an output dict
    output = {'ticket_number': ticket_number, 'segments': []}

    # iterate over the segments, parsing them
    for segment in segments:
        seg_dict = {}
        # clean the segment to just have single spaces
        seg_clean = re.sub(' +', ' ', segment).strip()

        # split the segment by spaces and assign values
        seg_split = seg_clean.split()
        seg_dict['flight_number'] = seg_split[0]
        seg_dict['departure_date'] = seg_split[1]
        seg_dict['origin_destination'] = seg_split[2]
        seg_dict['segment_status'] = seg_split[3]
        seg_dict['departure_time'] = seg_split[4]
        seg_dict['arrival_time'] = seg_split[5]
        seg_dict['fare_ladder'] = seg_split[6]

        # split up origin and destination
        seg_dict['origin'] = seg_dict['origin_destination'][:3]
        seg_dict['destination'] = seg_dict['origin_destination'][3:]

        output['segments'].append(seg_dict)

    return output
