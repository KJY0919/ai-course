class ParkingCalculator:
    @staticmethod
    def time_to_minutes(time_str):
        try:
            hours, minutes = map(int, time_str.split(':'))
            return hours * 60 + minutes
        except (ValueError, AttributeError):
            return None

    @staticmethod
    def calculate_fee(start_min, end_min):
        if start_min is None or end_min is None or end_min <= start_min:
            return 0
            
        total_duration = end_min - start_min
        if total_duration <= 30:
            return 0

        fee = 0
        current_pointer = start_min + 30
        
        while current_pointer < end_min:
            next_pointer = min(current_pointer + 10, end_min)
            mid_time = (current_pointer + next_pointer - 1) / 2
            is_night = 0 <= mid_time < 360
            unit_price = 600 if is_night else 500
            fee += unit_price
            current_pointer = next_pointer

        return min(fee, 20000)
