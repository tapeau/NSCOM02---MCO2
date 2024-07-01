# PING
A simple command-line client-side ping implementation developed in Python as Major Course Output #2 for DLSU NSCOM02 course (T3 2023-2024)

## Members
- John Lorenzo Tapia (S11)
- Harvey Ivan Chan (S12)

## Running the program
Build and run the client with the necessary parameters.

- Parameter 1 (string): The name or address of the server. Must be a string.
- Parameter 2 (int): The amount of echo requests the program will send to the server. Must be a positive integer.
```
python ICMP.py <server> <amount>
```

### Examples:
```
python ICMP.py localhost 4
```
```
python ICMP.py example.com 11
```

## Note regarding ICMP error messages
Some ICMP error messages may not be reported by the program due to the local system's firewall blocking the error message packets. If this occurs, turning off your local system's firewall, or adding a rule in it to allow for ICMP messages, should fix it.

## Additional credits
All additional credits and references can be found at the top of the source file.
