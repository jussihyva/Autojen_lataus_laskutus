from datetime import timedelta
import pandas as pd

def print_dst(date_time) -> bool:
#     date_time = pd.to_datetime(date_time, utc=True).tz_convert('Europe/Helsinki')
    date_time = pd.to_datetime(date_time, utc=True)
    if type(date_time) not in [type(pd.NaT), type(None)]:
    #     print(date_time.dst())
        offset_current = date_time.utcoffset()
    #     print("{} {}".format(date_time, offset_current))
        date_time -= timedelta(hours=1)
        offset_utc = date_time.utcoffset()
        if offset_utc == offset_current:
            date_time += timedelta(hours=1)
            offset_utc = date_time.utcoffset()
            date_time -= offset_utc
            offset_utc = date_time.utcoffset()
            if offset_utc > offset_current:
                date_time -= timedelta(hours=1)
                offset_utc = date_time.utcoffset()
    #             print("{} {} {}".format(date_time, offset_utc, "=0"))
            elif offset_utc < offset_current:
                date_time += timedelta(hours=1)
                offset_utc = date_time.utcoffset()
                if offset_utc == offset_current:
                    date_time -= timedelta(hours=1)
                    offset_utc = date_time.utcoffset()
    #                 print("{} {} {}".format(date_time, offset_utc, "=1"))
    #             else:
    #                 print("{} {} {}".format(date_time, offset_utc, "=2"))
    #         else:
    #             print("{} {} {}".format(date_time, offset_utc, 2))
        elif offset_utc > offset_current:
            date_time += timedelta(hours=1) - offset_utc
            offset_utc = date_time.utcoffset()
            if offset_utc == offset_current:
                date_time -= timedelta(hours=1)
    #             print("{} {} {}".format(date_time, offset_utc, 3))
    #         else:
    #             print("{} {} {}".format(date_time, offset_utc, 4))
        elif offset_utc < offset_current:
            date_time += timedelta(hours=1) - offset_utc
            offset_utc = date_time.utcoffset()
            if offset_utc == offset_current:
                date_time -= timedelta(hours=1)
    #             print("{} {} {}".format(date_time, offset_utc, 5))
    #         else:
    #             print("{} {} {}".format(date_time, offset_utc, 6))
    return date_time
