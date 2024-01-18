def all_slots_from_peaks(peaks = [(4, 100), (8,500), (12, 1000), (16, 500), (20, 1000), (24,300)]):
    slots = []
    for k in range(len(peaks)):
        (h1, r1) = peaks[k]
        (h2, r2) = peaks[(k+1)%len(peaks)]

        print('h1:', h1, 'h2:', h2)

        diff = r2 - r1
        steps = 2 * (h2 - h1) % 24
        inc = diff / steps

        print('peak', k, ':', (h1, r1), '->', (h2, r2), 'steps: ', steps, 'inc: ', inc) 
    
        for i in range(steps):
            step = r1 + inc * i 
            slots.append(round(step))

    return slots         