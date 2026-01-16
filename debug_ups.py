from pysnmp.hlapi import getCmd, SnmpEngine, CommunityData, UdpTransportTarget, ContextData, ObjectType, ObjectIdentity
import sys

# Config matches your successfull CLI test
IP = "10.1.9.224"
COMMUNITY = "s1lentb0b"

# The exact OIDs your main script uses
OIDS = {
    "model": "1.3.6.1.4.1.318.1.1.1.1.1.1.0",
    "status": "1.3.6.1.4.1.318.1.1.1.4.1.1.0",
    # We test just these two first to see if the basic connection works
}

print(f"--- DEBUGGING CONNECTION TO {IP} ---")

try:
    print("Building SNMP Request...")
    
    # This uses the EXACT logic from your main script
    iterator = getCmd(
        SnmpEngine(),
        CommunityData(COMMUNITY, mpModel=0), # mpModel=0 means SNMPv1
        UdpTransportTarget((IP, 161), timeout=3.0, retries=1),
        ContextData(),
        ObjectType(ObjectIdentity(OIDS["model"])),
        ObjectType(ObjectIdentity(OIDS["status"]))
    )

    print("Sending Request...")
    errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

    if errorIndication:
        print(f"!!! SNMP CONNECTION ERROR: {errorIndication}")
    elif errorStatus:
        print(f"!!! SNMP PROTOCOL ERROR: {errorStatus.prettyPrint()}")
    else:
        print("--- SUCCESS! ---")
        print(f"Model: {varBinds[0][1]}")
        print(f"Status Code: {varBinds[1][1]}")

except Exception as e:
    print("\n!!! PYTHON CRASHED !!!")
    import traceback
    traceback.print_exc()
