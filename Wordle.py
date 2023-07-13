import pygame as pg
import sys
import time
import json
from itertools import islice
import random

# The game state is held in global variables. We need to track which guess number is live (user gets 6 guesses)
# which letter of the guess is live (there are 5 letters in each word)
# Based on the guess number and guess letter, the game controls will be made live or inactive.
# The user can only enter their guess if they have entered 5 letters in that guess. The user can only
# delete a letter if they've entered at least one letter
# There is also a message string which allows us to communicate with the user
 
#the guess num is which guess the user is working on (1 to 6)
guess_num = 0
# the guess index is the letter of the guess the user is working on (1 to 5)
guess_index = 0
bln_enter = False
bld_del = False
winner = False
lose = False
message = ""
answer = ""

# Let's define the size of the game and some basic colours

width_s = 370
height_s = 720
white = (255,255,255)
black = (0,0,0)
background = (140, 200, 50)

# And the way the board will be laid out - this defines where the input area (controls and keyboard) begin and will be spaced

big_gap = 12
enter_top = 72 * 6 + big_gap
enter_del_width = (width_s - (big_gap * 3)) / 2

#these are the colours the keys change when we find out if a letter is in the answer

open_key= (190,190,190)
wrong_key = (100,100,100)
close_key = (240,240,0)
right_key = (0,200,0)
results = {1: open_key, 2: wrong_key, 3: close_key, 4: right_key}

# Load the words from a dictionary held in a json file
# I sourced this dictionary from https://github.com/dwyl/english-words
# who sourced it from  https://www.infochimps.com/datasets/word-list-350000-simple-english-words-excel-readable
# who hold the copyright

# An interesting enhancement might be to allow the user to set the number of letters in the target word :)

with open("words_dictionary.json", "r") as my_json:

    eng_dict = json.load(my_json) 
    wordle_dict = {k: v for k, v in eng_dict.items() if len(k) == 5}
    
end = len(wordle_dict)-2

# answers is a 6 entry dictionary, with values consisting of a
# list of 3 5 item strings (one for each letter), for the letters, the cell colour
# and the letter's guess status 

answers = {x: [["","","","",""],[open_key,open_key,open_key,open_key,open_key],[1,1,1,1,1]] for x in range(7)}

# letters is a 26 entry dictionary. The key is the letter (of course) and we also hold where that letter's key
# should be positioned on the screen, and the letter's status (ie - do we know if the letter is in the answer
# or not). The keyboard will be basic Qwerty - 3 rows with 10, 9 and 7 keys respectively

lst_ab = "qwertyuiopasdfghjklzxcvbnm"
keyb_layout = [10,9,7]
letters = {lst_ab[i]: [open_key,1.0,1.0] for i in range(len(lst_ab)-1)}

# WHile we're building the letters dictionary, we also capture the area in which the keyboard will be drawn.
# This will allow us to more easily identify when the user clicks on a letter and also help draw the messages
# area of the game interface

max_key_y = 0
max_key_x = 0
min_key_y = height_s
min_key_x = width_s

width = 30
height = 34
gap = big_gap/2
ltr_index = -1

for i in range(3):
    for j in range(keyb_layout[i]):
        ltr_index +=1   
        if ((j+1)+(i*keyb_layout[i])) <= 27:
            pos_y = (72*7) + gap*(i+1)+height*i
            pos_x = gap*(j+1)+width*j
            letters[lst_ab[ltr_index]]=[open_key,1,pos_x,pos_y]
            if pos_y < min_key_y:
                min_key_y = pos_y
            if pos_y > max_key_y:
                max_key_y = pos_y
            if pos_x < min_key_x:
                min_key_x=pos_x
            if pos_x > max_key_x:
                max_key_x=pos_x
max_key_y += height
max_key_x += width

# Let's initiate the game :)

pg.init()
fps = 30
CLOCK = pg.time.Clock()
screen = pg.display.set_mode((width_s,height_s),0,32)
screen.fill(background)

