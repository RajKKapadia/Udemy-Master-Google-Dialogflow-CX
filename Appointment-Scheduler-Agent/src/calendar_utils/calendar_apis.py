import random
import datetime
from typing import Dict, Any, List

from google.oauth2 import service_account
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import pytz
import gspread

from src import config


WORKING_DAY_W_START_END_TIME = {
    "Monday": {"start": "9:00", "end": "20:00"},
    "Tuesday": {"start": "9:00", "end": "20:00"},
    "Wednesday": {"start": "9:00", "end": "20:00"},
    "Thursday": {"start": "9:00", "end": "20:00"},
}


def get_calendar_service():
    credentials = service_account.Credentials.from_service_account_info(
        info=config.SERVICE_ACCOUNT_JSON,
        scopes=["https://www.googleapis.com/auth/calendar"],
    )
    service = build("calendar", "v3", credentials=credentials)
    return service


service = get_calendar_service()


async def append_to_google_sheet(input_dict: Dict[str, Any]) -> None:
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    credentials = Credentials.from_service_account_info(
        info=config.SERVICE_ACCOUNT_JSON, scopes=scopes
    )
    client = gspread.authorize(credentials)

    sheet = client.open_by_key(config.GOOGLE_SHEET_ID).worksheet("Sheet1")
    existing_headers = sheet.row_values(1)
    row_to_append = []
    for header in existing_headers:
        row_to_append.append(input_dict.get(header, ""))
    sheet.append_row(row_to_append, value_input_option="USER_ENTERED")
    return None


async def get_random_free_slots(
    working_days_w_start_end_time: Dict[str, Any] = WORKING_DAY_W_START_END_TIME,
    timezone: str = "Asia/Kolkata",
) -> List[str]:
    num_days = 7
    now = datetime.datetime.now(tz=pytz.timezone(timezone))
    end_time = now + datetime.timedelta(days=num_days)

    free_slots = []

    events_result = (
        service.events()
        .list(
            calendarId=config.GOOGLE_CALENDAR_ID,
            timeMin=now.isoformat(),
            timeMax=end_time.isoformat(),
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])

    busy_times = []
    for event in events:
        busy_times.append(
            {
                "start": event["start"].get("dateTime"),
                "end": event["end"].get("dateTime"),
            }
        )

    for i in range(num_days):
        date = now + datetime.timedelta(days=i)
        day_name = date.strftime("%A")

        if day_name in working_days_w_start_end_time:
            work_start = datetime.datetime.strptime(
                working_days_w_start_end_time[day_name]["start"], "%H:%M"
            ).time()
            work_end = datetime.datetime.strptime(
                working_days_w_start_end_time[day_name]["end"], "%H:%M"
            ).time()

            slot_time = datetime.datetime.combine(date.date(), work_start).replace(
                tzinfo=pytz.timezone(timezone)
            )
            end_of_day = datetime.datetime.combine(date.date(), work_end).replace(
                tzinfo=pytz.timezone(timezone)
            )

            while slot_time < end_of_day:
                slot_end_time = slot_time + datetime.timedelta(
                    minutes=config.MEETING_TIME
                )
                is_free = True

                for busy in busy_times:
                    busy_start = datetime.datetime.fromisoformat(busy["start"])
                    busy_end = datetime.datetime.fromisoformat(busy["end"])

                    if slot_time < busy_end and slot_end_time > busy_start:
                        is_free = False
                        break

                if is_free:
                    free_slots.append(slot_time.isoformat())

                slot_time += datetime.timedelta(minutes=config.MEETING_TIME)

    random_slots = random.sample(free_slots, min(4, len(free_slots)))
    return random_slots


