import curses

class PromptWindow:
    def __init__(self,stdscr=None,title=None):
        self.stdscr = stdscr
        self.title = title
        self.box_text = ""
        self.cursor_index = 0
        self.screen_h = 0
        self.screen_w = 0
        self.win_h = 0
        self.win_w = 0
        self.win_x = 0
        self.win_y = 0
    def set_win_dimensions(self, height, width ):
        self.screen_h, self.screen_w = self.stdscr.getmaxyx()
        self.win_h = height
        self.win_w = width
        self.win_y = (self.screen_h // 2) - (height // 2)
        self.win_x = (self.screen_w // 2) - (width // 2)

    def display(self, stdscr, height= 3, width = 20):
        self.stdscr = stdscr
        self.set_win_dimensions(height,width)
        win = curses.newwin( self.win_h,
                             self.win_w,
                             self.win_y,
                             self.win_x)
        
        win.box()
        win.addstr(0, (( self.win_w//2) - len(self.title)//2), self.title )

        running = True;

        while running:
            win.clear()
            win.box()
            win.addstr(0, (( self.win_w//2) - len(self.title)//2), self.title )

            if (len(self.box_text) < (self.win_w - 3)):
                win.addstr(1,1, self.box_text)
            else:
                win.addstr(1,1, self.box_text[self.cursor_index - (self.win_w-3):self.cursor_index])

            


        
        
            if (len(self.box_text) < (self.win_w - 3)):
                win.move(1,self.cursor_index+1)
            stdscr.refresh()
            win.refresh()
            key = stdscr.getkey()
            if (key == "KEY_BACKSPACE"): #backspace
                if (self.cursor_index == (len(self.box_text)-1)):
                    self.box_text = self.box_text[:-1]
                else:
                    self.box_text =self.box_text[:self.cursor_index-1]+\
                            self.box_text[self.cursor_index:]
                    if self.cursor_index > 0:
                        self.cursor_index -=1
            elif (key == "\n"): #enter
                running = False
            elif (key == "KEY_LEFT"): #left
                if self.cursor_index >= 0:
                    self.cursor_index -=1
            elif (key == "KEY_RIGHT"): #right
                if self.cursor_index < len(self.box_text):
                    self.cursor_index +=1
            else:
                if (self.cursor_index == (len(self.box_text)-1)):
                    self.box_text+= (key)
                else:
                    self.box_text =self.box_text[:self.cursor_index]+\
                            key + self.box_text[self.cursor_index:]

                self.cursor_index +=1

            #win.refresh()
            #stdscr.refresh()
        return self.box_text

            

            


        win.refresh()
        stdscr.refresh()






if __name__ == "__main__":
    my_aw = PromptWindow(title="enter rss feed link")
    print(curses.wrapper(my_aw.display, width=50))

