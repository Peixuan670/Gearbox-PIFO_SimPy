class Test_gearbox:
    # Serves like a controller

    # Three different threads:
    # 1. enque on arrival time
    # 2. deque on bw availibilty (tracked here)
    # 3. migration in a forever loop

    # Input pkt trace / pkt stream

    # Output pkt deque trace and stats