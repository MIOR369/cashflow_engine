#pragma once
#include <string>
#include <ctime>

time_t to_time(const std::string& date);
std::string to_string_date(time_t t);
