#include "date_utils.h"
#include <cstdio>

// string → time_t
time_t to_time(const std::string& date) {
    std::tm tm = {};
    sscanf(date.c_str(), "%d-%d-%d",
           &tm.tm_year, &tm.tm_mon, &tm.tm_mday);
    tm.tm_year -= 1900;
    tm.tm_mon -= 1;
    return mktime(&tm);
}

// time_t → string
std::string to_string_date(time_t t) {
    std::tm *tm = localtime(&t);
    char buffer[11];
    snprintf(buffer, sizeof(buffer), "%04d-%02d-%02d",
             tm->tm_year + 1900,
             tm->tm_mon + 1,
             tm->tm_mday);
    return std::string(buffer);
}
