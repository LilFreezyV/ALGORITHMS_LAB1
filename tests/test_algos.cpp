#include <gtest/gtest.h>
#include "algorithms.hpp"
#include <algorithm>
#include <iterator>
#include <random>
#include <vector>

using Fn = bool(*)(const std::vector<int>&, const std::vector<int>&);

static std::vector<Fn> all() {
    return {two_pointers, binary_search_alg, exponential_alg, double_binary_alg};
}

TEST(Algos, EdgeCases) {
    struct Case { std::vector<int> a, b; bool expected; };
    std::vector<Case> cases = {
        {{}, {}, false},
        {{}, {1,2,3}, false},
        {{1,2,3}, {}, false},
        {{1}, {1}, true},
        {{1}, {2}, false},
        {{1,2,3}, {3,4,5}, true},
        {{2,4,6}, {3,5,7}, false},
        {{1,1,1}, {1,1,1}, true},
        {{-5,-3,-1}, {-4,-2,0}, false},
        {{-5,-3,-1}, {-3,-2,0}, true},
        {{1,2,3,4,5}, {1}, true},
        {{1,2,3,4,5}, {5}, true},
        {{1,2,3,4,5}, {0}, false},
        {{1,2,3,4,5}, {6}, false},
    };
    for (auto fn : all()) {
        for (auto& c : cases) {
            EXPECT_EQ(fn(c.a, c.b), c.expected) 
                << "sizes " << c.a.size() << "x" << c.b.size();
        }
    }
}

TEST(Algos, DifferentialRandom) {
    std::mt19937 rng(12345);
    for (int iter = 0; iter < 500; ++iter) {
        int m = rng() % 200, n = rng() % 200;
        std::vector<int> a(m), b(n);
        for (auto& x : a) x = static_cast<int>(rng() % 1000) - 500;
        for (auto& x : b) x = static_cast<int>(rng() % 1000) - 500;
        std::sort(a.begin(), a.end());
        std::sort(b.begin(), b.end());

        std::vector<int> inter;
        std::set_intersection(a.begin(), a.end(), b.begin(), b.end(),
                              std::back_inserter(inter));
        bool expected = !inter.empty();

        for (auto fn : all()) {
            EXPECT_EQ(fn(a, b), expected) 
                << "iter " << iter << " sizes " << m << "x" << n;
        }
    }
}

// Сильно различающиеся размеры (путь галопа/деления) и единственный
// общий элемент в разных местах большего массива.
TEST(Algos, SkewedSingleCommon) {
    for (int m : {1, 3, 17, 100}) {
        for (int n : {1000, 4096, 100000}) {
            std::vector<int> big(n), small(m);
            for (int j = 0; j < n; ++j) big[j] = 2 * j + 1;
            for (int i = 0; i < m; ++i) small[i] = static_cast<int>(2 * (1LL * i * n / m));

            for (auto fn : all()) {
                EXPECT_FALSE(fn(small, big)) << m << "x" << n;
                EXPECT_FALSE(fn(big, small)) << n << "x" << m;
            }

            for (int pos : {0, n / 3, n / 2, n - 1}) {
                auto s = small;
                // Заменяем ближайший к pos элемент меньшего массива на big[pos],
                // сохраняя сортировку
                auto it = std::lower_bound(s.begin(), s.end(), big[pos]);
                if (it == s.end()) --it;
                *it = big[pos];
                std::sort(s.begin(), s.end());
                for (auto fn : all()) {
                    EXPECT_TRUE(fn(s, big)) << m << "x" << n << " pos " << pos;
                    EXPECT_TRUE(fn(big, s)) << n << "x" << m << " pos " << pos;
                }
            }
        }
    }
}

TEST(Algos, Symmetric) {
    std::vector<int> a = {1,3,5,7,9};
    std::vector<int> b = {2,4,6,8,10};
    for (auto fn : all()) {
        EXPECT_EQ(fn(a, b), fn(b, a));
    }
}