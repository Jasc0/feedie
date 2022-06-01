import feedparser as fp
import time
import html2text
import requests
import os

#feed = fp.parse("https://www.youtube.com/feeds/videos.xml?channel_id=UC2eYFnH61tmytImy1mTYvhA")
#print(feed.entries[0]["date"])

class Feed:
    def __init__(self, title="", url=None, feed = None):
        self.title = title #title of the url feed
        self.url = url # the xml/rss/atom url
        self.feed = feed # the feed object from feedparser
        self.entries = [] #Entries of this feed
    def fetch_entries(self):
        self.feed = fp.parse(self.url)
        for fp_entry in self.feed.entries:
            my_entry = Entry(feed=self)
            my_entry.parse_metadata_from_fp_entry(fp_entry)
            if my_entry.url in self.get_urls():
                existing_entry = self.get_entry_from_url(my_entry.url)
                existing_entry.description = my_entry.description
                existing_entry.thumbnail = my_entry.thumbnail

            else:
                self.entries.append(my_entry)
    def get_cache(self):
        cache_str = ""
        cache_str += f"{self.title}\t{self.url}\n"
        for entry in self.entries:
            cache_str += f"{entry.get_cache_str()}\n"
        return cache_str
    def get_urls(self):
        urls = []
        for entry in self.entries:
            urls.append(entry.url)
        return urls
    def get_entry_from_url(self,url):
        for entry in self.entries:
            if entry.url == url:
                return entry




class Feed_Folder:
    def __init__(self, title ="", feeds = [], sub_folders=[]):
        self.title = title
        self.feeds = feeds
        self.sub_folders = sub_folders
    #Maybe move cacheing to another part of the code
    def read_cache_file(self, path):
        c_file = open(path, "r")
        cache = c_file.read().split("\n")
        cur_feed = None
        for line in cache:
            line_items = line.split("\t")
            #feed line
            if (len(line_items) == 2):
                (title,url) = line_items
                if (url not in self.get_feed_urls()):
                    new_feed = Feed(url=url,title=title)
                    self.feeds.append(new_feed)
                    cur_feed = new_feed
                else:
                    cur_feed = self.get_feed_from_url(url)
                
                

            #entry line
            elif (len(line_items) == 5):
                (title, url, date, author, description) = line_items
                new_entry = Entry()
                new_entry.feed = cur_feed
                new_entry.title = title
                new_entry.url = url
                new_entry.author = author
                new_entry.description = bytes(description, encoding="utf-8").decode("utf-8", errors="backslashreplace")

                new_entry.date = time.strptime(date,"%Y%m%d%H%M")
                cur_feed.entries.append(new_entry)
            elif (len(line_items) == 6):
                (title, url, date, author, description, thumbnail) = line_items
                new_entry = Entry()
                new_entry.feed = cur_feed
                new_entry.title = title
                new_entry.url = url
                new_entry.author = author
                new_entry.description = bytes(description, encoding="utf-8").decode("utf-8", errors="backslashreplace")
                new_entry.thumbnail = thumbnail


                new_entry.date = time.strptime(date,"%Y%m%d%H%M")
                cur_feed.entries.append(new_entry)
        c_file.close()
    def write_cache_file(self, path):
        c_file = open(path,'w')
        cache_str = ""
        for feed in self.feeds:
            cache_str += feed.get_cache()
        c_file.write(cache_str)
        c_file.close()
    def get_recents(self):
        recents = []
        urls = []
        for feed in self.feeds:
            for entry in feed.entries:
                if entry.url not in urls:
                    recents.append(entry)
                    urls.append(entry.url)
        recents = sorted(recents, key=lambda entry: entry.get_date())
        recents.reverse()





        return recents
    def get_query(self, query):
        matched = []
        for feed in self.feeds:
            for entry in feed.entries:
                if (query in entry.title):
                    matched.append(entry)
        return matched
    def get_feed_urls(self):
        urls = []
        for feed in self.feeds:
            urls.append(feed.url)
        return urls
    def get_feed_from_url(self, url):
        ret_feed = None
        for feed in self.feeds:
            if (feed.url == url):
                ret_feed = feed 
        return ret_feed

class Sub_Folder(Feed_Folder):
    def __init__(self, master=None , title ="", feeds = [], sub_folders=None):
        self.master = master
        Feed_Folder.__init__(self, title = title, feeds = feeds, sub_folders=sub_folders)


