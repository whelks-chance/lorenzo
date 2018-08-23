from lxml import etree as ET

# For weird ENUM references, look here
# https://svn.filezilla-project.org/filezilla/FileZilla3/trunk/src/include/server.h?view=markup

queue_data = {
    'Host': 'localhost',
    'Port': 22,
    'Protocol': 1,
    'Type': 0,
    'User': 'ianh',
    'Logontype': 2,
    'TimezoneOffset': 0,
    'PasvMode': 'MODE_DEFAULT',
    'MaximumMultipleConnections': 0,
    'EncodingType': 'Auto',
    'BypassProxy': 0,
    'Name': 'New site',
    'files': [
        {
            'LocalFile': '/home/ianh/filezilla_dls/java_error_in_PYCHARM.hprof',
            'RemoteFile': 'java_error_in_PYCHARM.hprof',
            'RemotePath': '1 0 4 home 4 ianh',
            'Download': 1,
            'Size': 946972281,
            'DataType': 1
        }
    ]
}


def write_queue_XML(queue_data, filename="filename.xml"):
    root = ET.Element("FileZilla3", version="3.15.0.2", platform="*nix")
    queue = ET.SubElement(root, "Queue")
    server = ET.SubElement(queue, "Server")

    for key in queue_data.keys():
        print(key, queue_data[key])
        if key == 'files':
            for file in queue_data['files']:
                file_element = ET.SubElement(server, 'File')
                for file_key in file.keys():
                    ET.SubElement(file_element, key).text = str(file[file_key])
        else:
            ET.SubElement(server, key).text = str(queue_data[key])

    tree = ET.ElementTree(root)
    tree.write(filename, pretty_print=True)


write_queue_XML(queue_data, 'queue.xml')
