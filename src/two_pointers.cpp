#include "algorithms.hpp"

using namespace std;

bool two_pointers(const vector<int> &a, const vector<int> &b) {
    int m = a.size();
    int n = b.size();
    int p1 = 0, p2 = 0;
    while (p1 < m && p2 < n) {
        if (a[p1] == b[p2]) {
            return true;
        }
        if (a[p1] < b[p2]) {
            p1++;
        } else {
            p2++;
        }
    }
    return false;
}