async def is_slot_free(
    meeting_date: Dict[str, Any],
    meeting_time: Dict[str, Any],
    timezone: str = "Asia/Kolkata",
) -> bool:
    dt = datetime.datetime(
        int(meeting_date["year"]),
        int(meeting_date["month"]),
        int(meeting_date["day"]),
        int(meeting_time["hours"]),
        int(meeting_time["minutes"]),
        int(meeting_time["seconds"]),
        tzinfo=pytz.timezone(timezone),
    )
    slot_end = dt + datetime.timedelta(minutes=config.MEETING_TIME)

    events_result = (
        service.events()
        .list(
            calendarId=config.GOOGLE_CALENDAR_ID,
            timeMin=dt.isoformat(),
            timeMax=slot_end.isoformat(),
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )

    events = events_result.get("items", [])
    return len(events) == 0


async def create_event(
    meeting_date: Dict[str, Any],
    meeting_time: Dict[str, Any],
    timezone: str = "Asia/Kolkata",
):
    dt_start = datetime.datetime(
        int(meeting_date["year"]),
        int(meeting_date["month"]),
        int(meeting_date["day"]),
        int(meeting_time["hours"]),
        int(meeting_time["minutes"]),
        int(meeting_time["seconds"]),
        # tzinfo=pytz.timezone(timezone),
    )
    dt_end = dt_start + datetime.timedelta(minutes=30)

    event = {
        "summary": "Meeting",
        "start": {
            "dateTime": dt_start.isoformat(),
            "timeZone": timezone,
        },
        "end": {
            "dateTime": dt_end.isoformat(),
            "timeZone": timezone,
        },
        "reminders": {
            "useDefault": True,
        },
    }

    event_result = (
        service.events()
        .insert(
            calendarId=config.GOOGLE_CALENDAR_ID,
            body=event,
        )
        .execute()
    )

    return event_result


async def get_free_slots_for_day(
    meeting_date: Dict[str, Any],
    working_days_w_start_end_time: Dict[str, Any] = WORKING_DAY_W_START_END_TIME,
    timezone: str = "Asia/Kolkata",
) -> List[str]:
    # Create the datetime for the given day in the user's timezone
    tz = pytz.timezone(timezone)

    date = datetime.datetime(
        int(meeting_date["year"]), int(meeting_date["month"]), int(meeting_date["day"])
    )
    date = tz.localize(date)

    day_name = date.strftime("%A")

    # Return empty list if it's not a working day
    if day_name not in working_days_w_start_end_time:
        return []

    # Define working hours
    work_start = datetime.datetime.strptime(
        working_days_w_start_end_time[day_name]["start"], "%H:%M"
    ).time()
    work_end = datetime.datetime.strptime(
        working_days_w_start_end_time[day_name]["end"], "%H:%M"
    ).time()

    start_of_day = tz.localize(datetime.datetime.combine(date.date(), work_start))
    end_of_day = tz.localize(datetime.datetime.combine(date.date(), work_end))

    # Fetch events only for that single day
    events_result = (
        service.events()
        .list(
            calendarId=config.GOOGLE_CALENDAR_ID,
            timeMin=start_of_day.isoformat(),
            timeMax=end_of_day.isoformat(),
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])

    busy_times = []
    for event in events:
        busy_times.append(
            {
                "start": event["start"].get("dateTime"),
                "end": event["end"].get("dateTime"),
            }
        )

    free_slots = []
    slot_time = start_of_day

    while slot_time + datetime.timedelta(minutes=config.MEETING_TIME) <= end_of_day:
        slot_end_time = slot_time + datetime.timedelta(minutes=config.MEETING_TIME)
        is_free = True

        for busy in busy_times:
            busy_start = datetime.datetime.fromisoformat(busy["start"])
            busy_end = datetime.datetime.fromisoformat(busy["end"])
            if slot_time < busy_end and slot_end_time > busy_start:
                is_free = False
                break

        if is_free:
            free_slots.append(slot_time.isoformat())

        slot_time += datetime.timedelta(minutes=config.MEETING_TIME)

    random_slots = random.sample(free_slots, min(4, len(free_slots)))
    return random_slots
