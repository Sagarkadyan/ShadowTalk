import time
named_tuple = time.localtime()
formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", named_tuple)
print(formatted_time)