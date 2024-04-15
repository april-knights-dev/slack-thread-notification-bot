import json


class ThreadState:
    def __init__(self, filename):
        self.filename = filename
        self.data = self.load_state()

    def load_state(self):
        try:
            with open(self.filename, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_state(self):
        with open(self.filename, "w") as f:
            json.dump(self.data, f, indent=4)

    def get_message_count(self, thread_ts):
        return self.data.get(thread_ts, {}).get("message_count", 0)

    def increment_message_count(self, thread_ts):
        if thread_ts not in self.data:
            self.data[thread_ts] = {"message_count": 0, "last_broadcast_ts": None}
        self.data[thread_ts]["message_count"] += 1
        self.save_state()

    def reset_message_count(self, thread_ts, last_broadcast_ts=None):
        if thread_ts in self.data:
            self.data[thread_ts]["message_count"] = 1
            self.data[thread_ts]["last_broadcast_ts"] = last_broadcast_ts
        else:
            self.data[thread_ts] = {"message_count": 1, "last_broadcast_ts": last_broadcast_ts}
        self.save_state()

    def get_last_broadcast_ts(self, thread_ts):
        return self.data.get(thread_ts, {}).get("last_broadcast_ts")