from datetime import datetime, time
from typing import List, Tuple
def parse_work_hours(schedule_str: str) -> List[Tuple[time, time]]:
    """Parse work hours from string format HH:MM-HH:MM, HH:MM-HH:MM"""
    schedules = []
    parts = [p.strip() for p in schedule_str.split(",")]
    
    if len(parts) > 3:
        raise ValueError("Maximum 3 time intervals are allowed")
        
    for part in parts:
        try:
            start_str, end_str = part.split("-")
            start_time = datetime.strptime(start_str.strip(), "%H:%M").time()
            end_time = datetime.strptime(end_str.strip(), "%H:%M").time()
            
            if start_time >= end_time:
                raise ValueError(
                    f"Start time {start_time} must be before end time {end_time}"
                )
                
            schedules.append((start_time, end_time))
        except ValueError as e:
            raise ValueError(
                f"Invalid time format. Use HH:MM-HH:MM format. Error: {str(e)}"
            )
    
    return schedules

def calculate_non_working_hours(schedule) -> float:
    """Calculate non-working hours for a schedule"""
    working_minutes = 0
    
    # Calculate minutes for each time slot
    if schedule.start_time1 and schedule.end_time1:
        working_minutes += calculate_minutes_between(
            schedule.start_time1,
            schedule.end_time1
        )
    
    if schedule.start_time2 and schedule.end_time2:
        working_minutes += calculate_minutes_between(
            schedule.start_time2,
            schedule.end_time2
        )
    
    if schedule.start_time3 and schedule.end_time3:
        working_minutes += calculate_minutes_between(
            schedule.start_time3,
            schedule.end_time3
        )
    
    # Convert to hours
    working_hours = working_minutes / 60
    return 24 - working_hours

def calculate_minutes_between(start: time, end: time) -> int:
    """Calculate minutes between two time objects"""
    return (
        end.hour * 60 + end.minute
    ) - (
        start.hour * 60 + start.minute
    )
