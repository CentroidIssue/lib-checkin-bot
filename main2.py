from datetime import datetime, timezone, timedelta

# Thiết lập múi giờ Singapore với UTC+8
singapore_tz = timezone(timedelta(hours=8))

# Lấy thời gian hiện tại ở Singapore
singapore_time = datetime.now(singapore_tz)

# In thời gian ở Singapore để kiểm tra
print("Thời gian hiện tại ở Singapore:", singapore_time)

# Lấy timestamp từ thời gian Singapore
timestamp = singapore_time.timestamp()
print("Timestamp hiện tại ở Singapore:", timestamp)

# Lấy timestamp từ thời gian Singapore
timestamp = singapore_time.timestamp()
dt = datetime.fromtimestamp(timestamp)
formatted_time = dt.strftime("%H:%M:%S, %d-%m-%Y")
print("Giờ phút ngày tháng năm:", formatted_time)