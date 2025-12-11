from pynput import keyboard
i=0
#can be user as keylogger
def on_press(key):
    global i
    try:
        # print('alphanumeric key {0} pressed'.format(key.char))
        b=key.char
        if b=="/":
            print("hiii")
            i+=1
            
            if i>1:
                print("si")
                i=0
            else:
                print("io")
                
        else:
            print("hh")            


    except AttributeError:
        print('special key {0} pressed'.format(
            key))

def on_release(key):
    print('{0} released'.format(
        key))
    if key == keyboard.Key.esc:
        # Stop listener
        return False
def on_activate_h():
    print("hihi")
# Collect events until released
with keyboard.Listener(
        on_press=on_press,
        on_release=on_release
        ) as listener:
    listener.join()
