import listSelect as listSelect
import feedParse as feedParse
import config as config
import os
import socket
from curses import wrapper
import time
import threading
import ueberzug.lib.v0 as ueberzug


def get_list_item_from_entry(entry):
    li = listSelect.List_item()
    li.title = entry.title
    li.text = [entry.author, entry.get_date_human()]
    li.object = entry
    return li
def get_list_item_from_feed(f):
    li = listSelect.List_item()
    li.title = f.title
    li.text = []
    li.object = f
    return li
def get_list_item_from_feed_folder(ff):
    li = listSelect.List_item()
    li.title = ff.title
    li.text = []
    li.object = ff
    return li

def read_rss_list(path):
    if os.path.isfile(path):

        m_folder = feedParse.Feed_Folder(title="All")
        cur_folder = None 

        rss_file = open(path,'r')
        rss_list = rss_file.read().split("\n")
        for line in rss_list:
            line_items = line.split("\t")
            #comment line
            if line.startswith("#"):
                pass
            #folder terminator
            elif(len(line_items) == 1 and line_items[0].startswith("--\\")):
                cur_folder = None
            #folder initializer
            elif (len(line_items) == 1 and line_items[0].startswith("--")):
                title = line_items[0][2:]
                cur_folder = feedParse.Sub_Folder(title = title, master=m_folder, feeds = [])
                m_folder.sub_folders.append(cur_folder)
            #rss feed line
            elif(len(line_items) == 2):
                (title, url) = line_items
                m_folder.feeds.append(feedParse.Feed(title=title, url=url))
                if cur_folder:
                    cur_folder.feeds.append(m_folder.feeds[-1])
        rss_file.close()


    else:
        return None
    return m_folder
def first_run():
    #ADD ME
    #prompts user to add a feed to begin
    pass



def is_connected():
    #CREDIT https://stackoverflow.com/a/40283805
    try:
        # connect to the host -- tells us if the host is actually
        # reachable
        socket.create_connection(("1.1.1.1", 53))
        return True
    except OSError:
        pass
        return False

