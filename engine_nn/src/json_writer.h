#pragma once
#include <string>
#include <vector>
#include <sstream>
#include <iomanip>

// Minimal JSON writer — no external dependencies.
// Builds JSON strings for output to Python.

class JsonWriter {
public:
    // Escape a string for JSON output
    static std::string escape(const std::string& s) {
        std::ostringstream ss;
        for (char c : s) {
            if (c == '"')  ss << "\\\"";
            else if (c == '\\') ss << "\\\\";
            else if (c == '\n') ss << "\\n";
            else if (c == '\r') ss << "\\r";
            else if (c == '\t') ss << "\\t";
            else ss << c;
        }
        return ss.str();
    }

    static std::string number(double val, int precision = 6) {
        std::ostringstream ss;
        ss << std::fixed << std::setprecision(precision) << val;
        return ss.str();
    }

    static std::string boolean(bool val) {
        return val ? "true" : "false";
    }
};