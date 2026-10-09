plans = {
    "free": {
        "price": 0,
        "max_requests_per_day": -1,  # unlimited
        "features": ["basic_analysis", "demo_access"]
    },
    "pro": {
        "price": 29,
        "max_requests_per_day": -1,  # unlimited
        "features": ["EEG processing", "Audio synthesis", "API access"]
    },
    "enterprise": {
        "price": 199,
        "max_requests_per_day": -1,  # unlimited
        "features": ["Distributed nodes", "Realtime analytics", "Priority support"]
    }
}

def get_plan(name: str):
    return plans.get(name, plans["free"])

def check_usage(plan_name: str, usage_today: int):
    plan = get_plan(plan_name)
    limit = plan["max_requests_per_day"]
    if usage_today >= limit:
        return {"allowed": False, "limit": limit}
    return {"allowed": True, "remaining": limit - usage_today}

