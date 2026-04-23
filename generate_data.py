import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Configuration
NUM_SPACES = 44 # Total number of parking spaces (A, B, C, D, E blocks)
DAYS_HISTORY = 180 # 6 months of data

def generate_parking_data():
    print("Generating synthetic parking data...")
    data = []
    
    # Start date: 6 months ago from today
    start_date = datetime.now() - timedelta(days=DAYS_HISTORY)
    start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    
    current_date = start_date
    end_date = datetime.now()
    
    while current_date <= end_date:
        hour = current_date.hour
        day_of_week = current_date.weekday() # 0: Monday, 6: Sunday
        
        # Base occupancy probability based on time of day (Real-life simulation)
        if 0 <= hour < 7: # Night: Empty
            base_prob = 0.05
        elif 7 <= hour < 9: # Morning rush hour: Filling up
            base_prob = 0.4
        elif 9 <= hour < 16: # Working hours: Mostly full
            base_prob = 0.85
        elif 16 <= hour < 18: # Evening rush hour: Emptying
            base_prob = 0.5
        elif 18 <= hour < 22: # Evening: Partially full
            base_prob = 0.2
        else: # Late night
            base_prob = 0.05
            
        # Weekend adjustment (less predictable, generally lower occupancy)
        if day_of_week >= 5: 
            base_prob = base_prob * 0.4 + 0.1
            
        # Add some random noise (weather, events, etc.)
        noise = np.random.normal(0, 0.1)
        final_prob = np.clip(base_prob + noise, 0, 1)
        
        # Calculate occupied spaces
        occupied = np.random.binomial(NUM_SPACES, final_prob)
        empty = NUM_SPACES - occupied
        
        # Determine specific spots occupied (for potential future use)
        # We just need the total counts for the prediction model right now
        
        data.append({
            'timestamp': current_date,
            'day_of_week': day_of_week,
            'hour': hour,
            'is_weekend': 1 if day_of_week >= 5 else 0,
            'total_spaces': NUM_SPACES,
            'occupied_spaces': occupied,
            'empty_spaces': empty,
            'occupancy_rate': round((occupied / NUM_SPACES) * 100, 2)
        })
        
        # Advance by 1 hour
        current_date += timedelta(hours=1)
        
    df = pd.DataFrame(data)
    
    # Save to CSV
    csv_filename = 'historical_parking_data.csv'
    df.to_csv(csv_filename, index=False)
    print(f"Data generation complete! Saved {len(df)} rows to '{csv_filename}'.")
    return df

if __name__ == "__main__":
    generate_parking_data()