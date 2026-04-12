#!/usr/bin/env bash

echo "=== BUILD START ==="

g++ main.cpp \
parser.cpp \
simulator.cpp \
simulator_prob.cpp \
delay_engine.cpp \
multi_cause_engine.cpp \
impact_engine.cpp \
date_utils.cpp \
delay_utils.cpp \
risk_engine.cpp \
decision_engine.cpp \
advice_engine.cpp \
scenario_engine.cpp \
optimizer_engine.cpp \
structure_engine.cpp \
execution_engine.cpp \
margin.cpp \
final_engine.cpp \
-O3 -std=c++17 -o cashflow

chmod +x cashflow

echo "=== BUILD DONE ==="
ls -la
