import numpy as np


def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


if __name__ == "__main__":
    A = np.array([2, 1])
    B = np.array([4, 2])
    C = np.array([-2, -1])
    D = np.array([-1, 2])

    print(cosine_similarity(A, B))
    print(cosine_similarity(A, C))
    print(cosine_similarity(A, D))
