from tasks import add

result = add.delay(4, 6)

print(result.ready())
print(result.result)