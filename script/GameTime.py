import core.CacheContorl as cache
import core.GameConfig as gameconfig
import core.TextLoading as textload

# 时间初始化
def initTime():
    cache.gameTime['year'] = int(gameconfig.year)
    cache.gameTime['month'] = int(gameconfig.month)
    cache.gameTime['day'] = int(gameconfig.day)
    cache.gameTime['hour'] = int(gameconfig.hour)
    cache.gameTime['minute'] = int(gameconfig.minute)
    setSubMinute(0)
    pass

# 获取时间信息文本
def getDateText(gameTimeData = None):
    if gameTimeData == None:
        gameTimeData = cache.gameTime
    else:
        pass
    dateText = textload.getTextData(textload.stageWordId,'65')
    gameYear = str(gameTimeData['year'])
    gameMonth = str(gameTimeData['month'])
    gameDay = str(gameTimeData['day'])
    gameHour = str(gameTimeData['hour'])
    gameMinute = str(gameTimeData['minute'])
    gameYearText = gameYear + textload.getTextData(textload.stageWordId,'59')
    gameMonthText = gameMonth + textload.getTextData(textload.stageWordId,'60')
    gameDayText = gameDay + textload.getTextData(textload.stageWordId,'61')
    gameHourText = gameHour + textload.getTextData(textload.stageWordId,'62')
    gameMinuteText = gameMinute + textload.getTextData(textload.stageWordId,'63')
    dateText = dateText + gameYearText + gameMonthText + gameDayText + gameHourText + gameMinuteText
    return dateText

# 获取星期文本
def getWeekDayText():
    weekDay = getWeekDate()
    weekDateData = textload.getTextData(textload.messageId,'19')
    return weekDateData[weekDay]

# 增加分钟
def setSubMinute(subMinute):
    cacheMinute = cache.gameTime['minute']
    cacheMinute = int(cacheMinute) + int(subMinute)
    if cacheMinute >= 60:
        subHour = cacheMinute // 60
        cacheMinute = cacheMinute % 60
        cache.gameTime['minute'] = cacheMinute
        setSubHour(subHour)
    else:
        cache.gameTime['minute'] = cacheMinute

# 增加小时
def setSubHour(subHour):
    cacheHour = cache.gameTime['hour']
    cacheHour = int(cacheHour) + int(subHour)
    if cacheHour >= 24:
        subDay = cacheHour // 24
        cacheHour = cacheHour % 24
        cache.gameTime['hour'] = cacheHour
        setSubDay(subDay)
    else:
        cache.gameTime['hour'] = cacheHour

# 增加天数
def setSubDay(subDay):
    cacheDay = cache.gameTime['day']
    cacheMonth = cache.gameTime['month']
    cacheMonth = int(cacheMonth)
    cacheDay = int(cacheDay) + int(subDay)
    if cacheMonth == 1 or 3 or 5 or 7 or 8 or 10 or 12:
        if cacheDay >= 31:
            if cacheDay // 31 > 0:
                setSubMonth("1")
                cache.gameTime['day'] = cacheDay - 31
                setSubDay("0")
            else:
                setSubMonth("1")
                cache.gameTime['day'] = cacheDay
        else:
            cache.gameTime['day'] = cacheDay
    elif cacheMonth == 4 or 6 or 9 or 11:
        if cacheDay >= 30:
            if cacheDay // 30 > 0:
                setSubMonth("1")
                cache.gameTime['day'] = cacheDay - 30
                setSubDay("0")
            else:
                setSubMonth("1")
                cache.gameTime['day'] = cacheDay
        else:
            cache.gameTime['day'] = cacheDay
    elif cacheMonth == 2:
        leapYear = judgeLeapYear()
        if leapYear == "1":
            if cacheDay > 29:
                if cacheDay // 29 > 0:
                    setSubMonth("1")
                    cache.gameTime['day'] = cacheDay - 29
                    setSubDay("0")
                else:
                    setSubMonth("1")
                    cache.gameTime['day'] = cacheDay - 29
            else:
                cache.gameTime['day'] = cacheDay
        else:
            if cacheDay > 28:
                if cacheDay // 28 > 0:
                    setSubMonth("1")
                    cache.gameTime['day'] = cacheDay - 28
                    setSubDay("0")
                else:
                    setSubMonth("1")
                    cache.gameTime['day'] = cacheDay - 28
            else:
                cache.gameTime['day'] = cacheDay

#增加月数
def setSubMonth(subMonth):
    cacheMonth = cache.gameTime['month']
    cacheMonth = int(cacheMonth) + int(subMonth)
    if cacheMonth > 12:
        subYear = cacheMonth // 12
        cacheMonth = cacheMonth % 12
        cache.gameTime['month'] = cacheMonth
        setSubYear(subYear)
    else:
        cache.gameTime['month'] = cacheMonth

# 增加年数
def setSubYear(subMonth):
    cacheYear = cache.gameTime['year']
    cacheYear = int(cacheYear) + int(subMonth)
    cache.gameTime['year'] = cacheYear

# 计算星期
def getWeekDate():
    gameTime = cache.gameTime
    cacheYear = int(gameTime['year'])
    cacheYear = cacheYear - int(cacheYear / 100) * 100
    cacheCentury = int(cacheYear/100)
    cacheMonth = int(gameTime['month'])
    if cacheMonth == 1 or cacheMonth == 2:
        cacheMonth = cacheMonth + 12
        if cacheYear == 0:
            cacheYear = 99
            cacheCentury = cacheCentury - 1
        else:
            cacheYear = cacheYear - 1
    cacheDay =int(gameTime['day'])
    week = cacheYear + int(cacheYear/4) + int(cacheCentury/4) - 2 * cacheCentury + int(26 * (cacheMonth + 1)/10) + cacheDay - 1
    if week < 0:
        weekDay = (week % 7 + 7) % 7
    else:
        weekDay = week % 7
    return weekDay

# 判断当前是否是润年
def judgeLeapYear():
    cacheYear = int(cache.gameTime['year'])
    if cacheYear % 3200 == 0:
        if cacheYear % 172800 == 0:
            return "1"
        else:
            return "0"
    else:
        if cacheYear % 4 == 0 and cacheYear % 100 != 0:
            return "1"
        elif cacheYear % 100 == 0 and cacheYear % 400 == 0:
            return "1"
        else:
            return "0"
    pass