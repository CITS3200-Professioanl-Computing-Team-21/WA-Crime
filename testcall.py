import filter

def main():
    name, zone, year, mq, crime = input("Name: "), input("Zone: "), input("Year: "), input("Month/quarter: "), input("Crime: ")
    output = filter.filter(name, zone, year, mq, crime)
    print(output)

main()