pg.display.set_caption("My wordle game")

# And get stuck into the gameplay

def draw_answers():

# This function displays the answers and their status by letter in the answer grid on the top part of the game display

    global letters

    global screen
    global answers
    global black
    global big_gap
    global open_key
    global guess_index
    
    # These define the size of the letter boxes in the answer grid. Could possibly make this global?
    # Would need to set dynamically if we enhanced with the ability to select number of letters in answer

    height = 60
    width = 60
    gap = big_gap
    
    # In the 6 * 5 array of 6 5 letter guesses
    # i is the row, j is the column
    for i in range(6):
        for j in range(5):
            pos_y = gap*(i+1)+height*i
            pos_x = gap*(j+1)+width*j
            if i >= guess_num:
                back_col = open_key
            else:
                back_col = answers[i][1][j]
            # Change the colour of the boxes based on the guess's status
            guess_rect = pg.draw.rect(screen,back_col,pg.Rect(pos_x,pos_y,width,height))
            font = pg.font.Font(None,30)
            letter = font.render(answers[i][0][j],1,black,back_col)
            screen.blit(letter,(pos_x,pos_y))
            
    pg.display.flip()
    return True

def draw_func_keys(bln_ent=False,bln_del=False):

# This draws the enter and delete keys and makes them available or not as appropriate
# Can only press enter if 5 letters have been entered in the live guess
# Can only press delete if at least 1 letter has been entered in the live guess

    global letters

    global screen
    global big_gap
    global enter_top
    global enter_del_width                

    # Set the colour depending on whether the game state will allow you to click the buttons
    
    if bln_ent:
        ent_colour = open_key
    else:
        ent_colour = wrong_key
    if bln_del:
        del_colour = open_key
    else:
        del_colour = wrong_key
        
    font = pg.font.Font(None,30)
    enter_key = pg.draw.rect(screen,ent_colour,pg.Rect(big_gap,enter_top,enter_del_width,height))
    enter_t = font.render("Enter",True,black,ent_colour)
    screen.blit(enter_t,(big_gap,enter_top))

    del_key = pg.draw.rect(screen,del_colour,pg.Rect((big_gap * 2) + enter_del_width,enter_top,enter_del_width,height))
    del_t = font.render("Delete",1,black,del_colour)
    screen.blit(del_t,((big_gap * 2) + enter_del_width,enter_top))
    
    pg.display.flip()   

    return True


def draw_keyboard(lst_ab,letters):

#now to add the letter buttons

# letters takes the form of a 26 entry dictionary, with values consisting of the 
# letter's accuracy and colour of the key

    global screen
    
    global open_key
    global wrong_key
    global close_key
    global right_key
    
    global min_key_y
    global max_key_y
    global min_key_x
    global max_key_x
    
    global width
    global height
    global gap

    for item in letters.items():
        # Need to create 2 surfaces - the first is the image of the key (letter_key), 
        # and the colour is based on the accuracy of the guess as stored in the letters array
        # the second is the actual letter to display (letter)
        # The two are displayed in the same location
        letter_key = pg.draw.rect(screen,item[1][0],pg.Rect(item[1][2],item[1][3],width,height))
        font = pg.font.Font(None,30)
        letter = font.render(item[0],True,black)
        screen.blit(letter,(item[1][2],item[1][3]))
    return letters
      
