import io
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import User, WorkSchedule

async def generate_work_hours_histogram(session: AsyncSession, city: str) -> io.BytesIO:
    # Get all work schedules for the city for today
    today = datetime.now().date()
    schedules = await session.execute(
        select(WorkSchedule)
        .join(User)
        .where(User.city == city)
        .where(WorkSchedule.date == today)
    )
    schedules = schedules.scalars().all()

    # Process schedules into hourly data
    hour_counts = {}
    for schedule in schedules:
        # Process first interval
        if schedule.start_time1 and schedule.end_time1:
            start = schedule.start_time1.hour
            end = schedule.end_time1.hour
            for h in range(start, end):
                hour_counts[h] = hour_counts.get(h, 0) + 1
        
        # Process second interval
        if schedule.start_time2 and schedule.end_time2:
            start = schedule.start_time2.hour
            end = schedule.end_time2.hour
            for h in range(start, end):
                hour_counts[h] = hour_counts.get(h, 0) + 1
        
        # Process third interval
        if schedule.start_time3 and schedule.end_time3:
            start = schedule.start_time3.hour
            end = schedule.end_time3.hour
            for h in range(start, end):
                hour_counts[h] = hour_counts.get(h, 0) + 1

    # Create DataFrame for plotting
    all_hours = list(range(6, 24))  # 6 AM to 11 PM
    counts = [hour_counts.get(h, 0) for h in all_hours]
    df = pd.DataFrame({'Hour': all_hours, 'People Working': counts})

    # Create plot
    plt.figure(figsize=(10, 5))
    plt.bar(df['Hour'], df['People Working'])
    plt.xticks(df['Hour'])
    plt.xlabel('Hour of Day')
    plt.ylabel('Number of People Working')
    plt.title(f'Work Activity by Hour in {city}')
    plt.grid(True)
    plt.tight_layout()

    # Save plot to bytes buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return buf
