#include "algorithms.hpp"
#include <algorithm>
#include <chrono>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>

using Clock = std::chrono::steady_clock;
using Fn = bool(*)(const std::vector<int> &, const std::vector<int> &);

// Генератор "худшего случая" по рекомендации из задания:
// числа разной чётности, без общих элементов, элементы меньшего массива
// равномерно распределены по диапазону большего.
// Больший массив — подряд идущие нечётные 1, 3, 5, ..., 2*big-1.
// Меньший — чётные числа с шагом ~2*big/small, т.е. каждый его элемент
// "вклинивается" между соседними элементами большего по всей длине.
// Иначе (a = 0,2,4..., b = 1,3,5...) при M << N меньший массив
// заканчивается в самом начале большего и алгоритмы останавливаются рано.
static void gen_worst(int m, int n, std::vector<int> &a, std::vector<int> &b) {
    a.resize(m);
    b.resize(n);
    auto &small = (m <= n) ? a : b;
    auto &big = (m <= n) ? b : a;
    const long long s = static_cast<long long>(small.size());
    const long long g = static_cast<long long>(big.size());
    for (long long j = 0; j < g; ++j) big[j] = static_cast<int>(2 * j + 1);
    for (long long i = 0; i < s; ++i) small[i] = static_cast<int>(2 * (i * g / s));
}

// Функция замера времени.
// Прогрев, затем `runs` серий по `reps` вызовов; возвращаем медиану
// среднего времени одного вызова (мкс) — она устойчивее к выбросам.
static double measure(Fn f, const std::vector<int> &a, const std::vector<int> &b,
                      int reps, int runs) {
    volatile bool sink = f(a, b); // прогрев и защита от оптимизации

    std::vector<double> samples;
    samples.reserve(runs);
    for (int k = 0; k < runs; ++k) {
        auto t0 = Clock::now();
        for (int r = 0; r < reps; ++r) {
            sink = f(a, b);
        }
        auto t1 = Clock::now();
        samples.push_back(std::chrono::duration<double, std::micro>(t1 - t0).count() / reps);
    }
    (void) sink;

    std::nth_element(samples.begin(), samples.begin() + runs / 2, samples.end());
    return samples[runs / 2];
}

int main(int argc, char **argv) {
    // Путь к файлу с "сырыми данными" можно передать первым аргументом
    const std::string out_path = (argc > 1) ? argv[1] : "results.csv";

    struct Algo {
        std::string name;
        Fn fn;
    };

    std::vector<Algo> algos = {
        {"two_pointers", two_pointers},
        {"binary_search", binary_search_alg},
        {"exponential", exponential_alg},
        {"double_binary", double_binary_alg},
    };

    std::ofstream csv(out_path);
    if (!csv) {
        std::cerr << "Cannot open " << out_path << "\n";
        return 1;
    }
    csv << "algo,M,N,time_us\n";

    // Размеры массивов: степени двойки от 2^4 = 16 до 2^20 = 1 048 576
    std::vector<int> sizes;
    for (int s = 16; s <= (1 << 20); s *= 2) {
        sizes.push_back(s);
    }

    const int runs = 7;

    for (int M: sizes) {
        for (int N: sizes) {
            std::vector<int> a, b;
            gen_worst(M, N, a, b);

            int reps = std::max(1, static_cast<int>(2000000 / (M + N)));

            for (auto &algo: algos) {
                double t = measure(algo.fn, a, b, reps, runs);

                std::cout << algo.name << " M=" << M << " N=" << N
                        << " t=" << t << "us\n";

                csv << algo.name << "," << M << "," << N << "," << t << "\n";
            }
        }
    }

    std::cout << "Done. Results saved to " << out_path << "\n";
    return 0;
}
