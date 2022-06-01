import curses
from curses import wrapper
import threading
import ueberzug.lib.v0 as ueberzug

def pad_to_width(text_to_pad, amount):
    ret_str = [" "] * (amount)
    #ret_str = " " * (self.list_win_w - 1)
    for i in range(0,len(text_to_pad)):
        if (i < len(ret_str)):
            ret_str[i] = text_to_pad[i]
    return "".join(ret_str)

class ListMenu:
    def __init__(self, colors = None):
        self.stdscr = None
        self.sel_index = 0
        self.quit_flag = False
        self.list_win = None
        self.entries = []
        self.func_dict = {"scroll_down": self.scroll_down, 
            "scroll_up" : self.scroll_up,
            "quit" : self.quit,
            "get_entry" : self.get_entry}

        self.key_dict = {"j": ("scroll_down", None), 
            curses.KEY_DOWN: ("scroll_down", None), 
            "k" : ("scroll_up", None),
            curses.KEY_UP: ("scroll_up", None), 
            "Q" : ("quit", None),
            "\n" : ("get_entry", None)}

        self.return_value = None
        self.refresh = None
        self.refresh_args = []
        if colors:
            self.colors = colors
        else:
                        #normal fg,bg  #select fg,bg
            self.colors= [ (curses.COLOR_BLACK, curses.COLOR_GREEN),\
                           (curses.COLOR_WHITE, curses.COLOR_BLACK)]
        
        self.list_low_index = 0
        self.list_display_len = 0

        self.screen_h = 0
        self.screen_w = 0
        self.list_win_h = 0
        self.list_win_w = 0
    def set_win_dimensions(self, height_ratio=1, width_ratio=1 , y=0, x=0):
        self.screen_h, self.screen_w = self.stdscr.getmaxyx()
        self.list_win_h = int(height_ratio * (self.screen_h - y))
        self.list_win_w = int(width_ratio * (self.screen_w - x))
        self.list_win_y = y
        self.list_win_x = x
        if (self.list_win != None):
            self.list_win.resize(self.list_win_h,self.list_win_w)
            self.list_win.mvwin(y,x)
    def scroll_down(self, args=None):
        if( self.sel_index < (len(self.entries)-1)):
            self.sel_index +=1
        if( (self.sel_index - self.list_low_index) >= self.list_display_len):
            self.list_low_index +=1
