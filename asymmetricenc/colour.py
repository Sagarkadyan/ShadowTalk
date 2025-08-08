from colorama import Fore, Back, Style

print("=== Foreground (Text) Colors ===")
print(Fore.BLACK   + "BLACK"   + Style.RESET_ALL)
print(Fore.RED     + "RED"     + Style.RESET_ALL)
print(Fore.GREEN   + "GREEN"   + Style.RESET_ALL)
print(Fore.YELLOW  + "YELLOW"  + Style.RESET_ALL)
print(Fore.BLUE    + "BLUE"    + Style.RESET_ALL)
print(Fore.MAGENTA + "MAGENTA" + Style.RESET_ALL)
print(Fore.CYAN    + "CYAN"    + Style.RESET_ALL)
print(Fore.WHITE   + "WHITE"   + Style.RESET_ALL)
print(Fore.RESET   + "RESET (default terminal color)" + Style.RESET_ALL)

print("\n=== Background Colors ===")
print(Back.BLACK   + "BLACK"   + Style.RESET_ALL)
print(Back.RED     + "RED"     + Style.RESET_ALL)
print(Back.GREEN   + "GREEN"   + Style.RESET_ALL)
print(Back.YELLOW  + "YELLOW"  + Style.RESET_ALL)
print(Back.BLUE    + "BLUE"    + Style.RESET_ALL)
print(Back.MAGENTA + "MAGENTA" + Style.RESET_ALL)
print(Back.CYAN    + "CYAN"    + Style.RESET_ALL)
print(Back.WHITE   + "WHITE"   + Style.RESET_ALL)
print(Back.RESET   + "RESET (default terminal background)" + Style.RESET_ALL)

print("\n=== Styles ===")
print(Style.DIM    + "DIM"    + Style.RESET_ALL)
print(Style.NORMAL + "NORMAL" + Style.RESET_ALL)
print(Style.BRIGHT + "BRIGHT" + Style.RESET_ALL)
print(Style.RESET_ALL + "RESET_ALL (Back to normal)")

print("\n=== Combined Example ===")
for fore in [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN, Fore.WHITE]:
    for style in [Style.NORMAL, Style.DIM, Style.BRIGHT]:
        print(f"{style}{fore}This is {fore}{style}text{Style.RESET_ALL}", end=" | ")
    print()