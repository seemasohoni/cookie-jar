from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Optional
from datetime import datetime, date, timedelta
from pydantic import BaseModel
from models import User, Habit, LogEntry, CategoryEnum

app = FastAPI(title="Cookie Jar API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock database
db = {
    "users": {},
    "habits": {},
    "logs": []
}

# Add some fixture data for tests
user_id = "test-user-1"
habit_id = "test-habit-1"
bad_habit_id = "test-bad-habit"
db["users"][user_id] = User(id=user_id, total_cookies=150, streak_count=5)
db["habits"][habit_id] = Habit(id=habit_id, user_id=user_id, name="Read 20 pages", category=CategoryEnum.GOOD, target_daily=1)
db["habits"][bad_habit_id] = Habit(id=bad_habit_id, user_id=user_id, name="Eat junk food", category=CategoryEnum.BAD, target_daily=0)

class LogHabitRequest(BaseModel):
    habit_id: str
    timestamp: datetime
    trigger_type: str
    mood_tag: Optional[str] = None
    lat_long: Optional[str] = None

class CreateHabitRequest(BaseModel):
    name: str
    category: CategoryEnum
    target_daily: int = 1

@app.post("/habits")
async def create_habit(req: CreateHabitRequest, user_id: str = "test-user-1"):
    habit = Habit(user_id=user_id, name=req.name, category=req.category, target_daily=req.target_daily)
    db["habits"][habit.id] = habit
    return {"status": "success", "habit": habit.model_dump()}

@app.get("/habits")
async def get_habits(user_id: str = "test-user-1"):
    user_habits = [h.model_dump() for h in db["habits"].values() if h.user_id == user_id]
    return user_habits

@app.put("/habits/{habit_id}")
async def update_habit(habit_id: str, req: CreateHabitRequest, user_id: str = "test-user-1"):
    habit = db["habits"].get(habit_id)
    if not habit or habit.user_id != user_id:
        raise HTTPException(status_code=404, detail="Habit not found")
        
    habit.name = req.name
    habit.category = req.category
    habit.target_daily = req.target_daily
    return {"status": "success", "habit": habit.model_dump()}

@app.delete("/habits/{habit_id}")
async def delete_habit(habit_id: str, user_id: str = "test-user-1"):
    if habit_id not in db["habits"] or db["habits"][habit_id].user_id != user_id:
        raise HTTPException(status_code=404, detail="Habit not found")
        
    # Delete the habit
    del db["habits"][habit_id]
    
    # Clean up associated logs
    db["logs"] = [log for log in db["logs"] if log.habit_id != habit_id]
    
    return {"status": "success"}

@app.post("/habits/log")
async def log_habit(req: LogHabitRequest):
    habit = db["habits"].get(req.habit_id)
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    
    log_entry = LogEntry(
        habit_id=req.habit_id,
        timestamp=req.timestamp,
        trigger_type=req.trigger_type,
        mood_tag=req.mood_tag,
        lat_long=req.lat_long
    )
    db["logs"].append(log_entry)
    
    user = db["users"].get(habit.user_id)
    if user:
        if habit.category == CategoryEnum.GOOD:
            # Check if there are other good logs today
            today_logs = [log for log in db["logs"] if log.habit_id == habit.id and log.timestamp.date() == req.timestamp.date()]
            if len(today_logs) == 1:  # First log of the day
                user.streak_count += 1
            user.total_cookies += 1
        elif habit.category == CategoryEnum.BAD:
            # Bad habits don't instantly break the streak for tomorrow, but could reset current streak depending on rules
            # The prompt simply says it shouldn't break the streak logic for tomorrow for 11:59PM
            pass
        
    return {"status": "success", "log_entry": log_entry.model_dump()}

@app.get("/habits/{habit_id}/logs")
async def get_habit_logs(habit_id: str, user_id: str = "test-user-1"):
    habit = db["habits"].get(habit_id)
    if not habit or habit.user_id != user_id:
        raise HTTPException(status_code=404, detail="Habit not found")
        
    habit_logs = [log.model_dump() for log in db["logs"] if log.habit_id == habit_id]
    
    # Sort chronological newest first
    habit_logs.sort(key=lambda x: x["timestamp"], reverse=True)
    return habit_logs

@app.get("/analytics/vulnerability")
async def get_vulnerability_graph(user_id: str = "test-user-1", habit_id: Optional[str] = None, timescale: str = "all"):
    # Returns a Risk Score (0.0 - 1.0) for each of the 24 hours based on bad-habit density
    risk_scores = {str(i): 0.0 for i in range(24)}
    
    # Calculate time boundary based on timescale
    now = datetime.now()
    time_limit = None
    if timescale == "day":
        time_limit = now - timedelta(days=1)
    elif timescale == "week":
        time_limit = now - timedelta(weeks=1)
    elif timescale == "month":
        time_limit = now - timedelta(days=30)
    
    bad_habit_logs = []
    for log in db["logs"]:
        habit = db["habits"].get(log.habit_id)
        if habit and habit.category == CategoryEnum.BAD and habit.user_id == user_id:
            if habit_id is None or habit.id == habit_id:
                # Apply timescale filter if one is set
                if time_limit is None or log.timestamp >= time_limit:
                    bad_habit_logs.append(log)
            
    if not bad_habit_logs:
        return risk_scores
        
    # Calculate density
    hour_counts = {str(i): 0 for i in range(24)}
    max_count = 0
    for log in bad_habit_logs:
        hour = str(log.timestamp.hour)
        hour_counts[hour] += 1
        if hour_counts[hour] > max_count:
            max_count = hour_counts[hour]
            
    for hour, count in hour_counts.items():
        if max_count > 0:
            risk_scores[hour] = count / max_count
            
    return risk_scores

@app.get("/analytics/patterns")
async def get_pattern_analyzer(user_id: str = "test-user-1", habit_id: Optional[str] = None):
    """
    Groups and aggregates triggers by Time of Day and External Trigger Type.
    Returns: { "time_of_day": { "Morning": 5, ... }, "triggers": { "Social Media": 10, ... } }
    """
    logs = []
    for log in db["logs"]:
        habit = db["habits"].get(log.habit_id)
        if habit and habit.user_id == user_id:
            if habit_id is None or habit.id == habit_id:
                logs.append(log)
                
    time_of_day_counts = {"Morning": 0, "Afternoon": 0, "Evening": 0, "Night": 0}
    trigger_counts = {}
    
    for log in logs:
        # Time of day pattern
        hour = log.timestamp.hour
        if 5 <= hour < 12:
            time_of_day_counts["Morning"] += 1
        elif 12 <= hour < 17:
            time_of_day_counts["Afternoon"] += 1
        elif 17 <= hour < 21:
            time_of_day_counts["Evening"] += 1
        else:
            time_of_day_counts["Night"] += 1
            
        # Trigger type pattern
        trigger = log.trigger_type
        if trigger not in trigger_counts:
            trigger_counts[trigger] = 0
        trigger_counts[trigger] += 1
        
    return {
        "time_of_day": time_of_day_counts,
        "triggers": trigger_counts
    }

@app.get("/rewards/status")
async def get_rewards_status(user_id: str):
    user = db["users"].get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    total = user.total_cookies
    progress = total % 100
    next_milestone = ((total // 100) + 1) * 100
    
    return {
        "current_cookies": total,
        "progress_to_next_milestone": next_milestone - total,
        "current_progress": progress,
        "next_milestone_target": 100
    }
