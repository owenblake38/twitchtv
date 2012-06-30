from xml.etree import ElementTree as etree
import urllib2
import sqlite3
import os
import shutil
import json

config = {}

def main():
    #Load the JSON config file
    global config 
    config = json.load(open("settings.json"))
    #First thing we need to do is check that the downloaded shows database exists
    check_and_create_database()

    print "Starting checking for shows to download"
    for channel in config["shows"].keys():
        print channel + ":"
        url = "http://api.justin.tv/api/channel/archives/%s.xml?limit=%s" % (channel, config["results_count"])
        response = urllib2.urlopen(url)
        html = response.read()
        tree = etree.fromstring(html)
        for tree_node in tree.findall("object"):
            try:
                title = tree_node.find("title").text
                show_id = tree_node.find("id").text
                broadcast_part = tree_node.find("broadcast_part").text
                video_file = tree_node.find("video_file_url").text

                for show_title in config["shows"][channel]:
                    if show_title.lower() in title.lower():
                        if check_downloaded(tree_node.find("id").text) == False:
                            dlfile(video_file, title, broadcast_part, show_id, channel)

            except Exception, e:
                print e


def dlfile(url, title, part, show_id, channel):

    file_name = url.split('/')[-1]
    extension = file_name.split('.')[-1]
    u = urllib2.urlopen(url)
    f = open(file_name, 'wb')
    meta = u.info()
    file_size = int(meta.getheaders("Content-Length")[0])

    new_name = "%s pt%s-%s.%s" % (title, part, show_id, extension)
    new_name = remove(new_name)

    print "Downloading: (%s) %s Bytes: %s" % (new_name, file_name, file_size)

    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break
        file_size_dl += len(buffer)
        f.write(buffer)
        status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
        status = status + chr(8) * (len(status) + 1)
        print status,

    f.close()

    print new_name
    #Check the the destination folder(channel name) exists
    check_and_create_folder(channel)
    #Rename to file to a more friendly filename
    os.rename(file_name, new_name)
    #move the file to the channel name directory
    shutil.move(new_name, "./" + channel)
    #Add the downloaded show to the database
    add_downloaded(show_id, new_name)


def check_downloaded(video_id):
    connection = sqlite3.connect(config["database"])
    c = connection.cursor()
    c.execute("SELECT COUNT(*) FROM downloads WHERE id = ?", [video_id])
    
    count = c.fetchone()
    if count[0] > 0:
        return True
    else:
        return False


def add_downloaded(show_id, video_name):
    connection = sqlite3.connect(config["database"])
    with connection:
        c = connection.cursor()
        c.execute("INSERT INTO downloads VALUES (?,?)", [show_id, video_name])


def check_and_create_database():
    try:
        with open(config["database"]) as db:
            pass
    except IOError as e:
        #The database doesnt exists, we need to create it and create the downloads table.
        print "Database doesnt exist, creating database."
        connection = sqlite3.connect(config["database"])
        with connection:
            c = connection.cursor()
            c.execute("CREATE TABLE downloads(id INT, name TEXT)")

def check_and_create_folder(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

def remove(value):
    for c in "\\/:*?\"<>|":
        value = value.replace(c, '')
    return value

main()