def check_words(guess_txt,guess_num):

    # Compare the user's guesses to the answer, and update the letters too
    global answer
    global answers

    # We're going to pass through each letter in each guess and compare it to the answer
    # The letter can be in the same place as in the answer, in the answer or in a different place,
    # or not in the answer at all. Each has a different status and will need to be highlighted
    # in a different colour in the answer grid and keyboard
    # If a letter is in the same place in the guess as the answer it will be given an answer value of 
    # 4, which is larger than any other answer values. Therefore if the sum of all 5 guess letters' 
    # answer values is 20, all 5 guess letters are the same as all 5 answer letters and the guess is correct
    
    right_answer = 0

    for i in range(0,5):
        if answer[i].upper() == guess_txt[i].upper():
            answers[guess_num][1][i] = right_key
            answers[guess_num][2][i] = 4
        else:
            for j in range(0,5):
                if (i != j) and (answer[j].upper() == guess_txt[i].upper()):
                    answers[guess_num][1][i] = close_key
                    answers[guess_num][2][i] = 3
            # If the guess has already been checked, then this should always be 2 already
            # If it hasn't been checked then is should always be 1 (not checked)
            # but include this if just in case something unexpected happens :)
            if answers[guess_num][2][i] == 1:
                answers[guess_num][1][i] = wrong_key
                answers[guess_num][2][i] = 2
        right_answer += answers[guess_num][2][i]
        # Now that we've checked the 5 guess letters, update the letters array so we can update the keyboard
        # In fact, we should really be able to do this above, since letters is a dictionary keyed on the letters
        # but I guess I didn't think of that when I was writing this :D
        check_letters(guess_txt[i],answers[guess_num][1][i],answers[guess_num][2][i])

    if right_answer == 20:
        return True
    else:
        return False
                
def check_letters(guess_letter="",guess_colour=open_key,guess_type=1):
    # Update the array holding our letters with the letter's status as part of the answer using info 
    # from the latest guess. Could definitely just include this in the function to 
    # check the answers atually

    letters[guess_letter] = [guess_colour,guess_type,letters[guess_letter][2],letters[guess_letter][3]]
    
def enter_guess(guess_letter=""):

    # Enter the guess letter in the answers array and increase the guess_index
    
    global guess_num
    global guess_index
    global answers
    
    answers[guess_num][0][guess_index] = guess_letter
    guess_index += 1

def del_guess():

    # Delete the last letter in the current guess and decrease the guess_index
    
    global guess_num
    global guess_index
    global answers
    
    answers[guess_num][0][guess_index-1] = ""
    guess_index -= 1
       
def update_message():
    
    # Display the current message on the display below the keyboard
    
    global message
    
    my_font = pg.font.Font(None,15)
    my_message = my_font.render(message,True,black)
    msg_rec = my_message.get_rect(center=(width_s/2,max_key_y+height+(height_s-(max_key_y+height))/2))
    screen.fill(white,(0,(max_key_y+height),width_s,(height_s - (max_key_y+height))))
    screen.blit(my_message,msg_rec)
    pg.display.update()
    return True

# Now to run the thing

def user_click():

    # handle the user clicking on the game display
    
    global winner
    global lose
    
    global message
    global letters
    
    global guess_num
    global guess_index
    
    global max_key_y
    global max_key_x
    global min_key_y
    global min_key_x
    
    global bln_del
    global bln_enter

    x,y = pg.mouse.get_pos()

#  First check if they've clicked on one of the letter keys, but only if there are more spaces to accept the guess
#  If they have clicked on the keyboard identify the letter they clicked on and enter it in the live guess    
    if y >= min_key_y and y <= max_key_y and x >= min_key_x and x <= max_key_x:
        if guess_index <= 4:
            for item in letters.items():
                if y >= item[1][3] and y <= item[1][3]+height and x >= item[1][2] and x<= item[1][2] + width:
                    enter_guess(item[0])
                    break
        else:
            message = "You have already entered 5 letters. Delete one if you want to change the last letter"
        return True
    
# Now check if they've clicked on the delete key and delete the last letter in the current guess if there are any letters entered
    
    if y >= enter_top and y <= enter_top + 60 and x >= (big_gap + enter_del_width + big_gap) and x <= ((big_gap + enter_del_width)*2):
        if bln_del:
            del_guess()
        else:
            message="You cannot delete a letter until you have guessed a letter"
        return True  
    
