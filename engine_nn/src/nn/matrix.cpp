#include "matrix.h"
#include <sstream>
#include <iomanip>
#include <iostream>


Matrix::Matrix(int rows, int cols)
    : rows(rows), cols(cols), data(rows * cols, 0.0) {}

Matrix::Matrix(int rows, int cols, std::vector<double> data)
    : rows(rows), cols(cols), data(std::move(data)) {
    if ((int)this->data.size() != rows * cols) {
        throw std::runtime_error("Matrix: data size mismatch");
    }
}



double& Matrix::at(int i, int j) {
    return data[i * cols + j];
}

const double& Matrix::at(int i, int j) const {
    return data[i * cols + j];
}

// --- Core math ---

// Matrix multiplication
//   For each output cell, sum products across the shared dimension.
Matrix Matrix::multiply(const Matrix& other) const {
    if (cols != other.rows) {
        throw std::runtime_error(
            "Matrix multiply shape mismatch: " +
            std::to_string(rows) + "x" + std::to_string(cols) +
            " × " + std::to_string(other.rows) + "x" + std::to_string(other.cols)
        );
    }

    Matrix result(rows, other.cols);

    for (int i = 0; i < rows; i++) {
        for (int j = 0; j < other.cols; j++) {
            double sum = 0.0;
            for (int k = 0; k < cols; k++) {
                sum += at(i, k) * other.at(k, j);
            }
            result.at(i, j) = sum;
        }
    }

    return result;
}

// Element-wise addition
// Both matrices must be the same shape.
Matrix Matrix::add(const Matrix& other) const {
    if (!same_shape(other)) {
        throw std::runtime_error("Matrix add shape mismatch");
    }

    Matrix result(rows, cols);
    for (int i = 0; i < rows * cols; i++) {
        result.data[i] = data[i] + other.data[i];
    }
    return result;
}

Matrix Matrix::subtract(const Matrix& other) const {
    if (!same_shape(other)) {
        throw std::runtime_error("Matrix subtract shape mismatch");
    }

    Matrix result(rows, cols);
    for (int i = 0; i < rows * cols; i++) {
        result.data[i] = data[i] - other.data[i];
    }
    return result;
}

// Hadamard product — element-wise multiply
Matrix Matrix::hadamard(const Matrix& other) const {
    if (!same_shape(other)) {
        throw std::runtime_error("Matrix hadamard shape mismatch");
    }

    Matrix result(rows, cols);
    for (int i = 0; i < rows * cols; i++) {
        result.data[i] = data[i] * other.data[i];
    }
    return result;
}

// Transpose — flip rows and cols
// Used in backprop to route gradients backwards through layers.
Matrix Matrix::transpose() const {
    Matrix result(cols, rows);
    for (int i = 0; i < rows; i++) {
        for (int j = 0; j < cols; j++) {
            result.at(j, i) = at(i, j);
        }
    }
    return result;
}

// Apply a function to every element
// This is how we apply activation functions.
Matrix Matrix::apply(std::function<double(double)> fn) const {
    Matrix result(rows, cols);
    for (int i = 0; i < rows * cols; i++) {
        result.data[i] = fn(data[i]);
    }
    return result;
}

Matrix Matrix::scale(double scalar) const {
    Matrix result(rows, cols);
    for (int i = 0; i < rows * cols; i++) {
        result.data[i] = data[i] * scalar;
    }
    return result;
}


// He initialization — values from normal distribution
// scaled by sqrt(2/n) where n is number of inputs.
// This keeps signal from exploding or vanishing as it
// passes through many layers. 
void Matrix::randomize(double mean, double stddev) {
    std::random_device rd;
    std::mt19937 gen(rd());
    std::normal_distribution<double> dist(mean, stddev);
    for (auto& val : data) {
        val = dist(gen);
    }
}

void Matrix::fill(double value) {
    std::fill(data.begin(), data.end(), value);
}

bool Matrix::same_shape(const Matrix& other) const {
    return rows == other.rows && cols == other.cols;
}

std::string Matrix::to_string() const {
    std::ostringstream ss;
    ss << std::fixed << std::setprecision(4);
    ss << "[" << rows << "x" << cols << "]\n";
    for (int i = 0; i < rows; i++) {
        ss << "  [";
        for (int j = 0; j < cols; j++) {
            ss << std::setw(8) << at(i, j);
            if (j < cols - 1) ss << ", ";
        }
        ss << "]\n";
    }
    return ss.str();
}
