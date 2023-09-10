import numpy as np
import mip

def generate(n):
    b = np.round(np.random.random(size=(n, 1)), 1)
    a = np.round(np.random.random(size=(n, 1)), 1)

    ask = np.minimum(a, b)
    bid = np.maximum(a, b)
    ask_q = np.random.randint(0, 5, size=(n, 1))
    bid_q = np.random.randint(0, 5, size=(n, 1))

    prices = np.concatenate([bid, bid_q, ask, ask_q], axis=1)

    cost = np.random.random(size=(n, n))
    cost = np.zeros(shape=(n, n))
    p = np.random.random(size=(n, n))
    p = np.zeros(shape=(n, n))

    return prices, cost, p

def solve_greedy(prices, cost, p):
    n = prices.shape[0]
    priority = []
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            # i buys, j sells
            priority.append((i, j, (1-p[i, j])*((prices[i][0] - prices[j][2]) - cost[i, j])))

    priority.sort(key=lambda x: x[2], reverse=True)

    prices = np.copy(prices)
    orders = []
    for i, j, v in priority:
        if v >= 0:
            q = int(min(prices[i][1], prices[j][3]))
            if q <= 0:
                continue

            prices[i][1] -= q
            prices[j][3] -= q

            orders.append((i, j, q))

    return orders

def solve_linear(prices, cost, p):
    n = prices.shape[0]
    priority = np.zeros(shape=(n, n))
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            # i buys, j sells
            priority[i, j] = (1-p[i, j])*((prices[i][0] - prices[j][2]) - cost[i, j])

    m = mip.Model(sense=mip.MAXIMIZE)


    q = m.add_var_tensor(shape=(n, n), name="q", var_type=mip.INTEGER)
    m.objective = mip.xsum(q[i, j] * priority[i, j] for i in range(n) for j in range(n) if i != j)

    for i in range(n):
        m.add_constr(mip.xsum(q[i, j] for j in range(n)) <= prices[i][1])
    for j in range(n):
        m.add_constr(mip.xsum(q[i, j] for i in range(n)) <= prices[j][3])

    m.verbose = False
    m.optimize(max_seconds=10)
    orders = [(i, j, q[i, j].x) for i in range(n) for j in range(n) if q[i, j].x != 0]

    return orders


def eval(prices, cost, p, orders1, orders2):
    n = prices.shape[0]

    trials = 1000

    score1 = 0
    score2 = 0
    for _ in range(trials):
        edges = np.random.random(size=(n, n)) >= p
        # edges = np.ones(shape=(n, n))

        bid_q = np.zeros(shape=(n,))
        ask_q = np.zeros(shape=(n,))

        for i, j, q in orders1:
            if i == j:
                continue

            score1 += q * edges[i, j]*((prices[i][0] - prices[j][2]) - cost[i, j])

            bid_q[i] += q
            ask_q[j] += q


        assert (0 <= bid_q).all()
        assert (0 <= ask_q).all()
        assert (bid_q <= prices[:, 1]).all()
        assert (ask_q <= prices[:, 3]).all()

        bid_q = np.zeros(shape=(n,))
        ask_q = np.zeros(shape=(n,))

        for i, j, q in orders2:
            if i == j:
                continue

            score2 += q * edges[i, j]*((prices[i][0] - prices[j][2]) - cost[i, j])

            bid_q[i] += q
            ask_q[j] += q


        assert (0 <= bid_q).all()
        assert (0 <= ask_q).all()
        assert (bid_q <= prices[:, 1]).all()
        assert (ask_q <= prices[:, 3]).all()


    return score1/trials, score2/trials


if __name__ == "__main__":
    n = 3
    while True:
        prices, cost, p = generate(n)
        orders1 = solve_linear(prices, cost, p)
        orders2 = solve_greedy(prices, cost, p)
        score1, score2 = eval(prices, cost, p, orders1, orders2)
        print(f"linear programming: {score1}")
        print(f"greedy programming: {score2}")


        print(abs(score1-score2)/(1+max(score1, score2)))
        if abs(score1-score2)/(1+max(score1, score2)) >= 0.2:
            break
        # n += 1

    print(prices)
    print(cost)
    print(p)

    priority = np.zeros(shape=(n, n))
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            priority[i, j] = (1-p[i, j])*((prices[i][0] - prices[j][2]) - cost[i, j])

    print(priority)

    print(orders1)
    print(orders2)

