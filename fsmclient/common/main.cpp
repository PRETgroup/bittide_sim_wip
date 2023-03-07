//
#include <asio.hpp>
#include <iostream>
#include <chart.hpp>
#include <sstream>

using asio::ip::tcp;

std::vector<std::string> splitString(std::string str, char splitter){
    std::vector<std::string> result;
    std::string current = ""; 
    for(int i = 0; i < str.size(); i++){
        if(str[i] == splitter){
            if(current != ""){
                result.push_back(current);
                current = "";
            } 
            continue;
        }
        current += str[i];
    }
    if(current.size() != 0)
        result.push_back(current);
    return result;
}

void removeSubstrs(std::string& s, std::string p) { 
  std::string::size_type n = p.length();
  for (std::string::size_type i = s.find(p);
      i != std::string::npos;
      i = s.find(p))
      s.erase(i, n);
}

std::vector<std::string> resolveSignalsFromString(std::string ss) {
    removeSubstrs(ss,"[");
    removeSubstrs(ss,"'");
    removeSubstrs(ss,",");
    removeSubstrs(ss,"]");
    std::vector<std::string> all_tokens = splitString(ss,' ');
    return all_tokens;
}

std::string formatOutputSignals(std::vector<std::string> sigs) {
    std::string output = "[";

    for (std::string sig : sigs) {
        if(output != "[") {
            output += ", ";
        }
        output += "'";
        output += sig;
        output += "'";
    }

    output += "]";
    return output;
}

int main(int argc, char **argv)
{
    //arg1 : ip
    //arg2 : port
    //arg3 : node name
    //start a tcp client
    if (argc < 4) {
        std::cout << "Usage: ./fsmclient <ip> <port> <node name>" << std::endl;
        return 1;
    }

    asio::io_context io_context;
    tcp::socket s(io_context);
    tcp::resolver resolver(io_context);
    std::cout << "Attempting to connect to " << argv[1] << ":" << argv[2] << std::endl;
    tcp::resolver::query query(argv[1], argv[2]);
    asio::connect(s,resolver.resolve(query));
    std::cout << "Identifying to server as " << argv[3] << std::endl;
    std::string name = std::string(argv[3]) + "\n";
    asio::write(s, asio::buffer(name));

    TickData current_state;
    reset(&current_state);
    int tick_count = 0;
    while(true){ //run scchart
        //can't genericise interface variables unless we changed SCChart i/o to be map based
        //actually, we'll just hand-modify the code to reflect strings for now. can automate later

        //await a tick signal from the server
        asio::streambuf b;
        asio::read_until(s,b,"\n");
        //resolve the inbound signals
        std::istream is(&b);
        std::string inputSignalString;
        is >> inputSignalString;
        //tokenize
        std::vector<std::string> all_tokens = resolveSignalsFromString(inputSignalString);
        
        for(auto& token : all_tokens) {
            char* targetted_signal = inputsFromStr(&current_state.iface, token);
            if (targetted_signal == 0) {
                std::cout << "Signal " << token << " not found" << std::endl;
            }
            else (*targetted_signal) = 1;
        }
        //modify the current_state
        //run_tick
        tick(&current_state);
        //send back the resultant outputs
        std::vector<std::string> all_outputs = getPresentOutputs(&current_state.iface);
        std::string formatted_msg = formatOutputSignals(all_outputs) + "\n";
        asio::write(s, asio::buffer(formatted_msg));
        //print trace
        std::cout << "Tick " << tick_count << ", Inputs: " << inputSignalString << ", Outputs: " << formatted_msg << std::endl;
        tick_count++;
    }
}