# Now check if they've clicked on the enter key and check the current guess if it contains 5 letters

    if y >= enter_top and y <= enter_top + 60 and x >= (big_gap) and x <= ((big_gap + enter_del_width)):
        if bln_enter:
            # If the word is in the dictionary check it against the answer
            if "".join(answers[guess_num][0]) in wordle_dict.keys():
                guess_num += 1
                guess_index = 0
                # if the guess matches the answer tell the user they won
                if check_words(answers[guess_num-1][0],guess_num-1):
                    winner = True
                    message="You have found the correct answer"
                # If they're out of guesses tell them the game is over
                else:
                    if guess_num > 5:
                        lose = True
                        message = "You have not guessed the answer in 6 attempts. Game over"
            # If the word isn't in the dictionary tell the user so
            else:
                message="That word is not found in the dictionary"
        else:
            message="You cannot check a guess until you have entered 5 letters"     
    return True

def game_setup():

    # Initiate all the global variables and set up the layout
    global winner
    global lose
    global guess_index
    global guess_num
    global message
    global answers
    global letters
    global answer
    global keyb_layout

    
    winner = False
    lose = False
    guess_index=0
    guess_num = 0
    message = "New game"
    
    # Select an answer from the dictionary at random
    
    rand_ans = random.randrange(0,end)
    answer = list(islice(wordle_dict,rand_ans,rand_ans+1))[0]
    print(answer)

    # Set all the entries in the 6x5 answer array to not checked status
    answers = {x: [["","","","",""],[open_key,open_key,open_key,open_key,open_key],[1,1,1,1,1]] for x in range(7)}
    # Set all the letters in the letters array to not checked status
    lst_ab_ind = 0
    for i in range(3):
        for j in range(keyb_layout[i]):
            if ((j+1)+(i*9)) <= 26:
                # Not sure I actuall need to update the positions here in fact but it doesn't take long anyway
                pos_y = (72*7) + gap*(i+1)+height*i
                pos_x = gap*(j+1)+width*j
                letters[lst_ab[lst_ab_ind]]=[open_key,1,pos_x,pos_y]
            lst_ab_ind += 1    
    update_screen()
    
def update_screen():

    # Redraw the screen whenever something changes
    
    global lst_ab
    global letters
    global bln_enter
    global bln_del
 
    # If guess_index = 5 then the user has entered 5 letters in the current guess and can hit the enter button
    # If guess_index > 0 then the user has entered at least one letter in the current guess and can hit the delete button
    bln_enter = guess_index == 5
    bln_del = guess_index > 0
    
    # First draw the answers grid, updating the colours based on comparison with the answer
    if draw_answers() == False:
        print("Prob with answers")
        
    # Now redraw the function keys and make live or not depending on how many letters have been entered in the current guess
    if draw_func_keys(bln_enter,bln_del) == False:
        print("Prob with functions")
    
    # Redraw the keyboard and update colours of keys based on letter status vs answer
    letters = draw_keyboard(lst_ab,letters)
    if update_message() == False:
        print("Prob with message")
        
    # If the user has won (the last guess is identical to the answer) or lost (entered 6 guesses without getting the answer)
    # then return false to let the game state know the game is over
    if winner:
        #breakpoint()
        time.sleep(4)
        return False
    if lose:
        time.sleep(4)
        return False
    
    # If the user has neither won nor lost return true to let the game state know to continue
    return True

# Infinite loop while the game is running

game_setup()

while(True):
    for event in pg.event.get():
        # If the user clicks on the big X quit the game
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
        # If the user clicks elsewhere then handle that click as appropriate
        elif event.type == pg.MOUSEBUTTONDOWN:
            if user_click():
                # update_screen returns true if the user has won or lost - so start a new game
                # otherwise run the loop again
                if not update_screen():
                    game_setup()
               
    pg.display.update()
    CLOCK.tick(fps)
    


