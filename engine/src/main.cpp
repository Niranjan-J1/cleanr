#include <iostream>
#include <string>

int main(int argc, char* argv[]) {
    if (argc < 3) {
        std::cerr << "Usage: cleanr-engine <input.csv> <output.csv> [--fix]\n";
        return 1;
    }

    std::string input  = argv[1];
    std::string output = argv[2];

    std::cout << "{\n";
    std::cout << "  \"status\": \"stub\",\n";
    std::cout << "  \"input\": \"" << input << "\",\n";
    std::cout << "  \"rows_analyzed\": 0,\n";
    std::cout << "  \"issues\": []\n";
    std::cout << "}\n";

    return 0;

}