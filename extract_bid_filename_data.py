def extract_bids_filename_data(filename):
    """
    Extract key/value pairs from a BIDS filename that contain information
    about the data in the file.
    :param filename: The filename from which to extract key/value pairs
    :return: The key/value pairs extracted from the filename
    """
    data = {
        '_filename': str(filename)
    }
    # if filename.count('.') > 1:
    #     # Handle the case where a file as an extra extension, e.g. .bak,  by removing it
    #     reverse_index_of_last_dot = len(filename) - filename.rfind('.')
    #     filename = filename[:-reverse_index_of_last_dot]

    filename_no_ext = filename
    if '.' in filename:
        filename_arr = filename.split('.')

        base_filename, extension = filename_arr[:2]
        data['_extension'] = str(extension)

        long_extension = '.'.join(filename_arr[1:])
        data['_long_extension'] = long_extension

        filename_no_ext = filename_arr[0]

    key_value_pairs = filename_no_ext.split('_')
    for pair in key_value_pairs:
        if '-' in pair:
            key, value = pair.split('-')
            data[key] = value
        else:
            # If there's no - in the pair this might be a simple filename, e.g. ClassFile.cls
            if len(key_value_pairs) > 1:
                # There is only a postfix when the filename contains at least one key/value pair
                data['_postfix'] = str(pair)
    return data
