#include "algorithms.hpp"
#include <algorithm>

namespace {
    bool galloping_find(const std::vector<int>& v, size_t& pos, int target) {
        if (pos >= v.size()) return false;
        if (v[pos] == target) return true;
        if (v[pos] > target) return false;

        size_t step = 1;
        size_t lo = pos;
        size_t hi = pos + step;
        while (hi < v.size() && v[hi] < target) {
            lo = hi;
            step <<= 1;
            hi = pos + step;
        }
        if (hi > v.size()) hi = v.size();

        auto it = std::lower_bound(v.begin() + lo, v.begin() + hi, target);
        if (it != v.end() && *it == target) return true;
        pos = static_cast<size_t>(it - v.begin());
        return false;
    }
}

bool exponential_alg(const std::vector<int>& a, const std::vector<int>& b) {
    const auto& small = (a.size() <= b.size()) ? a : b;
    const auto& big   = (a.size() <= b.size()) ? b : a;
    size_t pos = 0;
    for (int x : small) {
        if (galloping_find(big, pos, x)) return true;
    }
    return false;
}