class Entry:
    def __init__(self, date=None, title=None, url=None, author=None, description=None, feed=None, thumbnail=None):
        self.date = date #date struct
        self.title = title #title string
        self.url = url #url string
        self.author = author #author string
        self.description = description #description string
        self.feed = feed #feed parser feed object
        self.thumbnail = thumbnail #thumbnail url string
        self.thumbnail_path = None
    def set_feed(self, feed):
        self.feed = feed
    def get_date_human(self):
        date = time.strftime("%d/%m/%y %H:%M", self.date)
        return date
    def get_date(self):
        date = time.strftime("%Y%m%d%H%M",self.date)
        return date

    def parse_metadata_from_fp_entry(self, entry):
        #getting url
        #if entry has an enclosure, get the url stored in the enclosure 
        if ( entry.enclosures and 'href' in entry.enclosures[0]): 
            self.url = entry.enclosures[0]['href']
        #if entry has the url in link, get the url from that 
        elif ('link' in entry):
            self.url = entry.link
        
        #getting date
        if ('published_parsed' in entry):
            self.date = entry.published_parsed
        elif ('date_parsed' in entry):
            self.date = entry.date_parsed
        #getting author
        if ('author' in entry):
            self.author = entry.author
        elif (self.feed):
            self.author = self.feed.title
        #getting entry title
        if ('title' in entry):
            self.title = entry.title
        elif (self.feed.title):
            self.title = f"{self.feed.title} {self.get_date_human()}"
        #getting entry description
        if ('description' in entry):
            d_text = entry.description
            h = html2text.HTML2Text()
            h.ignore_links = True
            h.ignore_images = True
            self.description = h.handle(d_text)

        ## Optional things

        #getting potential thumbnail
        if ('media_thumbnail' in entry):
            #for youtube
            self.thumbnail = entry.media_thumbnail[0]['url']


            
    def get_cache_str(self):
        # (title, url, date, author
        cache_string = f"{self.title}\t{self.url}\t{self.get_date()}\t{self.author}"
        cache_string += "\t" + str(self.description.encode(encoding="utf-8",errors="backslashreplace"))
        if self.thumbnail:
            cache_string += "\t" + self.thumbnail


        return cache_string

        
    def download_thumbnail(self, parent_dir = "/tmp"):
        if self.thumbnail:
            if not os.path.isdir(parent_dir):
                os.mkdir(parent_dir)
            down_file = requests.get(self.thumbnail)
            self.thumbnail_path = parent_dir+ "/feedie-" +\
                    self.title.replace(" ","-").replace("/","-") +\
                    self.get_date()
            with open (self.thumbnail_path, "wb") as file:
                file.write(down_file.content)
            

    def print_data(self):
        print("Title=" + str(self.title))
        print("url=" + self.url)
        print("date=" + self.get_date_human())
        print("author=" + self.author)
        print("description=" + self.description)

        if (self.thumbnail):
            print(self.thumbnail)


if (__name__ == "__main__"):
    #title = "Luke Smith"
    #feed_url = "https://www.youtube.com/feeds/videos.xml?channel_id=UC2eYFnH61tmytImy1mTYvhA"
    
    #title = "WaveForm"
    #feed_url = "https://feeds.feedburner.com/WaveformWithMkbhd?format=xml"
    
    title = "AP"
    feed_url = "https://www.pipes.digital/feed/1NjYgr9z"

    my_feed = Feed(title=title, url=feed_url)
    my_feed.parse()
    my_feed.fetch_entries()
    
    title = "r/LinuxMemes"
    feed_url = "https://www.reddit.com/r/linuxmemes/.rss"
    
    
    my_feed2 = Feed(title=title, url=feed_url)
    my_feed2.parse()
    my_feed2.fetch_entries()
    myFF = Feed_Folder(title="All",feeds=[my_feed,my_feed2],path="/home/jake/Build/feedie/test_cache")
    #myFF = Feed_Folder(title="All",feeds=[],path="/home/jake/Build/feedie/test_cache")
    #myFF.write_cache_file()
    #myFF.read_cache_file()
    recents = myFF.get_query("I")
    for i in range(20):
        print(recents[i].title + recents[i].get_date_human())


    #for entry in my_feed.entries:
        #cache_s = (entry.get_cache_string())
        #entry.parse_cache_string(cache_s)
        #entry.print_data()

    #my_entry = Entry(feed=my_feed)
    #my_entry.parse_metadata_from_fp_entry(my_feed.feed.entries[3])
    #print(my_feed.feed.entries[4])
    #my_entry.print_data()

    #print(my_feed.get_cache())











