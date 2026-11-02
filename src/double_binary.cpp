#include "algorithms.hpp"
#include <algorithm>

namespace {
    bool recursive_intersect(const std::vector<int>& a, size_t alo, size_t ahi,
                             const std::vector<int>& b, size_t blo, size_t bhi) {
        if (alo >= ahi || blo >= bhi) return false;

        size_t amid = alo + (ahi - alo) / 2;
        int pivot = a[amid];

        auto it = std::lower_bound(b.begin() + blo, b.begin() + bhi, pivot);
        size_t bpos = static_cast<size_t>(it - b.begin());

        if (bpos < bhi && b[bpos] == pivot) return true;

        return recursive_intersect(a, alo, amid, b, blo, bpos) ||
               recursive_intersect(a, amid + 1, ahi, b, bpos, bhi);
    }
}

bool double_binary_alg(const std::vector<int>& a, const std::vector<int>& b) {
    const auto& small = (a.size() <= b.size()) ? a : b;
    const auto& big   = (a.size() <= b.size()) ? b : a;
    return recursive_intersect(small, 0, small.size(), big, 0, big.size());
}