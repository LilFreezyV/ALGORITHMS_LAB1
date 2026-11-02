import csv
import math
import os
import sys
from collections import defaultdict

ALGOS = ["two_pointers", "binary_search", "exponential", "double_binary"]
COLORS = {"two_pointers": "#1f77b4", "binary_search": "#ff7f0e",
          "exponential": "#2ca02c", "double_binary": "#d62728"}
MARKERS = {"two_pointers": "circle", "binary_search": "square",
           "exponential": "triangle", "double_binary": "diamond"}

W, H = 900, 560
ML, MR, MT, MB = 90, 190, 50, 70  # поля: слева, справа (легенда), сверху, снизу
FONT = 'font-family="Arial, sans-serif"'


def load(path):
    # data[algo][(M, N)] = time_us
    data = defaultdict(dict)
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            data[row["algo"]][(int(row["M"]), int(row["N"]))] = float(row["time_us"])
    return data


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def pow_label(base, e):
    return f"{base}<tspan dy='-7' font-size='10'>{e}</tspan>"


def marker(kind, x, y, color):
    r = 4.5
    if kind == "circle":
        return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{color}"/>'
    if kind == "square":
        return f'<rect x="{x - r:.1f}" y="{y - r:.1f}" width="{2 * r}" height="{2 * r}" fill="{color}"/>'
    if kind == "triangle":
        return (f'<polygon points="{x:.1f},{y - r - 1:.1f} {x - r - 1:.1f},{y + r:.1f} '
                f'{x + r + 1:.1f},{y + r:.1f}" fill="{color}"/>')
    return (f'<polygon points="{x:.1f},{y - r - 1:.1f} {x + r + 1:.1f},{y:.1f} '
            f'{x:.1f},{y + r + 1:.1f} {x - r - 1:.1f},{y:.1f}" fill="{color}"/>')


def line_chart(series, xlabel, title, out):
    xs = [x for pts in series.values() for x, _ in pts]
    ys = [y for pts in series.values() for _, y in pts if y > 0]
    x0, x1 = math.log2(min(xs)), math.log2(max(xs))
    y0, y1 = math.floor(math.log10(min(ys))), math.ceil(math.log10(max(ys)))
    if x0 == x1:
        x1 = x0 + 1
    pw, ph = W - ML - MR, H - MT - MB

    def px(x):
        return ML + (math.log2(x) - x0) / (x1 - x0) * pw

    def py(y):
        return MT + ph - (math.log10(y) - y0) / (y1 - y0) * ph

    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<rect width="{W}" height="{H}" fill="white"/>',
         f'<text x="{ML + pw / 2}" y="28" text-anchor="middle" font-size="17" {FONT}>{esc(title)}</text>']

    # Сетка и подписи по Y: декады + промежуточные 2..9
    for e in range(y0, y1 + 1):
        y = py(10 ** e)
        o.append(f'<line x1="{ML}" y1="{y:.1f}" x2="{ML + pw}" y2="{y:.1f}" stroke="#bbb" stroke-dasharray="4,3"/>')
        o.append(f'<text x="{ML - 8}" y="{y + 4:.1f}" text-anchor="end" font-size="12" {FONT}>{pow_label(10, e)}</text>')
        if e < y1:
            for k in range(2, 10):
                yk = py(k * 10 ** e)
                o.append(f'<line x1="{ML}" y1="{yk:.1f}" x2="{ML + pw}" y2="{yk:.1f}" stroke="#eee"/>')
    # Сетка и подписи по X: степени двойки
    step = 1 if x1 - x0 <= 12 else 2
    for e in range(int(x0), int(x1) + 1):
        x = px(2 ** e)
        o.append(f'<line x1="{x:.1f}" y1="{MT}" x2="{x:.1f}" y2="{MT + ph}" stroke="#ddd" stroke-dasharray="4,3"/>')
        if (e - int(x0)) % step == 0:
            o.append(f'<text x="{x:.1f}" y="{MT + ph + 20}" text-anchor="middle" font-size="12" {FONT}>{pow_label(2, e)}</text>')
    o.append(f'<rect x="{ML}" y="{MT}" width="{pw}" height="{ph}" fill="none" stroke="#333"/>')
    o.append(f'<text x="{ML + pw / 2}" y="{H - 22}" text-anchor="middle" font-size="14" {FONT}>{esc(xlabel)}</text>')
    o.append(f'<text transform="translate(24,{MT + ph / 2}) rotate(-90)" text-anchor="middle" font-size="14" {FONT}>'
             f'Время одного вызова, мкс (лог. шкала)</text>')

    for algo in ALGOS:
        pts = sorted(series[algo])
        c = COLORS[algo]
        path = " ".join(f"{px(x):.1f},{py(y):.1f}" for x, y in pts)
        o.append(f'<polyline points="{path}" fill="none" stroke="{c}" stroke-width="2.2"/>')
        o.extend(marker(MARKERS[algo], px(x), py(y), c) for x, y in pts)

    # Легенда
    lx, ly = ML + pw + 20, MT + 10
    for i, algo in enumerate(ALGOS):
        y = ly + i * 26
        o.append(f'<line x1="{lx}" y1="{y}" x2="{lx + 30}" y2="{y}" stroke="{COLORS[algo]}" stroke-width="2.2"/>')
        o.append(marker(MARKERS[algo], lx + 15, y, COLORS[algo]))
        o.append(f'<text x="{lx + 38}" y="{y + 4}" font-size="13" {FONT}>{algo}</text>')

    o.append("</svg>")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(o))


