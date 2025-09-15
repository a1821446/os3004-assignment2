frames = [{'page': "frame"+str(i), 'last_used': i} for i in range(4)]
print(frames)
print(min(frames, key=lambda f: f['last_used']))