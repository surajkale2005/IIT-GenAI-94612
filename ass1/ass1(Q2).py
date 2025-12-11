numbers = input("Enter numbers (comma-separated): ")


num_list = numbers.split(",")

even = 0
odd = 0

for n in num_list:
    num = int(n)
    if num % 2 == 0:
        even += 1
    else:
        odd += 1
        
print("Even numbers:", even)
print("Odd numbers:", odd)
