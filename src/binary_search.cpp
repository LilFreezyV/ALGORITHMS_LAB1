#include "algorithms.hpp"
#include <algorithm>

bool binary_search_alg(const std::vector<int>& a, const std::vector<int>& b) {
    const auto& small = (a.size() <= b.size()) ? a : b;
    const auto& big   = (a.size() <= b.size()) ? b : a;
    for (int x : small) {
        if (std::binary_search(big.begin(), big.end(), x)) return true;
    }
    return false;
}