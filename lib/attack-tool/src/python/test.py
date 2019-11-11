import math
import random

min = 0
max = 5

random.seed()
for i in range(10):
    result = math.floor(min + (max - min) * pow(random.random(), 2))
    print(result)