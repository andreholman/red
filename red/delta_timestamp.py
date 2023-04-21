import datetime
def delta_timestamp(created):
    seconds = int(datetime.datetime.now().timestamp() - created)
    periods = [
        ('y', 31536000), # year
        ('mo', 2628000),  # month
        ('d', 86400),    # day
        ('h', 3600),     # hour
        ('m', 60),       # minute
        ('s', 1)         # second
    ]
    parts = []
    parts_appended = 0
    previous_index = 67

    for period_name, period_seconds in periods:
        if seconds >= period_seconds:
            if periods.index((period_name, period_seconds)) - previous_index >= 2:
                break
            previous_index = periods.index((period_name, period_seconds))
            
            period_value, seconds = divmod(seconds, period_seconds)
            parts.append('{}{}'.format(period_value, period_name))
            
            parts_appended += 1
            if parts_appended >= 2:
                break # stops after listing two date types
    return ' '.join(parts) if len(parts) > 0 else '0s'

while True:
    amount = input("> ")
    print(delta_timestamp(int(amount)))