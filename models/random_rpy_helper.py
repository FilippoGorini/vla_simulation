# simply return a random roll pitch yaw triad in the terminal

import numpy as np

def generate_random_rpy():
    # Roll (-180 to 180 degrees)
    roll = np.random.uniform(-np.pi, np.pi)
    # Pitch (-90 to 90 degrees to avoid gimbal lock)
    pitch = np.random.uniform(-np.pi/2, np.pi/2)
    # Yaw (-180 to 180 degrees)
    yaw = np.random.uniform(-np.pi, np.pi)
    
    return {'roll': roll, 'pitch': pitch, 'yaw': yaw}

# Example Output
angles = generate_random_rpy()
print(f"{angles['roll']:.4f} {angles['pitch']:.4f} {angles['yaw']:.4f}")


