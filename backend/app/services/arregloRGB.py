import numpy as np

def ajustar_matriz_rgb(sent, observed):
    """
    sent/observed: listas de listas [[R,G,B], ...] tamaño N×3
    return: M (3×3) tal que observed ≈ sent @ M
    """
    S = np.asarray(sent, dtype=float)      # N×3
    O = np.asarray(observed, dtype=float)  # N×3
    if S.ndim != 2 or S.shape[1] != 3 or O.shape != S.shape:
        raise ValueError("sent y observed deben ser N×3 y del mismo tamaño")
    M, *_ = np.linalg.lstsq(S, O, rcond=None)  # 3×3
    return M

def predecir_observado(rgb, M):
    return np.clip(np.asarray(rgb, float) @ M, 0, 255)

def comando_para_objetivo(objetivo_rgb, M):
    Minv = np.linalg.pinv(M)
    return np.clip(np.asarray(objetivo_rgb, float) @ Minv, 0, 255)

def ajustar_matriz_rgb_afin(sent, observed):
    S = np.asarray(sent, dtype=float)      # N×3
    O = np.asarray(observed, dtype=float)  # N×3
    if S.ndim != 2 or S.shape[1] != 3 or O.shape != S.shape:
        raise ValueError("sent y observed deben ser N×3 y del mismo tamaño")
    X = np.hstack([S, np.ones((S.shape[0], 1))])  # N×4
    A, *_ = np.linalg.lstsq(X, O, rcond=None)     # 4×3
    M, b = A[:3, :], A[3, :]                      # (3×3), (3,)
    return M, b

def predecir_observado_afin(rgb, M, b):
    return np.clip(np.asarray(rgb, float) @ M + b, 0, 255)

def comando_para_objetivo_afin(objetivo_rgb, M, b):
    Minv = np.linalg.pinv(M)
    return np.clip((np.asarray(objetivo_rgb, float) - b) @ Minv, 0, 255)




"""
254	86	165
90	199	17
61	112	208
49	46	137
33	62	232
71	171	76
103	215	205
1	226	99
224	180	43
209	55	240
216	71	36
250	219	48
60	225	103
68	169	25
215	121	97
240	165	56
102	229	38
64	244	153
201	179	141
54	64	212
"""
"""
190	134	230
79	227	161
40	155	255
80	105	255
1	93	255
50	206	232
46	161	239
0	219	240
190	186	178
172	68	255
244	158	199
188	202	182
0	219	241
36	212	168
201	170	97
199	178	188
60	236	193
1	190	233
173	178	230
30	98	255
"""


sent = [[254, 86, 165], [90, 199, 17], [61, 112, 208], [49, 46, 137], [33, 62, 232], [71, 171, 76], [103, 215, 205], [1, 226, 99], [224, 108, 43], [209, 55, 240], [216, 71, 36], [250, 219, 48], [60, 225, 103], [68, 169, 25], [215, 121, 97], [240, 165, 56], [102, 229, 38], [64, 244, 153], [201, 179, 141], [54, 64, 212]]       # N×3
observed = [[190, 134, 230], [79, 227, 161], [40, 155, 255], [80, 105, 255], [1, 93, 255], [50, 206, 232], [46, 161, 239], [0, 219, 240], [190, 186, 178], [172, 68, 255], [244, 158, 199], [188, 202, 182], [0, 219, 241], [36, 212, 168], [201, 170, 97], [199, 178, 188], [60, 236, 193], [1, 190, 233], [173, 178, 230], [30, 98, 255]]       # N×3

M = ajustar_matriz_rgb(sent, observed)
pred = predecir_observado([120,80,200], M)
to_send = comando_para_objetivo([120,80,200], M)

print(pred)
print(to_send)

# O con sesgo:
M, b = ajustar_matriz_rgb_afin(sent, observed)
pred2 = predecir_observado_afin([120,80,200], M, b)
to_send2 = comando_para_objetivo_afin([-120,80,200], M, b)

print(pred2)
print(to_send2)