#        if (self.sel_index < ((self.list_low_index + self.list_display_len) -1) and (self.sel_index < len(self.entries) -1) ):
#            self.sel_index +=1
#        elif (self.sel_index < len(entries) -1) :
#            self.list_low_index +=1
#            self.sel_index +=1

    def scroll_up(self, args=None):
        if (self.sel_index > self.list_low_index):
            self.sel_index -=1
        elif (self.sel_index > 0):
            self.list_low_index -=1
            self.sel_index -=1
    def quit(self, args=None):
        self.quit_flag = True
    def get_entry(self, args=None):
        self.return_value = self.entries[self.sel_index]
        self.quit()
        


        

            

    def display(self, stdscr, width_ratio=1, height_ratio=1, win_y=0, win_x=0, pad=1):
        self.stdscr = stdscr
        curses.curs_set(0)
        curses.init_pair(1, self.colors[0][0], self.colors[0][1] )
        curses.init_pair(2, self.colors[1][0], self.colors[1][1] )

        self.set_win_dimensions(height_ratio, width_ratio, win_y , win_x)
        #self.list_display_len = (self.list_win_h // (len(self.entries[0].text) + 1 + pad))
        key = ''
        old_w = self.list_win_w
        old_h = self.list_win_h
    
    
        list_win = curses.newwin(self.list_win_h, self.list_win_w, self.list_win_y, self.list_win_x)
        while (not self.quit_flag):
            self.set_win_dimensions(height_ratio, width_ratio, win_y , win_x)
            if self.entries[0].text:
                #                       height-1 for box       length of subheadinglines + title + pad
                self.list_display_len = ((self.list_win_h - 1 ) // (len(self.entries[0].text) + 1 + pad))
            else:
                self.list_display_len = ((self.list_win_h - 1 ) // (1 + pad))
            if (self.refresh):
                self.refresh(args=self.refresh_args)
            
            #if screen dimensions change, clear screen to avoid artifacts
            if (old_w != self.list_win_w or old_h != self.list_win_h):
                list_win.resize(self.list_win_h,self.list_win_w)
                stdscr.clear()
                list_win.clear()
                old_w = self.list_win_w
                old_h = self.list_win_h


            #for every entry between list_low_index and however many entries can be displayed above list_low_index
            for i,entry in enumerate(self.entries[self.list_low_index:(self.list_low_index+self.list_display_len)]):
                #line which entries start on, starting at 1 for box
                startline = 1 + ( i * (len(entry.text) + 1 + pad ))  # count  of lines each entry occupies 
                if (self.sel_index == (self.list_low_index + i)):
                    color = curses.color_pair(1)
                else:
                    color = curses.color_pair(2)

                list_win.addstr( startline, 1, pad_to_width(entry.title, (self.list_win_w-2)), color) # write title
                for j,text in enumerate(entry.text): # for every item in text list
                    list_win.addstr( (startline + 1 + j), 1, pad_to_width(text,self.list_win_w-2), color) # write subheading

    
    
            list_win.box()
    
    
    
            stdscr.refresh()
            list_win.refresh()
            curses.halfdelay(50)
            try:
                key = stdscr.getch()

                if (chr(key) in self.key_dict):
                    value, args = self.key_dict[chr(key)]
                    self.func_dict[value](args)
                elif (key in self.key_dict):
                    value, args = self.key_dict[(key)]
                    self.func_dict[value](args)
            except:
                pass
        return self.return_value


class List_item:
    def __init__(self):
        self.title = ""
        self.text = []
        self.object = None
    def set_title(self, title):
        self.title = title
    def set_text(self, text_list):
        self.text = text_list
    
    def get_title(self):
        return self.title
    def get_text(self):
        return self.text
    #def get_text(self, index):
    #    return self.text[index]

class textWin:
    def __init__(self, stdscr=None, colors = None, x=0, y=0, 
            screen_h = 0, screen_w = 0, text_win_h = 0, 
            text_win_w = 0, text=None):

        self.stdscr = stdscr

        if colors:
            self.colors = colors
        else:
                        #normal fg,bg  #select fg,bg
            self.colors= [ (curses.COLOR_BLACK, curses.COLOR_GREEN),\
                           (curses.COLOR_WHITE, curses.COLOR_BLACK)]
        self.text_win_x = x
        self.text_win_y = y
        self.screen_h = screen_h 
        self.screen_w = screen_w 
        self.text_win_h = text_win_h 
        self.text_win_w = text_win_w 
        self.text = text
        self.text_win = None
        self.image = None
        self.placement = None
    #def from_list_menu_get_coresponding_geometry(lm, thumbnail):
    def from_list_menu_get_coresponding_geometry(self, lm):
        self.text_win_x = lm.list_win_w
        self.text_win_y = 0
        self.text_win_w = (lm.screen_w - lm.list_win_w)
        self.text_win_h = lm.list_win_h
        if self.text_win:
            self.text_win.resize(self.text_win_h,self.text_win_w)
            self.text_win.mvwin(self.text_win_y,self.text_win_x)
        self.text = lm.entries[lm.sel_index].object.description
        #self.image = thumbnail
    def init(self,stdscr):
        self.stdscr = stdscr
        self.text_win = curses.newwin(self.text_win_h, self.text_win_w, self.text_win_y, self.text_win_x)

    def display(self):
        #if self.placement:
            #self.placement.visibility =  ueberzug.Visibility.INVISIBLE
        #self.init(stdscr)

        self.text_win.clear()

        self.text_win.box()
        line_c = 1
        if(self.image):
            line_c = ((self.text_win_h-2)//2) +1
                



        for line in self.text.split('\n'):
            if (line != ''):
                if (len(line) > self.text_win_w-2):
                    while len(line) > 0:
                        if (line_c < self.text_win_h-1):
                            if (len(line) < self.text_win_w-2):
                                self.text_win.addstr(line_c,1,line)
                                line = ""
                            else:
                                self.text_win.addstr(line_c,1,line[:self.text_win_w-2])
                                line = " " + line[self.text_win_w-2:]
                                line_c +=1
                        else:
                            break




                else:
                    if (line_c < self.text_win_h-1):
                        self.text_win.addstr(line_c,1,line)
                line_c +=1
        self.text_win.refresh()
        #if(self.image):
        #    if (self.placement == None):
        #        self.placement = canvas.create_placement('thumbnail', scaler="contain", synchronously_draw=True)

        #    self.placement.x = self.text_win_x+2
        #    self.placement.y = self.text_win_y+2
        #    self.placement.width = self.text_win_w 
        #    self.placement.height = self.text_win_h // 2
        #    self.placement.path = self.image
        #    self.placement.visibility =  ueberzug.Visibility.VISIBLE










if __name__ == "__main__":
    text = "What does encapsulation mean:\n In object-oriented computer programming (OOP) languages, the notion of encapsulation (or OOP Encapsulation) refers to the bundling of data, along with the methods that operate on that data, into a single unit. Many programming languages use encapsulation frequently in the form of classes. A class is a program-code-template that allows developers to create an object that has both variables (data) and behaviors (functions or methods). A class is an example of encapsulation in computer science in that it consists of data and methods that have been bundled into a single unit."
    tw = textWin(text_win_h = 20, text_win_w=30, text=text)
    tw.image = "/tmp/1"
    wrapper(tw.display)
'''

    Titles = [1,2,3,4,5,6,7,8,9]
    subtext= ["One","Two","Three","Four","Five","Six","Seven","Eight","Nine"]
    entries = []
    for i in range(0,9):
        entries.append(List_item())
        entries[i].set_title(str(Titles[i]))
        entries[i].set_text([subtext[i]])
    
    
    list_menu = ListMenu() 
    
    list_menu.entries = entries
    
    key_dict = {"j": list_menu.scroll_down, 
            curses.KEY_DOWN: list_menu.scroll_down, 
            "k" : list_menu.scroll_up,
            curses.KEY_UP: list_menu.scroll_up, 
            "Q" : list_menu.quit,
            "\n" : list_menu.get_entry
            }
    list_menu.key_dict = key_dict
    pad = 1 #lines between each entry
    print(wrapper(list_menu.display,0.5,0.5,0,0,pad).title)
#    print( pad_to_width("hahaha", 14))
'''
