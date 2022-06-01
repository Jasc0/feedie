import argparse
import os
import curses

   
def parse_browser_from_line(line):
        line = line[0].strip().split(':')
        browser_command = line.pop(0)
        browser_command = browser_command[8:]
        browser_urls    = line[0].strip().split(' ')
        return (browser_command, browser_urls)



def open_url(url, browsers, default_browser):
    url_found = False
    for browser in browsers:
        for array_url in browser.urls: 
            if array_url in url and not url_found:
                os.system(browser.command + " " +  url)
                url_found = True
    if not url_found:
        os.system(default_browser + " " +  url)

def translate_color(color_str):
    color_str = color_str.lower()
    if   color_str == "black":
        ret_color = curses.COLOR_BLACK
    elif color_str == "red":
        ret_color = curses.COLOR_RED
    elif color_str == "green":
        ret_color = curses.COLOR_GREEN
    elif color_str == "yellow":
        ret_color = curses.COLOR_YELLOW
    elif color_str == "blue":
        ret_color = curses.COLOR_BLUE
    elif color_str == "magenta":
        ret_color = curses.COLOR_MAGENTA
    elif color_str == "cyan":
        ret_color = curses.COLOR_CYAN
    elif color_str == "white":
        ret_color = curses.COLOR_WHITE
    return ret_color
def translate_to_color(color_int):
    if   color_int == curses.COLOR_BLACK:
        ret_color ="black" 
    elif color_int == curses.COLOR_RED:
        ret_color ="red" 
    elif color_int == curses.COLOR_GREEN:
        ret_color ="green" 
    elif color_int == curses.COLOR_YELLOW:
        ret_color ="yellow" 
    elif color_int == curses.COLOR_BLUE:
        ret_color ="blue" 
    elif color_int == curses.COLOR_MAGENTA:
        ret_color ="magenta" 
    elif color_int == curses.COLOR_CYAN:
        ret_color ="cyan" 
    elif color_int == curses.COLOR_WHITE:
        ret_color ="white" 
    return ret_color


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c",
                        "--config",
                        type=str,
                        default=(os.getenv("HOME")+"/.config/feedie/conf"),
                        help="use an alternative config file location")
    return parser.parse_args()
    
def read_config( conf_path ):
    #defaults
    config_dict = {
    "rss_path" : (os.getenv("HOME") + "/.config/feedie/rsslist"),
    "cache_path" : (os.getenv("HOME") + "/.cache/feedie/cache") ,
    "sel_fg"    : translate_color("black"),
    "sel_bg"    : translate_color("green"),
    "reg_fg"    : translate_color("white"),
    "reg_bg"    : translate_color("black"),
    "refresh_rate" : 300, # 5 mins
    "default_browser" : os.getenv("BROWSER"),
    "browsers" : []
            }
    #if the config file exists, read from that, see else
    if os.path.isfile(conf_path): 

        conf_file = open(conf_path, "r")
        conf = conf_file.read()
        conf = conf.split("\n")
        
        for line in conf:
            line = line.split("=")
            if (len(line) == 2):
                (key, value) = line
                key = key.strip()
                value = value.strip()
                if (key == "rss_path"):
                    config_dict["rss_path"] = value
                elif (key == "cache_path"):
                    config_dict["cache_path"] = value
                elif (key == "sel_fg"):
                    config_dict["sel_fg"] = translate_color(value)
                elif (key == "sel_bg"):
                    config_dict["sel_bg"] = translate_color(value)
                elif (key == "reg_fg"):
                    config_dict["reg_fg"] = translate_color(value)
                elif (key == "reg_bg"):
                    config_dict["reg_bg"] = translate_color(value)
                elif (key == "refresh_rate"):
                    config_dict["refresh_rate"] = int(value)
                elif (key == "default_browser"):
                    config_dict["default_browser"] = value
            elif line[0].startswith("BROWSER"):
                    config_dict["browsers"].append(parse_browser_from_line(line))

    #else make a config file and write to it the default values
    else:
        if not os.path.isdir(conf_path[:-5]):
            os.mkdir(conf_path[:-5])
        conf_file = open(conf_path, "w")
        for key, value in config_dict.items():
            if (key[-3:] == "_bg" or key[-3:] == "_fg"):
                conf_file.write(key + " = " + translate_to_color(value) + "\n")
            elif (key == "browsers"):
                for browser, urls in value:
                    conf_file.write("BROWSER " + browser + " : " + " ".join(urls)  + "\n")

            else:
                conf_file.write(key + " = " + str(value) + "\n")

    conf_file.close()



        

    
    return config_dict
