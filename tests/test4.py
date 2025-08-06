full_data = [
    {"a": 1, "b": 2},
    {"a": 3, "b": 4}
]

key = "b"

for d in full_data:
    d.pop(key, None)

print(full_data)