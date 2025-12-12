import math_utils


a=(int(input("Enter length of rectangle: ")))
b=(int(input("Enter breadth of rectangle: ")))
c=(int(input("Enter radius of circle: ")))

area_rec=math_utils.calculate_area_of_rectangle(a,b)
area_cir=math_utils.calculate_area_of_circle(c)

print("Area of Rectangle:",area_rec)
print("Area of Circle:",area_cir)