#run every time the list_win refreshes, used for downloading images and displaying description
def refresh(args = []):
    text_win = args[0]
    list_menu = args[1]
    placement = args[2]

    #download every thumbnail for each ListItem on screen
    for entry in list_menu.entries[list_menu.sel_index:list_menu.sel_index+list_menu.list_display_len]:
        if (entry.object.thumbnail_path == None):
            threading.Thread(target=entry.object.download_thumbnail, args=["/tmp/feedie"]).start()

    
    #initialize text_win if not present
    if text_win.text_win==None:
        text_win.init(list_menu.stdscr)
    #copy coresponding info and display it
    text_win.text  = list_menu.entries[list_menu.sel_index].object.description
    text_win.image = list_menu.entries[list_menu.sel_index].object.thumbnail_path
    text_win.from_list_menu_get_coresponding_geometry(list_menu)
    text_win.display()

    #display thumbnail
    ueberzug_display(placement,
            path=text_win.image,
            x=text_win.text_win_x+1,
            y=text_win.text_win_y+1,
            width=text_win.text_win_w-2,
            height=((text_win.text_win_h-1)//2)-1,
            scaler ="contain"
            )

def ueberzug_display(placement, path=None, x=0, y=0, height=10, width=10, scaler="contain"):
    if path:

        placement.x = x
        placement.y = y
        placement.width = width 
        placement.height = height 
        placement.path = path
        placement.scaler = scaler
        placement.visibility =  ueberzug.Visibility.VISIBLE

    else:
        placement.visibility =  ueberzug.Visibility.INVISIBLE


def get_main_menu_entries(master_ff):
    entries = []
    entries.append(get_list_item_from_feed_folder(master_ff))
    for subfolder in master_ff.sub_folders:
        entries.append(get_list_item_from_feed_folder(subfolder))
    for feed in master_ff.feeds:
        entries.append(get_list_item_from_feed(feed))
    return entries


def open_url(url=None, browsers=[], default_browser=None):
    url_found = False
    for browser, urls in browsers:
        for browser_url in urls: 
            if browser_url in url and not url_found:
                os.system(browser + " " +  url)
                url_found = True
    if not url_found:
        os.system(default_browser + " " +  url)





def goto_main_menu(lm):
    lm.return_value = "MM"
    lm.quit()

@ueberzug.Canvas(debug=False)
def display_gui(master_ff, config_dict, canvas):

    colors = [[config_dict["sel_fg"],config_dict["sel_bg"]],
              [config_dict["reg_fg"],config_dict["reg_bg"]]]

    list_menu = listSelect.ListMenu(colors)
    #select feed folder
    list_menu.entries = get_main_menu_entries(master_ff)
    
    #feed or feed_folder to pull entries from
    selected = (wrapper(list_menu.display))
    cur_source = selected #used when createing new list_menu
    cur_sel_i = 0
    cur_low_i = 0
    placement = canvas.create_placement('thumbnail')


    while(selected != None):
        list_menu = listSelect.ListMenu(colors)
        list_menu.refresh = refresh
        #list_menu.sel_index = cur_sel_i 
        #list_menu.list_low_index = cur_low_i  
        desc_win = listSelect.textWin()

        list_menu.func_dict["MainMenu"] = (goto_main_menu)
        list_menu.key_dict["M"] = ("MainMenu", list_menu)
        list_menu.key_dict["h"] = ("MainMenu", list_menu)


        list_menu.refresh_args = [desc_win, list_menu, placement]
        if (selected == "MM"):
            placement.visibility =  ueberzug.Visibility.INVISIBLE
            list_menu = listSelect.ListMenu(colors)
            list_menu.entries = get_main_menu_entries(master_ff)
            width_r = 1




        if (type(selected) == listSelect.List_item):
            width_r = 0.5
            #cur_sel_i = 0
            #cur_low_i = 0
            if (type(selected.object) == feedParse.Sub_Folder or type(selected.object) == feedParse.Feed_Folder):
                for entry in selected.object.get_recents():
                    list_menu.entries.append(get_list_item_from_entry(entry))
                cur_source = selected
                list_menu.cur_low_i = 0
                list_menu.cur_sel_i = 0
    
            elif(type(selected.object) == feedParse.Feed):
                for entry in selected.object.entries:
                    list_menu.entries.append(get_list_item_from_entry(entry))
                cur_source = selected
                list_menu.cur_low_i = 0
                list_menu.cur_sel_i = 0



    
            elif(type(selected.object) == feedParse.Entry):
                list_menu.list_low_index = cur_low_i
                list_menu.sel_index = cur_sel_i
                if (type(cur_source.object) == feedParse.Sub_Folder or type(cur_source.object) == feedParse.Feed_Folder):
                    for entry in cur_source.object.get_recents():
                        list_menu.entries.append(get_list_item_from_entry(entry))
    
                elif(type(cur_source.object) == feedParse.Feed):
                    for entry in cur_source.object.entries:
                        list_menu.entries.append(get_list_item_from_entry(entry))


                

                #open url
                open_url(url=selected.object.url, 
                        browsers=config_dict["browsers"],
                        default_browser = config_dict["default_browser"])

    
        
        selected = wrapper(list_menu.display,width_ratio=width_r)
        cur_sel_i = list_menu.sel_index
        cur_low_i = list_menu.list_low_index

#@ueberzug.Canvas(debug=False)
#def display_gui(master_ff, config_dict, canvas):
#
#    colors = [[config_dict["sel_fg"],config_dict["sel_bg"]],
#              [config_dict["reg_fg"],config_dict["reg_bg"]]]
#
#    list_menu = listSelect.ListMenu(colors)
#    #select feed folder
#    list_menu.entries = get_main_menu_entries(master_ff)
#    
#    #feed or feed_folder to pull entries from
#    source = (wrapper(list_menu.display))
#    lm_source = source #used when createing new list_menu
#    cur_sel_i = 0
#    cur_low_i = 0
#
#
#    placement = canvas.create_placement('thumbnail')
#    while(source != None):
#        list_menu = listSelect.ListMenu(colors)
#        list_menu.refresh = refresh
#        list_menu.sel_index = cur_sel_i 
#        list_menu.list_low_index = cur_low_i  
#        desc_win = listSelect.textWin()
#
#        list_menu.func_dict["MainMenu"] = (goto_main_menu)
#        list_menu.key_dict["M"] = ("MainMenu", list_menu)
#        list_menu.key_dict["h"] = ("MainMenu", list_menu)
#
#
#        list_menu.refresh_args = [desc_win, list_menu, placement]
#        if (source == "MM"):
#            placement.visibility =  ueberzug.Visibility.INVISIBLE
#            list_menu = listSelect.ListMenu(colors)
#            list_menu.entries = get_main_menu_entries(master_ff)
#            width_r = 1
#
#
#        if (type(source) == listSelect.List_item):
#            width_r = 0.5
#            cur_sel_i = 0
#            cur_low_i = 0
#            if (type(source.object) == feedParse.Sub_Folder or type(source.object) == feedParse.Feed_Folder):
#                for entry in source.object.get_recents():
#                    list_menu.entries.append(get_list_item_from_entry(entry))
#    
#            elif(type(source.object) == feedParse.Feed):
#                for entry in source.object.entries:
#                    list_menu.entries.append(get_list_item_from_entry(entry))
#
#
#
#    
#            elif(type(source.object) == feedParse.Entry):
#                if (type(lm_source.object) == feedParse.Sub_Folder or type(lm_source.object) == feedParse.Feed_Folder):
#                    for entry in lm_source.object.get_recents():
#                        list_menu.entries.append(get_list_item_from_entry(entry))
#    
#                elif(type(lm_source.object) == feedParse.Feed):
#                    for entry in lm_source.object.entries:
#                        list_menu.entries.append(get_list_item_from_entry(entry))
#
#
#                
#
#                #open url
#                open_url(url=source.object.url, 
#                        browsers=config_dict["browsers"],
#                        default_browser = config_dict["default_browser"])
#
#    
#        
#        source = wrapper(list_menu.display,width_ratio=width_r)
#        cur_sel_i = list_menu.sel_index
#        cur_low_i = list_menu.list_low_index
#
#
#
#
#
#
#
#
#    #from feed folder select

def refresh_feeds(master_ff, config_dict):
    while True:
        if is_connected:
            threads = []
            for i,feed in enumerate(master_ff.feeds):
                threads.append(threading.Thread(target=feed.fetch_entries))
                threads[i].start()
            for thread in threads:
                if thread.is_alive():
                    thread.join()
            #write cache and make parent dir of not there
            cache_parent_dir = "/".join(config_dict["cache_path"].split("/")[:-1])
            if not os.path.isdir(cache_parent_dir):
                os.mkdir(cache_parent_dir)
                print(f"added dir {cache_parent_dir}")
            master_ff.write_cache_file(config_dict["cache_path"])
        time.sleep(config_dict["refresh_rate"])




    

    
    


if __name__ == "__main__":
    #read configs
    args = config.parse_args()
    conf_path = args.config #path to the config file
    config_dict = config.read_config(conf_path);
    
    

    #read rss list
    #feedParse.File_Folder master_ff containing all feeds and folders
    master_ff = read_rss_list(config_dict["rss_path"])
    if master_ff:
        if os.path.isfile(config_dict["cache_path"]):
            master_ff.read_cache_file(config_dict["cache_path"])
            print("reading cache")

        
        gui_thread = threading.Thread(target=display_gui, args=[master_ff, config_dict])
        gui_thread.start()

        #fetch new entries if connected to web
        refresh_thread = threading.Thread(target=refresh_feeds, args=[master_ff, config_dict], daemon=True)
        refresh_thread.start()

            




        #for entry in master_ff.sub_folders[1].get_recents():

    else:
        first_run()






