import pysnmp.hlapi
print("--- LOOKING INSIDE pysnmp.hlapi ---")
print(dir(pysnmp.hlapi))

try:
    import pysnmp.hlapi.v3arch.sync
    print("\n--- LOOKING INSIDE pysnmp.hlapi.v3arch.sync ---")
    print(dir(pysnmp.hlapi.v3arch.sync))
except ImportError as e:
    print(f"\nCould not load v3arch: {e}")
