CXX = g++
CXXFLAGS = -std=c++17 -O2 -Wall

CASHFLOW_SRC = cashflow.cpp
CASHFLOW_BIN = cashflow

ENGINE_SRC = \
	main.cpp \
	parser.cpp \
	risk_engine.cpp \
	execution_engine.cpp \
	simulator.cpp \
	simulator_prob.cpp \
	optimizer_engine.cpp \
	structure_engine.cpp \
	final_engine.cpp \
	multi_cause_engine.cpp \
	impact_engine.cpp \
	margin.cpp \
	advice_engine.cpp \
	decision_engine.cpp \
	scenario_engine.cpp \
	delay_engine.cpp \
	date_utils.cpp \
	delay_utils.cpp

ENGINE_BIN = engine

all: $(CASHFLOW_BIN) $(ENGINE_BIN)

$(CASHFLOW_BIN): $(CASHFLOW_SRC)
	$(CXX) $(CXXFLAGS) -o $@ $^

$(ENGINE_BIN): $(ENGINE_SRC)
	$(CXX) $(CXXFLAGS) -o $@ $^

clean:
	rm -f $(CASHFLOW_BIN) $(ENGINE_BIN)