def winner_map(data, sizes, out):
    n = len(sizes)
    cell = 38
    ml, mt = 80, 60
    w = ml + n * cell + 200
    h = mt + n * cell + 90
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
         f'<rect width="{w}" height="{h}" fill="white"/>',
         f'<text x="{ml + n * cell / 2}" y="30" text-anchor="middle" font-size="17" {FONT}>'
         f'Самый быстрый алгоритм для каждой пары (M, N)</text>']
    for i, m in enumerate(sizes):          # строки: M снизу вверх
        y = mt + (n - 1 - i) * cell
        for j, nn in enumerate(sizes):
            t = {a: data[a][(m, nn)] for a in ALGOS}
            best = sorted(t, key=t.get)
            x = ml + j * cell
            o.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" fill="{COLORS[best[0]]}" stroke="white"/>')
            o.append(f'<text x="{x + cell / 2}" y="{y + cell / 2 + 4}" text-anchor="middle" font-size="10" '
                     f'fill="white" {FONT}>{t[best[1]] / t[best[0]]:.1f}</text>')
        o.append(f'<text x="{ml - 8}" y="{y + cell / 2 + 4}" text-anchor="end" font-size="12" {FONT}>'
                 f'{pow_label(2, m.bit_length() - 1)}</text>')
    for j, nn in enumerate(sizes):
        o.append(f'<text x="{ml + j * cell + cell / 2}" y="{mt + n * cell + 20}" text-anchor="middle" font-size="12" {FONT}>'
                 f'{pow_label(2, nn.bit_length() - 1)}</text>')
    o.append(f'<text x="{ml + n * cell / 2}" y="{mt + n * cell + 45}" text-anchor="middle" font-size="14" {FONT}>N</text>')
    o.append(f'<text x="24" y="{mt + n * cell / 2}" font-size="14" {FONT}>M</text>')
    o.append(f'<text x="{ml + n * cell / 2}" y="{mt + n * cell + 72}" text-anchor="middle" font-size="12" fill="#555" {FONT}>'
             f'число в клетке — во сколько раз победитель быстрее второго места</text>')
    lx = ml + n * cell + 20
    for i, algo in enumerate(ALGOS):
        y = mt + 10 + i * 28
        o.append(f'<rect x="{lx}" y="{y}" width="18" height="18" fill="{COLORS[algo]}"/>')
        o.append(f'<text x="{lx + 26}" y="{y + 14}" font-size="13" {FONT}>{algo}</text>')
    o.append("</svg>")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(o))


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join("results", "results.csv")
    out_dir = sys.argv[2] if len(sys.argv) > 2 else "plots"
    if not os.path.exists(src):
        print(f"Ошибка: файл {src} не найден. Сначала запустите бенчмарк.")
        return 1
    os.makedirs(out_dir, exist_ok=True)

    data = load(src)
    sizes = sorted({m for m, _ in data[ALGOS[0]]})

    def series(keys, xs):
        return {a: [(x, data[a][k]) for k, x in zip(keys, xs)] for a in ALGOS}

    # 1. M = N: рост времени при одинаковых размерах
    line_chart(series([(s, s) for s in sizes], sizes), "M = N (лог. шкала)",
               "Массивы одинакового размера (M = N)", os.path.join(out_dir, "equal_sizes.svg"))

    # 2. Фиксируем M (меньший массив), растим N
    for m in (sizes[0], sizes[len(sizes) // 2], sizes[-1]):
        line_chart(series([(m, n) for n in sizes], sizes), "N (лог. шкала)",
                   f"Зависимость от N при фиксированном M = {m}",
                   os.path.join(out_dir, f"fixed_M_{m}.svg"))

    # 3. Больший массив максимального размера, меняем соотношение N / M
    big = sizes[-1]
    pairs = [(m, big) for m in sizes]
    line_chart(series(pairs, [big // m for m in sizes]), "N / M (лог. шкала)",
               f"Зависимость от соотношения размеров при N = 2^{big.bit_length() - 1}",
               os.path.join(out_dir, "ratio.svg"))

    # 4. Карта победителей
    winner_map(data, sizes, os.path.join(out_dir, "winner_map.svg"))

    print(f"Графики сохранены в {out_dir}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
